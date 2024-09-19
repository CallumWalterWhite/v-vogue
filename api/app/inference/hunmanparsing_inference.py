from humanparsing.run_parsing import Parsing
import numpy as np
from PIL import Image
from utils_stableviton import get_mask_location, get_batch, tensor2img, center_crop

class HumanParsingInference():
    IMG_H = 512
    IMG_W = 384
    def __init__(self):
        self.parser = Parsing(0)
    
    def infer(self, file_path: str) -> bytes:
        input_image = Image.open(file_path)
        input_image = input_image.resize((self.IMG_W, self.IMG_H))  # Resize as a PIL image
        # input_image = np.asarray(input_image)  # Convert to numpy array after resizing
        model_parse = self.parser(input_image)
        return model_parse