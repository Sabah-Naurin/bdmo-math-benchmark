import json
import os
from config import DATASET_PATH, BASE_IMAGE_DIR, BATCH_OUTPUT_JSONL, ANSWER_KEY_PATH
from utils import encode_image

def create_batch_file(data, base_image_path, output_filename):
    ground_truth_lookup = {}

    with open(output_filename, 'w', encoding='utf-8') as f:
        for year, stages in data.items():
            for stage, regions in stages.items():
                for region, categories in regions.items():
                    for category, problems in categories.items():
                        for prob in problems:
                            # Unique ID for tracking results later
                            custom_id = f"{year}_{stage}_{region}_{category}_{prob['problem_no']}"
                            ground_truth_lookup[custom_id] = prob.get("answer")

                            # Prepare content with Vision support
                            user_content = [{"type": "input_text", "text": prob.get("problem_in_bangla", "")}]

                            image_path = prob.get("image_path")
                            if image_path:
                                instruction = "Analyze the provided math problem and image carefully. Only reply with the numeric answer."
                                full_image_path = os.path.join(base_image_path, image_path)
                                if os.path.exists(full_image_path):
                                    base64_image = encode_image(full_image_path)
                                    user_content.append({
                                        "type": "input_image",
                                        "image_url": f"data:image/jpeg;base64,{base64_image}"
                                    })
                                else:
                                    print(f"Warning: Image {full_image_path} not found.")
                            else:
                                instruction = "Analyze the provided math problem carefully. Only reply with the numeric answer."

                            # The Batch Request Object
                            batch_request = {
                                "custom_id": custom_id,
                                "method": "POST",
                                "url": "/v1/responses",
                                "body": {
                                    "model": "gpt-5.4",
                                    "reasoning": {"effort": "low"},
                                    "instructions": instruction,
                                    "input": [{"role": "user", "content": user_content}]
                                }
                            }
                            f.write(json.dumps(batch_request) + '\n')

    print(f"Batch file {output_filename} created.")
    return ground_truth_lookup

def main():
    print(f"Loading dataset from: {DATASET_PATH}")
    with open(DATASET_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print("\n--- Creating Batch File ---")
    bdmo_answer_key = create_batch_file(data, BASE_IMAGE_DIR, BATCH_OUTPUT_JSONL)

    with open(ANSWER_KEY_PATH, 'w') as f:
        json.dump(bdmo_answer_key, f)
    print(f"Answer key saved to: {ANSWER_KEY_PATH}")

if __name__ == "__main__":
    main()
