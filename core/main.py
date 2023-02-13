
import glob
import logging
import os
import threading
from datetime import datetime

import soundfile
from tqdm import tqdm
from omegaconf import OmegaConf
import pandas as pd


def create_tsv(cfg):
    """
    Function for creating tsv file containing all clips and corresponding info for given class.
    Other classes will regard as 'Other'.
    :param cfg:
    :return: tsv file for all clips.
    """
    if not cfg.labels_id_dict:
        raise NotImplementedError('Can not find label_id_dict, please call class_to_id first.')
    df_train = pd.read_csv(os.path.join(cfg.workspace, "audioset_train_strong.tsv"), sep='\t')
    df_eval = pd.read_csv(os.path.join(cfg.workspace, "audioset_eval_strong.tsv"), sep='\t')
    df = pd.concat([df_train, df_eval])
    count = 0
    print("Total rows are {}".format(len(df)))
    print("The Candidate labels are: {}".format(cfg.labels_id_dict.keys()))
    print("Start extract...")
    all_rows = pd.DataFrame(columns=df.columns)
    if not os.path.exists(cfg.destination_dir):
        os.makedirs(cfg.destination_dir)
    cfg.labels_id_dict = dict(map(lambda kv: (kv[0], kv[1][0]), cfg.labels_id_dict.items()))
    # cfg.labels_id_dict.values().map(lambda x: x[0])
    print(cfg.labels_id_dict)
    for class_name in tqdm(cfg.labels_id_dict.keys()):
        rows_label = df.loc[df['label'] == cfg.labels_id_dict[class_name]]
        rows = df.loc[df['segment_id'].isin(rows_label['segment_id'])]
        rows.loc[~rows['label'].isin(cfg.labels_id_dict.values()), ['label']] = 'Other'
        count += len(rows)
        if all_rows.empty:
            all_rows = rows
        else:
            all_rows = pd.concat([all_rows, rows])
    print(all_rows.value_counts('label'))
    all_rows.to_csv(os.path.join(cfg.destination_dir, 'metadata.tsv'), mode='w', header=True, sep='\t', index=None)
    print('Extract the match rows are {}'.format(count))


def cut_tail(x):
    target_list = x.split('_')
    start = target_list[-1]
    file_name = x.replace('_' + start, "")
    start = int(start) // 1000
    name = '{}_{}'.format(file_name, start)
    return name


def convert_label(label, cfg):
    if label != 'Other':
        labels_id_dict = dict(map(lambda kv: (kv[0], kv[1][0]), cfg.labels_id_dict.items()))
        label_list = list(labels_id_dict.values())
        index = label_list.index(label)
        return list(labels_id_dict.keys())[index]
    else:
        return label


def download(cfg, mini=False):
    # Create a logs directory if it doesn't exist
    if not os.path.exists("logs"):
        os.makedirs("logs")
    # Create a logging object
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # Create a file handler and set its level to INFO
    file_handler = logging.FileHandler("logs/{}.log".format(datetime.now().strftime("%Y-%m-%d_%H-%M-%S")))
    file_handler.setLevel(logging.INFO)

    # Create a logging format
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)

    # Add the file handler to the logger
    logger.addHandler(file_handler)

    # Create directories
    data_path = os.path.join(cfg.destination_dir, 'dataset')
    os.makedirs(data_path, exist_ok=True)
    csv_path = os.path.join(cfg.destination_dir, 'metadata.tsv')
    df = pd.read_csv(csv_path, sep='\t')
    if mini:
        df = df.sample(5)
    distinct_files = df['segment_id'].unique()
    logger.info(len(distinct_files))
    # Start the downloading threads
    threads = []
    for i in range(cfg.num_threads):
        thread = threading.Thread(target=_download_thread, args=(distinct_files, data_path, logger))
        thread.start()
        threads.append(thread)
    # Wait for all threads to finish
    for thread in threads:
        thread.join()


