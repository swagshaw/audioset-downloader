# audioset-downloader 
This repository provides a tool to download strong label audio clips from AudioSet, a large-scale dataset of annotated audio events. The tool can be used to build custom strong label audio datasets for machine learning tasks.

## Features
- Efficiently download audio files from AudioSet based on specific labels.
- Supports multiple parallel downloads to speed up the process.
- Flexibility to choose the number of audio files to download per label.
- Convenient logging system to keep track of the downloading process.
- Configuration of the downloading process can be done through a `config.yaml` file.
## Requirements
- python3
- ffmpeg
- youtube-dl 

## Usage
1. Clone this repository:

```bash
git clone https://github.com/your-username/audioset-downloader.git
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Run the `input_label.py` script to generate the label dictionary:
```bash
python input_label.py
```
4. Open the config.yaml file and paste the label dictionary that was generated in the previous step. Modify the other fields in the file as desired.

5. Run the main.py script to download audio clips: Downloads audio files to a folder `output/dataset` in current directory.
```bash
python main.py
```
Uses CSV files found in `core/` by default. Execute `process.py` in its' own directory.

## Configuration
The configuration of the tool is specified in the config.yaml file. The following fields are available:

- `labels`: List of labels to download.
- `labels_id_dict`: Dictionary mapping labels to AudioSet IDs.
- `csv_dataset`: Path to the CSV dataset.
- `workspace`: Workspace directory.
- `destination_dir`: Destination directory for the downloaded audio files.
- `fs`: Sampling frequency.
- `eval_rate`: Evaluation rate.
- `num_threads`: Number of threads to use when downloading.

## Why a downloader for AudioSet is needed

Exactly, that's why a downloader for AudioSet is needed. The CSV files provided by AudioSet contain only the information about the YouTube-IDs and the associated labels, but not the actual audio data. On the other hand, the TFRecord files contain the feature vectors, but not the raw audio signals, which is required for some machine learning tasks.

By using a downloader, users can download the audio data in a raw format and use it to train their models. This tool can help to save time and effort, as the user doesn't have to manually search for and download each individual audio clip from YouTube. The user can also use the tool to filter the audio clips based on their labels, allowing them to build a custom strong label dataset that is tailored to their specific needs.

## AudioSet
AudioSet can be downloaded from Google [here](https://research.google.com/audioset/download.html) as a set of CSV files. For each element in the dataset the CSV files list an associated YouTube ID, start time, end time and class labels. The CSV files are used to download AudioSet as raw audio files (WAV).

## Disclaimer
This repository is for educational and research purposes only. Please respect the terms of use and license agreements of AudioSet when using this tool.