import os
import json
import argparse
import pandas as pd
from tqdm import tqdm
from collections import defaultdict
import statsmodels.api as sm 

parser = argparse.ArgumentParser()

parser.add_argument('--data-file', type = str, help = "all data file")
parser.add_argument('--judgment-file', type = str, help = "judgemnt_file")
parser.add_argument('--model-name', type = str, help = "gpt4")

args = parser.parse_args()

def main():

    df = pd.read_csv(args.data_file)
    img_dict = {}
    for j in range(len(df)):
        row = df.iloc[j]
        img_dict[row['image_url']] = {'category': row['category']}
    
    with open(args.judgment_file, 'r') as f:
        judgements = json.load(f)
    
    model_data = judgements[args.model_name]

    outfile = f'gpt_4_model_analysis.json'

    if os.path.exists(outfile):
        with open(outfile, 'r') as f:
            model_analysis = json.load(f)
    else:
        model_analysis = {}

    ext = [0,0]
    math = [0,0]
    cat = {'time': [0,0], 'shopping': [0,0], 'navigation-transportation': [0,0], 'abstract': [0,0], 'app': [0,0], 'web': [0,0], 'infographics': [0,0], 'stvqa': [0,0], 'estvqa': [0,0]}
    count, total = 0, 0
    for key in model_data:
        if key in img_dict:
            img_data = img_dict[key]
            rating = model_data[key]
            count += rating
            total += 1
            cat[img_data['category']][1] += 1
            cat[img_data['category']][0] += rating

    model_analysis[args.model_name] = {'category': cat}
    print(f"Rating: {100 * count/total} | Total: {total} | CI 95%: {sm.stats.proportion_confint(count, total, alpha = 0.05)}")
    x = model_analysis[args.model_name]['category']
    for h in x:
        print(f'{h}: {100*x[h][0]/x[h][1]}')
    y = 100 * (x['stvqa'][0] + x['estvqa'][0])/(x['stvqa'][1] + x['stvqa'][1])
    print(f'Misc. Natural Scenes: {y}')


if __name__ == "__main__":
    main()