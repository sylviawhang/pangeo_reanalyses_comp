import xarray as xr
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm, ListedColormap
import numpy as np
from ncf_funct import area_weighted_mean, concat_era

# Sylvia Whang siw2111@barnard.edu, Spring 2025
# Functions to recreate plots in Figure 3.3 of S-RIP, Global-mean temperature anomolies from monthly climatology. 

def plot(xrds, savename, variable, lat, lon, lev, time):
    # try plotting MERRA2    
    xrds = xrds.unify_chunks()
    # find temperature anomaly at each pressure level from monthly climatological mean
    xrds = xrds[[variable]]
    xrds[variable] = xrds[variable]- 273  # convert K to celcius
    xrds = area_weighted_mean(xrds, lat, lon).groupby(f'{time}.month')
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
    plt.title ('ERA-5.1 Global-mean Temperature Anomaly')
    print(f'saving to... {savename}')
    plt.savefig(savename, dpi = 300)

if __name__ == '__main__':
    
    xrds = concat_era()
    xrds = xrds.sel(pressure_level = slice(1000,1))
    xrds = xrds.sel(valid_time = slice('1980-01-01','2024-01-01'))
    savename = '/home/siw2111/cmip6_reanalyses_comp/reanalyses_plots/03-03-2025/ERA51_anomaly_1980-2024.png'
    plot(xrds, savename, variable = 't', lon = 'longitude', lat = 'latitude', lev = 'pressure_level', time = 'valid_time')

    '''xrds = xr.open_dataset('/dx02/siw2111/JRA-55/JRA-55_T_interpolated.nc', chunks = 'auto' )
    #xrds = xrds.sortby('time')
    xrds = xrds.sel(pressure_level = slice(1000, 1))
    xrds = xrds.sel(initial_time0_hours = slice('1980-01-01', '2024-01-01') )
    savename = '/home/siw2111/cmip6_reanalyses_comp/reanalyses_plots/03-03-2025/JRA55_anomaly_1980-2024.png'
    plot(xrds, savename, variable = 'TMP_GDS4_HYBL_S123', lon = 'longitude', lat = 'latitude', lev = 'pressure_level', time = 'initial_time0_hours')'''
