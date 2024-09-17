import os
import sys
import torch
from app.inference.viton_hd_inference import VitonHDInference
from app.inference.cloth_segmentation_inference import ClothSegmentationInference
from app.inference.openpose_inference import OpenPoseInference
from app.inference.hunmanparsing_inference import HumanParsingInference
from app.inference.densepose_inference import DensePoseInference

cloth_segmentation_inference_runtime: ClothSegmentationInference = None
openpose_runtime: OpenPoseInference = None
humanparsing_runtime: HumanParsingInference = None

def __check_os_path():
    if os.path.dirname(os.path.dirname(os.path.abspath(__file__))) not in sys.path:
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def setup_cloth_seg():
    __check_os_path()
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    global cloth_segmentation_inference_runtime
    cloth_segmentation_inference_runtime = ClothSegmentationInference(device)
    
    #TODO: add vitonHD inference
    
def setup_open_pose():
    __check_os_path()
    global openpose_runtime
    openpose_runtime = OpenPoseInference()

def setup_human_parsing():
    __check_os_path()
    global humanparsing_runtime
    humanparsing_runtime = HumanParsingInference()

def setup_densepose():
    __check_os_path()
    global densepose_runtime
    densepose_runtime = DensePoseInference()

def setup_vitonHD():
    __check_os_path()
    global vitonHD_runtime
    vitonHD_runtime = VitonHDInference()
    
def get_densepose_runtime():
    if densepose_runtime:
        return densepose_runtime
    raise Exception("Densepose runtime not initialized")

def get_cloth_segmentation_inference_runtime():
    if cloth_segmentation_inference_runtime:
        return cloth_segmentation_inference_runtime
    raise Exception("Cloth segmentation runtime not initialized")

def get_openpose_runtime():
    if openpose_runtime:
        return openpose_runtime
    raise Exception("Openpose runtime not initialized")

def get_humanparsing_runtime():
    if humanparsing_runtime:
        return humanparsing_runtime
    raise Exception("Human parsing runtime not initialized")

def get_vitonHD_runtime():
    if vitonHD_runtime:
        return vitonHD_runtime
    raise Exception("VitonHD runtime not initialized")