# High level overview:
#
# 1) Delete v_top_songs_by_artist_tempo if exists. This ensures complete overwrite when rerun.
# 2) Join album with track + track_feature to get artist_id, song_name, tempo information.
# 3) Partition by artist_id and rank songs in terms of tempo for each partition. Rank 1 is applied to song with highest tempo.
# 4) Filter out rows with rank > 10 to only keep songs with rank <= 10 (top 10).
# 5) Join with artist table to get artist name.
# 6) Order the final result by artist_name in ascending order and tempo in descending order.
#
# Note in (5) we delayed the join with artist table so only filtered table (top 10 songs per artist) was joined. Less rows involved should result in better performance.
def create_top_songs_by_artist_tempo_view(cur):
    cur.execute(
        """
        DROP VIEW IF EXISTS v_top_songs_by_artist_tempo
    """
    )

    cur.execute(
        """
        CREATE VIEW v_top_songs_by_artist_tempo
        AS
            WITH artist_song_with_tempo AS (
                SELECT 
                    al.artist_id,
                    t.song_name,
                    tf.tempo
                FROM album AS al
                    INNER JOIN track AS t ON (al.album_id = t.album_id)
                    INNER JOIN track_feature AS tf ON (t.track_id = tf.track_id)
            ), artist_songs_ranked AS (
                SELECT
                    *,
                    ROW_NUMBER() OVER (PARTITION BY artist_id ORDER BY tempo DESC) AS rn
                FROM artist_song_with_tempo
            ), artist_songs_top AS (
                SELECT
                    artist_id,
                    song_name,
                    tempo
                FROM artist_songs_ranked
                WHERE rn <= 10
            )
            SELECT 
                a.artist_name,
                s.song_name,
                s.tempo
            FROM artist_songs_top AS s INNER JOIN artist AS a ON (s.artist_id = a.artist_id)
            ORDER BY artist_name ASC, tempo DESC
    """
    )
