# High level overview:
#
# 1) Delete v_artist_features_over_time if exists. This ensures complete overwrite when rerun.
# 2) Join artist + album + track + track_feature tables to link track features to artists.
# 3) Extract year from album's release_date. Note that some release_date are years already, which would result in strftime('%Y', al.release_date) < 0.
# 4) Group by artist + year to get each artist's each year's records.
# 5) Aggregate the groups to get per artist + year features
# 6) Sort by artist names in ascending order and years in ascending order.
def create_artist_features_over_time_view(cur):
    cur.execute(
        """
        DROP VIEW IF EXISTS v_artist_features_over_time
    """
    )

    cur.execute(
        """
        CREATE VIEW v_artist_features_over_time
        AS
            WITH artist_song_with_year AS (
                SELECT
                    a.artist_name,
                    CASE
                        WHEN CAST(strftime('%Y', al.release_date) AS INTEGER)  < 0 THEN al.release_date
                        ELSE strftime('%Y', al.release_date)
                    END AS release_year,
                    t.song_name AS song_name,
                    tf.*
                FROM artist AS a
                    INNER JOIN album AS al ON (a.artist_id = al.artist_id)
                    INNER JOIN track AS t ON (al.album_id = t.album_id)
                    INNER JOIN track_feature AS tf on (t.track_id = tf.track_id)
            )
            SELECT 
                artist_name, 
                release_year AS year,
                COUNT(*) AS num_of_songs,
                ROUND(avg(danceability), 5) AS avg_danceability,
                ROUND(avg(energy),5) AS avg_energy,
                ROUND(avg(instrumentalness),5) AS avg_instrumentalness,
                ROUND(avg(liveness),5) AS avg_liveness,
                ROUND(avg(loudness),5) AS avg_loudness,
                ROUND(avg(speechiness),5) AS avg_speechiness,
                ROUND(avg(tempo),5) AS avg_tempo,
                ROUND(avg(valence),5) AS avg_valence
            FROM artist_song_with_year
            GROUP BY artist_name, release_year
            ORDER BY artist_name ASC, year ASC
    """
    )
