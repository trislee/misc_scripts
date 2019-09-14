# -*- coding: UTF-8 -*-

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

import os
from collections import Counter

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
plt.style.use('trislee')
from matplotlib.lines import Line2D

import datashader as ds
from datashader import transfer_functions as tf

import colorcet

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

# CSV file containing crime data, downloaded from
# https://data.austintexas.gov/Public-Safety/Crime-Reports/fdj4-gpfu
input_csv = 'Crime_Reports.csv'

# categorizing crimes
#------------------------------------------------------------------------------#

# crime categories
category_codes = dict(
  zip(
    [
    'Auto',
    'Assault',
    'Burglary',
    'Domestic',
    'Drugs',
    'Fraud',
    'Misc',
    'Property',
    'Theft'],
  np.arange(9) ) )

# dict of crimes in each category
category_crimes = dict()

category_crimes['Assault'] = (
  'ASSAULT W/INJURY-FAM/DATE VIOL',
  'ASSAULT WITH INJURY',
  'ASSAULT BY CONTACT',
  'ASSAULT BY THREAT',
  'AGG ASSAULT',
  'ASSAULT BY CONTACT FAM/DATING',
  'AGG ASSAULT FAM/DATE VIOLENCE',
  'ROBBERY BY ASSAULT',
  'ASSAULT BY THREAT FAM/DATING',
  'FELONY ENHANCEMENT/ASSLT W/INJ',
  'AGG ASLT STRANGLE/SUFFOCATE',
  'AGG ROBBERY/DEADLY WEAPON',
  'TERRORISTIC THREAT',
  'TERRORISTIC THREAT-FAM/DAT VIO' )

category_crimes['Theft'] = (
  'THEFT',
  'THEFT BY SHOPLIFTING',
  'AUTO THEFT',
  'IDENTITY THEFT',
  'THEFT OF BICYCLE',
  'THEFT OF SERVICE',
  'THEFT FROM AUTO',
  'THEFT OF LICENSE PLATE',
  'THEFT FROM PERSON',
  'THEFT OF AUTO PARTS',
  'THEFT FROM BUILDING',
  'THEFT OF TRAILER',
  'THEFT OF METAL' )

category_crimes['Burglary'] = (
  'BURGLARY OF VEHICLE',
  'BURGLARY OF RESIDENCE',
  'BURGLARY NON RESIDENCE',
  'BURGLARY OF COIN-OP MACHINE' )

category_crimes['Drugs'] = (
  'PUBLIC INTOXICATION',
  'POSSESSION OF MARIJUANA',
  'POSS OF DRUG PARAPHERNALIA',
  'POSS CONTROLLED SUB/NARCOTIC',
  'VOCO - ALCOHOL  CONSUMPTION',
  'POSS OF ALCOHOL - AGE 17 TO 20',
  'LIQUOR LAW VIOLATION/OTHER',
  'DEL CONTROLLED SUB/NARCOTIC' )

category_crimes['Auto'] = (
  'DWI',
  'DRIVING WHILE INTOX / FELONY',
  'DWI 2ND',
  'DWI  .15 BAC OR ABOVE' )

category_crimes['Domestic'] = (
  'FAMILY DISTURBANCE',
  'RUNAWAY CHILD',
  'FAMILY DISTURBANCE/PARENTAL',
  'DATING DISTURBANCE',
  'CHILD CUSTODY INTERFERE',
  'CHILD ENDANGERMENT- ABANDONMEN',
  'INJURY TO CHILD' )

category_crimes['Property'] = (
  'CRIMINAL MISCHIEF',
  'CRIMINAL TRESPASS',
  'CRIMINAL TRESPASS/TRANSIENT',
  'GRAFFITI',
  'CRIMINAL TRESPASS/HOTEL',
  'DAMAGE CITY PROP',
  'CAMPING IN PARK',
  'URINATING IN PUBLIC PLACE',
  'VIOL OF PARK CURFEW' )

category_crimes['Fraud'] = (
  'FRAUD - OTHER',
  'FORGERY AND PASSING',
  'CRED CARD ABUSE - OTHER',
  'DEBIT CARD ABUSE',
  'COUNTERFEITING',
  'FORGERY - OTHER',
  'CRED CARD ABUSE BY FORGERY' )

category_crimes['Misc'] = (
  'HARASSMENT',
  'DISTURBANCE - OTHER' )

# latitude and longitude, and aspect ratio for city of Austin
#------------------------------------------------------------------------------#

x_range = x_lb, x_ub = -97.95, -97.5968
y_range = y_lb, y_ub = 30.13, 30.51

ratio = ((y_ub - y_lb) / (x_ub - x_lb))

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

