import pandas as pd
import numpy as np 

'''
Functions related to tracks dataset generation.
'''

# ----- Helper Functions -----

# Deduplicate the given tracks by their song names and return deduplicated tracks.
# tracks: list of tracks to be deduplicated.
# Can't deduplicate based on IDs since the same track may have different IDs (release version etc.)
# causing the same track to appear multiple times if based on ID.
def deduplicate_tracks(tracks):
    unique_tracks = []
    visited_names = set()

    for track in tracks:
        track_name = track['song_name']
        if track_name not in visited_names:
             unique_tracks.append(track)
             visited_names.add(track_name)
    
    return unique_tracks

# ----- Helper Functions End -----


# Fetch tracks associated with an album.
# album_id: the ID of the album.
# spotify: an object created after connecting to Spotipy library.
def fetch_tracks_by_album(album_id, spotify):
    # Search the tracks of an album using the Spotify API.
    tracks_search_result =  spotify.album_tracks(album_id=album_id, limit=50, offset=0)
    tracks_list_raw = tracks_search_result['items']

    tracks_list = []

    # Convert the raw tracks to the format compatible with the track table schema.
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

# Fetch all tracks across all albums.
# albums: all albums by all artists.
# spotify: an object created after connecting to Spotipy library.
# Final tracks are deduplicated based on their IDs.
def fetch_tracks_for_all_albums(albums, spotify):
    all_tracks_nested = []

    for album in albums:
        fetched_tracks = fetch_tracks_by_album(album['album_id'], spotify)
        all_tracks_nested.append(fetched_tracks)

    all_tracks = list(np.concatenate(all_tracks_nested).flat)
    unique_tracks = deduplicate_tracks(all_tracks)

    print(f'Number of tracks: all {len(all_tracks)} -> unique {len(unique_tracks)}')
    return unique_tracks


# Load the tracks into database's track table.
# tracks: the tracks to load.
# db_conn: a database connection.
def load_tracks_to_db(tracks, db_conn):
    tracks_df = pd.DataFrame(tracks)

    # Evaluate Nones.
    print('Number of NaN in tracks DF: ', tracks_df.isna().sum().sum())

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
            'explicit': 'NUMERIC',
            'disc_number': 'INTEGER',
            'type': 'TEXT',
            'song_uri': 'TEXT',
            'album_id': 'TEXT'
        }
    )