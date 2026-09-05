import random
import numpy as np
import torch
import logging

logger = logging.getLogger(__name__)

def set_seed(seed: int = 42) -> None:
    """Set deterministic random seeds across Python, NumPy, and PyTorch."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
    logger.info(f"Set random seed: {seed}")

def get_device() -> torch.device:
    """Detect and return appropriate torch device (CUDA GPU or CPU)."""
    if torch.cuda.is_available():
        device = torch.device("cuda")
        logger.info(f"Using GPU device: {torch.cuda.get_device_name(0)}")
    else:
        device = torch.device("cpu")
        logger.info("CUDA GPU unavailable. Operating on CPU.")
    return device
