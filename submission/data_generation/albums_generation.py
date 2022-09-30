import pandas as pd
import numpy as np

"""
Functions related to albums dataset generation.
"""

# ----- Helper Functions -----

# Deduplicate the given albums by their album names and return deduplicated albums.
# albums: list of albums to be deduplicated.
# Can't deduplicate based on IDs since the same album may have different IDs (release version etc.)
# causing the same album to appear multiple times if based on ID.
def deduplicate_albums(albums):
    unique_albums = []
    visited_names = set()

    for album in albums:
        album_name = album["album_name"]
        if album_name not in visited_names:
            unique_albums.append(album)
            visited_names.add(album_name)

    return unique_albums


# ----- Helper Functions End -----


# Fetch all albums by an artist.
# artist: the artist we are interested in.
# spotify: an object created after connecting to Spotipy library.
def fetch_albums_by_artist(artist, spotify):
    # Search the albums by an artist using the Spotify API.
    albums_search_result = spotify.artist_albums(
        artist_id=artist["artist_uri"], album_type="album", country="US"
    )
    albums_list_raw = albums_search_result["items"]

    albums_list = []

    # Convert the raw albums to the format compatible with the album table schema.
    for album_raw in albums_list_raw:
        # These properties could be empty.
        images = album_raw["images"]

        album = {
            "album_id": album_raw["id"],
            "album_name": album_raw["name"],
            "external_url": album_raw["external_urls"]["spotify"],
            "image_url": images[0]["url"]
            if len(images) > 0
            else "",  # Assign empty string if no image found.
            "release_date": album_raw["release_date"],
            "total_tracks": album_raw["total_tracks"],
            "type": album_raw["type"],
            "album_uri": album_raw["uri"],
            "artist_id": artist[
                "artist_id"
            ],  # Due to possibility of multiple artists, use artist id directly from input artist.
        }
        albums_list.append(album)

    return albums_list


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

    print(f"Number of albums: all {len(all_albums)} -> unique {len(unique_albums)}")
    return unique_albums


# Load the albums into database's album table.
# albums: the albums to load.
# db_conn: a database connection.
def load_albums_to_db(albums, db_conn):
    albums_df = pd.DataFrame(albums)

    # Evaluate Nones.
    print("Number of NaN in albums DF: ", albums_df.isna().sum().sum())

    albums_df.to_sql(
        name="album",
        con=db_conn,
        if_exists="replace",
        index=False,
        # Following https://www.sqlite.org/datatype3.html to translate the required datatypes to sqlite3 types.
        dtype={
            "album_id": "TEXT",
            "album_name": "TEXT",
            "external_url": "TEXT",
            "image_url": "TEXT",
            "release_date": "TEXT",
            "total_tracks": "INTEGER",
            "type": "TEXT",
            "album_uri": "TEXT",
            "artist_id": "TEXT",
        },
    )
