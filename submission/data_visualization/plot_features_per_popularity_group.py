import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Plot a point chart showing features per popularity group.
# conn: a sqlite3 database connection.
def plot_features_per_popularity_group(conn):
    # Rename the popularity groups to be more clear.
    query = """
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
    """
    df = pd.read_sql_query(sql=query, con=conn)
    point_plot = sns.pointplot(
        x="popularity_group",
        y="value",
        hue="feature",
        data=pd.melt(df, id_vars="popularity_group", var_name="feature"),
    )

    point_plot.set(
        xlabel="Popularity Group",
        ylabel="Value",
        title="Features Trend Among Popularity Groups",
    )

    # Adjust the legends.
    point_plot.legend(fontsize=8)
    sns.move_legend(point_plot, "center right")

    # Need to close otherwise will mix with other figures.
    plt.close()
    return point_plot
