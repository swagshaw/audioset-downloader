import argparse
import os

import hydra
from omegaconf import OmegaConf

import pandas as pd


def class_to_id(cfg):
    label_class_dict = pd.read_csv(os.path.join(cfg.workspace, "class_labels_indices.csv"), sep=',')
    print(label_class_dict.head())
    label_dict = {}
    for label in cfg.labels:
        label_id = label_class_dict.loc[label.lower() in label_class_dict['display_name'].lower()]['display_name']
        assert len(label_id) == 1, "Can not find the label id or multiple label id of {}.".format(label)
        label_dict[label] = label_id
    return label_dict


def create_tsv(cfg):
    """
    Function for creating tsv file containing all clips and corresponding info for given class.
    Other classes will regard as 'Other'.
    :param labels:
    :param cfg:
    :return: tsv file for all clips.
    """
    df_train = pd.read_csv(os.path.join(cfg.workspace, "audioset_train_strong.tsv"), sep='\t')
    df_eval = pd.read_csv(os.path.join(cfg.workspace, "audioset_eval_strong.tsv"), sep='\t')
    df = pd.concat([df_train, df_eval])
    print("Total rows are {}".format(len(df)))
    print("The Candidate labels are: {}".format(cfg.labels))
    for label in cfg.labels:
        assert label in label_class_dict['display_name'].unique(), "Can not find the label {} in the metadata".format(
            label)
    print("Start extract...")


def download(cfg):
    data_type = cfg.data_type
    workspace = cfg.workspace

    # Create directories
    data_path = os.path.join(workspace, 'dataset', data_type)
    os.makedirs(data_path, exist_ok=True)

    if data_type == 'develop':
        csv_path = os.path.join(workspace, '{}.tsv'.format('sur_develop_strong'))
        train_path = 'train_strong.tsv'
        valid_path = 'valid_strong.tsv'
        df = pd.read_csv(csv_path, sep='\t')
        if cfg.mini:
            print("Mini dataset mode...")
            df = df.sample(n=500)
        valid_rows = df.sample(frac=0.2)
        train_rows = df[~df.index.isin(valid_rows.index)]
        train_rows.to_csv(train_path, mode='w', header=True, sep='\t', index=None)
        valid_rows.to_csv(valid_path, mode='w', header=True, sep='\t', index=None)
    else:
        csv_path = os.path.join(workspace, '{}.tsv'.format('sur_eval_strong'))
        df = pd.read_csv(csv_path, sep='\t')
        if args.mini:
            print("Mini dataset mode...")
            df = df.sample(n=50)
        test_path = 'test_strong.tsv'
        df.to_csv(test_path, mode='w', header=True, sep='\t', index=None)

    print(df)
    distinct_files = df['segment_id'].unique()
    print(len(distinct_files))
    print(distinct_files[:5])
    root = os.getcwd()
    print('CWD:', root)
    # Extract videos from YouTube
    error_count = 0

    for file in tqdm(distinct_files):
        try:
            target_list = file.split('_')
            start = target_list[-1]
            file_name = file.replace('_' + start, "")
            start = int(start) // 1000
            URL = 'https://www.youtube.com/watch?v={}'.format(file_name)
            command = "ffmpeg -ss " + str(
                start) + " -t 10 -y -i $(youtube-dl -f 'bestaudio' -g " + URL + ") -ar " + str(
                16000) + " -- \"" + '{}/{}_{}'.format(data_path, file_name, start) + ".wav\""
            print('COMMAND:', command)
            os.system((command))
        except Exception:
            error_count += 1
            print("Couldn\'t download the audio")
    print('Number of files that could not be downloaded:', error_count)


def main(config):
    create_tsv(config)
    print(config.labels)


if __name__ == "__main__":
    config = OmegaConf.load('../config.yaml')
    main(config)
