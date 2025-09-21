import cv2
import os
import random

# Folder where your videos are stored
video_dir = "videos"
output_dir = "scaled_videos"
os.makedirs(output_dir, exist_ok=True)

# Pick a random video
videos = [f for f in os.listdir(video_dir) if f.lower().endswith((".mp4", ".avi", ".mov", ".mkv"))]
if not videos:
    raise FileNotFoundError("No videos found in the folder!")

video_file = random.choice(videos)
print(f"Selected video: {video_file}")

# Open video
cap = cv2.VideoCapture(os.path.join(video_dir, video_file))
if not cap.isOpened():
    raise IOError("Error opening video file")

# Get original FPS
fps = cap.get(cv2.CAP_PROP_FPS)
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
out_path = os.path.join(output_dir, f"scaled_{video_file}")
out = cv2.VideoWriter(out_path, fourcc, fps, (256, 256))

# Resize each frame
while True:
    ret, frame = cap.read()
    if not ret:
        break
    resized = cv2.resize(frame, (256, 256))
    out.write(resized)

cap.release()
out.release()
print(f"Saved scaled video to {out_path}")

