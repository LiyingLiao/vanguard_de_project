# Submission Readme

## Context
This is a take home project for the 2022 Vanguard data engineering apprenticeship interview.

Follow `Get Started` to get hands on experience with the project application. 

Follow `High Level Overview` to get a quick understanding of how this project was structured and built.

## Get Started
### Step 1 - Make a local copy of this project
Clone this project to your local machine. Follow the [official GitHub cloning guide](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository) for how to do this.

### Step 2 - Set up the environment
Open your terminal and `cd` into your local project folder (the clone), run the following commands to install the required dependencies:
```bash
# 1. Create a virtual environment
python -m venv .venv

# 2. Activate the virtual environment
source .venv/bin/activate # macOS
.venv/Scripts/Activate.ps1 # Windows

# 3. Update pip
python -m pip install --upgrade pip

# 4. Install dependencies from requirements.txt 
pip install -r requirements.txt

# 5 Set up required environmental variables
export SPOTIPY_CLIENT_ID=<your Spotify API client ID>
export SPOTIPY_CLIENT_SECRET=<your Spotify API client secret>
export SPOTIPY_REDIRECT_URI=http://localhost:8888/callback
```

> **Note**: Follow this [Onramp guide](https://github.com/onramp-io/vanguard_de_project#getting-spotify-authentication-credentials) to set up your own API client_id and client_secret

### Step 3 - Generate data
At this point, you should've set up your environment. Run the following command to generate the datasets and load them into a sqlite database:
```bash
python submission/data_generation.py
```
You should see a `spotify.db` file under the `submission/` folder. This is the database which you can query with tools such as [DB browser for SQLite](https://sqlitebrowser.org/).

### Step 4 - Create views
Run the following command to create the views:
```bash
python submission/view_creation.py
```
The following views should've been created inside the database:

* v_top_artists_by_followers
* v_top_songs_by_artist_duration
* v_top_songs_by_artist_tempo
* v_features_per_popularity_group
* v_artist_features_over_time

### Step 5 - Generate visualization
Run the following command to generate the visualization:
```bash
python submission/data_visualization.py
```
A PDF called `visualization.pdf` should've been created under the `submission/` folder. It includes a few plots based on the `views` you generated in step 4.

Congratulations! You've completed the project tutorial. For more details about the project design, refer to the next section.

## High Level Overview
The following diagram shows the file structure under the `submission/` folder:
```bash
submission
    ├── data_generation
    │   ├── __init__.py
    │   ├── albums_generation.py
    │   ├── artists_generation.py
    │   ├── track_features_generation.py
    │   └── tracks_generation.py
    ├── data_visualization
    │   ├── __init__.py
    │   ├── plot_counts_per_popularity_group.py
    │   ├── plot_features_of_an_artist_over_time.py
    │   ├── plot_features_per_popularity_group.py
    │   └── plot_top_artists_by_followers.py
    ├── view_creation
    │   ├── __init__.py
    │   ├── artist_features_over_time.py
    │   ├── features_per_popularity_group.py
    │   ├── top_artists_by_followers.py
    │   ├── top_songs_by_artist_duration.py
    │   └── top_songs_by_artist_tempo.py
    ├── data_generation.py
    ├── view_creation.py
    ├── data_visualization.py
    ├── spotify.db
    ├── visualization.pdf
    ├── seeds.py
    ├── requirements.txt
    └── readme.md
```

### The Runnable Files
These Python files at the top level are meant to be executed for creating project output:

* **data_generation.py** - responsible for data ETL
* **view_creation.py** - responsible to creating views on top of the raw tables
* **data_visualization.py** - responsible for generating the final visualization PDF

### The Helper Modules
For each runnable, there is a companion helper module with the same name e.g. the helper module for `data_generation.py` is called `data_generation`. The helper modules contain the core logics for this project:

* **data_generation** - contains ETL functions for each of the required tables
* **view_creation** - contains functions for creating the views. Each view resides in its own file.
* **data_visualization** - contains functions for generating the plots. Each plot resides in its own file.

### Sample Project Output
The following files are a sample result of executing this project application:

* **spotify.db** - the sqlite database containing the raw tables and the derived views. This is the result of running `data_generation.py` and `view_creation.py`
* **visualization** - the final PDF containing the plots. This is the result of running `data_visualization.py`

### Special Files

* **seeds.py** - a sample list of 20 artist names used as the project application input. The sample project output was created using this list.
* **requirements.txt** - contains the required dependencies for running this project application.
* **readme.md** - This file.

### Notable Design Decisions

* When searching artists on Spotify with artist names, I made sure that only artists with exact name matching are returned. This is to prevent wrong artists being fetched due to similar names. Name matching was case insensitive.
* Album and track deduplications were done based on their names instead of their IDs. This is due to Spotify storing the same album/track with different IDs. See this [StackOverflow reference](https://stackoverflow.com/questions/31741415/different-spotify-ids-for-the-same-track) as an example.
* When extracting `year` from album `release_date`, I noticed that some `release_date`s only contained `YYYY` instead of `YYYY-MM-DD`. A `CASE WHEN` statement was used to overcome this issue.
* After examining the extracted datasets based on the `seeds`, I noticed that there wasn't any null values, so I didn't make too much effort to clean the nulls. Instead, I added logics to print the number of nulls for each dataset for sanity checking.