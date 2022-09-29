import spotipy
import sys
from spotipy.oauth2 import SpotifyClientCredentials
import pprint
import pandas as pd
import numpy as np
import sqlite3
from seeds import seeds
from data_generation.artists_generation import fetch_artists, load_artists_to_db
from data_generation.albums_generation import fetch_albums_for_all_artists, load_albums_to_db
from data_generation.tracks_generation import fetch_tracks_for_all_albums, load_tracks_to_db
from data_generation.track_features_generation import fetch_features_for_all_tracks, load_tracks_features_to_db

"""
    Make sure you have the following environment variables set:
        SPOTIPY_CLIENT_ID
        SPOTIPY_CLIENT_SECRET
        SPOTIPY_REDIRECT_URI
"""

if __name__ == '__main__':
    # # Step 1: Create the datasets.
    spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials())
    
    artists = fetch_artists(seeds, spotify)
    print("artists_size: ",len(artists))

    albums = fetch_albums_for_all_artists(artists, spotify)
    print("albums_size: ",len(albums))

    tracks = fetch_tracks_for_all_albums(albums, spotify)
    print("tracks_size: ",len(tracks))

    track_features = fetch_features_for_all_tracks(tracks, spotify)
    print("track_features_size: ",len(track_features))

    print("All datasets are ready to be imported into db!!!")

    # Step 2: Write the datasets to DB.
    db_conn = sqlite3.connect('spotify.db')
    print("connected to db!!!")
    load_artists_to_db(artists, db_conn)
    load_albums_to_db(albums, db_conn)
    load_tracks_to_db(tracks, db_conn)
    load_tracks_features_to_db(track_features, db_conn)
    print("finished loading to db!!!")

    # res = spotify.album_tracks(album_id='2FfewmvnA0wctMD64KjOxP', limit=50, offset=0)
    # pprint.pprint(res['items'][0])