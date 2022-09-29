import spotipy
import sys
from spotipy.oauth2 import SpotifyClientCredentials
import pprint
import pandas as pd
import numpy as np
import sqlite3
from seeds import seeds
from data_generation.artists_generation import fetch_artists, load_artists_to_db

"""
    Make sure you have the following environment variables set:
        SPOTIPY_CLIENT_ID
        SPOTIPY_CLIENT_SECRET
        SPOTIPY_REDIRECT_URI
"""

# Fetch all albums by an artist.
# artist: the artist we are interested in.
# spotify: an object created after connecting to Spotipy library.
def fetch_albums_by_artist(artist, spotify):
    # Search the albums by an artist using the Spotify API.
    albums_search_result = spotify.artist_albums(artist_id=artist['artist_uri'], album_type='album', country='US')
    albums_list_raw = albums_search_result['items']

    albums_list = []

    # Convert the raw albums to the format compatible with the album table schema.
    for album_raw in albums_list_raw:
        # These properties could be empty.
        images = album_raw['images']

        album = {
            'album_id': album_raw['id'],
            'album_name': album_raw['name'],
            'external_url': album_raw['external_urls']['spotify'],
            'image_url': images[0]['url'] if len(images) > 0 else '', # Assign empty string if no image found.
            'release_date': album_raw['release_date'],
            'total_tracks': album_raw['total_tracks'],
            'type': album_raw['type'],
            'album_uri': album_raw['uri'],
            'artist_id': artist['artist_id'] # Due to possibility of multiple artists, use artist id directly from input artist.
        }
        albums_list.append(album)

    return albums_list

# Deduplicate the given albums by their album names and return deduplicated albums.
# albums: list of albums to be deduplicated.
# Can't deduplicate based on IDs since the same album may have different IDs (release version etc.)
# causing the same album to appear twice if based on ID.
def deduplicate_albums(albums):
    unique_albums = []
    visited_names = set()

    for album in albums:
        album_name = album['album_name']
        if album_name not in visited_names:
            unique_albums.append(album)
            visited_names.add(album_name)
    
    return unique_albums

# Fetch albums across all artists.
# artists: the list of artists we want to get the albums for.
# spotify: an object created after connecting to Spotipy library.
# Final albums are deduplicated based on their names.
def fetch_albums_for_all_artists(artists, spotify):
    all_albums_nested = []

    for artist in artists:
        fetched_albums = fetch_albums_by_artist(artist, spotify)
        all_albums_nested.append(fetched_albums)

    all_albums = list(np.concatenate(all_albums_nested).flat)
    unique_albums = deduplicate_albums(all_albums)
    return unique_albums

# Load the albums into database's album table.
# albums: the albums to load.
# db_conn: a database connection.
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
            'release_date': 'TEXT',
            'total_tracks': 'INTEGER',
            'type': 'TEXT',
            'album_uri': 'TEXT',
            'artist_id': 'TEXT'
        }
    )

# Fetch tracks associated with an album.
# album_id: the ID the album.
def fetch_tracks_by_album(album_id, spotify):
    # Search the tracks of an album using the Spotify API.
    tracks_search_result =  spotify.album_tracks(album_id=album_id, limit=50, offset=0)
    tracks_list_raw = tracks_search_result['items']

    tracks_list = []

    for track_raw in tracks_list_raw:
        track = {
            'track_id': track_raw['id'],
            'song_name': track_raw['name'],
            'external_url': track_raw['external_urls']['spotify'],
            'duration_ms': track_raw['duration_ms'], 
            'explicit': track_raw['explicit'],
            'disc_number': track_raw['disc_number'],
            'type': track_raw['type'],
            'song_uri': track_raw['uri'],
            'album_id': album_id
        }
        tracks_list.append(track)

    return tracks_list

# Deduplicate the given tracks based on their names.
#
# Same track may have different IDs, so can't deduplicate tracks based on ID.
def deduplicate_tracks(tracks):
    unique_tracks = []
    visited_names = set()

    for track in tracks:
        track_name = track['song_name']
        if track_name not in visited_names:
             unique_tracks.append(track)
             visited_names.add(track_name)
    
    return unique_tracks

