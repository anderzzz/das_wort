The following code implements a basic algorithm for semantic search in text data in Swedish. The code is part of a blog post: https://medium.com/@AJOhrn/semantisk-s%C3%B6kning-i-egen-data-f%C3%B6r-egen-maskin-2eaf837a2302

The code includes the parts:
* Create illustrative textdata in Swedish by scraping Wikipedia articles, see `make_raw_text.py`
* Create a vector database (Qdrant) given the SQL table with textdata, see `make_vec_db.py`
* Query the vector database, that is, perform the semantic search and gather the associated text data, see `semantic_searcher.py`

Supporting code is:
* `segment_text.py` for segmenting text into sentences, partially overlapping.
* `row_factory.py` for reusable SQL row factory.

The execution of the algorithm is configured in the `conf.yaml` file. Many variations of the algorithm can be run simply by changing the configuration file.

The repository contains an SQL table with text from Swedish-language Wikipedia articles for Swedish monarch from Sten Sture den Äldre and onwards. The table was created end of January 2024.

In order to execute a semantic search a vector database must first be created, which is done by executing the `make_vec_db.py` script. After that the `semantic_searcher.py` script can be executed. The search query is part of the configuration file.

The code is free to use and modify. I make no guarantees about the quality of the code. My intent is to educate, spread knowledge and make us all better at what we do, more peaceful and prosperous.