#!/usr/bin/env python3

"""Utility to create or update Elasticsearch index templates. If the number of shards is passed as a command-line argument, it uses that otherwise, it decides the number with either of the following criteria based on the flag passed as command-line argument:
    1. Number of data nodes available in the cluster
    2. The average data volume of the indices for last n days where n is a number

Usage:
    template.py put_template --index_pattern=<index_pattern> --use_data_nodes=<use_data_nodes> [--number_of_shards=<number_of_shards>]
    template.py put_template -h|--help
    template.py put_template -v|--version
    
Options:
    --index_pattern=<index_pattern>  Index pattern e.g. metrics-*, logs-*
    --use_data_nodes=<use_data_nodes>  Whether to use number of data nodes. Accepts True or False
    --number_of_shards=<number_of_shards>  Number of primary number shards e.g 1, 3, 4
    -h --help  Show this screen
    -v --version  Show version


"""

import chevron
import logging
from docopt import docopt
from es_properties import EsProperties
import requests
from requests.auth import HTTPBasicAuth
import math


logger = logging.getLogger("shard_utility")

# Create handlers
file_hdlr = logging.FileHandler("/tmp/es_shards_util.log")
console_hdlr = logging.StreamHandler()

# Set logging format
formatter = logging.Formatter(
    "%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s"
)
file_hdlr.setFormatter(formatter)
console_hdlr.setFormatter(formatter)

# Add handleres to logger
logger.addHandler(file_hdlr)
logger.addHandler(console_hdlr)

# Set log level
logger.setLevel(logging.INFO)

properties = EsProperties.read_es_properties()
logger.info("Elasticsearch properties %s", str(properties))
headers = {"Content-Type": "application/json"}


def put_templates(
    index_pattern: str, use_data_nodes: bool, number_of_shards: int = None
):

    num_shards = 1
    if number_of_shards != None:
        num_shards = number_of_shards
    else:
        num_shards = __get_number_shards(index_pattern, use_data_nodes)

    logger.info("Index pattern: %s and number of shards: %s", index_pattern, num_shards)
    put_template_response = __update(index_pattern, num_shards)
    logger.info("Index create/update response %s", put_template_response)


def __get_number_shards(index_pattern: str, use_data_nodes: bool):
    if use_data_nodes:
        return __get_shards_using_data_nodes()
    else:
        return __get_shards_using_indices_volume(index_pattern)


def __get_shards_using_indices_volume(index_pattern: str):
    request_url = (
        properties.url + "/" + "_cat/indices/" + index_pattern + "?v&format=JSON"
    )
    response = __execute_get_request(request_url)

    if not response.json():
        raise ValueError("No previouse details for index pattern: " + index_pattern)

    upper_bound = properties.number_of_days_to_sample
    if properties.number_of_days_to_sample <= len(response.json()):
        upper_bound = properties.number_of_days_to_sample
    else:
        upper_bound = len(response.json())

    total = 0.0
    for x in range(upper_bound):
        element = response.json()[x]
        total = total + __get_size(element.get("pri.store.size"))

    if total / properties.number_of_days_to_sample < 30:
        return 1
    else:
        return math.ceil(1 + (total / properties.number_of_days_to_sample) / 30)


def __get_size(size_str: str):
    if "gb" in size_str:
        return float(size_str.replace("gb", ""))
    elif "mb" in size_str:
        # TODO: convert it to GB
        return float(size_str.replace("mb", "")) / 1024
    elif "kb" in size_str:
        # TODO: convert it to GB
        return float(size_str.replace("kb", "")) / 1048576
    elif "b" in size_str:
        # TODO: convert it to GB
        return float(size_str.replace("b", "")) / 1073741824


def __get_shards_using_data_nodes():
    request_url = properties.url + "/" + "_cluster/health"
    response = __execute_get_request(request_url)
    if response.status_code == 200:
        return response.json().get("number_of_data_nodes")
    else:
        raise RuntimeError("Failed to get details from Elasticsearch")


def __execute_get_request(request_url: str):
    if len(properties.username) == 0 and len(properties.password) == 0:
        return requests.get(request_url, headers=headers)
    else:
        return requests.get(
            request_url,
            headers=headers,
            auth=HTTPBasicAuth(properties.username, properties.password),
        )


def __update(index_pattern: str, number_of_shards: int):
    result = __render_template(index_pattern, number_of_shards)
    return put_template(result, index_pattern).json()


def put_template(template: str, index_pattern: str):
    template_id = index_pattern.replace("_*", "_template")
    request_url = properties.url + "/_template" + "/" + template_id
    if len(properties.username) == 0 and len(properties.password) == 0:
        return requests.post(request_url, data=template, headers=headers)
    else:
        return requests.post(
            request_url,
            data=template,
            headers=headers,
            auth=HTTPBasicAuth(properties.username, properties.password),
        )


def __render_template(index_patterns: str, number_of_shards: int):
    with open("template/index_template.mustache", "r") as f:
        result = chevron.render(
            f, {"index_patterns": index_patterns, "number_of_shards": number_of_shards},
        )
        logger.info("Result of the template rendering from file: %s", result)
        return result


if __name__ == "__main__":
    arguments = docopt(__doc__, version="0.0.1")
    if (
        arguments["--index_pattern"]
        and arguments["--use_data_nodes"]
        and arguments["--number_of_shards"]
    ):
        put_templates(arguments["--index_pattern"], arguments["--number_of_shards"])
    elif arguments["--index_pattern"] and arguments["--use_data_nodes"]:
        put_templates(arguments["--index_pattern"], arguments["--use_data_nodes"])
    else:
        print(arguments)