if __name__ == '__main__':

  # 1. load in data, remove and rename extraneous columns
  #----------------------------------------------------------------------------#

  # read csv data
  df = pd.read_csv( input_csv )

  # we're only interested in these fields
  ndf = df[[
    'Highest Offense Description',
    'Latitude',
    'Longitude',
    'Occurred Date Time']].copy()

  # ignore any entry containing None or nan
  ndf = ndf.dropna()

  # rename columns
  ndf = ndf.rename(
    columns = {
      'Highest Offense Description' : 'offense',
      'Latitude' : 'lat',
      'Longitude' : 'lon' })

  # 2. generate dict that maps crimes onto category codes, apply to DataFrame
  #----------------------------------------------------------------------------#

  # create dict that maps crimes onto category codes
  crime_codes = dict( )
  for category, code in category_codes.items():
    for crime in category_crimes[category]:
      crime_codes[crime] = code

  # initialize empty DataFrame
  nndf = pd.DataFrame()

  # copy latitude and longitude columns of full dataframe from step 1.
  nndf['lon'] = ndf['lon']
  nndf['lat'] = ndf['lat']

  # create column of the crime category code for a given crime
  nndf['code'] = ndf['offense'].apply(crime_codes.get).astype('category')

  # remove rows containing uncategorized crimes
  nndf = nndf.dropna()

  # 3. generate plot of all crimes
  #----------------------------------------------------------------------------#

  plot_width = 1000
  plot_height = int(ratio * plot_width)

  # initialize datashader canvas
  cvs = ds.Canvas(
    plot_width = plot_width,
    plot_height = plot_height,
    x_range = x_range,
    y_range = y_range)

  # aggregate data onto datashader canvas
  agg = cvs.points(ndf, 'lon', 'lat',)

  # rasterize and color canvas data using a transfer function based on
  # equally-spaced histogram bins and the colorcet `fire` colormap
  img = tf.shade(agg, cmap = colorcet.palette.fire, how='eq_hist')

  # export image
  ds.utils.export_image(
    img = img,
    filename = 'datashader_all',
    fmt = ".png",
    background = 'black')

  # 3.1 generate SVG of colorbar that can be formatted nicely using a vector
  # graphics editing program like Inkscape
  #............................................................................#

  # generate custom-labelled colormap based on
  # https://matplotlib.org/3.1.1/gallery/ticks_and_spines/colorbar_tick_labelling_demo.html

  fig, ax = plt.subplots()

  data = np.clip(np.random.randn(250, 250), -1, 1)

  cax = ax.imshow(
    data,
    interpolation = 'nearest',
    cmap = ListedColormap( colorcet.fire ) )

  # Add colorbar, make sure to specify tick locations to match desired ticklabels
  cbar = fig.colorbar(cax, ticks=[-1, 1])
  cbar.ax.set_yticklabels(['less\ncrime', 'more\ncrime'])

  # save SVG of colormap to file
  plt.savefig('colorbar.svg')
  plt.close()


  # 4. generate plot of crimes colored by category
  #----------------------------------------------------------------------------#
  # use the first 9 colors of the `Glasbey Light` colormap from the colorcet package
  colors = colorcet.palette.glasbey_light[:9]

  # initialize datashader canvas
  cvs = ds.Canvas(
    plot_width = plot_width,
    plot_height = plot_height,
    x_range = x_range,
    y_range = y_range)

  # aggregate data onto datashader canvas, crouping by the column 'code'
  agg = cvs.points(nndf, 'lon', 'lat', ds.count_cat('code'))

  # rasterize and color canvas data using a transfer function based on
  # the list of colors we defined
  img = tf.shade(
    agg,
    color_key = colors)

  # export image
  ds.utils.export_image(
    img = img,
    filename = 'datashader_by_category_black',
    fmt = ".png",
    background = 'black')

  # 4.1 generate SVG of legend that can be formatted nicely using a vector
  # graphics editing program like Inkscape
  #............................................................................#

  legend_elements = list()

  # generate custom legend based on
  # https://matplotlib.org/3.1.1/gallery/text_labels_and_annotations/custom_legends.html

  # loop over categories, create legend entry with category name, code, and color
  for category, category_code in category_codes.items( ):
    element = Line2D(
      [0],
      [0],
      marker='o',
      color='k',
      label=category,
      markerfacecolor=colorcet.palette.glasbey_light[category_code],
      markersize=10)

    # append legend entry to list of legend entries
    legend_elements.append( element )

  # create arbitrary plot, we're only interested in the legend
  fig, ax = plt.subplots()
  legend = ax.legend(handles=legend_elements, loc='center')

  # format the legend the way I want
  legend.get_frame().set_linewidth(1)
  legend.get_frame().set_facecolor('k')
  plt.setp(legend.get_texts(), color='w')

  # save SVG of legend to file
  plt.savefig('legend.svg')
  plt.close()

  # 5. Save plot of all crimes for each category in separate plots.
  #----------------------------------------------------------------------------#

  # create output directory if it doesn't exist
  os.makedirs( 'datashader_by_category', exist_ok = True )

  for code in range(9):

    # initialize datashader canvas
    cvs = ds.Canvas(
      plot_width = plot_width,
      plot_height = plot_height,
      x_range = x_range,
      y_range = y_range)

    # aggregate data onto datashader canvas, crouping by the column 'code'
    agg = cvs.points(
      nndf[nndf['code'] == code],
      'lon',
      'lat',
      ds.count_cat('code'))

    # rasterize and color canvas data using a transfer function based on
    # the list of colors we defined
    img = tf.shade(
      agg,
      color_key = colors)

    # export image
    ds.utils.export_image(
      img = img,
      filename = f'datashader_by_category/code={code}',
      fmt = ".png",
      background = 'black')

  #----------------------------------------------------------------------------#

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#