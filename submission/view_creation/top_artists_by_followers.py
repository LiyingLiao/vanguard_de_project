# High level overview:
#
# 1) Delete v_top_artists_by_followers if exists. This ensures complete overwrite when rerun.
# 2) Order the artists by their follower numbers in descending order.
def create_top_artists_by_followers_view(cur):
    cur.execute(
        """
        DROP VIEW IF EXISTS v_top_artists_by_followers
    """
    )

    cur.execute(
        """
        CREATE VIEW v_top_artists_by_followers
        AS 
            SELECT
                artist_name,
                followers
            FROM artist
            ORDER BY followers DESC
    """
    )
