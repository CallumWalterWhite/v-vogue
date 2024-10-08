import os
import copy
import cv2
import numpy as np
from collections import OrderedDict
from cloth_segmentation.cloth_segmentation import ROOT_DIR
import torch


def load_checkpoint(model, checkpoint_path):
    checkpoint_path = os.path.join(ROOT_DIR, checkpoint_path)
    if not os.path.exists(checkpoint_path):
        raise Exception("----No checkpoints at given path----")
    model.load_state_dict(torch.load(checkpoint_path, map_location=torch.device("cpu")))
    print("----checkpoints loaded from path: {}----".format(checkpoint_path))
    return model


def load_checkpoint_mgpu(model, checkpoint_path):
    checkpoint_path = os.path.join(ROOT_DIR, checkpoint_path)
    if not os.path.exists(checkpoint_path):
        raise Exception("----No checkpoints at given path----")
    model_state_dict = torch.load(checkpoint_path, map_location=torch.device("cpu"))
    model.load_state_dict(model_state_dict)
    print("----checkpoints loaded from path: {}----".format(checkpoint_path))
    return model


def save_checkpoint(model, save_path):
    save_path = os.path.join(ROOT_DIR, save_path)
    print(save_path)
    if not os.path.exists(os.path.dirname(save_path)):
        os.makedirs(os.path.dirname(save_path))
    torch.save(model.state_dict(), save_path)


def save_checkpoints(opt, itr, net):
    save_checkpoint(
        net,
        os.path.join(opt.save_dir, "checkpoints", "itr_{:08d}_u2net.pth".format(itr)),
    )
