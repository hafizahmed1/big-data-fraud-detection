import gdown
import pandas as pd
import os
import io
class DataLoader:
  def __init__(self, file_id):
    self.file_id = file_id

  def get_drive_url(self, file_name):
    return f'https://drive.google.com/uc?id={self.file_id}&export=download&confirm=t&fileName={file_name}'

  def load_csv_from_drive(self, url, file_path):
    if os.path.exists(file_path):  # Check if file already exists locally
      print(f"{file_path} already exists, skipping download.")
      return pd.read_csv(file_path)
    else:
      print(f"Downloading {file_path} from {url}")
      response = gdown.download(url, quiet=False)
      if response:
        csv_data = gdown.download(url, quiet=True, output=None, fuzzy=True)
        if csv_data:
          return pd.read_csv(io.StringIO(csv_data.decode('utf-8')))
        else:
          raise ValueError("Could not read the CSV data from Google Drive.")
      else:
        raise ValueError("Could not download the CSV data from Google Drive.")

  def load_csv_files(self):
    files = {
      'sample_submission': 'sample_submission.csv',
      'test_identity': 'test_identity.csv',
      'test_transaction': 'test_transaction.csv',
      'train_identity': 'train_identity.csv',
      'train_transaction': 'train_transaction.csv'
    }

    data_frames = {}
    for key, file in files.items():
      file_path = os.path.join(r"C:\Users\ahmad\PycharmProjects\big-data-fraud-detection\ieee-fraud-detection", file)
  # Replace with your local directory
      try:
        data_frames[key] = self.load_csv_from_drive(self.get_drive_url(file), file_path)
      except Exception as e:
        print(f"Error loading {file}: {e}")
        raise e

    return data_frames

  def load_data(self):
    return self.load_csv_files()

if __name__ == "__main__":
  file_id = '1uhIL8j26uhxTgNArie6TQre_PTf28KMm'  # Replace with your shared Google Drive folder ID

  data_loader = DataLoader(file_id)
  data_frames = data_loader.load_data()

  for name, df in data_frames.items():
    print(f"{name} DataFrame:")
    print(df.head())
    print()

  # You can now use the data_frames dictionary in your analysis
  train_transaction_df = data_frames['train_transaction']
  # Add your analysis code here
