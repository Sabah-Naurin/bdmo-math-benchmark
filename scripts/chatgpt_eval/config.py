import os
try:
    from dotenv import load_dotenv
    # Load .env from the root of the project (two directories up)
    load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))
except ImportError:
    pass

# Base directory of the GitHub repo (two folders up from this file)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))

# --- Paths ---
# The json dataset
DATASET_PATH = os.path.join(PROJECT_ROOT, "data", "merged_dataset.json") 

# If you are running this by cloning the GitHub repo into Google Colab,
# use the Colab path to your mounted Google Drive where the images are stored.
BASE_IMAGE_DIR = "/content/drive/MyDrive/Senior Project" 

# Batch processing output files
BATCH_OUTPUT_JSONL = os.path.join(PROJECT_ROOT, "model_outputs", "chatgpt", "bmo_batch_bangla.jsonl")
ANSWER_KEY_PATH = os.path.join(PROJECT_ROOT, "model_outputs", "chatgpt", "answer_key.json")
RESULTS_SAVE_PATH = os.path.join(PROJECT_ROOT, "model_outputs", "chatgpt", "raw_batch_results_bangla.jsonl")

# --- API Configuration ---
# Ensure you have your OPENAI_API_KEY set in your environment variables.
# You can do this in your terminal before running the scripts:
# Windows (PowerShell): $env:OPENAI_API_KEY="your-key"
# Mac/Linux: export OPENAI_API_KEY="your-key"
# Or you can add it to the .env file in the root directory.
API_KEY = os.getenv('OPENAI_API_KEY')
