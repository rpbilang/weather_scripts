#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function
from netCDF4 import Dataset as nc
from wrf import getvar, get_cartopy, cartopy_xlim, cartopy_ylim, latlon_coords, interplevel, ALL_TIMES,CoordPair, xy_to_ll, ll_to_xy, interp1d, vinterp, to_np, is_staggered
from glob import glob
import pathlib, pandas as pd, xarray as xr,csv
import numpy as np


#Listing the directory and sorting of files
wrfdir= sorted(glob("/media/gil/guheat/aug_allfdda/wrfout_d03_*"))
ncfiles = [nc(x) for x in wrfdir]


#transform the lat_lon_pair to xy
x_y = ll_to_xy(ncfiles, 14.443028, 121.366665)
x = x_y[0]
y = x_y[1]
print(x)
print(y)

#for interpolation
ht = getvar(ncfiles, "height_agl", units="m")[:,y,x]
levels = np.asarray([30])
print(ht)


#Looping of files
#Extracting the windspeed variable
#wspd dimensions are ws(0),wd(1) x bottom_top x south_north x west_east
#1 for WD, 0 WS
elements = []
for i in range(len(ncfiles)):
	wspd = getvar(ncfiles, "uvmet_wspd_wdir", timeidx=i, method="cat", units="m s-1",meta=False)[0,:,y,x]
	interp_vals = to_np(interp1d(wspd,ht,levels))
	elements.append(interp_vals)

#For wind direction
windirect = []
for i in range(len(ncfiles)):
	wspd1 = getvar(ncfiles, "uvmet_wspd_wdir", timeidx=i, method="cat", units="m s-1",meta=False)[1,:,y,x]
	interp_vals = to_np(interp1d(wspd1,ht,levels))
	windirect.append(interp_vals)

#append windspeed and wind direction
windsd = np.concatenate((elements,windirect),axis=1)
#print(windsd)

with open('AFDDA.csv', 'w') as csvFile:
	writer = csv.writer(csvFile)
	writer.writerows(windsd)
csvFile.close()

#obs_csv = pd.DataFrame(elements).to_csv(r'BSWM_ws_112.csv')
#obs_csv1 = pd.DataFrame(windirect).to_csv(r'BSWM_wd_112.csv')
