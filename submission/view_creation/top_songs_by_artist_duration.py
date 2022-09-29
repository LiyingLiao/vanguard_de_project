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