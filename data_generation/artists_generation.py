'''
Functions related to artists dataset generation.
'''

# ----- Helper Functions -----

# Find exact artist match within artist_list.
# artist_name: the name of the artist you are looking for. Case insensitive.
# artist_list: list of artists in Spotify API from where you search for a match.
# If no match, returns None.
def find_artist_match(artist_name, artist_list):
    for artist in artist_list:
        if artist_name.lower() == artist['name'].lower():
            return artist
    return None

# ----- Helper Functions End -----


# Fetch information of an artist using spotipy.
# artist_name: The name of the artist we want to fetch info about.
# spotify: an object created after connecting to Spotipy library.
def fetch_artist(artist_name, spotify):
    # Fetch the raw artist dict from the Spotify API.
    artist_search_result = spotify.search(q=f'artist:{artist_name}', limit=10, type='artist')
    artist_list = artist_search_result['artists']['items']
    artist_raw = find_artist_match(artist_name, artist_list)

    if artist_raw is None:
        print("cannot find artist associated with: ", artist_name)
        return None

    # Convert the raw artist dict to the format compatible with the artist table schema.
    # These properties could be empty.
    genres = artist_raw['genres']
    images = artist_raw['images']

    artist = {
        'artist_id': artist_raw['id'],
        'artist_name': artist_raw['name'],
        'external_url': artist_raw['external_urls']['spotify'],
        'genre': genres[0] if len(genres) > 0 else '', # Assign empty string if no genre found.
        'image_url': images[0]['url'] if len(images) > 0 else '', # Assign empty string if no image found.
        'followers': artist_raw['followers']['total'],
        'popularity': artist_raw['popularity'],
        'type': artist_raw['type'],
        'artist_uri': artist_raw['uri']
    }

    return artist

# Fetch a list of artists in dict representation from the given artist_names.
# Deduplicate the artists by their IDs.
# artist_names: the list of artist names we use to look for the artists from Spotify.
# spotify: an object created after connecting to Spotipy library.
def fetch_artists(artist_names, spotify):
    artists = []
    visited_ids = set()

    for artist_name in artist_names:
        artist = fetch_artist(artist_name, spotify)
        if artist is not None and artist['artist_id'] not in visited_ids:
            artists.append(artist)
            visited_ids.add(artist['artist_id'])

    return artists

# Load the artists into database's artist table.
# artists: the artists to load.
# db_conn: a database connection.
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