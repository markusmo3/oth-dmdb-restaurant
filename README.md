# Repository Overview
* `data` contains all the data that we work with and a Dockerfile to import the deduped data into mongodb
* `jupyter` contains a Dockerfile to run Jupyter notebook
* `notebooks` contains the notebooks that were used for testing and playing around with the data
* `src` contains the final python source code
  * `main.py` is the main source file to execute
  * `utils.py` is a file for utility functions and contains config values
  * `clean.py` contains the old approach to data cleaning and only exists for documentation purposes
  * `test_*.py` test classes
* `docker-compose.yml` docker-compose file to run the Jupyter notebook
* `importToMongo.bat` Batch script to build a Dockerfile, that imports the generated data into a remote mongodb, hosted by atlas
* `requirements.txt` Pip Requirements document
* `up.bat` helper batch script to run the Jupyter notebook

# Minimal workflow
* install all pip dependencies
* run `src/main.py`
  * the files `data/work/deduped_clean.json` and `data/work/deduped_raw.json` got generated
* import them into MongoDB
  * either by using the importToMongo.bat script, that calls the `data/Dockerfile-mongoimport`, 
  which needs some modification to import into a custom server
  * or by calling the mongoimport utility directly (requires mongodb to be installed locally)

# Important Note
I played around a lot and came to the solution in `src/clean.py`, but on 05.01.2020 
i had another idea, which turned out to be A LOT better, find 
all the duplicates and was a lot simpler.

That new solution can be found in `src/main.py`.
The Paper was originally written for the old solution, which is why i completely copied
and rewrote it.

# Software used
* Python 3.7.2
* PyCharm Professional 2019.3
* pip packages in `requirements.txt`

# Docker
This repository contains the necessary files to run Jupyter Notebooks under Docker.
Just run `docker-compose up` in the root directory or execute the `up.bat` script.

It also includes a Dockerfile to import the finished deduped data into mongodb,
which can be called with `importToMongo.bat`.

Download and install Docker (Desktop): <https://www.docker.com/products/docker-desktop>

# Paper
This project includes writing a paper about it, which can be found here: 

New Solution: <https://www.overleaf.com/read/cptxymqmrhmk>

Old Solution: <https://www.overleaf.com/read/vzdpqgxvdzrb>

## Credentials
The credentials contained in this repository were invalidated before making them public.
