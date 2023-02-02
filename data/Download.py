import os
import argparse
import pandas as pd
from tqdm import tqdm


def main(args):
    data_type = args.data_type
    workspace = args.workspace

    # Create directories
    data_path = os.path.join(workspace, 'dataset', data_type)
    os.makedirs(data_path, exist_ok=True)

    if data_type == 'train' or 'validation':
        csv_path = os.path.join(workspace, '{}.tsv'.format('train_strong'))
    elif data_type == 'test':
        csv_path = os.path.join(workspace, '{}.tsv'.format('eval_strong'))

    df = pd.read_csv(csv_path, sep='\t')
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract AudioSet Dataset')
    parser.add_argument('--workspace', type=str, required=True, help='Directory of your workspace.')
    parser.add_argument('--data_type', type=str, required=True, choices=['train', 'validation', 'test'])
    args = parser.parse_args()

    main(args)
