import os

from tqdm import tqdm
from PIL import Image
import numpy as np

import warnings

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

import torch
import torch.nn.functional as F
import torchvision.transforms as transforms

from cloth_segmentation.cloth_segmentation.data.base_dataset import Normalize_image
from cloth_segmentation.cloth_segmentation.utils.saving_utils import load_checkpoint_mgpu

from cloth_segmentation.cloth_segmentation.networks import U2NET

device = os.environ.get("DEVICE", "cuda")

image_dir = os.environ.get("INPUT_DIR", "input_images")
result_dir = os.environ.get("OUTPUT_DIR", "output_images")

os.makedirs(result_dir, exist_ok=True)

checkpoint_path = "checkpoint_u2net.pth"
do_palette = True


def get_palette(num_cls):
    """Returns the color map for visualizing the segmentation mask.
    Args:
        num_cls: Number of classes
    Returns:
        The color map
    """
    n = num_cls
    palette = [0] * (n * 3)
    for j in range(0, n):
        lab = j
        palette[j * 3 + 0] = 0
        palette[j * 3 + 1] = 0
        palette[j * 3 + 2] = 0
        i = 0
        while lab:
            palette[j * 3 + 0] |= ((lab >> 0) & 1) << (7 - i)
            palette[j * 3 + 1] |= ((lab >> 1) & 1) << (7 - i)
            palette[j * 3 + 2] |= ((lab >> 2) & 1) << (7 - i)
            i += 1
            lab >>= 3
    return palette


transforms_list = []
transforms_list += [transforms.ToTensor()]
transforms_list += [Normalize_image(0.5, 0.5)]
transform_rgb = transforms.Compose(transforms_list)

net = U2NET(in_ch=3, out_ch=4)
net = load_checkpoint_mgpu(net, checkpoint_path)
net = net.to(device)
net = net.eval()

palette = get_palette(4)




def get_mask_array(img):
    img = img.convert("RGB")
    # img = img.resize((768, 768), resample=Image.BICUBIC)
    img.thumbnail((768, 768), Image.LANCZOS)
    image_tensor = transform_rgb(img)
    image_tensor = torch.unsqueeze(image_tensor, 0)

    output_tensor = net(image_tensor.to(device))
    output_tensor = F.log_softmax(output_tensor[0], dim=1)
    output_tensor = torch.max(output_tensor, dim=1, keepdim=True)[1]
    output_tensor = torch.squeeze(output_tensor, dim=0)
    output_tensor = torch.squeeze(output_tensor, dim=0)
    output_arr = output_tensor.cpu().numpy()
    return output_arr



if __name__=="__main__":
    images_list = sorted(os.listdir(image_dir))
    images_list = [x for x in images_list if x!=".keep"]
    pbar = tqdm(total=len(images_list))


    for image_name in images_list:
        img = Image.open(os.path.join(image_dir, image_name))
        output_arr = get_mask_array(img)

        output_img = Image.fromarray(output_arr.astype("uint8"), mode="L")
        if do_palette:
            output_img.putpalette(palette)
        output_img.save(os.path.join(result_dir, image_name[:-3] + "png"))
        img.save(os.path.join(result_dir, image_name[:-4] + "_orig.png"))
        pbar.update(1)

    pbar.close()
