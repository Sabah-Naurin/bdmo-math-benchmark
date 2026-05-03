from config import BATCH_OUTPUT_JSONL
from utils import get_openai_client

def main():
    client = get_openai_client()

    print(f"--- Uploading Batch File ({BATCH_OUTPUT_JSONL}) ---")
    with open(BATCH_OUTPUT_JSONL, "rb") as f:
        batch_input_file = client.files.create(
            file=f,
            purpose="batch"
        )

    print("\n--- Starting Batch Job ---")
    batch_job = client.batches.create(
        input_file_id=batch_input_file.id,
        endpoint="/v1/responses",
        completion_window="24h"
    )

    print(f"Batch Job ID: {batch_job.id}")
    print("Please save this ID! You will need it to check the status and get results.")
    
    # Save the job id to a small text file for convenience
    with open("current_batch_job_id.txt", "w") as f:
        f.write(batch_job.id)
    print("Job ID also saved to current_batch_job_id.txt")

    job_status = client.batches.retrieve(batch_job.id)
    print(f"Initial Status: {job_status.status}")
    print(f"Requests: {job_status.request_counts}")

if __name__ == "__main__":
    main()
