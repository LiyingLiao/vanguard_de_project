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
                        WHEN popularity >= 95 THEN 'tier_1'
                        WHEN popularity >= 90 THEN 'tier_2'
                        WHEN popularity >= 85 THEN 'tier_3'
                        WHEN popularity >= 80 THEN 'tier_4'
                        ELSE 'tier_5'
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
                ROUND(AVG(energy), 4) AS avg_energy,
                ROUND(AVG(danceability), 4) AS avg_danceability,
                ROUND(AVG(instrumentalness), 4) AS avg_instrumentalness,
                ROUND(AVG(liveness), 4) AS avg_liveness
            FROM song_feature_with_popularity_group
            GROUP BY popularity_group
            ORDER BY popularity_group ASC
    ''')

def create_artist_features_over_time_view(cur):
    cur.execute('''
        DROP VIEW IF EXISTS v_artist_features_over_time
    ''')
    
    cur.execute('''
        CREATE VIEW v_artist_features_over_time
        AS
            with artist_song_with_year as (
                select
                    a.artist_name as artist_name,
                    CASE
                        WHEN CAST(strftime('%Y', al.release_date) as INTEGER)  < 0 THEN al.release_date
                        ELSE strftime('%Y', al.release_date)
                    end as release_year,
                    t.song_name as song_name,
                    tf.*
                from artist as a
                    inner join album as al on (a.artist_id = al.artist_id)
                    inner join track as t on (al.album_id = t.album_id)
                    inner join track_feature as tf on (t.track_id = tf.track_id)
            )
            select 
                artist_name, 
                release_year as year,
                count(*) as num_of_songs,
                round(avg(danceability), 5) as avg_danceability,
                ROUND(avg(energy),5) as avg_energy,
                ROUND(avg(instrumentalness),5) as avg_instrumentalness,
                ROUND(avg(liveness),5) as avg_liveness,
                ROUND(avg(loudness),5) as avg_loudness,
                ROUND(avg(speechiness),5) as avg_speechiness,
                ROUND(avg(tempo),5) as avg_tempo,
                ROUND(avg(valence),5) as avg_valence
            from artist_song_with_year
            group by artist_name, release_year
            order by artist_name asc, year asc
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

    create_artist_features_over_time_view(cur)
    print('Created artist features over time view')