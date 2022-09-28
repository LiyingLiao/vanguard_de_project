import sqlite3

def create_top_artists_by_followers_view(cur):
    cur.execute('''
        DROP VIEW IF EXISTS v_top_artists_by_followers
    ''')
    
    cur.execute('''
        CREATE VIEW v_top_artists_by_followers
        AS 
            SELECT
                artist_name,
                followers
            FROM artist
            ORDER BY followers DESC
    ''')

def create_top_songs_by_artist_duration_view(cur):
    cur.execute('''
        DROP VIEW IF EXISTS v_top_songs_by_artist_duration
    ''')
    
    cur.execute('''
        CREATE VIEW v_top_songs_by_artist_duration
        AS
            WITH artist_songs AS (
                SELECT 
                    al.artist_id AS artist_id,
                    t.song_name AS song_name,
                    t.duration_ms AS duration_ms
                FROM track AS t INNER JOIN album AS al ON (t.album_id = al.album_id)
            ), artist_songs_ranked AS (
                SELECT
                    *,
                    ROW_NUMBER() OVER (PARTITION BY artist_id ORDER BY duration_ms DESC) AS rn
                FROM artist_songs
            ), artist_songs_top AS (
                SELECT
                    artist_id,
                    song_name,
                    duration_ms
                FROM artist_songs_ranked
                WHERE rn <= 10
            )
            SELECT 
                a.artist_name AS artist_name,
                s.song_name AS song_name,
                s.duration_ms AS duration_ms
            FROM artist_songs_top AS s INNER JOIN artist AS a ON (s.artist_id = a.artist_id)
            ORDER BY artist_name ASC, duration_ms DESC
    ''')

def create_top_songs_by_artist_tempo_view(cur):
    cur.execute('''
        DROP VIEW IF EXISTS v_top_songs_by_artist_tempo
    ''')
    
    cur.execute('''
        CREATE VIEW v_top_songs_by_artist_tempo
        AS
            WITH track_with_feature AS (
                SELECT 
                    t.album_id AS album_id,
                    t.song_name AS song_name,
                    tf.tempo AS tempo
                FROM track AS t 
                    INNER JOIN track_feature AS tf ON (t.track_id = tf.track_id)
            ), artist_songs AS (
                SELECT 
                    al.artist_id AS artist_id,
                    twf.song_name AS song_name,
                    twf.tempo AS tempo
                FROM track_with_feature AS twf INNER JOIN album AS al ON (twf.album_id = al.album_id)
            ), artist_songs_ranked AS (
                SELECT
                    *,
                    ROW_NUMBER() OVER (PARTITION BY artist_id ORDER BY tempo DESC) AS rn
                FROM artist_songs
            ), artist_songs_top AS (
                SELECT
                    artist_id,
                    song_name,
                    tempo
                FROM artist_songs_ranked
                WHERE rn <= 10
            )
            SELECT 
                a.artist_name AS artist_name,
                s.song_name AS song_name,
                s.tempo AS tempo
            FROM artist_songs_top AS s INNER JOIN artist AS a ON (s.artist_id = a.artist_id)
            ORDER BY artist_name ASC, tempo DESC
    ''')

def create_avg_feature_value_per_group_view(cur):
    cur.execute('''
        DROP VIEW IF EXISTS v_avg_feature_value_per_popularity_group
    ''')
    
    cur.execute('''
        CREATE VIEW v_avg_feature_value_per_popularity_group
        AS
            WITH artist_with_popularity_group AS (
                SELECT 
                    *,
                    CASE  
                        WHEN popularity >= 90 THEN 'high'
                        WHEN popularity >= 80 THEN 'medium'
                        ELSE 'low'
                    END AS popularity_group
                FROM artist
            ), song_feature_with_popularity_group AS (
                SELECT 
                    a.popularity_group AS popularity_group,
                    tf.energy AS energy,
                    tf.danceability AS danceability,
                    tf.instrumentalness AS instrumentalness,
                    tf.liveness AS liveness
                FROM artist_with_popularity_group AS a 
                    INNER JOIN album AS al ON (a.artist_id = al.artist_id)
                    INNER JOIN track AS t ON (al.album_id = t.album_id)
                    INNER JOIN track_feature AS tf ON (t.track_id = tf.track_id)
            )
            SELECT
                popularity_group,
                AVG(energy) AS avg_energy,
                AVG(danceability) AS avg_danceability,
                AVG(instrumentalness) AS avg_instrumentalness,
                AVG(liveness) AS avg_liveness
            FROM song_feature_with_popularity_group
            GROUP BY popularity_group
    ''')

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