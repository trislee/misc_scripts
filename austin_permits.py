# -*- coding: UTF-8 -*-

"""Analyze Austin's urban sprawl using permit data
"""

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

import os

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.cm import get_cmap

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

# CSV file containing crime data, downloaded from
# https://data.austintexas.gov/Building-and-Development/Issued-Construction-Permits/3syk-w9eu
input_csv = 'Issued_Construction_Permits.csv'

# pickled DataFrame of permit data
output_dir_new = 'new_permits_all_years'
output_dir_all = 'all_permits_all_years'

# latitude and longitude, and aspect ratio for city of Austin
x_range = x_lb, x_ub = -97.95, -97.5968
y_range = y_lb, y_ub = 30.13, 30.51

ratio = ((y_ub - y_lb) / (x_ub - x_lb))

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

if __name__ == '__main__':

  # create directory if it doesn't already exist
  os.makedirs( output_dir_new, exist_ok = True )
  os.makedirs( output_dir_all, exist_ok = True )

  # load in data and remove empty rows
  df = pd.read_csv( input_csv )

  ndf = df[[
    'Calendar Year Issued',
    'Latitude',
    'Longitude',
    'Work Class' ]]

  # use Matplotlib's Viridis cmap
  cmap = get_cmap('viridis')

  # 1. generate plots for new permits only
  #----------------------------------------------------------------------------#

  # loop over all superyears
  for superyear in range( 1981, 2018):

    # initialize figure with correct aspect ratio
    fig, ax = plt.subplots(figsize = (8, 8 * ratio))

    # set background color to black
    ax.set_facecolor('k')

    # loop over all years before superyear
    for year in range(superyear, 1980, -1):

      # convert year to index between 0 and 1, for colormap
      color_idx = (year - 1981) / float(2018 - 1981)

      # get latitude and longitude of all new permits in the given year
      lats = ndf[(
        (ndf['Calendar Year Issued'] == year) &
        (ndf['Work Class'] == 'New'))]['Latitude']
      lons = ndf[(
        (ndf['Calendar Year Issued'] == year) &
        (ndf['Work Class'] == 'New'))]['Longitude']

      # plot latitude and longitude
      ax.scatter(
        lons,
        lats,
        s = 0.15,
        linewidth = 0,
        facecolor = cmap(color_idx),
        marker = ',')

      # draw year in upper right corner
      ax.text(
        x_ub-0.01,
        y_ub-0.01,
        str(superyear),
        fontsize = 20,
        color = 'w',
        ha = 'right',
        va = 'top')

      # set latitude and longitude limits
      ax.set_xlim(x_range)
      ax.set_ylim(y_range)

      plt.subplots_adjust(0,0,1,1)

    # save figure
    plt.savefig(
      os.path.join(output_dir_new, f'{superyear}.png' ),
      dpi = 200)
    plt.close()

  # 2. generate plots for all permits, on both new and existing buildings
  #----------------------------------------------------------------------------#

  # loop over all superyears
  for superyear in range( 1981, 2018):

    # initialize figure with correct aspect ratio
    fig, ax = plt.subplots(figsize = (8, 8 * ratio))

    # set background color to black
    ax.set_facecolor('k')

    # loop over all years before superyear
    for year in range(superyear, 1980, -1):

      # convert year to index between 0 and 1, for colormap
      color_idx = (year - 1981) / float(2018 - 1981)

      # get latitude and longitude of all new permits in the given year
      lats = ndf[((ndf['Calendar Year Issued'] == year))]['Latitude']
      lons = ndf[((ndf['Calendar Year Issued'] == year))]['Longitude']

      # plot latitude and longitude
      ax.scatter(
        lons,
        lats, s = 0.15,
        linewidth = 0,
        facecolor = cmap(color_idx),
        marker = ',')

      # draw year in upper right corner
      ax.text(
        x_ub-0.01,
        y_ub-0.01,
        str(superyear),
        fontsize = 20,
        color = 'w',
        ha = 'right',
        va = 'top')

      # set latitude and longitude limits
      ax.set_xlim(x_range)
      ax.set_ylim(y_range)

      plt.subplots_adjust(0,0,1,1)

    # save figure
    plt.savefig(
      os.path.join(output_dir_all, f'{superyear}.png' ),
      dpi = 200)
    plt.close()

  # 3. generate SVG of colorbar for legend, that can be formatted nicely using
  # a vector graphics editing program like Inkscape
  #............................................................................#

  # generate custom-labelled colormap based on
  # https://matplotlib.org/3.1.1/gallery/ticks_and_spines/colorbar_tick_labelling_demo.html

  fig, ax = plt.subplots()

  data = np.clip(np.random.randn(250, 250), -1, 1)

  cax = ax.imshow(
    data,
    interpolation = 'nearest',
    cmap = 'viridis' )

  # Add colorbar, make sure to specify tick locations to match desired ticklabels
  cbar = fig.colorbar(cax, ticks= np.linspace(-1, 1, 5))

  years = np.linspace( 1980, 2020, 5)
  years = [f'{int(year)}' for year in years]
  cbar.ax.set_yticklabels(years)

  # save SVG of colormap to file
  plt.savefig('colorbar.svg')
  plt.close()

  # 4. generate plots for all permits, for the first and last years, uncolored
  #----------------------------------------------------------------------------#

  for year in [1981, 2018]:

    # convert year to index between 0 and 1, for colormap
    # color_idx = (year - 1981) / float(2018 - 1981)

    # get latitude and longitude of all new permits in the given year
    lats = ndf[((ndf['Calendar Year Issued'] == year))]['Latitude']
    lons = ndf[((ndf['Calendar Year Issued'] == year))]['Longitude']

    fig, ax = plt.subplots(figsize = (8, 8 * ratio))
    ax.set_facecolor('k')

    # plot latitude and longitude
    ax.scatter(
      lons,
      lats,
      s = 0.15,
      linewidth = 0,
      marker = ',')

    # draw year in upper right corner
    ax.text(
      x_ub-0.01,
      y_ub-0.01,
      str(year),
      fontsize = 20,
      color = 'w',
      ha = 'right',
      va = 'top')

    # set latitude and longitude limits
    ax.set_xlim(x_range)
    ax.set_ylim(y_range)

    plt.subplots_adjust(0,0,1,1)

    # save figure
    plt.savefig(f'{year}.png', dpi = 200)
    plt.close()

  #----------------------------------------------------------------------------#

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
