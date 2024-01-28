"""Fetch data from Wikipedia.

"""
import yaml
import json
import wikipedia

#
# Parse the configuration file
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)