# Fetch all tracks across all albums.
#
# Final tracks are deduplicated based on their IDs.
def fetch_tracks_for_all_albums(albums, spotify):
    all_tracks_nested = []

    for album in albums:
        fetched_tracks = fetch_tracks_by_album(album['album_id'], spotify)
        all_tracks_nested.append(fetched_tracks)

    all_tracks = list(np.concatenate(all_tracks_nested).flat)
    unique_tracks = deduplicate_tracks(all_tracks)
    return unique_tracks


def load_tracks_to_db(tracks, db_conn):
    tracks_df = pd.DataFrame(tracks)
    tracks_df.to_sql(
        name='track', 
        con=db_conn, 
        if_exists='replace', 
        index=False,
        # Following https://www.sqlite.org/datatype3.html to translate the required datatypes to sqlite3 types.
        dtype={
            'track_id': 'TEXT',
            'song_name': 'TEXT',
            'external_url': 'TEXT',
            'duration_ms': 'INTEGER',
            'explicit': 'NUMERIC', # use text for now, convert to date type later
            'disc_number': 'INTEGER',
            'type': 'TEXT',
            'song_uri': 'TEXT',
            'album_id': 'TEXT'
        }
    )


def transform_track_features(track_features_raw):
    track_features = {
        'track_id': track_features_raw['id'],
        'danceability': track_features_raw['danceability'],
        'energy': track_features_raw['energy'],
        'instrumentalness': track_features_raw['instrumentalness'], 
        'liveness': track_features_raw['liveness'],
        'loudness': track_features_raw['loudness'],
        'speechiness': track_features_raw['speechiness'],
        'tempo': track_features_raw['tempo'],
        'type': track_features_raw['type'],
        'valence': track_features_raw['valence'],
        'song_uri': track_features_raw['uri']
    }

    return track_features


def fetch_features_for_all_tracks(tracks, spotify):
    track_ids = [t['track_id'] for t in tracks]

    # spotipy.audio_features can only support 100 ids per time, will group ids into batches of 100.
    # last batch may be less than 100, 
    
    all_tracks_features_nested = []

    for i in range(0, len(track_ids), 100):
        # It's possible that a track may NOT have feature, in which case the returned element is None.
        tracks_features_raw = spotify.audio_features(track_ids[i:i+100])
        transformed_track_features = [transform_track_features(tfr) for tfr in tracks_features_raw if tfr is not None]
        all_tracks_features_nested.append(transformed_track_features)

    # # deal with the last batch
    # last_batch_size = len(track_ids) % 100
    # # factor out these 3 lines to a function.
    # tracks_features_raw = spotify.audio_features(track_ids[-last_batch_size:])
    # transformed_track_features = [transform_track_features(tfr) for tfr in tracks_features_raw]
    # all_tracks_features_nested.append(transformed_track_features)

    all_tracks_features = list(np.concatenate(all_tracks_features_nested).flat)
    return all_tracks_features
    

def load_tracks_features_to_db(tracks_features, db_conn):
    tracks_features_df = pd.DataFrame(tracks_features)

    # Evaluate nulls.
    print('Number of NaN in track_features DF: ', tracks_features_df.isna().sum().sum())

    tracks_features_df.to_sql(
        name='track_feature', 
        con=db_conn, 
        if_exists='replace', 
        index=False,
        # Following https://www.sqlite.org/datatype3.html to translate the required datatypes to sqlite3 types.
        dtype={
            'track_id': 'TEXT',
            'danceability': 'REAL',
            'energy': 'REAL',
            'instrumentalness': 'REAL',
            'liveness': 'REAL',
            'loudness': 'REAL',
            'speechiness': 'REAL',
            'tempo': 'REAL',
            'type': 'TEXT',
            'valence': 'REAL',
            'song_uri': 'TEXT'
        }
    )


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