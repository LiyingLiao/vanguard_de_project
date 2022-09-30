# High level overview:
#
# 1) Delete v_top_songs_by_artist_duration if exists. This ensures complete overwrite when rerun.
# 2) Join album with track to get artist_id, song_name, duration_ms information.
# 3) Partition by artist_id and rank songs in terms of duration_ms for each partition. Rank 1 is applied to song with highest duration_ms.
# 4) Filter out rows with rank > 10 to only keep songs with rank <= 10 (top 10).
# 5) Join with artist table to get artist name.
# 6) Order the final result by artist_name in ascending order and duration_ms in descending order.
#
# Note in (5) we delayed the join with artist table so only filtered table (top 10 songs per artist) was joined. Less rows involved should result in better performance.
def create_top_songs_by_artist_duration_view(cur):
    cur.execute(
        """
        DROP VIEW IF EXISTS v_top_songs_by_artist_duration
    """
    )

    cur.execute(
        """
        CREATE VIEW v_top_songs_by_artist_duration
        AS
            WITH artist_songs AS (
                SELECT 
                    al.artist_id,
                    t.song_name,
                    t.duration_ms
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
                a.artist_name,
                s.song_name,
                s.duration_ms
            FROM artist_songs_top AS s INNER JOIN artist AS a ON (s.artist_id = a.artist_id)
            ORDER BY artist_name ASC, duration_ms DESC
    """
    )
