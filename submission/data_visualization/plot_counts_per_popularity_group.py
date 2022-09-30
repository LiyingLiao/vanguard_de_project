import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Plot a multi bar chart showing artists and albums counts per popularity group.
def plot_counts_per_popularity_group(conn):
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
            num_artists AS artists,
            num_albums AS albums
        FROM v_features_per_popularity_group
    """
    df = pd.read_sql_query(sql=query, con=conn)
    # Create a DF specific to cat plot.
    cat_df = pd.melt(
        df, id_vars="popularity_group", var_name="category", value_name="count"
    )
    cat_plot = sns.catplot(
        x="popularity_group", y="count", hue="category", data=cat_df, kind="bar"
    )

    # Adjust the figure size.
    cat_plot.figure.set_size_inches(10, 10)

    cat_plot.set(
        xlabel="Popularity Group (based on artist popularity value)",
        ylabel="Count",
        title="Number of Artists and Albums in Each Popularity Group",
    )

    # Give bar values.
    ax = cat_plot.facet_axis(0, 0)
    for c in ax.containers:
        ax.bar_label(c, padding=1.0)

    # Need to close otherwise will mix with other figures.
    plt.close()
    return cat_plot
