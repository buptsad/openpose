# ────────── visualization.py  (minimal‑change version) ──────────
import cv2
import numpy as np
import os
import logging

# Get a logger for this module
logger = logging.getLogger(__name__)

# ----------------- 画一根骨架线的工具 -----------------
def draw_bone(img, landmarks, connections, color=(0, 255, 0)):
    """
    img            : BGR 图
    landmarks      : [(x, y), ...]  已是“要画”的坐标
    connections    : [(idx1, idx2), ...]
    """
    for idx1, idx2 in connections:
        x1, y1 = landmarks[idx1]
        x2, y2 = landmarks[idx2]
        cv2.line(img,
                 (int(x1), int(y1)),
                 (int(x2), int(y2)),
                 color, 2, cv2.LINE_AA)

# ----------------- 主函数 -----------------
def generate_video_with_selected_frames(std_video,
                                        pat_video,
                                        dtw_result,
                                        output_video_path,
                                        video_path_pat,
                                        stages,
                                        config,
                                        save_lowest_scores=True):
    """
    只把【硬编码索引】替换为从 Config 读取：
        • 锚点：config.NORMALIZATION_JOINTS[0]
        • 骨架：config.KEY_ANGLES
    其余算法与最早版本 1:1 保持一致
    """
    # 如需最低分帧，可保留 evaluation；否则可删
    try:
        from .evaluation import select_lowest_score_frames
    except ImportError:
        def select_lowest_score_frames(*args, **kwargs):
            return []
    lowest_score_frames = select_lowest_score_frames(dtw_result, stages)

    # ---------- 打开被测视频 ----------
    cap_pat = cv2.VideoCapture(video_path_pat)
    if not cap_pat.isOpened():
        raise IOError(f"无法打开视频 {video_path_pat}")

    fps   = cap_pat.get(cv2.CAP_PROP_FPS)
    width = int(cap_pat.get(cv2.CAP_PROP_FRAME_WIDTH))
    height= int(cap_pat.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc= cv2.VideoWriter_fourcc(*'XVID')
    out   = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

    # ---------- 从 DTW 构建帧映射 ----------
    pat_to_std = {pat_idx: std_idx for std_idx, pat_idx in dtw_result['alignment_path']}

    frame_idx, save_id = 0, 1
    anchor_id = config.NORMALIZATION_JOINTS[0]   # ← 唯一锚点（替代旧的 11）
    logger.info(f"锚点 ID: {anchor_id}")
    logger.info(f"Normalization joints: {config.NORMALIZATION_JOINTS}")

    while cap_pat.isOpened():
        ok_pat, img_pat = cap_pat.read()
        if not ok_pat or frame_idx >= len(pat_video):
            break

        # 取患者 & 对应标准帧
        pat_frame = pat_video[frame_idx]
        std_idx = pat_to_std.get(frame_idx, 0)
        std_idx = min(std_idx, len(std_video) - 1)
        std_frame = std_video[std_idx]

        # ---------- 平移（单锚点差值，原逻辑） ----------
        pat_anchor = np.array(pat_frame['landmarks'][anchor_id][1:])
        std_anchor = np.array(std_frame['landmarks'][anchor_id][1:])
        translation = pat_anchor - std_anchor

        # ---------- 提取坐标 ----------
        pat_landmarks = [(lm[1], lm[2]) for lm in pat_frame['landmarks']]
        std_landmarks = [(lm[1] + translation[0], lm[2] + translation[1])
                         for lm in std_frame['landmarks']]

        # ---------- 绘制骨架 ----------
        for joints in config.KEY_ANGLES.values():
            j1, j2, j3 = joints
            draw_bone(img_pat, pat_landmarks, [(j1, j2), (j2, j3)], color=(255, 0, 0))  # 患者：蓝红
            draw_bone(img_pat, std_landmarks, [(j1, j2), (j2, j3)], color=(0, 255, 0))  # 标准：绿色

        # ---------- 保存最低得分帧 ----------
        if save_lowest_scores and frame_idx in [f[0] for f in lowest_score_frames]:
            low_dir = os.path.join(os.path.dirname(output_video_path), "low_score_frames")
            os.makedirs(low_dir, exist_ok=True)
            cv2.imwrite(os.path.join(low_dir, f"frame_{save_id}.jpg"), img_pat)
            save_id += 1

        out.write(img_pat)
        frame_idx += 1

    cap_pat.release()
    out.release()
    print(f"✅ 已输出：{output_video_path}")
# ─────────────── End of visualization.py ───────────────
