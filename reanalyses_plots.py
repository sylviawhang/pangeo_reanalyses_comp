import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
from ncf_funct import cdf_merge, replace_coordinate

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

def annual_zonal_mean(xrds, lon, time, variable, title):
    if title == 'MERRA-2':
        xrds = xrds.sel(lev = slice(2.00000000e+02, 1.00000000e-01))
    if title == 'JRA-55' : 
        xrds = replace_coordinate(xrds)
    xrds = xrds[[variable]]
    zonal_mean_xrds = xrds.mean(dim = [lon, time])
    print(zonal_mean_xrds)
    return zonal_mean_xrds

def seasonal_zonal_mean(xrds, lon, time, variable, title):
    if title == 'MERRA-2':
        xrds = xrds.sel(lev = slice(2.00000000e+02, 1.00000000e-01))
    if title == 'JRA-55' : 
        xrds = replace_coordinate(xrds)
    xrds = xrds[[variable]]
    seasonal_xrds = xrds.groupby(f"{time}.season").mean(time)
    seasonal_xrds = seasonal_xrds.mean(dim = [lon])
    print(seasonal_xrds)
    return seasonal_xrds

def plot_zonal_means(xrds, savename, lat, lon, lev, time, variable, title):
    # Goal create a 1 x 5 plot for MERRA2 with temperatures
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

if __name__ == '__main__':
    # plot MERRA2
    '''file = '/dx02/siw2111/MERRA-2/MERRA2_100.instM_3d_asm_Np.198001.nc4' # dummy
    savename = '/home/siw2111/reanalyses_plots/02-06-2025/seasonal_zonal_temp_MERRA2_0206.png'
    print(f'reading... {file}')
    xrds = xr.open_dataset(file, chunks = 'auto')
    plot_zonal_means(xrds, savename, lat = 'lat', lon = 'lon', lev ='lev', time = 'time', variable = 'T', title = 'MERRA-2')
    xrds = xrds.close()'''

    '''#plot ERA-5
    file = '/dx02/siw2111/MERRA-2/MERRA2_100.instM_3d_asm_Np.198001.nc4' # dummy
    savename = '/home/siw2111/reanalyses_plots/02-06-2025/seasonal_zonal_temp_ERA5_0206.png'
    print(f'reading... {file}')
    xrds = xr.open_dataset(file, chunks = 'auto')
    plot_zonal_means(xrds, savename, lat = 'latitude', lon = 'longitude', lev ='pressure_level', time = 'valid_time', variable = 't', title = 'ERA-5')
    xrds = xrds.close()'''

    # plot JRA55
    #file = '/dx02/siw2111/JRA-55/JRA-55_ALL-TIME' 
    savename = '/home/siw2111/reanalyses_plots/02-06-2025/seasonal_zonal_T_JRA55_0206.png'
    #print(f'reading... {file}')
    #xrds = xr.open_dataset(file, chunks = 'auto')
    xrds = cdf_merge()
    plot_zonal_means(xrds, savename, lat = 'g4_lat_2', lon = 'g4_lon_3', lev ='lv_HYBL1', time = 'initial_time0_hours', variable = 'TMP_GDS4_HYBL_S123', title = 'JRA-55')


























def plot_temp_vs_time(file, savename):
    xrds = xr.open_dataset(file)
    
    #xrds = cdf_merge()
    #xrds = xrds.sel(lev = slice(1.00000000e+02, 1.00000000e+00)) # select pressure levels 100hPA - 1hPA for MERRA2
    #xrds = xrds.sortby('time') #sort time for MERRA2
    
    xrds = xrds.sel(valid_time = slice('1980-01-01', '2024-11-01'))
    global_mean_xrds = xrds.mean(dim = ['longitude', 'latitude', 'pressure_level']) # average over latitude, longitude, and pressure
    print(global_mean_xrds)
    
    xr.plot.line(global_mean_xrds['t'], x = 'valid_time')
    plt.title('ERA-5')
    plt.xlabel('time (YYYY)')
    plt.ylabel('temperature (K)')
    plt.ylim(225,235)
    
    print(f'saving to... {savename}')
    plt.savefig(savename, dpi = 400)


