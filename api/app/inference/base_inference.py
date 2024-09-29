class BaseInference:
    IMG_H = 512
    IMG_W = 384
    def __init__(self, image_h=512, image_w=384):
        self.IMG_H = image_h
        self.IMG_W = image_w