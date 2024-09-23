import io
from PIL import Image

def convert_pil_image_to_bytes(image: Image) -> bytes:
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

def convert_bytes_to_pil_image(image_bytes: bytes) -> Image:
    return Image.open(io.BytesIO(image_bytes))