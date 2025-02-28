import xarray as xr
import numpy as np
from scipy.interpolate import interp1d

# net cdf functions 

def cdf_merge(files_path = '/dx02/siw2111/JRA-55/*.nc', savename = '/dx02/siw2111/JRA-55/JRA-55_T.nc', concat_dim = 
              'initial_time0_hours', variable = 'TMP_GDS4_HYBL_S123'):
    print(f'merging files... {files_path}')
    xrds = xr.open_mfdataset(files_path, combine = 'nested', concat_dim = concat_dim, chunks = 'auto')
    xrds = xrds[[variable]] # select temperature
    print(xrds)

    print(f"saving to... {savename}")
    xrds.to_netcdf(savename) # Export netcdf file
    print(f'saved as... {savename}')
    
    return xrds

def sort_coordinate(xrds):
    xrds = xrds.sortby('time') # sort time for MERRA2

    return xrds

def replace_coordinate(xrds): 
    # replace pressure levels with values for JRA55
    print(xrds.coords['lv_HYBL1'].values)
    print(len(xrds.coords['lv_HYBL1'].values))
    levels = np.array([998.5,995.5,991.499,985.498,976.996,965.994,952.991,936.986,917.982,896.978,873.47,846.961,817.954,786.946,754.44,720.429,684.417,
                    647.412,609.901,571.895,533.887,495.879,458.376,421.872,386.368,351.863,318.866,287.361,257.364,228.857,201.86,176.864,153.869,
                    132.875,113.881,96.89,81.643,67.638,55.15,44.666,36.081,29.145,23.53,18.989,15.32,12.351,9.971,8.049,6.493,5.24,4.222,3.383,
                    2.684,2.089,1.584,1.16,0.805])
    xrds = xrds.assign_coords(lv_HYBL1  = levels)
    print(xrds)

    return xrds

def interpolate(xrds1, xrds2):
    # interpolate xrds1 dimension to match xrds2
    # xrds1 = JRA-55, xrds2 = ERA5, dimension = pressure
    print(f'interpolating {xrds1} to {xrds2}')

    # select common times
    print('selecting common times...')
    common_time = np.intersect1d(xrds1['initial_time0_hours'], xrds2['valid_time'])
    xrds1 = xrds1.sel(initial_time0_hours = common_time)
    xrds2 = xrds2.sel(valid_time = common_time)

    # interpolate xrds1 to xrds2 spacial grid
    print('interpolating to common spatial grid...')
    xrds2_lat = xrds2['latitude']
    xrds2_lon = xrds2['longitude']
    xrds1_interp = xrds1.interp(g4_lat_2 = xrds2_lat, g4_lon_3 = xrds2_lon)
    xrds1_interp = xrds1_interp.drop_vars('g4_lat_2')
    xrds1_interp = xrds1_interp.drop_vars('g4_lon_3')

    # interpolate to xrds2 pressure level
    print('interpolating to common pressure levels...')
    xrds2_lev = xrds2['pressure_level']
    xrds1_interp = xrds1_interp.interp(lv_HYBL1 = xrds2_lev)
    xrds1_interp = xrds1_interp.drop_vars('lv_HYBL1')
    print(xrds1_interp)

    return xrds1_interp
    
    
    '''xrds1_levs = xrds1_interp['lv_HYBL1']
    xrds1_temperature = xrds1_interp['TMP_GDS4_HYBL_S123']
    xrds2_levs = xrds2['pressure_level']

    interp_func = interp1d(xrds1_levs, xrds1_temperature, axis=1, bounds_error=False, fill_value="extrapolate")
    interp_temp = interp_func(xrds2_levs)
    xrds1_interpolated = xr.DataArray(interp_temp, dims=xrds1_interp['TMP_GDS4_HYBL_S123'].dims, coords=xrds1_interp.coords)
    print(xrds1_interpolated)'''

if __name__ == '__main__':
    '''xrds1 = xr.open_dataset('/dx02/siw2111/JRA-55/JRA-55_T.nc', chunks = 'auto')
    xrds2 = xr.open_dataset('/dx02/siw2111/ERA-5/ERA-5_T.nc', chunks = 'auto')
    xrds1_interp = interpolate(xrds1, xrds2)
    savename = '/dx02/siw2111/JRA-55/JRA-55_T_interpolated.nc'
    print(f'saving to... {savename}')
    xrds1_interp.to_netcdf(savename)
    print('saving complete')'''

    cdf_merge(files_path = '/dx02/siw2111/ERA-5/unmerged/*.nc', savename ='/dx02/siw2111/ERA-5/ERA-5_T.nc', concat_dim = 'valid_time', variable = 't')


    