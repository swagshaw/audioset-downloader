from omegaconf import OmegaConf
import sys
sys.path.append('/home/xiaoyang/audioset-downloader/')
from core.main import create_tsv

config = OmegaConf.load('../config.yaml')
create_tsv(config)