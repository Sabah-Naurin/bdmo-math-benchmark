import json
import os
from config import DATASET_PATH, BASE_IMAGE_DIR
from utils import get_openai_client, encode_image

def api_call(client, input_text: str, base64_image: str | None):
    user_content = [{"type": "input_text", "text": input_text}]

    if base64_image:
        instruction = "Analyze the provided math problem and image carefully. Only reply with the numeric answer."
        user_content.append({
            "type": "input_image",
            "image_url": f"data:image/jpeg;base64,{base64_image}"
        })
    else:
        instruction = "Analyze the provided math problem carefully. Only reply with the numeric answer."

    response = client.responses.create(
        model="gpt-5.4",
        reasoning={"effort": "low"},
        instructions=instruction,
        input=[{"role": "user", "content": user_content}]
    )

    usage = response.usage
    print(f"Tokens used: {usage.input_tokens} (prompt) + {usage.output_tokens} (completion) = {usage.total_tokens} total")
    return response.output_text

def main():
    client = get_openai_client()
    
    with open(DATASET_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print("--- Running Initial Single Evaluations ---")
    total_correct = 0
    total_incorrect = 0
    processed_count = 0
    
    # Change this limit to test more or fewer samples
    EVAL_LIMIT = 2

    stop_processing = False
    for year, stages in data.items():
        if stop_processing: break
        for stage, regions in stages.items():
            if stop_processing: break
            for region, categories in regions.items():
                if stop_processing: break
                for category, problems in categories.items():
                    if stop_processing: break
                    for prob in problems:
                        if processed_count >= EVAL_LIMIT:
                            stop_processing = True
                            break

                        prob_no = prob.get("problem_no")
                        english_text = prob.get("problem_in_bangla", "")
                        image_path = prob.get("image_path")
                        ground_truth = str(prob.get("answer"))

                        base64_image = None
                        if image_path:
                            full_image_path = os.path.join(BASE_IMAGE_DIR, image_path)
                            if os.path.exists(full_image_path):
                                base64_image = encode_image(full_image_path)
                            else:
                                print(f"Warning: Image {full_image_path} not found.")

                        print(f"Evaluating Problem {prob_no}...")
                        gpt_answer = api_call(client, english_text, base64_image)
                        processed_count += 1

                        if ground_truth == gpt_answer:
                            total_correct += 1
                            print(f"Problem {prob_no}: Correct\nGround Truth: {ground_truth} GPT Answer: {gpt_answer}\n")
                        else:
                            total_incorrect += 1
                            print(f"Problem {prob_no}: Incorrect\nGround Truth: {ground_truth} GPT Answer: {gpt_answer}\n")

    if total_correct + total_incorrect > 0:
        accuracy = (total_correct / (total_correct + total_incorrect)) * 100
        print(f"Single Eval Total Problems:  {total_correct + total_incorrect}")
        print(f"Single Eval Total Correct:   {total_correct}")
        print(f"Single Eval Total Incorrect: {total_incorrect}")
        print(f"Single Eval Accuracy:        {accuracy}%")

if __name__ == "__main__":
    main()