def plot_zonal_temp(file = '/dx02/siw2111/ERA-5/ERA5_TEMP_ALL-TIME.nc' , savename = '/home/siw2111/reanalyses_plots/ERA5_zonal_mean.png'):
    xrds = xr.open_dataset(file)

    xrds= xrds.sel(valid_time = slice('1980-01-01', '2024-11-01')) #select only time from 1980-2024
    
    zonal_mean_xrds = xrds.mean(dim = ['longitude', 'valid_time']) #average over longitudes, and time (?)
    print(zonal_mean_xrds)
    
    xr.plot.contour(zonal_mean_xrds['t'], x = 'latitude', y = 'pressure_level', size = 5, aspect = 'auto', yincrease = False, add_colorbar = True, vmin = 190, vmax = 270, cmap = 'turbo', robust = False, extend = 'neither', levels =17, yscale = 'log') 
    xr.plot.contourf(zonal_mean_xrds['t'], x = 'latitude', y = 'pressure_level', size = 5, aspect = 'auto', 
                     yincrease = False, 
                     add_colorbar = True, 
                     vmin = 190, vmax = 270, 
                     cmap = 'turbo', 
                     robust = False, 
                     extend = 'neither',  
                     levels =17, 
                     yscale = 'log') 

    plt.title('ERA-5')
    plt.xlabel('latitude (degrees N)')
    plt.ylabel('pressure (hPa)')

    print(f'saving to... {savename}')
    plt.savefig(savename, dpi = 300)

def MERRA2():
    file = '/dx02/siw2111/MERRA-2/MERRA-2_TEMP_ALL-TIME.nc4'

    xrds = xr.open_dataset(file)
    xrds = xrds.sel(lev = slice(1.00000000e+02, 1.00000000e+00)) # select pressure levels 100hPA - 1hPA for MERRA2
    print(xrds) 

    zonal_mean_xrds = xrds.mean(dim = ['lon', 'time'])
    print(zonal_mean_xrds)
    
    xr.plot.contour(zonal_mean_xrds['T'], x = 'lat', y = 'lev', size = 5, aspect = 'auto', yincrease = False, add_colorbar = True, vmin = 190, vmax = 270, cmap = 'turbo', robust = False, extend = 'neither', levels = 17, yscale = 'log') 
    xr.plot.contourf(zonal_mean_xrds['T'], x = 'lat', y = 'lev', size = 5, aspect = 'auto', yincrease = False, add_colorbar = True, vmin = 190, vmax = 270, cmap = 'turbo', robust = False, extend = 'neither',  levels = 17, yscale = 'log') 
    #plt.clabel(CS, fontsize = "smaller", colors = 'k')

    plt.title('MERRA-2')
    plt.xlabel('latitude (degrees N)')
    plt.ylabel('pressure (hPa)')

    plt.savefig('/home/siw2111/reanalyses_plots/MERRA2_zonal-mean.png', dpi = 300)

def JRA55():
    file = '/dx02/siw2111/JRA-55/JRA-55_TEMP_ALL-TIME'

    #xrds = xr.open_dataset(file)
    xrds = cdf_merge()

    # assign pressure levels
    lv_hPa = np.array([113.881, 96.890, 81.643, 67.638, 551.50, 44.666, 36.081, 29.145, 23.530, 18.989, 15.320, 12.351, 9.971, 8.049, 6.493, 5.240, 4.222, 3.383, 2.684, 2.089, 1.584, 1.160, 0.805]) # pressure in hPa corresponding to JRA-55 levels 35-57.
    xrds = xrds.assign_coords(lv_HYBL1  = lv_hPa)

    # select time 1980-2024
    xrds = xrds.sel(initial_time0_hours = slice('1980-01-01', '2024-11-01'))
    
    print(xrds)

    zonal_mean_xrds = xrds.mean(dim = ['g4_lon_3', 'initial_time0_hours'])
    print(zonal_mean_xrds)
    
    xr.plot.contour(zonal_mean_xrds['TMP_GDS4_HYBL_S123'], x = 'g4_lat_2', y = 'lv_HYBL1', size = 5, aspect = 'auto', yincrease = False, add_colorbar = True, vmin = 190, vmax = 270, cmap = 'turbo', robust = False, extend = 'neither',  levels = 17, yscale = 'log') 
    xr.plot.contourf(zonal_mean_xrds['TMP_GDS4_HYBL_S123'], x = 'g4_lat_2', y = 'lv_HYBL1', size = 5, aspect = 'auto', yincrease = False, add_colorbar = True, vmin = 190, vmax = 270, cmap = 'turbo', robust = False, extend = 'neither',  levels = 17, yscale = 'log') 

    plt.ylim(100,1.00)
    plt.title('JRA-55')
    plt.xlabel('latitude (degrees N)')
    plt.ylabel('pressure (hPa)')

    plt.savefig('/home/siw2111/reanalyses_plots/JRA55_zonal-mean_122.png', dpi = 300)



    