from torch import nn, Tensor
from einops import rearrange
import torch

from genie.attention import SelfAttention
from genie.config import GenieConfig  # Add this import


class Mlp(nn.Module):
    def __init__(
        self,
        d_model: int,
        mlp_ratio: float = 4.0,
        mlp_bias: bool = True,
        mlp_drop: float = 0.0,
    ) -> None:
        super().__init__()
        hidden_dim = int(d_model * mlp_ratio)
        self.fc1 = nn.Linear(d_model, hidden_dim, bias=mlp_bias)
        self.act = nn.GELU()
        self.fc2 = nn.Linear(hidden_dim, d_model, bias=mlp_bias)
        self.drop = nn.Dropout(mlp_drop)

    def forward(self, x: Tensor) -> Tensor:
        x = self.drop(self.act(self.fc1(x)))
        x = self.drop(self.fc2(x))
        return x


class STBlock(nn.Module):
    # See Figure 4 of https://arxiv.org/pdf/2402.15391.pdf
    def __init__(
        self,
        num_heads: int,
        d_model: int,
        qkv_bias: bool = False,
        proj_bias: bool = True,
        qk_norm: bool = True,
        use_mup: bool = True,
        attn_drop: float = 0.0,
        mlp_ratio: float = 4.0,
        mlp_bias: bool = True,
        mlp_drop: float = 0.0,
    ) -> None:
        super().__init__()
        self.norm1 = nn.Identity() if qk_norm else nn.LayerNorm(d_model, eps=1e-05)
        # sequence dim is over each frame's 16x16 patch tokens
        self.spatial_attn = SelfAttention(
            num_heads=num_heads,
            d_model=d_model,
            qkv_bias=qkv_bias,
            proj_bias=proj_bias,
            qk_norm=qk_norm,
            use_mup=use_mup,
            attn_drop=attn_drop,
        )

        # sequence dim is over time sequence (16)
        self.temporal_attn = SelfAttention(
            num_heads=num_heads,
            d_model=d_model,
            qkv_bias=qkv_bias,
            proj_bias=proj_bias,
            qk_norm=qk_norm,
            use_mup=use_mup,
            attn_drop=attn_drop,
        )
        
        self.norm2 = nn.Identity() if qk_norm else nn.LayerNorm(d_model, eps=1e-05)
        self.mlp = Mlp(d_model=d_model, mlp_ratio=mlp_ratio, mlp_bias=mlp_bias, mlp_drop=mlp_drop)
        
        # Separate projections for history and future actions
        self.history_action_proj = nn.Linear(3, d_model // 2)
        self.future_action_proj = nn.Linear(3, d_model // 2)
        
        # Gates to control action influence
        self.history_gate = nn.Parameter(torch.zeros(1))
        self.future_gate = nn.Parameter(torch.zeros(1))

    def forward(self, x_TSC: Tensor, history_actions=None, future_actions=None) -> Tensor:
        # x_TSC: (B, T, S, d_model)
        B, T, S, D = x_TSC.shape
        
        # Spatial attention - reshape to process all spatial tokens across all frames
        x_BSC = rearrange(x_TSC, 'B T S C -> (B T) S C')  # Treat each frame independently
        x_BSC = x_BSC + self.spatial_attn(self.norm1(x_BSC))
        x_TSC = rearrange(x_BSC, '(B T) S C -> B T S C', B=B, T=T)

        # Temporal attention - reshape to process temporal dimension
        x_TC = rearrange(x_TSC, 'B T S C -> (B S) T C')  # Process temporal for each spatial location
        x_TC = x_TC + self.temporal_attn(x_TC, causal=True)
        x_TSC = rearrange(x_TC, '(B S) T C -> B T S C', B=B, S=S)

        # Prepare MLP input with action conditioning
        mlp_input = self.norm2(x_TSC)
        
        # Apply action conditioning BEFORE MLP
        if history_actions is not None and future_actions is not None:
            num_history = history_actions.shape[1]
            num_future = future_actions.shape[1]
            
            # Initialize action modulation tensor
            action_modulation = torch.zeros_like(mlp_input)
            
            # Process history frames (apply to first num_history frames)
            if num_history > 0 and num_history <= T:
                history_emb = self.history_action_proj(history_actions)  # (B, num_history, d_model//2)
                history_emb = history_emb.unsqueeze(2).expand(-1, -1, S, -1)  # (B, num_history, S, d_model//2)
                history_modulation = torch.sigmoid(self.history_gate) * history_emb
                
                # Apply to first num_history frames, first half of d_model
                action_modulation[:, :num_history, :, :D//2] = history_modulation
                
            # Process future frames (apply to frames after history)
            if num_future > 0 and num_history + num_future <= T:
                future_emb = self.future_action_proj(future_actions)  # (B, num_future, d_model//2)
                future_emb = future_emb.unsqueeze(2).expand(-1, -1, S, -1)  # (B, num_future, S, d_model//2)
                future_modulation = torch.sigmoid(self.future_gate) * future_emb
                
                # Apply to frames after history, second half of d_model
                action_modulation[:, num_history:num_history+num_future, :, D//2:] = future_modulation
        
            # Add action modulation to MLP input
            mlp_input = mlp_input + action_modulation
    
        # Apply MLP
        x_TSC = x_TSC + self.mlp(mlp_input)
        return x_TSC


class STTransformerDecoder(nn.Module):
    def __init__(self, config: GenieConfig):
        super().__init__()
        self.layers = nn.ModuleList([STBlock(
            num_heads=config.num_heads,
            d_model=config.d_model,
            qkv_bias=config.qkv_bias,
            proj_bias=config.proj_bias, 
            qk_norm=config.qk_norm,
            use_mup=config.use_mup,
            attn_drop=config.attn_drop,
            mlp_ratio=config.mlp_ratio,
            mlp_bias=config.mlp_bias,
            mlp_drop=config.mlp_drop,
        ) for _ in range(config.num_layers)])

    def forward(self, tgt, history_actions=None, future_actions=None):
        x = tgt
        for layer in self.layers:
            x = layer(x, history_actions=history_actions, future_actions=future_actions)
        return x
