from humanparsing.run_parsing import Parsing
from PIL import Image
from app.core.config import settings
from app.inference.base_inference import BaseInference

class HumanParsingInference(BaseInference):
    def __init__(self):
        super().__init__(settings.IMAGE_SIZING_H, settings.IMAGE_SIZING_W)
        self.parser = Parsing(0)
    
    def infer(self, file_path: str) -> bytes:
        input_image = Image.open(file_path)
        input_image = input_image.resize((self.IMG_W, self.IMG_H))  # Resize as a PIL image
        # input_image = np.asarray(input_image)  # Convert to numpy array after resizing
        model_parse = self.parser(input_image)
        return model_parse