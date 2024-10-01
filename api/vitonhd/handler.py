from omegaconf import OmegaConf
from vitonhd.cldm.model import create_model
from vitonhd.cldm.plms_hacked import PLMSSampler
from vitonhd.cldm.cldm import ControlLDM
from utils_stableviton import tensor2img
import torch
import io
from PIL import Image
import numpy as np


class VitonInferenceRequest:
    image: str
    cloth: str
    densepose: str
    agn_img: str
    agn_mask: str
    img_h: int
    img_w: int
    
class VitonInferenceResponse:
    image_array: np.ndarray

class VitonInferenceEndpointHandler():
    def __init__(self, path=""):
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        config = OmegaConf.load("./configs/VITONHD.yaml")
        config.model.params.img_H = self.IMG_H
        config.model.params.img_W = self.IMG_W
        self.params = config.model.params
        model: ControlLDM = create_model(config_path=None, config=config)
        load_cp = torch.load(path, map_location=device)
        load_cp = load_cp["state_dict"] if "state_dict" in load_cp.keys() else load_cp
        model.load_state_dict(load_cp)
        model = model.cuda()
        model.eval()
        self.model = model
        self.sampler = PLMSSampler(self.model)

    def __call__(self, data: VitonInferenceRequest) -> VitonInferenceResponse:
        return self.inference(data)
    
    @classmethod
    def convert_bytes_to_pil_image(cls, image_bytes: bytes) -> Image:
        return Image.open(io.BytesIO(image_bytes))
    
    @classmethod
    def get_tensor(cls, img, h, w, is_mask=False):
        img = np.array(img.resize((w, h))).astype(np.float32)
        if not is_mask:
            img = (img / 127.5) - 1.0
        else:
            img = (img < 128).astype(np.float32)[:,:,None]
        return torch.from_numpy(img)[None].cuda()
        
    @classmethod
    def get_batch(cls, image, cloth, densepose, agn_img, agn_mask, img_h, img_w):
        batch = dict()
        batch["image"] = cls.get_tensor(image, img_h, img_w)
        batch["cloth"] = cls.get_tensor(cloth, img_h, img_w)
        batch["image_densepose"] = cls.get_tensor(densepose, img_h, img_w)
        batch["agn"] = cls.get_tensor(agn_img, img_h, img_w)
        batch["agn_mask"] = cls.get_tensor(agn_mask, img_h, img_w, is_mask=True)
        batch["txt"] = ""
        return batch
    
    @classmethod
    def tensor2img(cls, x):
        '''
        x : [BS x c x H x W] or [c x H x W]
        '''
        if x.ndim == 3:
            x = x.unsqueeze(0)
        BS, C, H, W = x.shape
        x = x.permute(0,2,3,1).reshape(-1, W, C).detach().cpu().numpy()
        x = np.clip(x, -1, 1)
        x = (x+1)/2
        x = np.uint8(x*255.0)
        if x.shape[-1] == 1:
            x = np.concatenate([x,x,x], axis=-1)
        return x
    
    def inference(self, request: VitonInferenceRequest, batch_size: int = 1) -> VitonInferenceResponse:
        vton_img: Image = self.convert_bytes_to_pil_image(request.image)
        garm_img: Image = self.convert_bytes_to_pil_image(request.cloth)
        mask: Image = self.convert_bytes_to_pil_image(request.agn_mask)
        masked_vton_img: Image = self.convert_bytes_to_pil_image(request.agn_img)
        densepose: Image = self.convert_bytes_to_pil_image(request.densepose)
        
        batch = self.get_batch(
            vton_img, 
            garm_img, 
            densepose, 
            masked_vton_img, 
            mask, 
            self.IMG_H, 
            self.IMG_W
        )
        
        torch.cuda.empty_cache()
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
        shape = (4, self.IMG_H//8, self.IMG_W//8) 

        output, _, _ = self.sampler.sample(
            20,
            bs,
            shape,
            c,
            x_T=start_code,
            verbose=False,
            eta=0.0,
            unconditional_conditioning=uc_full,
        )
        
        output = self.model.decode_first_stage(output)
        output = tensor2img(output)
        pil_output = Image.fromarray(output)
        
        return VitonInferenceResponse(image=self.tensor2img(pil_output))