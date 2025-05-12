# pose_detector.py
import cv2
import mediapipe as mp
import math
import numpy as np

class PoseDetector:
    def __init__(self, mode=False, smooth=True, detection_con=0.5, track_con=0.5):
        self.mode = mode
        self.smooth = smooth
        self.detection_con = detection_con
        self.track_con = track_con

        self.mp_draw = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=self.mode,
            smooth_landmarks=self.smooth,
            min_detection_confidence=self.detection_con,
            min_tracking_confidence=self.track_con
        )
        self.results = None

    def find_pose(self, img, draw=True):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(img_rgb)
        if self.results.pose_landmarks and draw:
            self.mp_draw.draw_landmarks(
                img, self.results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS)
        return img

    def find_position(self, img, draw=True):
        self.lm_list = []
        if self.results.pose_landmarks:
            for idx, lm in enumerate(self.results.pose_landmarks.landmark):
                h, w = img.shape[:2]
                cx, cy = int(lm.x * w), int(lm.y * h)
                self.lm_list.append([idx, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)
        return self.lm_list

    def find_angle(self, img, p1, p2, p3, draw=True):
        if len(self.lm_list) < max(p1, p2, p3) + 1:
            return 0

        x1, y1 = self.lm_list[p1][1:]
        x2, y2 = self.lm_list[p2][1:]
        x3, y3 = self.lm_list[p3][1:]

        vector1 = (x1 - x2, y1 - y2)
        vector2 = (x3 - x2, y3 - y2)

        dot_product = vector1[0] * vector2[0] + vector1[1] * vector2[1]
        cross_product = vector1[0] * vector2[1] - vector1[1] * vector2[0]
        angle = math.degrees(math.atan2(cross_product, dot_product))
        angle = abs(angle)  # 取绝对值表示0-180度范围

        if draw:
            cv2.line(img, (x1, y1), (x2, y2), (255, 255, 255), 3)
            cv2.line(img, (x3, y3), (x2, y2), (255, 255, 255), 3)
            for x, y in [(x1, y1), (x2, y2), (x3, y3)]:
                cv2.circle(img, (x, y), 10, (0, 0, 255), cv2.FILLED)
                cv2.circle(img, (x, y), 15, (0, 0, 255), 2)
            cv2.putText(img, f"{int(angle)}°", (x2 - 50, y2 + 50),
                        cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
        return angle


class VideoAnalyzer(PoseDetector):
    def __init__(self, config=None, **kwargs):
        super().__init__(**kwargs)
        # Use provided config or import default if none provided
        if config is None:
            from .config import Config
            self.key_angles = Config.KEY_ANGLES
            self.normalization_joints = Config.NORMALIZATION_JOINTS
        else:
            self.key_angles = config.KEY_ANGLES
            self.normalization_joints = getattr(config, 'NORMALIZATION_JOINTS', [11, 12, 23])
        
        # Store the config object for other methods to access
        self.config = config

    def process_video(self, video_path, skip_frames=2):
        """
        提取视频中的姿势特征序列
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"无法打开视频文件：{video_path}")
        sequence = []
        frame_count = 0

        while cap.isOpened():
            success, img = cap.read()
            if not success:
                break

            # 如果需要跳帧，可取消注释下面的代码
            # if frame_count % (skip_frames+1) != 0:
            #     frame_count += 1
            #     continue

            self.find_pose(img)
            lm_list = self.find_position(img, draw=False)
            angles = self._get_frame_angles(img)

            frame_data = {
                'landmarks': lm_list,
                'angles': angles,
                'norm_landmarks': self._normalize_landmarks(lm_list)
            }
            sequence.append(frame_data)
            frame_count += 1

        cap.release()
        return sequence

    def _normalize_landmarks(self, lm_list):
        """
        使用新的归一化方法，参考 Compare_pose.py 中的 l2_normalize 算法：
        1. 根据所有关键点计算包围盒（box = [min_x, min_y, max_x, max_y]）
        2. 计算 temp_x = (max_x - min_x)/2, temp_y = (max_y - min_y)/2
        3. 若 temp_x <= temp_y，则 sub_x = min_x - (temp_y - temp_x), sub_y = min_y；
           否则，sub_x = min_x, sub_y = min_y - (temp_x - temp_y)
        4. 对每个关键点，计算偏移坐标 (x - sub_x, y - sub_y)，并将所有偏移坐标组成一维向量，
           计算该向量的 L2 范数 norm_val，再除以 norm_val得到归一化后的坐标。
        """
        if len(lm_list) == 0:
            return []
        
        # 对于并非所有关键点存在的情况，返回空列表
        if not all(k in [lm[0] for lm in lm_list] for k in self.normalization_joints):
            return []

        # 计算包围盒
        xs = [lm[1] for lm in lm_list]
        ys = [lm[2] for lm in lm_list]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        # 计算半宽和半高
        temp_x = (max_x - min_x) / 2
        temp_y = (max_y - min_y) / 2

        # 按照 Compare_pose.py 的处理（这里 box[0]=min_x, box[1]=min_y, box[2]=max_x, box[3]=max_y，且 min_x<=max_x, min_y<=max_y）
        if temp_x <= temp_y:
            sub_x = min_x - (temp_y - temp_x)
            sub_y = min_y
        else:
            sub_x = min_x
            sub_y = min_y - (temp_x - temp_y)

        # 对每个关键点，计算相对于 sub_x, sub_y 的偏移
        normalized_coords = []
        for lm in lm_list:
            norm_x = lm[1] - sub_x
            norm_y = lm[2] - sub_y
            normalized_coords.append([norm_x, norm_y])
        # 将所有坐标平铺成一维向量，计算 L2 范数
        flat_coords = [coord for pair in normalized_coords for coord in pair]
        norm_val = np.linalg.norm(flat_coords)
        if norm_val == 0:
            return normalized_coords
        # 对每个关键点进行归一化
        normalized = [[x / norm_val, y / norm_val] for (x, y) in normalized_coords]
        return normalized

    def _get_frame_angles(self, img):
        return {k: self.find_angle(img, *v, draw=False) for k, v in self.key_angles.items()}
    
    # Adding the draw_bone function from visualization
    def draw_bone(self, img, landmarks, connections, color=(0, 255, 0)):
        """
        绘制骨架连接
        :param img: 图像
        :param landmarks: 关节点坐标列表
        :param connections: 连接关节点的索引对列表
        :param color: 绘制颜色
        """
        for connection in connections:
            x1, y1 = landmarks[connection[0]]
            x2, y2 = landmarks[connection[1]]
            cv2.line(img, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
    
    # Adding the function to process overlap video
    def _process_overlap_video(self, std_video, pat_video, dtw_result, output_video_path, video_path_pat, save_lowest_scores=True, config=None):
        """
        生成带有患者骨架和标准骨架的视频（标准骨架通过平移与患者肩关节对齐）。
        
        :param std_video: 标准视频的骨架数据
        :param pat_video: 患者视频的骨架数据
        :param dtw_result: DTW对齐结果
        :param output_video_path: 输出视频路径
        :param video_path_pat: 患者视频路径
        :param save_lowest_scores: 是否保存得分最低的帧
        """
        try:
            try:
                from .evaluation import detect_action_stages
                from .visualization import generate_video_with_selected_frames
            except ImportError:
                from evaluation import detect_action_stages
                from visualization import generate_video_with_selected_frames
            
            # Auto-detect action stages
            stages = detect_action_stages(pat_video)
            
            # Use the config from parameters or instance
            use_config = config if config else self.config
            
            # Call the standalone function from visualization.py
            generate_video_with_selected_frames(
                std_video,
                pat_video,
                dtw_result,
                output_video_path,
                video_path_pat,
                stages,
                config=use_config,
                save_lowest_scores=save_lowest_scores
            )
            
        except Exception as e:
            print(f"Error in _process_overlap_video: {str(e)}")
            raise
