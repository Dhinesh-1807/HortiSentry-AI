import torch
import torch.nn as nn
from torchvision.models import mobilenet_v3_small, MobileNet_V3_Small_Weights
import logging

logger = logging.getLogger(__name__)

class HortiSentryMobileNetV3(nn.Module):
    """
    Generic PyTorch Transfer Learning Architecture based on MobileNetV3 Small.
    Supports configurable N-class classification heads for crop disease identification.
    """

    def __init__(self, num_classes: int = 4, pretrained: bool = True, freeze_features: bool = False):
        super(HortiSentryMobileNetV3, self).__init__()
        self.num_classes = num_classes
        self.pretrained = pretrained

        if pretrained:
            try:
                weights = MobileNet_V3_Small_Weights.DEFAULT
                self.backbone = mobilenet_v3_small(weights=weights)
                logger.info("Loaded pretrained MobileNetV3 Small ImageNet weights.")
            except Exception as e:
                logger.warning(f"Could not download/load pretrained weights ({e}). Initializing randomly.")
                self.backbone = mobilenet_v3_small(weights=None)
                self.pretrained = False
        else:
            self.backbone = mobilenet_v3_small(weights=None)

        if freeze_features:
            for param in self.backbone.features.parameters():
                param.requires_grad = False
            logger.info("Froze MobileNetV3 feature extractor layers.")

        # Replace final classifier layer with N-class output head
        # MobileNetV3 Small classifier structure:
        # (0): Linear(in_features=576, out_features=1024, bias=True)
        # (1): Hardswish()
        # (2): Dropout(p=0.2, inplace=True)
        # (3): Linear(in_features=1024, out_features=1000, bias=True)
        in_features = self.backbone.classifier[3].in_features
        self.backbone.classifier[3] = nn.Linear(in_features, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.backbone(x)

    def unfreeze(self):
        """Unfreeze all layers for end-to-end fine tuning."""
        for param in self.parameters():
            param.requires_grad = True
        logger.info("Unfroze all MobileNetV3 layers for fine-tuning.")

class TomatoMobileNetV3(HortiSentryMobileNetV3):
    """Specialized MobileNetV3 Small for Tomato disease classification (4 classes)."""
    def __init__(self, num_classes: int = 4, pretrained: bool = True, freeze_features: bool = False):
        super(TomatoMobileNetV3, self).__init__(num_classes=num_classes, pretrained=pretrained, freeze_features=freeze_features)

class PotatoMobileNetV3(HortiSentryMobileNetV3):
    """Specialized MobileNetV3 Small for Potato disease classification (3 classes)."""
    def __init__(self, num_classes: int = 3, pretrained: bool = True, freeze_features: bool = False):
        super(PotatoMobileNetV3, self).__init__(num_classes=num_classes, pretrained=pretrained, freeze_features=freeze_features)
