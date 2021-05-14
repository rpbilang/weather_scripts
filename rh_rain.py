#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function
from wrf import getvar, get_cartopy, cartopy_xlim, cartopy_ylim, latlon_coords, interplevel, ALL_TIMES,CoordPair, xy_to_ll, ll_to_xy, interp1d, vinterp, to_np, is_staggered
from glob import glob
import pathlib, pandas as pd, xarray as xr,csv
import numpy as np
import os
import sys
import gc

#Listing the directory and sorting of files
d = xr.open_dataset('2010com.nc')

# set constants
pq0 = 379.90516
a2 = 17.2693882
a3 = 273.16
a4 = 35.86

# set variables

dq2 = d.variables['Q2'][:,:,:]
dt2 = d.variables['T2'][:,:,:]
dpsfc = d.variables['PSFC'][:,:,:]
rain = d.variables['RAINC'][:,:,:]
rainc = d.variables['RAINNC'][:,:,:]


#calculate the rh
rh2 = (dq2/((pq0/dpsfc)*np.exp(a2*((dt2-a3)/((dt2-a4))))))
d["RH2"] = (("Time","south_north","west_east"),rh2)
del rh2
gc.collect()

accum = []
for i in range(len(rainc)):
        current = rain[i,:,:] + rainc[i,:,:]
        if i == 0:
                currentppn = current
                accum.append(currentppn)
        else:
                prev_total = rain[i-1]+rainc[i-1]
                now = current-prev_total
                accum.append(now)

d["RAIN"] = (("Time","south_north","west_east"),accum)
d.to_netcdf("2010fin.nc")


