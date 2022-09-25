import spotipy
import sys
from spotipy.oauth2 import SpotifyClientCredentials
import pprint
import pandas as pd
import sqlite3
from seeds import seeds
# import sqlalchemy as sa


"""
    Make sure you have the following environment variables set:
        SPOTIPY_CLIENT_ID
        SPOTIPY_CLIENT_SECRET
        SPOTIPY_REDIRECT_URI
"""

print(seeds)

spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials())

# Could be None.
def fetch_artist(artist_name, spotify):
    artist_search_result = spotify.search(q=f'artist:{artist_name}', limit=1, type='artist')
    artist_list = artist_search_result['artists']['items']
    if len(artist_list) == 0:
        return None
    
    artist_raw = artist_list[0]
    artist = {
        'artist_id': artist_raw['id'],
        'artist_name': artist_raw['name'],
        'external_url': artist_raw['external_urls']['spotify'],
        'genre': artist_raw['genres'][0], # could be empty list, need to check emptiness before accessing the 1st element.
        'image_url': artist_raw['images'][0]['url'], # could be empty list, need to check emptiness before accessing the 1st element.
        'followers': artist_raw['followers']['total'],
        'popularity': artist_raw['popularity'],
        'type': artist_raw['type'],
        'artist_uri': artist_raw['uri']
    }

    return artist

def fetch_artists(artist_names, spotify):
    fetched_artists = []

    for artist_name in artist_names:
        fetched_artists.append(fetch_artist(artist_name, spotify))

    return fetched_artists

# artist_id | artist_name | external_url | genre | image_url | followers | popularity | type | artist_uri

# define artist search term.
artist_name = 'travis'
# Query to get 1 artist result



if len(artist_list) > 0:
    artist_raw = artist_list[0]
    # Extract data for artist table.

    artist = {
        'artist_id': artist_raw['id'],
        'artist_name': artist_raw['name'],
        'external_url': artist_raw['external_urls']['spotify'],
        'genre': artist_raw['genres'][0], # could be empty list, need to check emptiness before accessing the 1st element.
        'image_url': artist_raw['images'][0]['url'], # could be empty list, need to check emptiness before accessing the 1st element.
        'followers': artist_raw['followers']['total'],
        'popularity': artist_raw['popularity'],
        'type': artist_raw['type'],
        'artist_uri': artist_raw['uri']
    }

    print(type(artist['artist_id']))

    # artist['artist_id'] = artist_raw['id']
    # artist['artist_name'] = artist_raw['name']
    # artist['external_url'] = artist_raw['external_urls']['spotify']
    # artist['genre'] = artist_raw['genres'][0] # could be empty list, need to check emptiness before accessing the 1st element.
    # artist['image_url'] = artist_raw['images'][0]['url'] # could be empty list, need to check emptiness before accessing the 1st element.
    # artist['followers'] = artist_raw['followers']['total']
    # artist['popularity'] = artist_raw['popularity']
    # artist['type'] = artist_raw['type']
    # artist['artist_uri'] = artist_raw['uri']
    
    # Artist in pandas dataframe format.
    artist_df = pd.DataFrame([artist])

    db_file_name = 'spotify.db'
    conn = sqlite3.connect(db_file_name)

    # to_sql doc: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_sql.html#pandas-dataframe-to-sql
    #
    # Following https://www.sqlite.org/datatype3.html to translate the datatypes to sqlite3 types.
    num_inserted = artist_df.to_sql(
        name='artist', 
        con=conn, 
        if_exists='replace', 
        index=False, 
        dtype={
            'artist_id': 'TEXT',
            'artist_name': 'TEXT',
            'external_url': 'TEXT',
            'genre': 'TEXT',
            'image_url': 'TEXT',
            'followers': 'INTEGER',
            'popularity': 'INTEGER',
            'type': 'TEXT',
            'artist_uri': 'TEXT'
        }
    )

    # print(num_inserted)

    # print(artist_df)
    
    # pprint.pprint(artist_id)

