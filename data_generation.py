import spotipy
import sys
from spotipy.oauth2 import SpotifyClientCredentials
import pprint
import pandas as pd
import numpy as np
import sqlite3
from seeds import seeds

"""
    Make sure you have the following environment variables set:
        SPOTIPY_CLIENT_ID
        SPOTIPY_CLIENT_SECRET
        SPOTIPY_REDIRECT_URI
"""

# Fetch information of an artist using spotipy.
#
# artist_name: The name of the artist we want to fetch info about.
# spotify: an object created after connecting to Spotipy library.
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

# Fetches a list of artists in dict representation from the given artist_names.
def fetch_artists(artist_names, spotify):
    fetched_artists = []

    for artist_name in artist_names:
        fetched_artist = fetch_artist(artist_name, spotify)
        if fetched_artist is not None:
            fetched_artists.append(fetched_artist)

    return fetched_artists

def load_artists_to_db(artists, db_conn):
    artists_df = pd.DataFrame(artists)
    artists_df.to_sql(
        name='artist', 
        con=db_conn, 
        if_exists='replace', 
        index=False,
        # Following https://www.sqlite.org/datatype3.html to translate the required datatypes to sqlite3 types.
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




def fetch_albums_by_artist(artist, spotify):
    albums_search_result = spotify.artist_albums(artist_id = artist['artist_uri'], album_type = 'album', country = 'US')
    albums_list_raw = albums_search_result['items']

    albums_list = []

    for album_raw in albums_list_raw:
        album = {
            'album_id': album_raw['id'],
            'album_name': album_raw['name'],
            'external_url': album_raw['external_urls']['spotify'],
            'image_url': album_raw['images'][0]['url'], # could be empty list, need to check emptiness before accessing the 1st element.
            'release_date': album_raw['release_date'],
            'total_tracks': album_raw['total_tracks'],
            'type': album_raw['type'],
            'album_uri': album_raw['uri'],
            'artist_id': artist['artist_id'] # due to possibility of multiple artists, use artist id directly from input artist.
        }
        albums_list.append(album)

    return albums_list


def fetch_albums_for_all_artists(artists, spotify):
    all_albums_nested = []

    for artist in artists:
        fetched_albums = fetch_albums_by_artist(artist, spotify)
        all_albums_nested.append(fetched_albums)

    all_albums = list(np.concatenate(all_albums_nested).flat)
    return all_albums


def load_albums_to_db(albums, db_conn):
    albums_df = pd.DataFrame(albums)
    albums_df.to_sql(
        name='album', 
        con=db_conn, 
        if_exists='replace', 
        index=False,
        # Following https://www.sqlite.org/datatype3.html to translate the required datatypes to sqlite3 types.
        dtype={
            'album_id': 'TEXT',
            'album_name': 'TEXT',
            'external_url': 'TEXT',
            'image_url': 'TEXT',
            'release_date': 'TEXT', # use text for now, convert to date type later
            'total_tracks': 'INTEGER',
            'type': 'TEXT',
            'album_uri': 'TEXT',
            'artist_id': 'TEXT'
        }
    )

if __name__ == '__main__':
    # Step 1: Create the datasets.
    spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials())
    
    artists = fetch_artists(seeds, spotify)
    albums = fetch_albums_for_all_artists(artists=artists, spotify=spotify)

    # Step 2: Write the datasets to DB.
    db_conn = sqlite3.connect('spotify.db')
    load_artists_to_db(artists, db_conn)
    load_albums_to_db(albums, db_conn)

    # print(len(albums))