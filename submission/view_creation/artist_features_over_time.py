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