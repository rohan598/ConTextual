import os
import json
import openai
import regex
import argparse
import pandas as pd
from tqdm import tqdm
import numpy as np

parser = argparse.ArgumentParser()

parser.add_argument('--data-file', type = str, help = "data file")
parser.add_argument('--master', type = str, help = "model responses")
parser.add_argument('--model-name', type = str, help = "gpt4")

args = parser.parse_args()

PROMPT = """You are ImageTaskEvaluatorGPT, an expert language model at judging whether or not a response adequately addresses an instruction in the context of an image. More specifically, you will be given the following:

1. An instruction: This is a question, an imperative request, or something similar about the image which requires a response.
2. A ground-truth response: This is the ground-truth response to the instruction in the context of the image annotated by the human annotator.
3. A predicted response: This response attempts to address the instruction in the context of the image without having access to the ground-truth response.

Your job is judge whether the predicted response is correct given the ground-truth response and the instruction.
 
Some things to remember:
- Even though you are just a language model, the instructions mostly require an objective answer i.e., the ground-truth response and instruction should be sufficient for you to judge the correctness of the predicted response. You do not need to have access to the complete image description.
- You are capable of judging response quality, accounting for important factors like correctness, relevance, fluency, specificity, etc. 
- You think step-by-step, and ultimately respond with your "Judgement: " as "Yes" or "No". Here, "Yes" implies that the predicted response is correct according to you, and "No" implies that the predicted response is not correct.
- Many times the predicted responses provide long explanations for their decision. In such cases, focus on whether the ground-truth response can be inferred from the predicted response or not. 

Instruction: {instruction}
Ground-truth Response: {groundtruth}
Predicted Response: {prediction}"""

def get_prompt(instruction, groundtruth, prediction):
    prompt = PROMPT.format(instruction = instruction, groundtruth = groundtruth, prediction = prediction)
    messages = [{"role": "user", "content": prompt}]
    return messages

def main():

    with open(args.master, 'r') as f:
        data = json.load(f)

    model = args.model_name
    model_responses = data[model]
    # print(model_responses)

    outfile = 'gpt4_judgments.json'
    if os.path.exists(outfile):
        with open(outfile, 'r') as f:
            judgement = json.load(f)
        if not (model in judgement):
            judgement[model] = {}
    else:
        judgement = {}
        judgement[model] = {}

    df = pd.read_csv(args.data_file)
    print(len(df))
    df = df.dropna(subset = ['response'])
    print(len(df))

    for j in tqdm(range(len(df))):
        image_url = df.iloc[j]['image_url']
        try:
            if image_url in model_responses and not (image_url) in judgement[model]:
                instruction = df.iloc[j]['instruction']
                ground_truth = df.iloc[j]['response']
                model_response = model_responses[image_url]
                completion = openai.ChatCompletion.create(
                    model = "gpt-4", 
                    messages = get_prompt(instruction, ground_truth, model_response)
                )
                output = completion['choices'][0]['message']['content']
                print(output)
                search  = regex.search("Judgement: ", output)
                if search == None:
                    if output == "Yes":
                        judgement[model][image_url] = 1
                    elif output == "No": 
                        judgement[model][image_url] = 0
                    continue
                index = search.span()[1]                
                output = output[index:]
                if "Yes" in output:
                    judgement[model][image_url] = 1
                elif "No" in output:
                    judgement[model][image_url] = 0
                else:
                    continue
                with open(outfile, 'w') as f:
                    print(judgement[model][image_url])
                    json.dump(judgement, f)
        except:
            continue

if __name__ == "__main__":
    main()