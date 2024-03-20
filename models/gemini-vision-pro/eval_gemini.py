import typing
import vertexai
import http.client
import urllib.request
from google.cloud import aiplatform
from vertexai.preview.generative_models import GenerativeModel, Image

import os
import json
import openai
import argparse
import pandas as pd
from tqdm import tqdm

import base64
import requests

'''
    gcloud auth application-default login
'''

parser = argparse.ArgumentParser()
parser.add_argument("--image-file", type=str, required=True)
parser.add_argument("--outfile", type=str, default = 'master.json')
args = parser.parse_args()

def load_image_from_url(image_url: str) -> Image:
    with urllib.request.urlopen(image_url) as response:
        response = typing.cast(http.client.HTTPResponse, response)
        image_bytes = response.read()
    return Image.from_bytes(image_bytes)

def generate(image, text, context = None):
    model = GenerativeModel("gemini-pro-vision")
    responses = model.generate_content(
    [image, text],
        generation_config={
            "max_output_tokens": 2048,
            "temperature": 0.4,
            "top_p": 1,
            "top_k": 32
        },
        stream=True,
    )

    for response in responses:
        return response.candidates[0].content.parts[0].text

def main():

    model = "gemini-pro-vision"
    outfile = args.outfile

    if os.path.exists(outfile):
        with open(outfile, 'r') as f:
            master = json.load(f) 
        if not (model in master):
            master[model] = {}
    else:
        master = {}
        master[model] = {}

    df = pd.read_csv(args.image_file)

    for j in tqdm(range(len(df))):
        image_url = df.iloc[j]['image_url']
        try:
            if not (image_url in master[model]):
                text = df.iloc[j]['instruction']
                image = load_image_from_url(image_url)
                response = generate(image, text)
                master[model][image_url] = response
                with open(outfile, 'w') as f:
                    json.dump(master, f)
        except:
            continue

if __name__ == "__main__":
    main()