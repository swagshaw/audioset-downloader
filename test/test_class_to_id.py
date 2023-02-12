import csv
import os

import pandas as pd
from omegaconf import OmegaConf

from core.main import class_to_id

config = OmegaConf.load('../config.yaml')
# config.labels = []
print(config.labels)

print(class_to_id(config))

# # label_id = [row[mid] for row in label_class_dict if (label.lower() in row[display_name].lower())]
# with open(os.path.join(config.workspace, "class_labels_indices.csv")) as label_file:
#     label_class_dict = pd.read_csv(label_file).to_dict()
#     # print('Baby cry' in 'Baby cry, infant cry')
#     labels = config.labels
#     for label in labels:
#         for key, value in label_class_dict['display_name'].items():
#             if label.lower() == value.lower():
#                 print(label_class_dict['mid'].get(key), value)

        # print(row[index], row[mid], row[display_name])
