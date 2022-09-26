import sqlite3

if __name__ == '__main__':
    db_conn = sqlite3.connect('spotify.db')
    cur = db_conn.cursor()

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
            LIMIT 10
    ''')
