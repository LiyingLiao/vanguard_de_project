import sqlite3

db_name = 'spotify.db'
con = sqlite3.connect(db_name)

cur = con.cursor()

# Create the artist table if not already exists.
has_artist_tb = cur.execute('select 1 from sqlite_master where name = "artist"').fetchone() is not None

if not has_artist_tb:
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






