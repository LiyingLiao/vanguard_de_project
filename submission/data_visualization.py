import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# Plot a bar chart showing the top artists in terms of followers.
def plot_top_artists_by_followers(conn):
    # sns.set(rc={'figure.figsize':(15,8.27)})
    
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
    bar_plot.figure.set_size_inches(15, 8.27)
    bar_plot.set(
        xlabel='Artist Name', 
        ylabel='Followers (in millions)', 
        title='Top 10 Artists By Followers'
    )

    # The first container has the follower numbers. Use them as the bar labels.
    followers = bar_plot.containers[0]
    bar_plot.bar_label(followers)
    
    plt.close()
    return bar_plot

# Plot a point chart showing features per popularity group.
def plot_features_per_popularity_group(conn):
    query = '''
        SELECT 
            case
                when popularity_group = 'tier_1' then '95+'
                when popularity_group = 'tier_2' then '90+'
                when popularity_group = 'tier_3' then '85+'
                when popularity_group = 'tier_4' then '80+'
                else '80-'
            end as popularity_group,
            avg_energy AS energy,
            avg_danceability AS danceability,
            avg_liveness AS liveness,
            avg_valence AS valence
        FROM v_features_per_popularity_group
    '''
    df = pd.read_sql_query(sql=query, con=conn)
    point_plot = sns.pointplot(
            x='popularity_group', 
            y='value', 
            hue='feature', 
            data=pd.melt(df, id_vars='popularity_group', var_name='feature')
        )
    
    point_plot.set(
        xlabel="Popularity Group", 
        ylabel= "Value", 
        title='Features Trend Among Popularity Groups'
    )

    point_plot.legend(fontsize=8)
    sns.move_legend(point_plot, "center right")
    
    plt.close()
    return point_plot

# Plot a multi bar chart showing artists and albums counts per popularity group.
def plot_counts_per_popularity_group(conn):
    query = '''
        SELECT 
            case
                when popularity_group = 'tier_1' then '95+'
                when popularity_group = 'tier_2' then '90+'
                when popularity_group = 'tier_3' then '85+'
                when popularity_group = 'tier_4' then '80+'
                else '80-'
            end as popularity_group,
            num_artists AS artists,
            num_albums AS albums
        FROM v_features_per_popularity_group
    '''
    df = pd.read_sql_query(sql=query, con=conn)
    cat_df = pd.melt(df, id_vars='popularity_group', var_name='category', value_name='count')
    cat_plot = sns.catplot(x='popularity_group', y='count', hue='category', data=cat_df, kind='bar')

    # Adjust the figure size.
    cat_plot.figure.set_size_inches(10, 10)

    cat_plot.set(
        xlabel='Popularity Group', 
        ylabel='Count', 
        title='Number of Artists and Albums in Each Popularity Group'
    )

    ax = cat_plot.facet_axis(0, 0)
    for c in ax.containers:
        ax.bar_label(c, padding=1.0)
    
    plt.close()
    return cat_plot

# Plot a point chart showing features for an artist over time.
def plot_features_of_an_artist_over_time(conn):
    query = '''
        SELECT
            year,
            avg_danceability AS danceability,
            avg_energy AS energy,
            avg_liveness AS liveness,
            avg_valence AS valence
        FROM v_artist_features_over_time
        WHERE artist_name = 'Ed Sheeran'
    '''
    df = pd.read_sql_query(sql=query, con=conn)
    point_plot = sns.pointplot(
            x='year', 
            y='value', 
            hue='feature', 
            data=pd.melt(df, id_vars='year', var_name='feature')
        )

    point_plot.set(
        xlabel="Year", 
        ylabel= "Value", 
        title='Song Features for Ed Sheeran Over The Years'
    )

    point_plot.legend(fontsize=8)
    sns.move_legend(point_plot, 'best')
    
    plt.close()
    return point_plot

if __name__ == '__main__':
    conn = sqlite3.connect("spotify.db")
    print('Connected to database')

    plots = []

    plots.append(plot_top_artists_by_followers(conn))
    print('Plotted top artists by followers')

    plots.append(plot_features_of_an_artist_over_time(conn))
    print('Plotted features of an artist over time')

    plots.append(plot_counts_per_popularity_group(conn))
    print('Plotted counts per popularity group')

    plots.append(plot_features_per_popularity_group(conn))
    print('Plotted features per popularity group')

    print(len(plots))

    with PdfPages('visualization.pdf') as pdf_pages:
        for plot in plots:
            pdf_pages.savefig(plot.figure)