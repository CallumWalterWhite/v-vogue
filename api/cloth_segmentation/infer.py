import os
import shutil
from tqdm.notebook import tqdm
from PIL import Image
import numpy as np
import torch
import torch.nn.functional as F
import torchvision.transforms as transforms
import cv2

from data.base_dataset import Normalize_image
from utils.saving_utils import load_checkpoint_mgpu
from networks import U2NET

device = 'cuda'

# Create directories if they don't exist
image_dir = 'input_images'
result_dir = 'output_images'
checkpoint_path = 'trained_checkpoint/checkpoint_u2net.pth'


if not os.path.exists(image_dir):
    os.makedirs(image_dir)
if not os.path.exists(result_dir):
    os.makedirs(result_dir)

# Clear output directory before processing
for file in os.listdir(result_dir):
    file_path = os.path.join(result_dir, file)
    try:
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
    except Exception as e:
        print(f'Failed to delete {file_path}. Reason: {e}')

# Clear input directory before uploading new images
# for file in os.listdir(image_dir):
#     file_path = os.path.join(image_dir, file)
#     try:
#         if os.path.isfile(file_path) or os.path.islink(file_path):
#             os.unlink(file_path)
#         elif os.path.isdir(file_path):
#             shutil.rmtree(file_path)
#     except Exception as e:
#         print(f'Failed to delete {file_path}. Reason: {e}')

def get_palette(num_cls):
    """ Returns the color map for visualizing the segmentation mask. """
    n = num_cls
    palette = [0] * (n * 3)
    for j in range(0, n):
        lab = j
        palette[j * 3 + 0] = 0
        palette[j * 3 + 1] = 0
        palette[j * 3 + 2] = 0
        i = 0
        while lab:
            palette[j * 3 + 0] |= (((lab >> 0) & 1) << (7 - i))
            palette[j * 3 + 1] |= (((lab >> 1) & 1) << (7 - i))
            palette[j * 3 + 2] |= (((lab >> 2) & 1) << (7 - i))
            i += 1
            lab >>= 3
    return palette

transforms_list = [transforms.ToTensor(), Normalize_image(0.5, 0.5)]
transform_rgb = transforms.Compose(transforms_list)

transform_2 = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
])
        

net = U2NET(in_ch=3, out_ch=4)

def load_checkpoint_mgpu(model, checkpoint_path):
    """ Load checkpoint for multi-GPU training """
    if not os.path.isfile(checkpoint_path):
        raise FileNotFoundError(f"Checkpoint file not found: {checkpoint_path}")

    # Load checkpoint
    checkpoint = torch.load(checkpoint_path, map_location='cpu')

    # Load state dict
    model.load_state_dict(checkpoint.get('state_dict', checkpoint), strict=False)
    return model

net = load_checkpoint_mgpu(net, checkpoint_path)
net = net.to(device)
net = net.eval()

palette = get_palette(4)

def get_palette(num_cls):
    """ Returns the color map for visualizing the segmentation mask. """
    n = num_cls
    palette = [0] * (n * 3)
    for j in range(0, n):
        lab = j
        palette[j * 3 + 0] = 0
        palette[j * 3 + 1] = 0
        palette[j * 3 + 2] = 0
        i = 0
        while lab:
            palette[j * 3 + 0] |= (((lab >> 0) & 1) << (7 - i))
            palette[j * 3 + 1] |= (((lab >> 1) & 1) << (7 - i))
            palette[j * 3 + 2] |= (((lab >> 2) & 1) << (7 - i))
            i += 1
            lab >>= 3
    return palette

palette = get_palette(4)

# Process images
images_list = sorted(os.listdir(os.path.join(image_dir)))
for image_name in images_list:
    img = Image.open(os.path.join(image_dir, image_name)).convert('RGB')
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
    output_img = Image.fromarray(output_image)
    
    # Resize the output image back to the original image size
    output_img = output_img.resize(img_size, Image.BICUBIC)
    
    # Save the result
    output_img.save(os.path.join(result_dir, image_name[:-4] + '_generated_overlay.png'))
