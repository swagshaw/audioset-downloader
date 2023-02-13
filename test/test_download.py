from omegaconf import OmegaConf
import sys

sys.path.append('/home/xiaoyang/audioset-downloader/')
from core.main import download

config = OmegaConf.load('../config.yaml')

download(config, mini=True)
