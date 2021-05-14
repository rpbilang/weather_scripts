#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function
from netCDF4 import Dataset as nc
from wrf import getvar, get_cartopy, cartopy_xlim, cartopy_ylim, latlon_coords, interplevel, ALL_TIMES,CoordPair, xy_to_ll, ll_to_xy, interp1d, vinterp, to_np, is_staggered
from glob import glob
import pathlib, pandas as pd, xarray as xr,csv
import numpy as np
import datetime


#Listing the directory and sorting of files
wrfdir= sorted(glob("wrfout_d04*"))
ncfiles = [nc(x) for x in wrfdir]

#transform the lat_lon_pair to xy
x_y = ll_to_xy(ncfiles, 14.443028,121.366665)
x = x_y[0]
y = x_y[1]

rain = getvar(ncfiles, "RAINC", timeidx=ALL_TIMES, method="cat",meta=False)[:,y,x]
rainc = getvar(ncfiles, "RAINNC", timeidx=ALL_TIMES, method="cat",meta=False)[:,y,x]
rh = getvar(ncfiles, "rh",timidx=ALL_TIMES,method='cat',meta=False)[:,y,x]
times = getvar(ncfiles, "times", timeidx=ALL_TIMES,meta=False)
time = pd.to_datetime(times)
accum = []
for i in range(len(rainc)):
	current = rain[i] + rainc[i] 
	if i == 0:
		currentppn = current
		accum.append(currentppn) 
	else:
		prev_total = rain[i-1]+rainc[i-1] 
		now = current-prev_total
		accum.append(now)

accum = pd.DataFrame(np.row_stack(accum))
rhf = pd.DataFrame(np.row_stack(rh))
time = pd.DataFrame(np.row_stack(time))
final = pd.concat([time,accum,rhf],axis=1)

obs_csv = pd.DataFrame(final).to_csv(r'rain.csv') 
