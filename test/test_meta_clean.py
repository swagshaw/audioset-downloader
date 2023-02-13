from omegaconf import OmegaConf
import sys

sys.path.append('/home/xiaoyang/audioset-downloader/')
from core.main import meta_clean
config = OmegaConf.load('../config.yaml')
meta_clean(config)