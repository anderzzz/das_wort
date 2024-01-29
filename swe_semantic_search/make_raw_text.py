"""Create the raw text data to be used in the semantic search.

This script collects the text from Swedish language Wikipedia.

"""
import os
import yaml
import wikipedia
import sqlite3

from segment_text import make_segments_of_

#
# Parse the configuration file and sql strings file
with open('./conf.yaml', 'r') as f:
    config = yaml.safe_load(f)
with open('./sql_strings.yaml', 'r') as f:
    sql_strings = yaml.safe_load(f)

#
# Prepare the Wikipedia API
wikipedia.set_lang("sv")

#
# Connect to the SQLite database. In case the database file already exists, it is overwritten.
if os.path.exists(config['text_source']['text_data_file']):
    os.remove(config['text_source']['text_data_file'])
conn = sqlite3.connect(config['text_source']['text_data_file'])
cur = conn.cursor()

#
# Create the table and the insert statement
cur.execute(sql_strings['sql_create'])

#
# Iterate over pages, fetch data, segment text per page and insert into database
for k_page, page_title in enumerate(config['text_source']['wikipedia']['swedish_monarchs']):
    page = wikipedia.page(page_title)
    data_chunk = {
        'text_id': k_page,
        'title': page.title,
        'url': page.url,
        'content': page.content,
    }
    text_segments = make_segments_of_(
        text=data_chunk['content'],
        max_words_in_segment=config['segmentor']['max_segment_size'],
        n_overlapping_sentences=config['segmentor']['n_overlapping_sentences'],
    )
    for k_segment, segment in enumerate(text_segments):
        cur.execute(sql_strings['sql_insert'], (
            data_chunk['text_id'],
            k_segment,
            data_chunk['title'],
            data_chunk['url'],
            segment
        ))

#
# Commit and close connection
conn.commit()
conn.close()
