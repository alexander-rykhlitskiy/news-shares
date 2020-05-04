import glob, os
import json

NETWORKS = ['odnoklassniki', 'vkontakte', 'facebook', 'viber', 'telegram']

stats = []
for file in glob.glob('tmp/*.json'):
    with open(file, 'r') as f:
        stat = json.load(f)
        stat = {k:v for k, v in stat.items() if v and v.get('tags')}
        stats.append(stat)

def has_in_tags(data, word):
    return bool([True for tag in data['tags'] if word in tag.lower()])

def has_in_title(data, word):
    return word.lower() in data['title'].lower()

def has(word):
    def result_condition(data):
        return has_in_title(data, word) or has_in_tags(data, word)
    return result_condition

def sum_social_networks(stats, condition=None):
    result = {network:0 for network in NETWORKS}
    news_number = 0
    for stat in stats:
        for _url, data in stat.items():
            if condition:
                if not condition(data):
                    continue
            news_number += 1
            for network in NETWORKS:
                if data[network]:
                    result[network] += int(data[network])
    return result, news_number

def shares(sums):
    reposts_number = sum([number for _network, number in sums.items()])
    result = {}
    for network, number in sums.items():
        share = number / reposts_number
        result[network] = '{:.3f}'.format(share)
    return result

def analyze(word):
    sums, news_number = sum_social_networks(stats, condition=has(word))
    result = shares(sums)
    print(f"{result} - {news_number} - {word}")

analyze('')
# analyze('коронавирус')
# analyze('лукашенко')
# analyze('россия')
# analyze('минск')

import pandas as pd
import numpy as np

all_stats = {}
for stat in stats:
    all_stats = {**all_stats, **stat}

df = pd.DataFrame.from_dict(all_stats, orient='index')
df[NETWORKS] = df[NETWORKS].applymap(lambda x: np.int64(x) if x else 0)
print(df)

pd.options.display.max_colwidth = 120
def most_popular(network):
    return df.sort_values(network, ascending = False, inplace = False).reset_index().head(10)[NETWORKS + ['title']]

for network in NETWORKS:
    print(network)
    print(most_popular(network))
    print()

# sum_all = sum_social_networks(stats)
# print(shares(sum_all))
# sum_coron = sum_social_networks(stats, condition=has('коронавирус'))
# print(shares(sum_coron))
# for network, number in sum_all.items():
#     print(f"{network}: {round(sum_coron[network] / number, ROUND_BASE)}")

