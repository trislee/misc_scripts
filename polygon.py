# -*- coding: UTF-8 -*-

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

import os

import numpy as np

import matplotlib.pyplot as plt

from PIL import Image, ImageDraw

import imageio

from skimage.morphology import binary_dilation

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

fft_dir = 'polygons_2048/polygons_fft'
polygon_dir = 'polygons_2048/polygons'

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

def polygon_vertices(N, n):

  c0 = (N - 1) / 2.
  c1 = (N - 1) / 2.

  r = 0.4 * N

  x = np.arange(int(np.ceil(n)))

  v = np.zeros((int(np.ceil(n)), 2))
  v[:, 1] = c0 + r * np.cos(2 * np.pi * x / float(n))
  v[:, 0] = c1 + r * np.sin(2 * np.pi * x / float(n))

  return np.array(v, dtype = np.int)

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

def scale_values_unity( array ):

  """Scale array values to [0,1].
  """

  min_val = np.amin( array )
  max_val = np.amax( array )
  array -= min_val
  array /= ( max_val - min_val )

  return array

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

N = 512

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

if __name__ == '__main__':

  os.makedirs( polygon_dir, exist_ok = True )
  os.makedirs( fft_dir, exist_ok = True )


  ns = np.linspace(3, 8, 501)
  selem = np.ones((5, 5))

  for i, n in enumerate(ns):

    p = polygon_vertices( N = N, n = n )
    pl = [tuple(i) for i in p]

    im = Image.new('L', (N, N), 0)
    ImageDraw.Draw(im).polygon(pl, outline = 1, fill = 0)
    mask = np.array(im)

    mask = binary_dilation(image = mask, selem = selem)

    imageio.imwrite(
      os.path.join(
        polygon_dir,
        f'n={n:.2f}.png'),
      mask.astype(np.float))

    fft = np.fft.fftshift(np.abs(np.fft.fft2(mask)))
    fft = scale_values_unity(fft)

    lfft = np.log( fft + 1e-8)

    imageio.imwrite(
      os.path.join(
        fft_dir,
        f'fft_n={n:.2f}.png'),
      lfft)

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#