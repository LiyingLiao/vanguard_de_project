def create_features_per_popularity_group_view(cur):
    cur.execute('''
        DROP VIEW IF EXISTS v_features_per_popularity_group
    ''')
    
    cur.execute('''
        CREATE VIEW v_features_per_popularity_group
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
                    a.artist_name AS artist_name,
                    al.album_name AS album_name,
                    t.song_name AS song_name,
                    tf.energy AS energy,
                    tf.danceability AS danceability,
                    tf.instrumentalness AS instrumentalness,
                    tf.liveness AS liveness,
                    tf.valence AS valence
                FROM artist_with_popularity_group AS a 
                    INNER JOIN album AS al ON (a.artist_id = al.artist_id)
                    INNER JOIN track AS t ON (al.album_id = t.album_id)
                    INNER JOIN track_feature AS tf ON (t.track_id = tf.track_id)
            )
            SELECT
                popularity_group,
                COUNT(DISTINCT artist_name) AS num_artists,
                COUNT(DISTINCT album_name) AS num_albums,
                COUNT(DISTINCT song_name) AS num_songs,
                ROUND(AVG(energy), 4) AS avg_energy,
                ROUND(AVG(danceability), 4) AS avg_danceability,
                ROUND(AVG(instrumentalness), 4) AS avg_instrumentalness,
                ROUND(AVG(liveness), 4) AS avg_liveness,
                ROUND(AVG(valence), 4) AS avg_valence
            FROM song_feature_with_popularity_group
            GROUP BY popularity_group
            ORDER BY popularity_group ASC
    ''')