import os
import sys
import torch
from app.inference.cloth_segmentation_inference import ClothSegmentationInference
from app.inference.openpose_inference import OpenPoseInference
from app.inference.hunmanparsing_inference import HumanParsingInference

cloth_segmentation_inference_runtime: ClothSegmentationInference = None
openpose_runtime: OpenPoseInference = None
humanparsing_runtime: HumanParsingInference = None

def setup_cloth_seg():
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    global cloth_segmentation_inference_runtime
    cloth_segmentation_inference_runtime = ClothSegmentationInference(device)
    
    #TODO: add vitonHD inference
    
def setup_open_pose():
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    global openpose_runtime
    openpose_runtime = OpenPoseInference()

def setup_human_parsing():
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    global humanparsing_runtime
    humanparsing_runtime = HumanParsingInference()
    
    
def get_cloth_segmentation_inference_runtime():
    return cloth_segmentation_inference_runtime

def get_openpose_runtime():
    return openpose_runtime

def get_humanparsing_runtime():
    return humanparsing_runtime