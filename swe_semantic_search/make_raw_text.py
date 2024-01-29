"""Create the raw text data to be used in the semantic search.

This script collects the text from Swedish language Wikipedia.

"""
import yaml
import wikipedia
import sqlite3

from segment_text import make_segments_of_

#
# Parse the configuration file
with open('./conf.yaml', 'r') as f:
    config = yaml.safe_load(f)

#
# Prepare the Wikipedia API
wikipedia.set_lang("sv")

#
# Connect to the SQLite database
conn = sqlite3.connect(config['text_source']['text_data_file'])
cur = conn.cursor()
sql_create = """
CREATE TABLE document (
    surrogate_key INT PRIMARY KEY AUTOINCREMENT,
    text_id INTEGER,
    segment_id INTEGER,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    content TEXT NOT NULL,
    UNIQUE (text_id, segment_id)
);
"""
cur.execute(sql_create)

#
# Prepare the SQL statement to be used for inserting data
sql_insert = """
INSERT INTO document (text_id, segment_id, title, url, content)
VALUES (?, ?, ?, ?, ?)
"""

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
        cur.execute(sql_insert, (
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
