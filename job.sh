# Clone the repository
git clone https://github.com/<username>/audioset-downloader.git

# Navigate to the repository directory
cd audioset-downloader

# Install the required packages
pip install -r requirements.txt

# Run the input_labels.py script to generate the labels dict
python input_labels.py

# Update the config.yaml file with the generated labels dict
# Open the config.yaml file and paste the generated labels dict under the "labels_id_dict" field

# Start the downloading process
python main.py

# The downloaded audio files will be saved in the destination_dir specified in the config.yaml file
# The logs of the downloading process will be saved in the 'logs' directory