def _download_thread(distinct_files, data_path, logger):
    error_count = 0
    # Extract videos from YouTube
    for file in tqdm(distinct_files):
        try:
            file_name = cut_tail(file)
            target_list = file_name.split('_')
            start = target_list[-1]
            URL = 'https://www.youtube.com/watch?v={}'.format(file_name)
            command = "ffmpeg -ss " + str(
                start) + " -t 10 -y -i $(youtube-dl -f 'bestaudio' -g " + URL + ") -ar " + str(
                16000) + " -- \"" + '{}/{}'.format(data_path, file_name) + ".wav\""
            logger.info('COMMAND:', command)
            os.system(command)
        except Exception:
            error_count += 1
            logger.error("Couldn\'t download the audio {}".format(file))
    print('Number of files that could not be downloaded:', error_count)


def meta_clean(cfg):
    data_path = os.path.join(cfg.destination_dir, 'dataset')
    csv_path = os.path.join(cfg.destination_dir, 'metadata.tsv')
    df = pd.read_csv(csv_path, sep='\t')
    files = glob.glob(pathname='*.wav', root_dir=data_path)
    print('Find {} audio files'.format(len(files)))
    df['name'] = df['segment_id'].map(cut_tail)
    df['name'] = df['name'].map(lambda x: x + '.wav')
    df['label'] = df['label'].apply(convert_label, args=[cfg])
    for i, row in tqdm(df.iterrows()):
        try:
            audio_path = os.path.join(data_path, row['name'])
            _, _ = soundfile.read(audio_path)
        except Exception:
            df = df.drop(df[df['name'] == row['name']].index)
    print(df.head())
    return df


def split(cfg, pool):
    pool = pool.assign(duration=lambda x: (x['end_time_seconds'] - x['start_time_seconds']))
    whole_dict = {}
    for i, rows in pool.iterrows():
        if rows['label'] not in whole_dict.keys():
            whole_dict[rows['label']] = 0
        else:
            whole_dict[rows['label']] += rows['end_time_seconds'] - rows['start_time_seconds']
    print(whole_dict)
    eval_dict = {}
    for k in whole_dict.keys():
        eval_dict[k] = whole_dict[k] * cfg.eval_rate
    eval_dict.pop('Other')
    distinct_files = pool['name'].unique()
    select_files = []
    for label in eval_dict.keys():
        rows = pool.loc[pool['label'] == label]
        count = eval_dict[label]
        for i, row in rows.iterrows():
            if count <= 0:
                print(count)
                break
            select_files.append(row['name'])
            duration = row['duration']
            count = count - duration
    select_files = set(select_files)
    print('The eval set has {} clips'.format(len(select_files)))
    train_files = set(distinct_files) - set(select_files)
    print('The train set has {} clips'.format(len(train_files)))
    eval_rows = pool.loc[pool['name'].isin(select_files)]
    train_rows = pool.loc[pool['name'].isin(train_files)]

    train_path = 'train_strong.tsv'
    valid_path = 'valid_strong.tsv'
    test_path = 'test_strong.tsv'

    train_rows = train_rows.drop(train_rows[train_rows['label'] == 'Other'].index)
    valid_rows = eval_rows.sample(frac=0.5)
    test_rows = eval_rows[~eval_rows.index.isin(valid_rows.index)]

    train_rows.to_csv(os.path.join(cfg.destination_dir, train_path), mode='w', header=True, sep='\t', index=None)
    valid_rows.to_csv(os.path.join(cfg.destination_dir, valid_path), mode='w', header=True, sep='\t', index=None)
    test_rows.to_csv(os.path.join(cfg.destination_dir, test_path), mode='w', header=True, sep='\t', index=None)

    print('Train: {}, Valid: {}, Test: {}.'.format(len(train_rows), len(valid_rows), len(test_rows)))


def main(config):
    create_tsv(config)
    download(config, mini=False)
    clean_pool = meta_clean(config)
    split(config, clean_pool)


if __name__ == "__main__":
    config = OmegaConf.load('../config.yaml')
    main(config)
