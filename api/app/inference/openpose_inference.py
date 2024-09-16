import os
import numpy as np
import torch
from PIL import Image
from openpose.annotator.util import resize_image, HWC3
from openpose.annotator.openpose import OpenposeDetector

class OpenPoseKeypoins:
    def __init__(self, pose_keypoints_2d: list) -> None:
        self.pose_keypoints_2d = pose_keypoints_2d
    pose_keypoints_2d: list = []

    def __json__(self):
        return {
            'pose_keypoints_2d': self.pose_keypoints_2d
        }

class OpenPoseInference():
    IMG_H = 1024
    IMG_W = 768
    def __init__(self):
        self.preprocessor = OpenposeDetector()
    
    def infer(self, file_path: str, resolution=384) -> OpenPoseKeypoins:
        input_image = np.asarray(Image.open(file_path))
        input_image = input_image.resize((self.IMG_W, self.IMG_H))
        with torch.no_grad():
            input_image = HWC3(input_image)
            input_image = resize_image(input_image, resolution)
            H, W, C = input_image.shape
            # assert (H == 512 and W == 384), f'Incorrect input image shape {H}x{W}'
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
                candidate[i][0] *= 384
                candidate[i][1] *= 512

            keypoints: OpenPoseKeypoins = OpenPoseKeypoins(candidate)
        return keypoints