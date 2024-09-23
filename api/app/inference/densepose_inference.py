from detectron2.projects.DensePose.apply_net_gradio import DensePose4Gradio
from app.inference.base_inference import BaseInference
from PIL import Image
from app.core.config import settings

class DensePoseInference(BaseInference):
    def __init__(self):
        super().__init__(settings.IMAGE_SIZING_H, settings.IMAGE_SIZING_W)
        ##TODO: move url to settings
        self.densepose_model_hd = DensePose4Gradio(
            cfg='../detectron2/projects/DensePose/configs/densepose_rcnn_R_50_FPN_s1x.yaml',
            model='https://dl.fbaipublicfiles.com/densepose/densepose_rcnn_R_50_FPN_s1x/165712039/model_final_162be9.pkl',
            #TODO: add the model to the repo
        )
    
    def infer(self, file_path: str) -> Image:
        input_image = Image.open(file_path)
        input_image = input_image.resize((self.IMG_W, self.IMG_H))
        model_parse = self.densepose_model_hd.execute(input_image)
        return model_parse