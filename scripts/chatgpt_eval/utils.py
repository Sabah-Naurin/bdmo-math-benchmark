import base64
from openai import OpenAI
from config import API_KEY

def get_openai_client():
    if not API_KEY:
        raise ValueError("OPENAI_API_KEY environment variable not set. Please set it before running.")
    return OpenAI(api_key=API_KEY)

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")
