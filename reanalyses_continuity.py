import xarray as xr
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm, ListedColormap
import numpy as np
from ncf_funct import cdf_merge, replace_coordinate, sort_coordinate, interpolate

def global_mean_monthly(xrds, lat, lon, time, variable):
    xrds = xrds[[variable]]
    xrds = xrds.mean(dim = [lat, lon]) # fix this ** need weighted area mean
    xrds = xrds.groupby(f'{time}'.month).mean(time) # take global monthly mean
    print(xrds)
    return xrds

def plot(xrds, savename, variable, lat, lon, lev, time):
    # try plotting MERRA2    
    xrds = xrds.unify_chunks()
    # find temperature anomaly at each pressure level from monthly climatological mean
    xrds = xrds[[variable]]
    xrds[variable] = xrds[variable]- 273  # convert K to celcius
    xrds = xrds.mean(dim = [lat, lon]).groupby(f'{time}.month')
    xrds_clim_mean = xrds.mean(time)
    print(xrds_clim_mean)
    xrds_anom = xrds- xrds_clim_mean
    print(xrds_anom)

    # custom color map
    boundaries = [-8, -4, -2, -1, -0.5, 0.5, 1, 2, 4, 8]
    custom_colors = ['darkviolet', 'mediumblue', 'royalblue', 'deepskyblue', 'white', 'yellow', 'gold', 'orange', 'red']
    custom_cmap = ListedColormap(custom_colors)
    norm = BoundaryNorm(boundaries, custom_cmap.N)


    # plot temperature anomaly as a function of time (x), pressure (y)
    xr.plot.contourf(xrds_anom[variable],
                       x = time, 
                       y = lev, 
                       yincrease = False, 
                       yscale = 'log',
                       yticks =  [1000, 500, 300, 200, 100, 50, 30, 20, 10, 5,3,2,1],
                       add_colorbar = True,
                       cmap = custom_cmap,
                        levels = boundaries,
                        norm = norm,
                        figsize = (12,4))
    plt.xlabel('time, YYYY')
    plt.ylabel('pressure, hpa')
    plt.title ('ERA5 Global-mean Temperature Anomaly')
    print(f'saving to... {savename}')
    plt.savefig(savename, dpi = 300)

def rem(era5, merra2, jra55):
    # in progress... need to interpolate to common grid
    common_time = np.intersect1d(jra55['initial_time0_hours'], merra2['time'])
    era5 = era5.sel(valid_time = common_time)
    merra2 = merra2.sel(time = common_time)
    jra55 = jra55.sel(initial_time0_hours = common_time)

    #select commmon pressure levels
    common_lev = np.intersect1d(era5['pressure_level'], merra2['lev'])
    era5 = era5.sel(pressure_level = common_lev)
    merra2 = merra2.sel(lev = common_lev)
    jra55 = jra55.sel(pressure_level = common_lev)

    jra55 = jra55.rename({'latitude':'lat', 'longitude':'lon', 'pressure_level':'plev', 'initial_time0_hours': 'time', 'TMP_GDS4_HYBL_S123':'ta'})
    era5 = era5.rename({'latitude':'lat', 'longitude':'lon', 'pressure_level':'plev', 'valid_time': 'time', 't':'ta'})
    merra2 = merra2.rename({'lat':'lat', 'lon':'lon', 'lev':'plev', 'time': 'time', 'T':'ta'})
    print(f'merra2... {merra2}')
    print(f'era5... {era5}')
    print(f'jra55... {jra55}')

    # take the average
    rem = (era5 + merra2 + jra55)/3

    print(rem)
    return rem

if __name__ == '__main__':
    jra55 = xr.open_dataset('/dx02/siw2111/JRA-55/JRA-55_T_interpolated.nc', chunks = 'auto')
    era5 = xr.open_dataset('/dx02/siw2111/ERA-5/ERA-5_T.nc')
    merra2 = xr.open_dataset('/dx02/siw2111/MERRA-2/MERRA-2_TEMP_ALL-TIME.nc4')
    rem(era5, merra2, jra55)
    
    '''xrds = cdf_merge(files_path = '/dx02/siw2111/ERA-5/unmerged/*.nc', concat_dim = 'valid_time', variable = 't')
    xrds = xrds.sel(pressure_level = slice(1000,1))
    xrds = xrds.sel(valid_time = slice('1980-01-01','2014-01-01'))
    savename = '/home/siw2111/reanalyses_plots/02-25-2025/ERA5_anomaly_1980-2014.png'
    plot(xrds, savename, variable = 't', lon = 'longitude', lat = 'latitude', lev = 'pressure_level', time = 'valid_time')'''