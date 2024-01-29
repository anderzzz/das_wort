"""Fetch data from Swedish language Wikipedia.

"""
import yaml
import csv
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
with open(config['text_source']['text_data_file'], 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=config['text_source']['field_names'])
    writer.writeheader()

    for k_page, page_title in enumerate(config['text_source']['wikipedia']['swedish_monarchs']):
        page = wikipedia.page(page_title)
        data_chunk = {
            'document_id': k_page,
            'title': page.title,
            'url': page.url,
            'content': page.content,
        }
        if not data_chunk.keys() == config['text_source']['field_names']:
            raise ValueError('The keys of the data chunk do not match the field names in the configuration file.')

        writer.writerow(data_chunk)
