import os

import pandas as pd
from omegaconf import OmegaConf


def class_to_id(cfg):
    label_class_dict = pd.read_csv(os.path.join(cfg.workspace, "class_labels_indices.csv")).to_dict()
    label_dict = {}
    for label in cfg.labels:
        label_id = [label_class_dict['mid'].get(key) for key, value in label_class_dict['display_name'].items() if
                    (label.lower() in value.lower())]
        label_dict[label] = label_id
        if len(label_id) != 1:
            print('Expect one id but find {} has {}. \n'.format(label, label_id))
    print('Your label_id_dict is: ' + str(label_dict) + '\n')
    print('Please paste it to the configuration file.')
    return


if __name__ == "__main__":
    config = OmegaConf.load('../config.yaml')
    class_to_id(config)