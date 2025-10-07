import cv2
import torch
import numpy as np
import json
from pathlib import Path
from tqdm import tqdm
from einops import rearrange

from magvit2.models.lfqgan import VQModel
from magvit2.config import VQConfig

# -------------------------------
# Settings
# -------------------------------
video_path = "test-vid-2.mp4"
ckpt_path = "checkpoints/finetuned_epoch90.ckpt"
out_dir = Path("external_data")
out_dir.mkdir(parents=True, exist_ok=True)
out_bin = out_dir / "video_0.bin"
out_meta = out_dir / "metadata.json"
batch_size = 8
resize_hw = (256, 256)

# -------------------------------
# Load tokenizer
# -------------------------------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
tokenizer = VQModel(VQConfig()).to(device).eval()
state = torch.load(ckpt_path, map_location=device)
if "state_dict" in state:
    tokenizer.load_state_dict(state["state_dict"], strict=False)
else:
    tokenizer.load_state_dict(state, strict=False)

# -------------------------------
# Count frames
# -------------------------------
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    raise FileNotFoundError(f"Could not open {video_path}")

num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
frame_rate = float(cap.get(cv2.CAP_PROP_FPS))
if frame_rate <= 0:
    print("Warning: Invalid frame rate. Setting to default (30.0)")
    frame_rate = 30.0

# Test encode one dummy frame to infer latent H,W
test_frame = torch.zeros(1, 3, *resize_hw).to(device)
with torch.no_grad():
    quant, _, _, _ = tokenizer.encode(test_frame)
latent_h, latent_w = quant.shape[2], quant.shape[3]

# Create memmap for token IDs (uint32)
video_data = np.memmap(out_bin, dtype=np.uint32, mode="w+",
                       shape=(num_frames, latent_h, latent_w))

# -------------------------------
# Encode frames
# -------------------------------
frame_idx, frames = 0, []
for _ in tqdm(range(1), desc="Encoding frames"):
    ret, frame = cap.read()
    if not ret or frame is None or frame.size == 0:
        print(f"Warning: Skipping invalid frame at index {frame_idx}")
        continue

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = cv2.resize(frame, resize_hw)
    frame = frame.astype(np.float32) / 255.0
    tensor = torch.from_numpy(frame).permute(2, 0, 1)
    frames.append(tensor)

    if len(frames) == batch_size:
        batch = torch.stack(frames).to(device)
        with torch.no_grad():
            # Normalize to [-1,1]
            quant, _, _, _ = tokenizer.encode(batch * 2 - 1)
            # Convert to token IDs (B,H,W), each entry in [0, 2^bits)
            token_ids = tokenizer.quantize.bits_to_indices(
                quant.permute(0, 2, 3, 1) > 0
            ).cpu().numpy().astype(np.uint32)

        video_data[frame_idx:frame_idx + token_ids.shape[0]] = token_ids
        frame_idx += token_ids.shape[0]
        frames = []

# Handle leftover frames
if frames:
    batch = torch.stack(frames).to(device)
    original_batch = batch.clone()  # Store the original batch for comparison
    with torch.no_grad():
        quant, _, _, _ = tokenizer.encode(batch * 2 - 1)
        token_ids = tokenizer.quantize.bits_to_indices(
            quant.permute(0, 2, 3, 1) > 0
        ).cpu().numpy().astype(np.uint32)

    video_data[frame_idx:frame_idx + token_ids.shape[0]] = token_ids
    frame_idx += token_ids.shape[0]
    
print(token_ids.shape)
print(token_ids)

print(quant)
print(quant.shape)

# ATTEMPT TO RECONSTRUCT

# -------------------------------
# DECODE
# -------------------------------
with torch.no_grad():
    # Convert numpy array to torch tensor
    token_ids_tensor = torch.from_numpy(token_ids).long().to(device)
    
    # Convert token IDs back to quantized latents
    # With this corrected version:
    # Step 1: Convert indices to bits using corrected indices_to_bits
    bits = tokenizer.quantize.indices_to_bits(token_ids_tensor.flatten())
    # Step 2: Reshape to match original quantized shape
    bits = bits.view(token_ids_tensor.shape[0], token_ids_tensor.shape[1], token_ids_tensor.shape[2], tokenizer.quantize.codebook_dim)
    # Step 3: Convert bits to quantized values (-1 or 1)
    quant_reconstructed = bits.float() * 2.0 - 1.0
    # Step 4: Reshape to (B, C, H, W) format
    quant_reconstructed = quant_reconstructed.permute(0, 3, 1, 2)
    
    # Set print options to show full tensor
    torch.set_printoptions(threshold=float('inf'), linewidth=200, precision=6)
    
    print("Original quant:")
    print(quant)
    print("Original quant shape:", quant.shape)
    
    print("\nReconstructed quant:")
    print(quant_reconstructed)
    print("Reconstructed quant shape:", quant_reconstructed.shape)
    
    # Reset print options to default
    torch.set_printoptions(profile="default")
    
    # Check if they match
    quant_diff = torch.abs(quant - quant_reconstructed).max()
    print(f"\nMax difference: {quant_diff:.6f}")
    
    if quant_diff < 1e-6:
        print("✅ Perfect reconstruction in latent space!")
        
        # Now decode back to image
        reconstructed_frames = tokenizer.decode(quant_reconstructed)
           
        # Normalize from [-1,1] to [0,1]
        reconstructed_frames = (reconstructed_frames + 1) / 2
        reconstructed_frames = torch.clamp(reconstructed_frames, 0, 1)

        # Scale to [0,255] and save images
        # Original frame
        original_np = (original_batch[0].permute(1, 2, 0).cpu().numpy() * 255).astype(np.uint8)
        original_bgr = cv2.cvtColor(original_np, cv2.COLOR_RGB2BGR)
        cv2.imwrite("original_frame.png", original_bgr)
        
        # Reconstructed frame
        reconstructed_np = (reconstructed_frames[0].permute(1, 2, 0).cpu().numpy() * 255).astype(np.uint8)
        reconstructed_bgr = cv2.cvtColor(reconstructed_np, cv2.COLOR_RGB2BGR)
        cv2.imwrite("reconstructed_frame.png", reconstructed_bgr)
        
        print("✅ Saved original_frame.png and reconstructed_frame.png")

        # Get the original frame - use the stored original batch
        original_frame = original_batch[0]  # First frame from the original batch
        
        print("\nOriginal frame shape:", original_frame.shape)
        print("\nReconstructed frame shape:", reconstructed_frames.shape)

        print("original frame")
        print(original_frame)

        print("reconstructed frame")  
        print(reconstructed_frames[0])  # First reconstructed frame

cap.release()
print("\n🎬 Frame reconstruction test completed!")
