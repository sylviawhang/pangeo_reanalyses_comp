import xarray as xr
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm, ListedColormap
import numpy as np
from ncf_funct import cdf_merge, replace_coordinate, sort_coordinate

def global_mean_monthly(xrds, lat, lon, time, variable):
    xrds = xrds[[variable]]
    xrds = xrds.mean(dim = [lat, lon])
    xrds = xrds.groupby(f'{time}'.month).mean(time) # take global monthly mean
    print(xrds)
    return xrds

def plot(xrds, savename):
    # try plotting MERRA2    
    
    # find temperature anomaly at each pressure level from monthly climatological mean
    xrds = xrds[['T']]
    xrds['T'] = xrds['T']- 273  # convert K to celcius
    xrds = xrds.mean(dim = ['lat', 'lon']).groupby('time.month')
    xrds_clim_mean = xrds.mean('time')
    print(xrds_clim_mean)
    xrds_anom = xrds- xrds_clim_mean
    print(xrds_anom)

    # custom color map
    boundaries = [-8, -4, -2, -1, -0.5, 0.5, 1, 2, 4, 8]
    custom_colors = ['darkviolet', 'mediumblue', 'royalblue', 'deepskyblue', 'white', 'yellow', 'gold', 'orange', 'red']
    custom_cmap = ListedColormap(custom_colors)
    norm = BoundaryNorm(boundaries, custom_cmap.N)


    # plot temperature anomaly as a function of time (x), pressure (y)
    xr.plot.contourf(xrds_anom['T'],
                       x = 'time', 
                       y = 'lev', 
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
    plt.title ('MERRA2 Global-mean Temperature Anomaly')
    print(f'saving to... {savename}')
    plt.savefig(savename, dpi = 300)


if __name__ == '__main__':
    xrds = xr.open_dataset('/dx02/siw2111/MERRA-2/MERRA-2_TEMP_ALL-TIME.nc4', chunks = 'auto')
    xrds = sort_coordinate(xrds)
    xrds = xrds.sel(lev = slice(1000,1))
    #xrds = xrds.sel(time = slice('1980-01-01','2014-01-01'))
    savename = '/home/siw2111/reanalyses_plots/02-25-2025/MERRA2_anomaly_1980-2024.png'
    plot(xrds, savename)