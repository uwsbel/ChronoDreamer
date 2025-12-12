import json
from dataclasses import dataclass

from genie.factorization_utils import nth_root


@dataclass
class GenieConfig:
    num_layers: int
    num_heads: int
    d_model: int
    T: int = 16  # temporal sequence length
    S: int = 1024  # spatial sequence length, e.g. 32x32
    image_vocab_size: int = 65536  # image_vocab_size: number of distinct image tokens;
    # actual model vocab size is larger to include special (e.g. mask) tokens.
    use_mup: bool = False

    # Contact prediction
    contact_vocab_size: int = 65536  # vocab size for contact tokens (adjust if different)
    contact_loss_weight: float = 2.0  # weight for contact prediction loss

    # Joint angles prediction
    num_joint_channels: int = 4  # number of joint angle channels (theta_0, theta_1, theta_2, theta_3)
    joint_loss_weight: float = 1.0  # weight for joint angle prediction loss

    # Factorization for large vocabs (e.g. Open-MAGVIT2)
    num_factored_vocabs: int = 1
    factored_vocab_size: int = None

    # MaskGIT training (all arbitrary numbers)
    max_corrupt_rate: float = 0.2  # Corrupt all tokens, uniform between [0, max_corrupt_rate]
    # Case 1: MLM training.
    # Case 2: Not standard MLM, `non_mlm`. Some earlier frames are left unmasked, as in Copilot4D.
    non_mlm_ratio: float = 0.5
    num_prompt_frames: int = 8

    # Attention
    qkv_bias: bool = False
    proj_bias: bool = True
    attn_drop: float = 0.0
    qk_norm: bool = True

    # MLP
    mlp_ratio: float = 4.0
    mlp_drop: float = 0.0
    mlp_bias: bool = True

    def save_pretrained(self, json_path):
        with open(json_path, "w") as f:
            json.dump(vars(self), f)

    @classmethod
    def from_pretrained(cls, json_path):
        with open(json_path, "r") as f:
            config = json.load(f)

        return cls(**config)

    def shallow_copy(self):
        return GenieConfig(**vars(self))

    def __post_init__(self):
        self.factored_vocab_size = nth_root(self.image_vocab_size, self.num_factored_vocabs)
