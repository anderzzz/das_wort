"""Fetch data from Wikipedia.

"""
import yaml
import json
import wikipedia

#
# Parse the configuration file
with open('./conf.yaml', 'r') as f:
    config = yaml.safe_load(f)

#
# Prepare the Wikipedia API
wikipedia.set_lang("sv")

#
# Iterate over pages and fetch data
all_data = []
for k_page, page_title in enumerate(config['text_source']['wikipedia']['swedish_monarchs']):
    page = wikipedia.page(page_title)
    all_data.append({
        'document_id': k_page,
        'title': page.title,
        'url': page.url,
        'content': page.content,
    })

with open(config['text_source']['db_file'], 'w') as f:
    json.dump(all_data, f, indent=4, ensure_ascii=False)
