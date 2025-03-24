import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
from ncf_funct import cdf_merge, replace_coordinate
import colorcet as cc

'''        Variable Names
            ERA5,              MERRA2,    JRA55 
Latitude: 'latitude',         'lat',        'g4_lat_2'
Longitude: 'longitude',        'lon',      'g4_lon_3'
Pressure:  'pressure_level',   'lev',       'lv_HYBL1'
Time:      'valid_time',       'time',   'initial_time0_hours'
Temperature: 't'       ,         'T'      'TMP_GDS4_HYBL_S123' 
U-wind        'u'       ,        'U'          
Ozone:         'o3'               'O3'                       '''

# plotting functions

def annual_zonal_mean(xrds, lon, time, variable):
    xrds = xrds[[variable]]
    zonal_mean_xrds = xrds.mean(dim = [lon, time])
    #print(zonal_mean_xrds)
    return zonal_mean_xrds

def seasonal_zonal_mean(xrds, lon, time, variable):
    xrds = xrds[[variable]]
    seasonal_xrds = xrds.groupby(f"{time}.season").mean(time)
    seasonal_xrds = seasonal_xrds.mean(dim = [lon])
    #print(seasonal_xrds)
    return seasonal_xrds

def plot_zonal_means(xrds, savename, lat, lon, lev, time, variable, title):
    # Goal create a 1 x 5 plot of climatological zonal means
    fig, axes = plt.subplots(nrows=5, ncols=1, figsize=(10, 25), sharex = False, layout = 'constrained')
    vmin, vmax, levels, cmap = 185, 275, 19, 'jet' # configure
    
    annual_xrds = annual_zonal_mean(xrds, lon, time, variable, title)
    #annual_xrds = xr.open_dataset('/dx02/siw2111/MERRA-2/MERRA2_T_zonal_annual')
    print(annual_xrds)
    xr.plot.contourf(annual_xrds[variable],
            x = lat,
            y = lev, 
            yincrease =  False,
            add_colorbar=True,
            add_labels = False,
            ax=axes[0],
            vmin= vmin,
            vmax= vmax,
            cmap= cmap,
            extend="both",
            levels = levels,
            yscale = 'log',
            ylim = (1000, 1))
    xr.plot.contour(annual_xrds[variable],
            x = lat,
            y = lev, 
            yincrease =  False,
            add_colorbar= False,
            add_labels = False,
            ax=axes[0],
            vmin= vmin,
            vmax= vmax,
            colors ="k",
            levels = levels,
            yscale = 'log',
            ylim = (1000, 1))
    annual_xrds.close()
    
    axes[0].set_ylim(1000,1)
    axes[0].set_ylabel('Pressure (hPa)', fontsize = 15)
    axes[0].set_title('Annual', fontsize = 15)
    
    seasonal_xrds  = seasonal_zonal_mean(xrds, lon, time, variable, title)
    #seasonal_xrds = xr.open_dataset('/dx02/siw2111/JRA-55/JRA55_T_zonal_seasonal')
    print(seasonal_xrds)
    for i, season in enumerate(("DJF", "MAM", "JJA", "SON")):
        xr.plot.contourf(seasonal_xrds[variable].sel(season=season), 
            x = lat,
            y = lev, 
            yincrease =  False,
            add_colorbar=True,
            add_labels = False,
            ax=axes[i + 1],
            vmin= vmin,
            vmax= vmax,
            cmap= cmap,
            extend="both",
            levels = levels,
            yscale = 'log',
            ylim = (1000, 1))
        xr.plot.contour(seasonal_xrds[variable].sel(season = season),
            x = lat,
            y = lev, 
            yincrease =  False,
            add_colorbar= False,
            add_labels = False,
            ax=axes[i + 1],
            vmin= vmin,
            vmax= vmax,
            colors ="k",
            levels = levels,
            yscale = 'log',
            ylim = (1000, 1))

        axes[i+1].set_ylabel('Pressure (hPa)', fontsize = 15)
        axes[i+1].set_title(season, fontsize = 15)
        axes[i+1].set_ylim(1000, 1)
    seasonal_xrds.close()

    axes[4].set_xlabel('Latitude (Deg N)', fontsize = 15)
    fig.suptitle("CMIP6 Zonal Mean Temperature 2000-2014" , fontsize= 20)
    
    print(f' saving to... {savename}')
    plt.savefig(savename, dpi = 250)

def plot_annual(xrds, lon, lat, lev, time, variable, savename):
    annual_xrds = annual_zonal_mean(xrds, lon, time, variable)
    
    boundaries = [180, 185, 190, 195, 200, 205, 210, 215, 220, 225, 230, 235, 240, 245, 250, 255, 260, 265, 270, 275, 280, 285, 290, 295, 300]
    plt.figure(figsize = (12,6), layout = 'constrained')
    xr.plot.contourf(annual_xrds[variable],
            x = lat,
            y = lev, 
            yincrease =  False,
            add_colorbar=True,
            cbar_kwargs= {'label':'Temperature, K', 'drawedges':True, 'ticks':boundaries},
            levels = boundaries,
            add_labels = False,
            cmap= cc.cm.rainbow_bgyr_10_90_c83,
            extend="neither",
            yscale = 'log',
            ylim = (1000, 1))
    cs = xr.plot.contour(annual_xrds[variable],
            x = lat,
            y = lev, 
            yincrease =  False,
            add_colorbar= False,
            add_labels = False,
            linewidths = 0.5,
            colors ="k",
            levels = boundaries,
            yscale = 'log',
            ylim = (1000, 1))
    plt.clabel(cs, cs.levels, fontsize=10)
    annual_xrds.close()
    
    cbar = plt.gca().collections[0].colorbar  # Get the colorbar object
    cbar.ax.tick_params(length=0)
    cbar.ax.set_ylabel('Temperature, K', fontsize=12) 

    plt.ylim(1000,1)
    plt.ylabel('Pressure, hPa', fontsize = 12)
    plt.xlabel('Latitude, deg N', fontsize = 12)
    plt.title('GISS-E2-1-G Zonal Mean Temperature (Annual 1980-2014)', fontsize = 15)

    print(f'saving to... {savename}')
    plt.savefig(savename, dpi = 300)

if __name__ == '__main__':
    xrds = xr.open_dataset('/dx02/siw2111/MERRA-2/MERRA-2_TEMP_ALL-TIME.nc4', chunks = 'auto')
    xrds = xrds.sortby('time')
    print(xrds)
    xrds = xrds.sel(time = slice('1980-01-01', '2014-01-01'))
    xrds = xrds.sel(lev = slice(1000,1))
    print(xrds)
    savename = '/home/siw2111/cmip6_reanalyses_comp/reanalyses_plots/03-20-2025/MERRA2_zonal-mean_1980-2014.png'
    plot_annual(xrds, lon = 'lon', lat = 'lat', lev = 'lev', time = 'time', variable = 'T', savename = savename )