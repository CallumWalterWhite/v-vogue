# import logging
# import os
# import sys
# import torch
# from app.core.config import Settings
# from app.inference.viton_hd_inference import VitonHDInference
# from app.inference.cloth_segmentation_inference import ClothSegmentationInference
# from app.inference.openpose_inference import OpenPoseInference
# from app.inference.humanparsing_inference import HumanParsingInference
# from app.inference.densepose_inference import DensePoseInference

# cloth_segmentation_inference_runtime: ClothSegmentationInference = None
# openpose_runtime: OpenPoseInference = None
# humanparsing_runtime: HumanParsingInference = None

# def __check_os_path():
#     if os.path.dirname(os.path.dirname(os.path.abspath(__file__))) not in sys.path:
#         sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# def setup_cloth_seg(device):
#     __check_os_path()
#     global cloth_segmentation_inference_runtime
#     cloth_segmentation_inference_runtime = ClothSegmentationInference(device)
    
#     #TODO: add vitonHD inference
    
# def setup_open_pose(device):
#     __check_os_path()
#     global openpose_runtime
#     openpose_runtime = OpenPoseInference()

# def setup_human_parsing(device):
#     __check_os_path()
#     global humanparsing_runtime
#     humanparsing_runtime = HumanParsingInference()

# def setup_densepose(device):
#     __check_os_path()
#     global densepose_runtime
#     densepose_runtime = DensePoseInference()

# def setup_vitonHD(device):
#     __check_os_path()
#     global vitonHD_runtime
#     vitonHD_runtime = VitonHDInference(device)
    
# def get_densepose_runtime():
#     if densepose_runtime:
#         return densepose_runtime
#     raise Exception("Densepose runtime not initialized")

# def get_cloth_segmentation_inference_runtime():
#     if cloth_segmentation_inference_runtime:
#         return cloth_segmentation_inference_runtime
#     raise Exception("Cloth segmentation runtime not initialized")

# def get_openpose_runtime():
#     if openpose_runtime:
#         return openpose_runtime
#     raise Exception("Openpose runtime not initialized")

# def get_humanparsing_runtime():
#     if humanparsing_runtime:
#         return humanparsing_runtime
#     raise Exception("Human parsing runtime not initialized")

# def get_vitonHD_runtime():
#     if vitonHD_runtime:
#         return vitonHD_runtime
#     raise Exception("VitonHD runtime not initialized")

# logger = logging.getLogger(__name__)

# def setup_all_inference_models(settings: Settings):
#     device = 'cuda' if torch.cuda.is_available() else 'cpu'
#     logger.info(f"Using device: {device}")

#     if settings.LOAD_VITONHD_MODEL:
#         setup_vitonHD(device)

#     if settings.LOAD_CLOTH_SEGMENTATION_MODEL:
#         setup_cloth_seg(device)
    
#     if settings.LOAD_OPEN_POSE_MODEL:
#         setup_open_pose(device)
    
#     if settings.LOAD_HUMAN_PARSING_MODEL:
#         setup_human_parsing(device)

#     if settings.LOAD_DENPOSE_MODEL:
#         setup_densepose(device)
import os
import sys
import torch
import logging
from typing import Optional

from app.inference.viton_hd_inference import VitonHDInference
from app.inference.cloth_segmentation_inference import ClothSegmentationInference
from app.inference.openpose_inference import OpenPoseInference
from app.inference.humanparsing_inference import HumanParsingInference
from app.inference.densepose_inference import DensePoseInference
from app.core.config import Settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InferenceManager:
    vitonHD_runtime: Optional[VitonHDInference] = None
    cloth_segmentation_runtime: Optional[ClothSegmentationInference] = None
    openpose_runtime: Optional[OpenPoseInference] = None
    humanparsing_runtime: Optional[HumanParsingInference] = None
    densepose_runtime: Optional[DensePoseInference] = None

    @classmethod
    def __check_os_path(cls):
        """
        Ensures that the parent directory is in sys.path.
        """
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if parent_dir not in sys.path:
            sys.path.append(parent_dir)
            logger.debug(f"Added {parent_dir} to sys.path")

    @classmethod
    def setup_cloth_seg(cls, device: str):
        cls.__check_os_path()
        if cls.cloth_segmentation_runtime is None:
            try:
                cls.cloth_segmentation_runtime = ClothSegmentationInference(device)
                logger.info("Cloth Segmentation model initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize Cloth Segmentation model: {e}")
                raise

    @classmethod
    def setup_open_pose(cls, device: str):
        cls.__check_os_path()
        if cls.openpose_runtime is None:
            try:
                cls.openpose_runtime = OpenPoseInference()
                logger.info("OpenPose model initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize OpenPose model: {e}")
                raise

    @classmethod
    def setup_human_parsing(cls, device: str):
        cls.__check_os_path()
        if cls.humanparsing_runtime is None:
            try:
                cls.humanparsing_runtime = HumanParsingInference()
                logger.info("Human Parsing model initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize Human Parsing model: {e}")
                raise

    @classmethod
    def setup_densepose(cls, device: str):
        cls.__check_os_path()
        if cls.densepose_runtime is None:
            try:
                cls.densepose_runtime = DensePoseInference()
                logger.info("DensePose model initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize DensePose model: {e}")
                raise

    @classmethod
    def setup_vitonHD(cls, device: str):
        cls.__check_os_path()
        if cls.vitonHD_runtime is None:
            try:
                cls.vitonHD_runtime = VitonHDInference(device)
                logger.info("VitonHD model initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize VitonHD model: {e}")
                raise

    @classmethod
    def get_densepose_runtime(cls) -> DensePoseInference:
        if cls.densepose_runtime:
            return cls.densepose_runtime
        logger.error("DensePose runtime not initialized.")
        raise RuntimeError("DensePose runtime not initialized.")

    @classmethod
    def get_cloth_segmentation_runtime(cls) -> ClothSegmentationInference:
        if cls.cloth_segmentation_runtime:
            return cls.cloth_segmentation_runtime
        logger.error("Cloth Segmentation runtime not initialized.")
        raise RuntimeError("Cloth Segmentation runtime not initialized.")

    @classmethod
    def get_openpose_runtime(cls) -> OpenPoseInference:
        if cls.openpose_runtime:
            return cls.openpose_runtime
        logger.error("OpenPose runtime not initialized.")
        raise RuntimeError("OpenPose runtime not initialized.")

    @classmethod
    def get_humanparsing_runtime(cls) -> HumanParsingInference:
        if cls.humanparsing_runtime:
            return cls.humanparsing_runtime
        logger.error("Human Parsing runtime not initialized.")
        raise RuntimeError("Human Parsing runtime not initialized.")

    @classmethod
    def get_vitonHD_runtime(cls) -> VitonHDInference:
        if cls.vitonHD_runtime:
            return cls.vitonHD_runtime
        logger.error("VitonHD runtime not initialized.")
        raise RuntimeError("VitonHD runtime not initialized.")

    @classmethod
    def setup_all_inference_models(cls, settings: Settings):
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        logger.info(f"Using device: {device}")

        if settings.LOAD_VITONHD_MODEL:
            cls.setup_vitonHD(device)

        if settings.LOAD_CLOTH_SEGMENTATION_MODEL:
            cls.setup_cloth_seg(device)
        
        if settings.LOAD_OPEN_POSE_MODEL:
            cls.setup_open_pose(device)
        
        if settings.LOAD_HUMAN_PARSING_MODEL:
            cls.setup_human_parsing(device)

        if settings.LOAD_DENPOSE_MODEL:
            cls.setup_densepose(device)
