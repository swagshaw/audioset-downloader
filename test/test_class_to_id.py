from omegaconf import OmegaConf
import sys
sys.path.append('/home/xiaoyang/audioset-downloader/')
from core.input_label import class_to_id

config = OmegaConf.load('../config.yaml')
print(config.labels)
class_to_id(config)

