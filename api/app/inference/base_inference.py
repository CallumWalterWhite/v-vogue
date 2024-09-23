class BaseInference:
    IMG_H = 1024
    IMG_W = 768
    def __init__(self, image_h=1024, image_w=768):
        self.IMG_H = image_h
        self.IMG_W = image_w