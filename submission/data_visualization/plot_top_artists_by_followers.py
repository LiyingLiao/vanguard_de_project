import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Plot a bar chart showing the top artists in terms of followers.
# conn: a sqlite3 database connection.
def plot_top_artists_by_followers(conn):
    # Pick the top 10 artists and change followers unit to millions.
    query = '''
        SELECT 
            artist_name, 
            (followers/1000000) AS followers 
        FROM v_top_artists_by_followers 
        LIMIT 10
    '''
    df = pd.read_sql_query(sql=query, con=conn)

    bar_plot = sns.barplot(data=df, x='artist_name', y='followers', palette='rocket')
    
    # Adjust the figure size.
    bar_plot.figure.set_size_inches(13, 8)
    
    bar_plot.set(
        xlabel='Artist Name', 
        ylabel='Followers (in millions)', 
        title='Top 10 Artists By Followers'
    )

    # The first container has the follower numbers. Use them as the bar labels.
    followers = bar_plot.containers[0]
    bar_plot.bar_label(followers)
    
    # Need to close otherwise will mix with other figures.
    plt.close()
    return bar_plot