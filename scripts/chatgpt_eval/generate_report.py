import json
import os
import pandas as pd
from config import PROJECT_ROOT, ANSWER_KEY_PATH, RESULTS_SAVE_PATH, DATASET_PATH

# --- Configuration ---
CSV_REPORT_PATH = os.path.join(PROJECT_ROOT, "evaluations", "chatgpt_results.csv")
SUMMARY_JSON_PATH = os.path.join(PROJECT_ROOT, "evaluations", "summary_metrics.json")

def evaluate_results():
    print("Loading dataset to check for images...")
    with open(DATASET_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    has_image_lookup = {}
    for year, stages in data.items():
        for stage, regions in stages.items():
            for region, categories in regions.items():
                for category, problems in categories.items():
                    for prob in problems:
                        custom_id = f"{year}_{stage}_{region}_{category}_{prob.get('problem_no', '')}"
                        has_image_lookup[custom_id] = bool(prob.get("image_path"))

    print("Loading answer key and raw results...")
    
    with open(ANSWER_KEY_PATH, 'r') as f:
        bdmo_answer_key = json.load(f)

    batch_results = []
    # Using the RESULTS_SAVE_PATH from config (where get_results.py downloaded the jsonl)
    with open(RESULTS_SAVE_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                batch_results.append(json.loads(line))

    evaluation_data = []
    total_correct = 0
    total_count = len(batch_results)

    print("Evaluating model outputs...")
    for result in batch_results:
        custom_id = result['custom_id']
        
        # Extract metadata from the custom_id (year_stage_region_category_probNo)
        # Note: category might have underscores (e.g., 'higher_secondary')
        id_parts = custom_id.split('_')
        year = id_parts[0]
        stage = id_parts[1]
        region = id_parts[2]
        problem_no = id_parts[-1]
        category = "_".join(id_parts[3:-1])
        
        gpt_answer = None
        if 'response' in result and 'body' in result['response'] and 'output' in result['response']['body']:
            for block in result['response']['body']['output']:
                if block.get('type') == 'message':
                    gpt_answer = block['content'][0]['text'].strip()

        ground_truth = str(bdmo_answer_key.get(custom_id)).strip()
        is_correct = (gpt_answer == ground_truth)
        has_image = has_image_lookup.get(custom_id, False)

        if is_correct:
            total_correct += 1

        evaluation_data.append({
            "problem_id": custom_id,
            "year": year,
            "stage": stage,
            "region": region,
            "category": category,
            "problem_no": problem_no,
            "has_image": has_image,
            "ground_truth": ground_truth,
            "gpt_answer": gpt_answer,
            "is_correct": is_correct
        })

    # Ensure evaluations directory exists
    os.makedirs(os.path.dirname(CSV_REPORT_PATH), exist_ok=True)

    # Save detailed CSV
    df = pd.DataFrame(evaluation_data)
    df.to_csv(CSV_REPORT_PATH, index=False)
    
    # Calculate and save summary metrics
    accuracy = (total_correct / total_count) * 100 if total_count > 0 else 0
    
    summary = {
        "model": "gpt-5.4",
        "total_problems": total_count,
        "correct": total_correct,
        "accuracy_percentage": round(accuracy, 2)
    }
    
    with open(SUMMARY_JSON_PATH, 'w') as f:
        json.dump(summary, f, indent=4)

    print(f"\n--- Evaluation Complete ---")
    print(f"Total: {total_count}")
    print(f"Correct: {total_correct}")
    print(f"Accuracy: {accuracy:.2f}%")
    print(f"\nDetailed CSV saved to: {CSV_REPORT_PATH}")
    print(f"Summary metrics saved to: {SUMMARY_JSON_PATH}")

if __name__ == "__main__":
    evaluate_results()
