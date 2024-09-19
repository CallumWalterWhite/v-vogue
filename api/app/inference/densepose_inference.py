from pathlib import Path
import sys
import os
from detectron2.projects.DensePose.apply_net_gradio import DensePose4Gradio
import numpy as np
from PIL import Image

class DensePoseInference():
    IMG_H = 512
    IMG_W = 384
    def __init__(self):
        ##TODO: move url to settings
        self.densepose_model_hd = DensePose4Gradio(
            cfg='../detectron2/projects/DensePose/configs/densepose_rcnn_R_50_FPN_s1x.yaml',
            model='https://dl.fbaipublicfiles.com/densepose/densepose_rcnn_R_50_FPN_s1x/165712039/model_final_162be9.pkl',
            #TODO: add the model to the repo
        )
    
    def infer(self, file_path: str) -> bytes:
        input_image = Image.open(file_path)
        input_image = input_image.resize((self.IMG_W, self.IMG_H))
        model_parse = self.densepose_model_hd.execute(input_image)
        return model_parse