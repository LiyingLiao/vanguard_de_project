import sqlite3

db_file_name = 'spotify.db'
conn = sqlite3.connect(db_file_name)

cur = conn.cursor()

# Check if a table exists.
def has_table(cur, table_name):
    res = cur.execute(f'select name from sqlite_master where name = "{table_name}"').fetchone()
    return res is not None

# Create artist table.
if not has_table(cur, 'artist'):
    create_artist_tb_statement = '''
    CREATE TABLE artist (
        artist_id VARCHAR(50),
        artist_name VARCHAR(255),
        external_url VARCHAR(100),
        genre VARCHAR(100),
        image_url VARCHAR(100),
        followers INT,
        popularity INT,
        type VARCHAR(50),
        artist_uri VARCHAR(100)
    )
    '''
    cur.execute(create_artist_tb_statement)
    print('artist table created.')

# Create album table.
if not has_table(cur, 'album'):
    create_album_tb_statement = '''
    CREATE TABLE album (
        album_id VARCHAR(50),
        album_name VARCHAR(255),
        external_url VARCHAR(100),
        image_url VARCHAR(100),
        release_date DATE,
        total_tracks INT,
        type VARCHAR(50),
        album_uri VARCHAR(100),
        artist_id VARCHAR(50)
    )
    '''
    cur.execute(create_album_tb_statement)
    print('album table created.')

# Create track table.
if not has_table(cur, 'track'):
    create_track_tb_statement = '''
    CREATE TABLE track (
        track_id VARCHAR(50),
        song_name VARCHAR(255),
        external_url VARCHAR(100),
        duration_ms INT,
        explicit BOOLEAN,
        disc_number INT,
        type VARCHAR(50),
        song_uri VARCHAR(100),
        album_id VARCHAR(50)
    )
    '''
    cur.execute(create_track_tb_statement)
    print('track table created.')

# Create track_feature table.
if not has_table(cur, 'track_feature'):
    create_track_feature_tb_statement = '''
    CREATE TABLE track_feature (
        track_id VARCHAR(50),
        danceability DOUBLE,
        energy DOUBLE,
        instrumentalness DOUBLE,
        liveness DOUBLE,
        loudness DOUBLE,
        speechiness DOUBLE,
        tempo DOUBLE,
        type VARCHAR(50),
        valence DOUBLE,
        song_uri VARCHAR(100)
    )
    '''
    cur.execute(create_track_feature_tb_statement)
    print('track_feature table created.')



