import json
import os
from config import ANSWER_KEY_PATH, RESULTS_SAVE_PATH
from utils import get_openai_client

def main():
    client = get_openai_client()

    # Try to read the batch job ID from the text file
    batch_job_id = None
    if os.path.exists("current_batch_job_id.txt"):
        with open("current_batch_job_id.txt", "r") as f:
            batch_job_id = f.read().strip()
    
    if not batch_job_id:
        batch_job_id = input("Enter your Batch Job ID: ").strip()

    print(f"Checking status for Batch Job ID: {batch_job_id}")
    job_status = client.batches.retrieve(batch_job_id)
    print(f"Status: {job_status.status}")

    if job_status.status == "completed":
        print(f"\nTOTAL BATCH USAGE:")
        print(f"Input Tokens: {job_status.usage.input_tokens}")
        print(f"Output Tokens: {job_status.usage.output_tokens}")
        print(f"Total: {job_status.usage.total_tokens}")

        file_response = client.files.content(job_status.output_file_id)
        batch_results = [json.loads(line) for line in file_response.text.split('\n') if line]

        # Load answer key
        with open(ANSWER_KEY_PATH, 'r') as f:
            bdmo_answer_key = json.load(f)

        total_correct = 0
        total_count = len(batch_results)

        print("\n--- Batch Results ---")
        for result in batch_results:
            custom_id = result['custom_id']
            gpt_answer = None
            if 'response' in result and 'body' in result['response'] and 'output' in result['response']['body']:
                for block in result['response']['body']['output']:
                    if block.get('type') == 'message':
                        gpt_answer = block['content'][0]['text'].strip()

            ground_truth = bdmo_answer_key.get(custom_id)

            if gpt_answer == str(ground_truth):
                total_correct += 1
                status = "CORRECT"
            else:
                status = "INCORRECT"

            print(f"ID: {custom_id}")
            print(f"   GPT Answer: {gpt_answer} | Ground Truth: {ground_truth} | {status}")

        accuracy = (total_correct / total_count) * 100 if total_count > 0 else 0
        print(f"\nBatch Total: {total_count}")
        print(f"Batch Correct: {total_correct}")
        print(f"Batch Accuracy: {accuracy:.2f}%")

        with open(RESULTS_SAVE_PATH, 'w', encoding='utf-8') as f:
            f.write(file_response.text)
        print(f"Raw results securely saved to: {RESULTS_SAVE_PATH}")
    else:
        print(f"\nJob is not yet completed. Please run this script again later.")

if __name__ == "__main__":
    main()
