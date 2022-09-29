import sqlite3
from view_creation.top_artists_by_followers import *
from view_creation.top_songs_by_artist_duration import *
from view_creation.top_songs_by_artist_tempo import *
from view_creation.avg_feature_value_per_group import *
from view_creation.artist_features_over_time import *

'''
Run this file to create the views.
'''

if __name__ == '__main__':
    db_conn = sqlite3.connect('spotify.db')
    cur = db_conn.cursor()

    print('Established DB connection')
    
    create_top_artists_by_followers_view(cur)
    print('Created top artists by followers view')

    create_top_songs_by_artist_duration_view(cur)
    print('Created top songs by artist duration view')

    create_top_songs_by_artist_tempo_view(cur)
    print('Created top songs by artist tempo view')

    create_avg_feature_value_per_group_view(cur)
    print('Created average feature value by popularity group view')

    create_artist_features_over_time_view(cur)
    print('Created artist features over time view')