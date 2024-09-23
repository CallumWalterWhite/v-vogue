import numpy as np
import torch
from PIL import Image
from openpose.annotator.util import HWC3
from openpose.annotator.openpose import OpenposeDetector
from app.core.config import settings
from app.inference.base_inference import BaseInference

class OpenPoseKeypoins:
    def __init__(self, pose_keypoints_2d: list) -> None:
        self.pose_keypoints_2d = pose_keypoints_2d
    pose_keypoints_2d: list = []

    def __json__(self):
        return {
            'pose_keypoints_2d': self.pose_keypoints_2d
        }

class OpenPoseInference(BaseInference):
    def __init__(self):
        super().__init__(settings.IMAGE_SIZING_H, settings.IMAGE_SIZING_W)
        self.preprocessor = OpenposeDetector()
        self.preprocessor.body_estimation.model.to('cuda' if torch.cuda.is_available() else 'cpu')
    
    def infer(self, file_path: str, resolution: int = None) -> OpenPoseKeypoins:
        if resolution is None:
            resolution = self.IMG_W
        input_image = Image.open(file_path)
        input_image = input_image.resize((self.IMG_W, self.IMG_H))  # Resize as a PIL image
        input_image = np.asarray(input_image)  # Convert to numpy array after resizing
        with torch.no_grad():
            input_image = HWC3(input_image)
            # input_image = resize_image(input_image, resolution)
            # H, W, C = input_image.shape
            # assert (H == 512 and W == 384), f'Incorrect input image shape {H}x{W}' #TODO: This bad boy really only works with 512x384 images... smh, its because of get_mask_location in utils_stableviton.py
            pose, detected_map = self.preprocessor(input_image, hand_and_face=False)

            candidate = pose['bodies']['candidate']
            subset = pose['bodies']['subset'][0][:18]
            for i in range(18):
                if subset[i] == -1:
                    candidate.insert(i, [0, 0])
                    for j in range(i, 18):
                        if (subset[j]) != -1:
                            subset[j] += 1
                elif subset[i] != i:
                    candidate.pop(i)
                    for j in range(i, 18):
                        if (subset[j]) != -1:
                            subset[j] -= 1

            candidate = candidate[:18]

            for i in range(18):
                candidate[i][0] *= self.IMG_W
                candidate[i][1] *= self.IMG_H

            keypoints: OpenPoseKeypoins = OpenPoseKeypoins(candidate)
        return keypoints