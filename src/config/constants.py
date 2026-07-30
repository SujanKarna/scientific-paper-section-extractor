import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Define the base directory for raw data
DATA_DIR = os.path.join(BASE_DIR, 'data')
RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')