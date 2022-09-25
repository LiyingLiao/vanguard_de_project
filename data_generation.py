import spotipy
import sys
from spotipy.oauth2 import SpotifyClientCredentials
import pprint

"""
    Make sure you have the following environment variables set:
        SPOTIPY_CLIENT_ID
        SPOTIPY_CLIENT_SECRET
        SPOTIPY_REDIRECT_URI
"""

spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials())

# artist_id | artist_name | external_url | genre | image_url | followers | popularity | type | artist_uri

# define artist search term.
artist_name = 'travis'
# Query to get 1 artist result
artist_search_result = spotify.search(q=f'artist:{artist_name}', limit=1, type='artist')
artist_list = artist_search_result['artists']['items']

if len(artist_list) > 0:
    artist = artist_list[0]
    # Extract data for artist table.
    artist_id = artist['id']
    artist_name = artist['name']
    external_url = artist['external_urls']['spotify']
    genre = artist['genres'][0] # could be empty list, need to check emptiness before accessing the 1st element.
    image_url = artist['images'][0]['url'] # could be empty list, need to check emptiness before accessing the 1st element.
    followers = artist['followers']['total']
    popularity = artist['popularity']
    type = artist['type']
    artist_uri = artist['uri']
    
    pprint.pprint(artist_id)

