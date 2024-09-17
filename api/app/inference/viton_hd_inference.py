from pathlib import Path
import sys
import os
from vitonhd.cldm.model import create_model
from vitonhd.cldm.plms_hacked import PLMSSampler
from utils_stableviton import tensor2img
from omegaconf import OmegaConf
from PIL import Image
import numpy as np
import torch

class VitonHDInference():
    IMG_H = 1024
    IMG_W = 768
    def __init__(self):
        ##TODO: move url to settings
        config = OmegaConf.load("./configs/VITON.yaml")
        config.model.params.img_H = self.IMG_H
        config.model.params.img_W = self.IMG_W
        self.params = config.model.params
        model = create_model(config_path=None, config=config)
        model.load_state_dict(torch.load("./checkpoints/VITONHD_1024.ckpt", map_location="cpu")["state_dict"])
        self.model = model.cuda()
        model.eval()
        self.sampler = PLMSSampler(model)

    def infer(self, batch, n_steps) -> bytes:
        z, cond = self.model.get_input(batch, self.params.first_stage_key)
        z = z
        bs = z.shape[0]
        c_crossattn = cond["c_crossattn"][0][:bs]
        if c_crossattn.ndim == 4:
            c_crossattn = self.model.get_learned_conditioning(c_crossattn)
            cond["c_crossattn"] = [c_crossattn]
        uc_cross = self.model.get_unconditional_conditioning(bs)
        uc_full = {"c_concat": cond["c_concat"], "c_crossattn": [uc_cross]}
        uc_full["first_stage_cond"] = cond["first_stage_cond"]
        for k, v in batch.items():
            if isinstance(v, torch.Tensor):
                batch[k] = v.cuda()
        self.sampler.model.batch = batch

        ts = torch.full((1,), 999, device=z.device, dtype=torch.long)
        start_code = self.model.q_sample(z, ts)
        torch.cuda.empty_cache()
        output, _, _ = self.sampler.sample(
            n_steps, 
            bs,
            (4, self.IMG_H//8, self.IMG_W//8),
            cond,
            x_T=start_code, 
            verbose=False,
            eta=0.0,
            unconditional_conditioning=uc_full,       
        )

        output = self.model.decode_first_stage(output)
        output = tensor2img(output)
        pil_output = Image.fromarray(output)
        return pil_output