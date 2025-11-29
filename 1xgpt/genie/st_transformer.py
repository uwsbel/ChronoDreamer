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
        self.spatial_attn = SelfAttention(
            num_heads=num_heads,
            d_model=d_model,
            qkv_bias=qkv_bias,
            proj_bias=proj_bias,
            qk_norm=qk_norm,
            use_mup=use_mup,
            attn_drop=attn_drop,
        )

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
        
        # REMOVED: action projections and gates

    def forward(self, x_TSC: Tensor) -> Tensor:  # Simplified!
        B, T, S, D = x_TSC.shape  # S = S_original + 1 (includes action token)
        
        # Spatial attention - action token participates in attention
        x_BSC = rearrange(x_TSC, 'B T S C -> (B T) S C')
        x_BSC = x_BSC + self.spatial_attn(self.norm1(x_BSC))
        x_TSC = rearrange(x_BSC, '(B T) S C -> B T S C', B=B, T=T)

        # Temporal attention - action tokens attend across time
        x_TC = rearrange(x_TSC, 'B T S C -> (B S) T C')
        x_TC = x_TC + self.temporal_attn(x_TC, causal=True)
        x_TSC = rearrange(x_TC, '(B S) T C -> B T S C', B=B, S=S)

        # MLP
        x_TSC = x_TSC + self.mlp(self.norm2(x_TSC))
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

    def forward(self, tgt):  # Simplified!
        x = tgt
        for layer in self.layers:
            x = layer(x)
        return x