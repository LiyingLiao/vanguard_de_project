import sqlite3
import pandas
import seaborn as sns
import matplotlib.pyplot as plt


# tips = sns.load_dataset("tips")
# g = sns.relplot(data=tips, x="total_bill", y="tip")
# g.ax.axline(xy1=(10, 2), slope=.2, color="b", dashes=(5, 2))


class spotify_db:

    def __init__(self):
        self.conn = self.load_db()
        self.cursor = self.conn.cursor()

    def load_db(self):
        conn = sqlite3.connect("spotify.db")
        return conn

    def query_ds(self, query: str):
        df = pandas.read_sql_query(sql=query, con=self.conn)
        # df = pandas.read_sql_table(table_name="artist", con=self.conn)
        return df


def main():
    db = spotify_db()

    # # Create visualization for top 10 artists by followers
    # query1 = "SELECT artist_name, (followers/1000000) AS followers FROM v_top_artists_by_followers LIMIT 10"
    # # "SELECT artist_name, followers FROM artist ORDER BY followers DESC LIMIT 10"
    # top_artists_by_followers_df = db.query_ds(query1)

    # top_10_artists_by_followers = sns.barplot(data=top_artists_by_followers_df, x="artist_name", y="followers", palette="rocket")
    # top_10_artists_by_followers.set(xlabel="Artist Name", ylabel= "Followers (in millions)", title='Top 10 Artists By Followers')

    # top_10_artists_by_followers.bar_label(top_10_artists_by_followers.containers[0])

    # for followers in top_10_artists_by_followers.containers:
    #     top_10_artists_by_followers.bar_label(followers,)

    # plt.show()
    # plt.savefig('Top_10_Artists_By_Followers.png')

    
    # Create visualization for 
    query2 = "SELECT popularity_group, ROUND(avg_energy, 4), ROUND(avg_danceability, 4), ROUND(avg_instrumentalness, 4), ROUND(avg_liveness, 4) FROM v_avg_feature_value_per_popularity_group"
    avg_feature_value_per_popularity_group_df = db.query_ds(query2)

    # avg_feature_value_per_popularity_group = sns.lineplot(data=avg_feature_value_per_popularity_group_df)
    avg_feature_value_per_popularity_group = sns.lineplot(x='popularity_group', y='value', hue='variable', 
             data=pandas.melt(avg_feature_value_per_popularity_group_df, ['popularity_group']))

    avg_feature_value_per_popularity_group.set(xlabel="Popularity Group", ylabel= "Features", title='Features Trend Among Popularity Groups')

    # for feature in avg_feature_value_per_popularity_group.containers:
    #     avg_feature_value_per_popularity_group.bar_label(feature,)

    plt.show()
    # plt.savefig('Top_10_Artists_By_Followers.pdf')


if __name__ == "__main__":
    main()