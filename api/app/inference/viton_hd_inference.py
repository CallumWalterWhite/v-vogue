from pathlib import Path
import sys
import os
from vitonhd.cldm.model import create_model
from vitonhd.cldm.plms_hacked import PLMSSampler
from vitonhd.cldm.cldm import ControlLDM
from utils_stableviton import tensor2img
from omegaconf import OmegaConf
from PIL import Image
import numpy as np
import torch
from app.core.config import settings

class VitonHDInference():
    IMG_H = 1024
    IMG_W = 768
    def __init__(self, device):
        ##TODO: move url to settings
        config = OmegaConf.load(settings.VITONHD_MODEL_CONFIG_PATH)
        config.model.params.img_H = self.IMG_H
        config.model.params.img_W = self.IMG_W
        self.params = config.model.params
        model: ControlLDM = create_model(config_path=None, config=config)
        load_cp = torch.load(settings.VITONHD_MODEL_PATH, map_location=device)
        load_cp = load_cp["state_dict"] if "state_dict" in load_cp.keys() else load_cp
        model.load_state_dict(load_cp)
        model = model.cuda()
        model.eval()
        self.model = model
        self.sampler = PLMSSampler(self.model)
    #TODO: viton model not using gpu at inference, not sure why
    def infer(self, batch, n_steps) -> Image:
        z, c = self.model.get_input(batch, self.params.first_stage_key)
        bs = z.shape[0]
        c_crossattn = c["c_crossattn"][0][:bs]
        if c_crossattn.ndim == 4:
            c_crossattn = self.model.get_learned_conditioning(c_crossattn)
            c["c_crossattn"] = [c_crossattn]
        uc_cross = self.model.get_unconditional_conditioning(bs)
        uc_full = {"c_concat": c["c_concat"], "c_crossattn": [uc_cross]}
        uc_full["first_stage_cond"] = c["first_stage_cond"]
        for k, v in batch.items():
            if isinstance(v, torch.Tensor):
                batch[k] = v.cuda()
        self.sampler.model.batch = batch

        ts = torch.full((1,), 999, device=z.device, dtype=torch.long)
        start_code = self.model.q_sample(z, ts)     

        output, _, _ = self.sampler.sample(
            n_steps,
            bs,
            (4, self.IMG_H//8, self.IMG_W//8),
            c,
            x_T=start_code,
            verbose=False,
            eta=0.0,
            unconditional_conditioning=uc_full,
        )
        
        output = self.model.decode_first_stage(output)
        output = tensor2img(output)
        pil_output = Image.fromarray(output)
        return pil_output