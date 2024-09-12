import os
from PIL import Image
import numpy as np
import torch
import torch.nn.functional as F
import torchvision.transforms as transforms
import cv2
import io
from cloth_segmentation.data.base_dataset import Normalize_image

def infer(net, device, image_path) -> bytes:
    transforms_list = [transforms.ToTensor(), Normalize_image(0.5, 0.5)]
    transform_rgb = transforms.Compose(transforms_list)

    transform_2 = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ])
    # palette = get_palette(4)
    img = Image.open(image_path).convert('RGB')
    img_size = img.size

    # Resize the image and mask together to ensure they align
    img = img.resize((768, 768), Image.BICUBIC)
    image_tensor = transform_rgb(img)
    image_tensor_l = transform_2(img)
    image_tensor = torch.unsqueeze(image_tensor, 0)  # [1, 3, H, W]

    output_tensor = net(image_tensor.to(device))
    output_tensor = F.log_softmax(output_tensor[0], dim=1)
    output_tensor = torch.max(output_tensor, dim=1, keepdim=True)[1]
    output_tensor = torch.squeeze(output_tensor, dim=0)
    output_tensor = torch.squeeze(output_tensor, dim=0)
    output_arr = output_tensor.cpu().numpy()

    # Create a binary mask where clothes are set to True
    mask = np.isin(output_arr, [1, 2, 3])

    # Ensure the mask is the same size as the image tensor
    mask_resized = cv2.resize(mask.astype(np.uint8), (image_tensor.shape[3], image_tensor.shape[2]), interpolation=cv2.INTER_NEAREST)

    # Convert the 2D mask into a 3D mask by replicating across the color channels
    mask_3d = np.stack([mask_resized] * 3, axis=0)  # [3, H, W]

    # Convert the image tensor to a NumPy array
    image_tensor_np = image_tensor_l.cpu().numpy()  # [3, H, W]

    # Apply the mask: set clothes to black
    image_tensor_np[mask_3d == 1] = -1  # Black color in normalized [-1, 1] space

    # Denormalize image to [0, 255]
    image_tensor_np = ((image_tensor_np + 1) * 127.5).astype(np.uint8)

    # Convert back to PIL Image for saving or displaying
    output_image = image_tensor_np.transpose(1, 2, 0)  # [H, W, 3]
    output_img: Image = Image.fromarray(output_image)
    output_img = output_img.resize(img_size, Image.BICUBIC)

    img_byte_arr = io.BytesIO()
    output_img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

    # output_img.save(new_image_path) #might need to revert to this
