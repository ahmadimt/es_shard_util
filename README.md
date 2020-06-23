# Elasticsearch Utility for creating  or updating index templates

Utility to create or update Elasticsearch index templates based on number of data nodes or the data volumes of previous indices. 

## Description
If the number of shards is passed as a command-line argument, it uses that otherwise, it decides the number with either of the following criteria, based on the flag passed at command-line:
* Number of data nodes available in the cluster or 
* The average data volume of the indices in the last n days. Here n can be defined in `template.ini` file.

This utility is helpful when we have rolling indices. For example, one index per day, a typical use case of log processing.

## Setup Python Depenedencies

### Enable virtual environment

#### Installation
`python3 -m pip install --user virtualenv`

Navigate to the utility directory and run

`python3 -m venv venv`

#### Activation
The following command activates the virtual environment

`. venv/bin/activate`

### Install Utility Dependencies
`python setup.py install`


## Running the Utility
`./template.py put_template --index_pattern=<index_pattern> --use_data_nodes=<use_data_nodes> [--number_of_shards=<number_of_shards>]`

or

`./template.py put_template --index_pattern=<index_pattern> --use_data_nodes=<use_data_nodes>`

`index_pattern`     string representing the base name of the indices.e.g log-*.
`use_data_nodes`    this flag dictates to check number of the data nodes in cluster and then use the number as number of primary shards. 
`number_of_shards` is an optional parameter. If you provide via command-line , that number will be used, otherwise it will decide the number of shards as described in [here](#Description).
