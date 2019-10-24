[![Build Status](https://travis-ci.org/dlesz/RecSysExperiment.svg?branch=master)](https://travis-ci.org/dlesz/RecSysExperiment)

# RS Experiment

This repository is home to the source code implemented for *Interactive Data Visualization for a better understanding of Recommender Systems*, Master Thesis by Dennis Leszkowicz, IT-University of Copenhagen, Denmark (January 2019).

The source code is two fold, first part is a Flask web application that implements the recommender system described in the paper. The second part is a collection of notebooks and scripts that shows how the system came along, making it possible to recreate the needed data structures from scratch.

### Credits

Thanks to Ben Frederickson for the [Implicit](https://github.com/benfred/implicit/) library

Thanks to Òscar Celma for creating the Last.fm 360K Users Dataset. The dataset can be downloaded [here]( 
http://ocelma.net/MusicRecommendationDataset/index.html).

A cleaned Last.fm dataset in hdf5 used for this project has been borrowed from Ben Frederickson, more info [here](https://github.com/benfred/implicit/blob/master/implicit/datasets/lastfm.py).

---
## Getting Started

### 1. Install requirements.

This project has been developed in Python 3.7 in anaconda virtual environment. 

``conda create --name <envname> python=3.7``

``conda activate <envname>``

`` pip install -r requirements.txt ``

Dendencies included in `requirements.txt`

[`flask`](http://flask.pocoo.org/)
[`h5py`](https://www.h5py.org/)
[`implicit`](http://github.com/benfred/implicit/)
[`Jinja2`](https://pypi.org/project/Jinja2/)
[`markupsafe`](https://pypi.org/project/MarkupSafe/)
[`matplotlib`](http://matplotlib.org/)
[`numpy`](http://www.numpy.org/)

[`pylast`](https://pypi.org/project/pylast/)
[`redis`](https://pypi.org/project/redis/)
[`scipy`](http://www.scipy.org/)
[`seaborn`](http://seaborn.pydata.org/)
[`tables`](https://pypi.org/project/tables/)
[`tqdm`](https://pypi.org/project/tqdm/)
[`wordcloud`](https://github.com/amueller/word_cloud)

Additionally make sure to install [Jupyter notebook](https://jupyter.org/) for the notebook ``.ipynb`` collection.

---
# 1. Download data

To download the needed data there are two options:

**Option A (quick):** Running the shell script ```sh download_data.sh``` will download and place all the aggregated data in ```flaskapp/data/```

___

**Option B (slow):** Run scripts located in `scripts/` folder to recreate the data structures used for the webapp. This process takes hours, and requires you to:

1. Download the lastfm dataset ```lastfm_360k.hdf5``` [here](https://github.com/benfred/recommender_data/releases/download/v1.0/lastfm_360k.hdf5) and place it in ``flaskapp/data/``.

2. Download ```lastfm_tags_cleaned.csv``` dataset [here](https://drive.google.com/open?id=1-sDvO0BDi2rBzqBW061kdZa4lfIS_9-R) and place it here ```flaskapp/data/```.




In order to recreate the data structures used for this project,`.py` script in following order.


1. `01make_user_profile_dict.py`

2. `02make_tag_aggregations.py`

## Development mode

```
# set to True if development mode, otherwise production mode.
dev_mode = False
```

In order to run debug mode in the Flask enviroment this variable is set `dev_mode = True` in `app.py`. This ensures that the debugger and hot code-reloading is on.

---

# 2. Run locally

1. start the redis server by runnning `redis-server`.

2. run `python app.py ` from the `flaskapp/` folder.

or alternatively set `export FLASK_ENV=development` / `export FLASK_ENV=deployment`  and run `flask run`

NB! `app.py` should run just fine.

This will run the web application on http://127.0.0.1:6543/

# 3. Deploy with Docker Compose

```docker-compose up -d --build```

This will run the web application on http://127.0.0.1:6543/

to stop the service run:

```docker-compose stop```
