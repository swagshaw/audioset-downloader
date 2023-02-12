from omegaconf import OmegaConf

from core.main import class_to_id

config = OmegaConf.load('../config.yaml')
config.labels = []
print(config.labels)

print(class_to_id(config))