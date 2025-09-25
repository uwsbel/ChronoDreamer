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
from lpips import LPIPS  # pip install lpips


# ------------------------------
# Dataset
# ------------------------------
class ImageFolderDataset(Dataset):
    def __init__(self, img_dir, transform=None):
        self.img_paths = sorted(
            glob.glob(os.path.join(img_dir, "**", "*.jpg"), recursive=True)
        )
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
    ckpt_path="checkpoints/finetuned_epoch20.ckpt",
    save_dir="checkpoints",
    batch_size=8,
    num_epochs=10,
    lr=1e-5,
    device="cuda",
    freeze_codebook=True
):

    # Transform: resize to 256x256, to tensor, normalize [0,1] → [-1,1]
    transform = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.ToTensor(),
        transforms.Lambda(lambda x: x * 2 - 1)  # [-1,1]
    ])

    dataset = ImageFolderDataset(data_dir, transform)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True, num_workers=4, pin_memory=True)

    # Load pretrained autoencoder
    model = VQModel(VQConfig()).to(device)
    state = torch.load(ckpt_path, map_location=device)
    if "state_dict" in state:
        model.load_state_dict(state["state_dict"], strict=False)
    else:
        model.load_state_dict(state, strict=False)

    model.train()

    # Freeze codebook embeddings if requested
    if freeze_codebook:
        for param in model.quantize.parameters():
            param.requires_grad = False

    # Losses
    l1_loss = nn.L1Loss()
    perceptual_loss = LPIPS(net="vgg").to(device)  # LPIPS with VGG backbone

    def recon_loss(recon, target):
        loss_l1 = l1_loss(recon, target)
        loss_perc = perceptual_loss(recon, target).mean()
        return loss_l1 + 0.2 * loss_perc  # weight perceptual loss

    # Optimizer (only trainable params)
    optimizer = optim.AdamW(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=lr,
        betas=(0.9, 0.999),
        weight_decay=1e-6
    )

    os.makedirs(save_dir, exist_ok=True)

    for epoch in range(num_epochs):
        total_loss = 0
        for imgs in dataloader:
            imgs = imgs.to(device)

            # Forward: safer to call model(imgs)
            recon, _, _ = model(imgs)

            loss = recon_loss(recon, imgs)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        avg_loss = total_loss / len(dataloader)
        print(f"Epoch [{epoch+1}/{num_epochs}] - Loss: {avg_loss:.6f}")

        # Save checkpoint every 20 epochs
        if (epoch + 1) % 20 == 0:
            ckpt_out = os.path.join(save_dir, f"finetuned_epoch{epoch+1}.ckpt")
            torch.save({
                "state_dict": model.state_dict(),
                "epoch": epoch+1,
                "optimizer_state_dict": optimizer.state_dict(),
                "loss": avg_loss,
            }, ckpt_out)
            print(f"Saved checkpoint: {ckpt_out}")


if __name__ == "__main__":
    train(
        data_dir="exp_data",          # folder with images
        ckpt_path="checkpoints/finetuned_epoch20.ckpt",
        save_dir="checkpoints",
        batch_size=6,
        num_epochs=200,
        lr=1e-4,
        device="cuda" if torch.cuda.is_available() else "cpu",
        freeze_codebook=True
    )

