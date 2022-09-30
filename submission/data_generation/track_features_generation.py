import pandas as pd
import numpy as np

"""
Functions related to track features dataset generation.
"""

# ----- Helper Functions -----

# Convert the raw track features to the format compatible with the track_feature table schema.
# track_features_raw: track features from the Spotify API.
def transform_track_features(track_features_raw):
    track_features = {
        "track_id": track_features_raw["id"],
        "danceability": track_features_raw["danceability"],
        "energy": track_features_raw["energy"],
        "instrumentalness": track_features_raw["instrumentalness"],
        "liveness": track_features_raw["liveness"],
        "loudness": track_features_raw["loudness"],
        "speechiness": track_features_raw["speechiness"],
        "tempo": track_features_raw["tempo"],
        "type": track_features_raw["type"],
        "valence": track_features_raw["valence"],
        "song_uri": track_features_raw["uri"],
    }

    return track_features


# ----- Helper Functions End -----


# Fetch all track features with all tracks.
# tracks: all tracks by all artists.
# spotify: an object created after connecting to Spotipy library.
def fetch_features_for_all_tracks(tracks, spotify):
    track_ids = [t["track_id"] for t in tracks]

    all_tracks_features_nested = []

    # spotipy.audio_features can only support 100 ids per time, will group ids into batches of 100.
    # last batch may be less than 100,
    for i in range(0, len(track_ids), 100):
        # It's possible that a track may NOT have feature, in which case the returned element is None.
        tracks_features_raw = spotify.audio_features(track_ids[i : i + 100])
        transformed_track_features = [
            transform_track_features(tfr)
            for tfr in tracks_features_raw
            if tfr is not None
        ]
        all_tracks_features_nested.append(transformed_track_features)

    all_tracks_features = list(np.concatenate(all_tracks_features_nested).flat)
    return all_tracks_features


# Load the track features into database's track_feature table.
# tracks_features: the track features to load.
# db_conn: a database connection.
def load_tracks_features_to_db(tracks_features, db_conn):
    tracks_features_df = pd.DataFrame(tracks_features)

    # Evaluate Nones.
    print("Number of NaN in track_features DF: ", tracks_features_df.isna().sum().sum())

    tracks_features_df.to_sql(
        name="track_feature",
        con=db_conn,
        if_exists="replace",
        index=False,
        # Following https://www.sqlite.org/datatype3.html to translate the required datatypes to sqlite3 types.
        dtype={
            "track_id": "TEXT",
            "danceability": "REAL",
            "energy": "REAL",
            "instrumentalness": "REAL",
            "liveness": "REAL",
            "loudness": "REAL",
            "speechiness": "REAL",
            "tempo": "REAL",
            "type": "TEXT",
            "valence": "REAL",
            "song_uri": "TEXT",
        },
    )
