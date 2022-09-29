import sqlite3
from matplotlib.backends.backend_pdf import PdfPages
from data_visualization.plot_top_artists_by_followers import *
from data_visualization.plot_features_per_popularity_group import *
from data_visualization.plot_counts_per_popularity_group import *
from data_visualization.plot_features_of_an_artist_over_time import *

'''
Run this file to create the visualizations.
'''

if __name__ == '__main__':
    conn = sqlite3.connect("spotify.db")
    print('Connected to database')

    # Will hold the plots to be saved in one PDF.
    plots = []

    plots.append(plot_top_artists_by_followers(conn))
    print('Plotted top artists by followers')

    plots.append(plot_features_of_an_artist_over_time(conn))
    print('Plotted features of an artist over time')

    plots.append(plot_counts_per_popularity_group(conn))
    print('Plotted counts per popularity group')

    plots.append(plot_features_per_popularity_group(conn))
    print('Plotted features per popularity group')

    print('Number of plots: ', len(plots))

    with PdfPages('visualization.pdf') as pdf_pages:
        for plot in plots:
            pdf_pages.savefig(plot.figure)

    print('Done creating the visualization PDF!')