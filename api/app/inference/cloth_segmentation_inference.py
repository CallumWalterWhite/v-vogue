import os
import torch
from cloth_segmentation.networks.u2net import U2NET
from cloth_segmentation.inference import infer as segmentation_infer
from app.core.config import settings

class ClothSegmentationInference():
    def __init__(self, device):
        self.device = device
        cloth_segmentation_model = U2NET(in_ch=3, out_ch=4)
        if not os.path.isfile(settings.CLOTH_SEGMENTATION_MODEL_PATH):
            raise FileNotFoundError(f"Checkpoint file not found: {settings.CLOTH_SEGMENTATION_MODEL_PATH}")
        checkpoint = torch.load(settings.CLOTH_SEGMENTATION_MODEL_PATH, map_location=device)
        cloth_segmentation_model.load_state_dict(checkpoint.get('state_dict', checkpoint), strict=False)
        self.cloth_segmentation_model = cloth_segmentation_model.to(device)
        self.cloth_segmentation_model.eval()
    
    def infer(self, file_path: str) -> bytes:
        return segmentation_infer(self.cloth_segmentation_model, self.device, file_path)