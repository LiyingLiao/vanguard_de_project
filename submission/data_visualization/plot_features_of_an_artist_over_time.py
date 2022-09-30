import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Plot multi point chart showing features for an artist over time.
# conn: a sqlite3 database connection.
# artist_name: Name of the artist you are interested in. Defaults to Ed Sheeran.
def plot_features_of_an_artist_over_time(conn, artist_name="Ed Sheeran"):
    query = f"""
        SELECT
            year,
            avg_danceability AS danceability,
            avg_energy AS energy,
            avg_liveness AS liveness,
            avg_valence AS valence
        FROM v_artist_features_over_time
        WHERE artist_name = '{artist_name}'
    """
    df = pd.read_sql_query(sql=query, con=conn)
    point_plot = sns.pointplot(
        x="year",
        y="value",
        hue="feature",
        data=pd.melt(df, id_vars="year", var_name="feature"),
    )

    point_plot.set(
        xlabel="Year",
        ylabel="Value",
        title="Song Features for Ed Sheeran Over The Years",
    )

    # Adjust the legends.
    point_plot.legend(fontsize=8)
    sns.move_legend(point_plot, "center right")

    # Need to close otherwise will mix with other figures.
    plt.close()
    return point_plot
