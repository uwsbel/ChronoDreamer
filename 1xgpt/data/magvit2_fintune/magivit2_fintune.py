import os
import glob
from pathlib import Path
import numpy as np
from PIL import Image

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
import torch.optim as optim

from magvit2.models.lfqgan import VQModel
from magvit2.config import VQConfig


# ------------------------------
# Dataset
# ------------------------------
class ImageFolderDataset(Dataset):
    def __init__(self, img_dir, transform=None):
        self.img_paths = sorted(
        glob.glob(os.path.join(img_dir, "**", "*.jpg"), recursive=True))
        self.transform = transform

    def __len__(self):
        return len(self.img_paths)

    def __getitem__(self, idx):
        img = Image.open(self.img_paths[idx]).convert("RGB")
        if self.transform:
            img = self.transform(img)
        return img


# ------------------------------
# Training loop
# ------------------------------
def train(
    data_dir="frames",
    ckpt_path="checkpoints/finetuned_epoch10.ckpt",
    save_dir="checkpoints",
    batch_size=8,
    num_epochs=10,
    lr=1e-5,
    device="cuda"
):

    # Transform: resize to 256x256, to tensor, normalize [0,1] → [-1,1]
    transform = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.ToTensor(),  # [0,1]
        transforms.Lambda(lambda x: x * 2 - 1)  # [-1,1]
    ])

    dataset = ImageFolderDataset(data_dir, transform)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True, num_workers=4, pin_memory=True)

    # Load pretrained autoencoder
    model = VQModel(VQConfig(), ckpt_path=ckpt_path).to(device)
    model.train()

    # Loss + optimizer
    criterion = nn.L1Loss()
    optimizer = optim.Adam(model.parameters(), lr=lr)

    os.makedirs(save_dir, exist_ok=True)
    
    save_epoch = 0

    for epoch in range(num_epochs):
        total_loss = 0
        for imgs in dataloader:
            imgs = imgs.to(device)

            # Encode & decode
            quant, _, _, _ = model.encode(imgs)
            recon = model.decode(quant)

            loss = criterion(recon, imgs)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        avg_loss = total_loss / len(dataloader)
        print(f"Epoch [{epoch+1}/{num_epochs}] - Loss: {avg_loss:.6f}")

        # Save checkpoint
        if epoch%20 == 19 :
            ckpt_out = os.path.join(save_dir, f"finetuned_epoch{save_epoch+1}.ckpt")
            torch.save({
                "state_dict": model.state_dict(),
                "epoch": epoch+1,
                "optimizer_state_dict": optimizer.state_dict(),
                "loss": avg_loss,
            }, ckpt_out)
            print(f"Saved checkpoint: {ckpt_out}")
            save_epoch += 1


if __name__ == "__main__":
    train(
        data_dir="exp_data",          # folder with frame_0.jpg ... frame_N.jpg
        ckpt_path="checkpoints/finetuned_epoch10.ckpt",
        save_dir="checkpoints",
        batch_size=8,
        num_epochs=200,
        lr=2e-5,
        device="cuda" if torch.cuda.is_available() else "cpu"
    )

