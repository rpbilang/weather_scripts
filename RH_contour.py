from netCDF4 import Dataset
import matplotlib.pyplot as plt
from matplotlib.cm import get_cmap
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
import cartopy
import cartopy.crs as crs
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature
from cartopy.feature import NaturalEarthFeature
from wrf import (to_np, getvar, smooth2d, get_cartopy, cartopy_xlim,
                 cartopy_ylim, latlon_coords, ALL_TIMES, ll_to_xy)
import numpy as np
import xarray as xr
import io
from PIL import Image

# Open the NetCDF file
ncfile = [Dataset("/media/gil/guheat/Guheat/BEM/wrfout_d03_2018-04-22_01:00:00"),
	  Dataset("/media/gil/guheat/Guheat/BEM/wrfout_d03_2018-04-23_01:00:00"),
	  Dataset("/media/gil/guheat/Guheat/BEM/wrfout_d03_2018-04-24_01:00:00"),
	  Dataset("/media/gil/guheat/Guheat/BEM/wrfout_d03_2018-04-25_01:00:00"),
	  Dataset("/media/gil/guheat/Guheat/BEM/wrfout_d03_2018-04-26_01:00:00"),
	  Dataset("/media/gil/guheat/Guheat/BEM/wrfout_d03_2018-04-27_01:00:00"),
	  Dataset("/media/gil/guheat/Guheat/BEM/wrfout_d03_2018-04-28_01:00:00"),
	  Dataset("/media/gil/guheat/Guheat/BEM/wrfout_d03_2018-04-29_01:00:00")]
RH2 = getvar(ncfile, "rh2", timeidx=ALL_TIMES,method="cat")
T2 = getvar(ncfile, "T2",timeidx=ALL_TIMES,method="cat")
T2F = (T2-273.15)*(9/5)+32  #fahrenheit

#get the mean 
rh2 = RH2.groupby('Time.hour').mean('Time')
t2  = T2F.groupby('Time.hour').mean('Time')

#create the heat index equation
HI = -(42.379)+(2.04901523*t2)+(10.14333127*rh2)-(0.22475541*t2*rh2)-((6.83783*(10**-3))*(t2**2))-((5.481717*(10**-2))*(rh2**2))+((1.22874*(10**-3))*(t2**2)*(rh2))+((8.5282*(10**-4))*(t2)*(rh2**2))-((1.99*(10**-6))*(t2**2)*(rh2**2))

#transform the lat_lon_pair to xy
#Set extent map
a = 120.817165
b = 14.327035
c = 121.214992
d = 14.817328
x_y = ll_to_xy(ncfile, b, a)
x_y2 = ll_to_xy(ncfile, d, c)
x = x_y[0]
y = x_y[1]
x1 = x_y2[0]
y1 = x_y2[1]
print(x,y)
print(x1,y1)

#convert HI to celsius
HIC = (HI-32)*(5/9)
HIC = HIC.squeeze('hour')
HIC = HIC[34:89,22:65]
print(HIC)

# Get the latitude and longitude points
lats, lons = latlon_coords(HIC)

# Get the cartopy mapping object
cart_proj = get_cartopy(T2)
# Create a figure
fig = plt.figure(figsize=(12,6))

# Set the GeoAxes to the projection used by WRF
ax = plt.axes(projection=crs.PlateCarree())

# Download and add the states and coastlines
fname = 'municities.shp'
fname1 = 'gadm36_PHL_2.shp'

shape_feature = ShapelyFeature(Reader(fname).geometries(), crs.PlateCarree(),
			       facecolor='none')
shape_feature1 = ShapelyFeature(Reader(fname1).geometries(), crs.PlateCarree(),
			       facecolor='none')
ax.add_feature(shape_feature1, linewidth=0.6, edgecolor="black")
#ax.add_feature(shape_feature, linewidth=1, edgecolor="black")
#ax.coastlines('10m', linewidth=1)

# Define evenly spaced contour levels: -2.5, -1.5, ... 15.5, 16.5 with the
# specific colours
levels = np.arange(30,45,1, dtype=int)
#lin=np.linspace(26.7,32.82,4,dtype=float)
lin2=np.linspace(32.82,39.4,4,dtype=float)
lin3=np.linspace(39.4,52.3,4,dtype=float)
#print(lin,lin2,lin3)
#levels = np.array([25,26,28.74,30.78,32.82,35.013,37.21,39.4,43.7])


# Make the contour outlines and filled contours for the smoothed sea level
# pressure.
cmap = LinearSegmentedColormap.from_list('name',['blue',
		       "aqua","lime","lawngreen","yellow","gold","orange","tomato","red"])
print(cmap)
CS=plt.contourf(to_np(lons), to_np(lats), to_np(HIC),levels=levels,
             transform=crs.PlateCarree(),
             cmap=cmap,alpha=0.8,extend='both')
#plt.clabel(CS,colors='black',fontsize=10,inline=1,fmt='%1.0f',ticks=100)

#save image in memory in PNG format
png1 = io.BytesIO()
fig.savefig(png1, format="png")
#load this image into PIL
png2 = Image.open(png1)
#save as tiff
png2.save('HI.tiff')
png1.close()

# Add a color bar
plt.colorbar(ax=ax, shrink=.98)

#Set extent map
a = 120.817165
b = 14.327035
c = 121.214992
d = 14.817328

#call for extent map
#ax.set_extent([a,c,b,d])

#plt.title("Heat Index (C)")

plt.show()
