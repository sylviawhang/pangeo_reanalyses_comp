import xarray as xr
import numpy as np
from scipy.interpolate import interp1d

# net cdf functions 

def cdf_merge(files_path, savename, concat_dim,  variable):
    # ex. files path \home\data\*.nc
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

def area_weighted_mean(xrds, lat, lon):
    # create weights
    weights = np.cos(np.deg2rad(xrds[lat]))
    weights.name = "weights"
    
    # take weighted mean
    xrds_weighted = xrds.weighted(weights)
    weighted_mean = xrds_weighted.mean(dim = [lat, lon])
    return weighted_mean

def interpolate_grid(xrds1, xrds2):
    # assume all datasets have the same coordinate names
    print(f'interpolating {xrds1} to {xrds2} grid')
    xrds2_lat = xrds2['lat']
    xrds2_lon = xrds2['lon']
    xrds1_interp = xrds1.interp(lat = xrds2_lat, lon = xrds2_lon)
    print(xrds2)
    print(xrds1_interp)
    return xrds1_interp

def interpolate_plev(xrds1, xrds2):
    print('interpolating to common pressure levels...')
    xrds2_plev = xrds2['plev']
    xrds1_interp = xrds1.interp(plev = xrds2_plev)
    print(xrds1_interp)
    return xrds1_interp

def concat_era(era5 = xr.open_dataset('/dx02/siw2111/ERA-5/ERA-5_T.nc', chunks = 'auto'), era51 = xr.open_dataset('/dx02/siw2111/ERA-5/ERA-5.1/ERA5-1-gridded.nc', chunks = 'auto')):
    # insert era5.1 2000-2006 data into era5
    print(era51.coords['valid_time'].values)
    era5_pre = era5.sel(valid_time = slice('1980-01-01', '1999-12-01'))
    print(era5_pre)
    era5_post = era5.sel(valid_time = slice('2006-02-01', '2024-01-01'))
    print(era51)
    print(era5_post)
    era51_concat = xr.concat([era5_pre, era51, era5_post], dim = 'valid_time')
    print(era51_concat)
    return era51_concat

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

if __name__ == '__main__':
    '''merra2 = xr.open_dataset('/dx02/siw2111/MERRA-2/MERRA-2_TEMP_ALL-TIME.nc4', chunks = 'auto')
    era5 = xr.open_dataset('/dx02/siw2111/ERA-5/ERA-5_T.nc', chunks = 'auto')
    
    era5 = era5.rename({'latitude':'lat', 'longitude':'lon', 'pressure_level':'plev', 'valid_time': 'time', 't':'ta'})
    merra2 = merra2.rename({'lat':'lat', 'lon':'lon', 'lev':'plev', 'time': 'time', 'T':'ta'})
    
    lon = merra2.coords['lon'].values
    merra2 = merra2.assign_coords(lon = np.add(lon,180)) 
    print(merra2)

    merra2 = interpolate_grid(merra2, era5)'''

    era5 = xr.open_dataset('/dx02/siw2111/ERA-5/ERA-5_T.nc', chunks = 'auto')
    era51 = xr.open_dataset('/dx02/siw2111/ERA-5/ERA-5.1/ERA5-1-gridded.nc', chunks = 'auto')

    concat_era(era5, era51)


    
    