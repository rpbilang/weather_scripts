##File modified from the script done by m1t9. Check https://gist.github.com/m1t9/0538d9df1dad9e941f78845462f237


import sys
import numpy as np
from netCDF4 import Dataset

print('\nstart read .nc file\n')

# INPUT NETCDF4 FILE NAME
nc_fileID = str(input('Input netcdf file name: '))

# VERIFY THAT FILE EXISTS
try:
    file_chk = open(nc_fileID)
except FileNotFoundError:
    sys.exit('\nERROR! file not found')

# READ NETCDF FILE AND PRINT AVIABLE VARIABLES
root = Dataset(nc_fileID)
print(root)
dims = root.dimensions
ndims = len(dims)

dic = {}
dic2 = {}
print('\navailable variables in selected .NC file:\n')
vars = root.variables
print(vars)
nvars = len(vars)
n = 0
for var in vars:
    # sys.stdout.write('-'+var+' ')
    print('#',n,'   ',var, vars[var].shape)
    dic[str(var)] = n
    l = vars[var].shape
    dic2[str(var)] = len(l)
    n += 1
print('\n')

# INPUT VARIABLES THAT YOU WANT TO READ
nc_data = []
iter_var = []
iter_var.append(input('write the variables you want to read (through the gap): ').split(' '))
iter_var = iter_var[0]
try:
    for v in iter_var:
        dic[v]
except KeyError:
    sys.exit('\nvariable name error\n')

# WARNING!
# MAX DIMENSIONS OF MASSIVE: 3

var_inter_n = {}
ni = 0
for i in iter_var:
    if (dic2[i] == 1):
        nc_data.append(np.array(root.variables[i][:], dtype=np.float32))
    if (dic2[i] == 2):
        nc_data.append(np.array(root.variables[i][:,:], dtype=np.float32))
    if (dic2[i] == 3):
        nc_data.append(np.array(root.variables[i][:,:,:], dtype=np.float32))
    var_inter_n[i] = ni
    ni += 1

print('\nread complete\n')

# WRITE GRID OF INPUT WIND NETCDF DIMENSION (REGULAR GRID WITH FIXED STEP IN SPACE\TIME)
# OUTPUT FILE CONTAIN TWO COLOMNS WITH LONGITUDE AND LATITUDE COORDINATES
chk = input('write wind grid? y/n ')
if (chk != 'n'):
    outfile2_name = 'uvsp_grd.dat'
    outfile2 = open(outfile2_name, 'w')
    for i in range((len(root.variables['XLONG']))):
        for j in range(len(root.variables['XLAT'])):
            outfile2.write(str(root.variables['XLONG'][i])+'    '+str(root.variables['XLAT'][j])+'\n')
    print('wind grid write complete')

# WRITE CHECK
check = input('start create meteo files? y/n ')
if (check == 'n'):
    sys.exit()

# USING CONST LIST
nodata_value = -999.000
grid_unit = 'm' #  m or degree
longitude_name = 'XLONG'
latitude_name = 'XLAT'
time_name = 'XTIME'
n_quantity = 1
x_llcorner = np.asarray(root.variables[longitude_name][-1,0])
y_llcorner = np.asarray(root.variables[latitude_name][0,-1])

from pyproj import Proj, transform
def reproject_wgs_to_utm(longitude,latitude):
	proj_wgs = Proj(init='epsg:4326')
	proj_utm = Proj(init='epsg:32651')
	x,y = transform(proj_wgs,proj_utm,longitude,latitude)
	return x,y
x_llcorner,y_llcorner = reproject_wgs_to_utm(x_llcorner,y_llcorner)
dy = root.__dict__['DY']
dx = root.__dict__['DX']
month = str(input('Name of File: '))

for i in iter_var:

    # LIST OF AVIABLE OUTPUT DATA FOR DELFT3D METEO INPUT FILES
    if (i == 'U10'): fmt = '.amu'
    if (i == 'V10'): fmt = '.amv'
    if (i == 'PSFC'): fmt = '.amp'
    if (i == 'RH2'): fmt = '.amr'
    if (i == 'RAIN'): fmt = '.ext'
    if (i == 'SWDOWN'): fmt = '.ext'
    if (i == 'T2F'): fmt = '.amt'

    # FOR SINGLE MONTH CHOOSE ONE:
    mnth_chck = True 
    # mnth_chck = True
    outfile_name = str(i)+'_'+month+fmt
    outfile = open(outfile_name, 'w')
    outfile.write('FileVersion = 1.03\n')
    outfile.write('filetype = meteo_on_equidistant_grid\n')
    outfile.write('NODATA_value = '+str(nodata_value)+'\n')
    n_cols = vars[i].shape[2]
    outfile.write('n_cols = '+str(n_cols)+'\n')
    n_rows = vars[i].shape[1]
    outfile.write('n_rows = '+str(n_rows)+'\n')
    outfile.write('grid_unit = '+str(grid_unit)+'\n')
    outfile.write('x_llcorner = '+str(x_llcorner)+'\n')
    outfile.write('y_llcorner = '+str(y_llcorner)+'\n')
    outfile.write('dx = '+str(dx)+'\n')
    outfile.write('dy = '+str(dy)+'\n')
    outfile.write('n_quantity = '+str(n_quantity)+'\n')
    quantity1 = '???'
    unit1 = '???'
    if (i == 'U10'):
        quantity1 = 'x_wind'
        unit1 = 'm s-1'
    elif (i == 'V10'):
        quantity1 = 'y_wind'
        unit1 = 'm s-1'
    elif (i == 'PSFC'):
        quantity1 = 'air_pressure'
        unit1 = 'Pa'
    elif (i == 'RH2'):
        quantity1 = 'relative humidity'
        unit1 = '%'
    elif (i == 'SWDOWN'):
        quantity1 = 'downward short wave flux at ground surface'
        unit1 = 'W m-2'
    elif (i == 'RAIN'):
        quantity1 = 'Precipitation'
        unit1 = 'mm'
    elif (i == 'T2F'):
        quantity1 = 'Air Temperature at 2m'
        unit1 = 'Celsius'

    outfile.write('quantity1 = '+quantity1+'\n')
    outfile.write('unit1 = '+unit1+'\n')
    time1 = 0

    # WRITE DATA IN FILE
    for t in range(len(root.variables[time_name])):
        outfile.write('TIME = ' + str(root.variables[time_name][t]) + ' minutes since ' + str(root.__dict__['SIMULATION_START_DATE'])+ '\n')
        for n in range(int(vars[i].shape[1])):
            for m in range(int(vars[i].shape[2])):
                if i == 't2m':
                    outfile.write(str(nc_data[var_inter_n[i]][t, n, m] - 273.150)+' ')
                else:
                    outfile.write(str(nc_data[var_inter_n[i]][t, n, m])+' ')
            outfile.write('\n')
    print('done')

