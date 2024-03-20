import os
import json
import openai
import argparse
import pandas as pd
from tqdm import tqdm

parser = argparse.ArgumentParser()
parser.add_argument("--data-file", type=str, required=True)
args = parser.parse_args()


def get_payload(text, image_url):
    payload = {
        "messages": [
            {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": text
                },
                {
                "type": "image_url",
                "image_url": {
                    "url": image_url
                }
                },
            ]
            }
            ],
            "max_tokens": 300
        }
    return payload


def main():

    model = "gpt-4-vision-preview"
    outfile = "master.json"

    if os.path.exists(outfile):
        with open(outfile, 'r') as f:
            master = json.load(f) 
        if not (model in master):
            master[model] = {}
    else:
        master = {}
        master[model] = {}

    df = pd.read_csv(args.data_file)

    for j in tqdm(range(len(df))):
        image_url = df.iloc[j]['image_url']
        try:
            if not (image_url in master[model]):
                instruction = df.iloc[j]['instruction']
                text = instruction
                messages = get_payload(text, image_url)['messages']
                response = openai.ChatCompletion.create(model = "gpt-4-vision-preview", messages = messages, max_tokens=300)
                output = response['choices'][0]['message']['content']
                master[model][image_url] = output
                with open(outfile, 'w') as f:
                    json.dump(master, f)
        except:
            continue

if __name__ == "__main__":
    main()