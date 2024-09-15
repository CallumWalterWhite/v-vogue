import os
import sys
import torch
from app.inference.cloth_segmentation_inference import ClothSegmentationInference

from app.openpose.run_openpose import OpenPose

cloth_segmentation_inference_runtime: ClothSegmentationInference = None

def setup_cloth_seg():
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    global cloth_segmentation_inference_runtime
    cloth_segmentation_inference_runtime = ClothSegmentationInference(device)
    
    #TODO: add vitonHD inference
    
def setup_open_pose():
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    global openpose_runtime
    openpose_runtime = OpenPose()
    
    
def get_cloth_segmentation_inference_runtime():
    return cloth_segmentation_inference_runtime