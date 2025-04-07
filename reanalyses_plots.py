import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
from ncf_funct import detrend_fct, difference
from datetime import datetime
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

def annual_zonal_mean_detrended(xrds, lon, time, variable):
    xrds = xrds[[variable]]
    xrds = detrend_fct(xrds)
    zonal_mean_xrds = xrds.mean(dim = [lon, time])
    #print(zonal_mean_xrds)
    return zonal_mean_xrds

def seasonal_zonal_mean(xrds, lon, time, variable):
    xrds = xrds[[variable]]
    seasonal_xrds = xrds.groupby(f"{time}.season").mean(time)        
    seasonal_xrds = seasonal_xrds.mean(dim = [lon])
    #print(seasonal_xrds)
    return seasonal_xrds

def seasonal_zonal_mean_detrended(xrds, lon, time, variable):
    xrds = xrds[[variable]]
    seasonal_xrds = xrds.groupby(f"{time}.season").map(detrend_fct)
    seasonal_xrds = seasonal_xrds.groupby(f"{time}.season").mean(dim = time)
    
    seasonal_xrds = seasonal_xrds.mean(dim = [lon])
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

# plot to compare MERRA2 and JRA55

def load_reans(time_range:tuple):
    # load jra55
    time_slice = slice(f'{time_range[0]}-01-01', f'{time_range[1]}-12-01')

    model_xrds = xr.open_dataset('/dx02/siw2111/JRA-55/JRA-55_T_interpolated.nc')
    print(model_xrds)
    print(model_xrds.variables['TMP_GDS4_HYBL_S123'].values)
    model_xrds = model_xrds.rename({'latitude':'lat', 'longitude':'lon', 'pressure_level':'plev', 'initial_time0_hours': 'time', 'TMP_GDS4_HYBL_S123':'ta'})
    model_xrds = model_xrds.sel(plev = slice(1000,1))
    print(model_xrds)
    model_xrds =model_xrds.sel(time = time_slice)
    model_xrds = detrend_fct(model_xrds) # detrend 

    # load reanalysis
    rean_xrds = xr.open_dataset('/dx02/siw2111/MERRA-2/MERRA-2_TEMP_ALL-TIME.nc4', chunks = 'auto')
    rean_xrds = rean_xrds.rename({'lat':'lat', 'lon':'lon', 'lev':'plev', 'time': 'time', 'T':'ta'})
    rean_xrds = rean_xrds.sel(plev = slice(1000,1))
    rean_xrds = rean_xrds.sortby('time')
    
    rean_xrds = rean_xrds.sel(time = time_slice)
    rean_xrds = detrend_fct(rean_xrds) #detrend 


    annual_model = annual_zonal_mean(model_xrds, 'lon', 'time', 'ta')
    seasonal_model = seasonal_zonal_mean(model_xrds, 'lon', 'time', 'ta')

    annual_rean = annual_zonal_mean(rean_xrds, 'lon', 'time', 'ta')
    seasonal_rean = seasonal_zonal_mean(rean_xrds, 'lon', 'time', 'ta')

    xrds_li = [(annual_model, annual_rean), (seasonal_model, seasonal_rean)]
    diff_li = []

    for model, rean in xrds_li:
        diff = difference(model, rean)
        diff_li.append(diff)

    annual_diff = diff_li[0] 
    seasonal_diff = diff_li[1] 

    maximum = max(float(diff_li[0]['ta'].max()), float(diff_li[1]['ta'].max()))
    minimum = max(float(diff_li[0]['ta'].min()), float(diff_li[1]['ta'].min()))
    print(f'maximum difference: {maximum} \n minimum difference: {minimum}')

    data = (annual_model, annual_rean, annual_diff, seasonal_model, seasonal_rean, seasonal_diff)

    return data, maximum, minimum
    
def compare_rean(data, savename, time_range):

    annual_model, annual_rean, annual_diff, seasonal_model, seasonal_rean, seasonal_diff = data
    fig, axes = plt.subplots(nrows = 5, ncols = 3, figsize = (25, 20), 
                             sharex = True, sharey = False, layout = 'constrained')

    fig.suptitle(f'Zonal Mean Temperature \n in {time_range[0]}-{time_range[1]}', fontsize = 20)

    k = 0
    for name, annual, seasonal in [('JRA-55', annual_model, seasonal_model), ('MERRA2',annual_rean, seasonal_rean)]:
        # plot model
        boundaries = [180, 185, 190, 195, 200, 205, 210, 215, 220, 225, 230, 235, 240, 245, 250, 255, 260, 265, 270, 275, 280, 285, 290, 295, 300]
        cf = xr.plot.contourf(annual['ta'],
                x = 'lat',
                y = 'plev', 
                yincrease =  False,
                add_colorbar=True,
                cbar_kwargs= {'label':'Temperature, K', 'drawedges':True, 'ticks':boundaries},
                levels = boundaries,
                add_labels = False,
                cmap= cc.cm.rainbow4,
                extend="neither",
                yscale = 'log',
                ylim = (1000, 1),
                ax = axes[0,k])
        cs = xr.plot.contour(annual['ta'],
                x = 'lat',
                y = 'plev', 
                yincrease =  False,
                add_colorbar= False,
                add_labels = False,
                linewidths = 0.5,
                colors ="k",
                levels = boundaries,
                yscale = 'log',
                ylim = (1000, 1),
                xlim = (-89, 89),
                ax = axes[0,k])
        plt.clabel(cs, cs.levels, fontsize=10)
        annual.close()

        axes[0,k].set_ylabel('Pressure, hPa', fontsize = 15)
        axes[0,k].set_title(f'{name} \nAnnual', fontsize = 15)

        cbar = cf.colorbar  # Get the colorbar object
        cbar.ax.tick_params(length=0)
        #cbar.ax.set_ylabel('Temperature, K', fontsize=15) 

        for i, season in enumerate(("DJF", "MAM", "JJA", "SON")):
            cf = xr.plot.contourf(seasonal['ta'].sel(season=season), 
                x = 'lat',
                y = 'plev', 
                yincrease =  False,
                add_colorbar=True,
                cbar_kwargs= {'label':'Temperature, K', 'drawedges':True, 'ticks':boundaries},
                levels = boundaries,
                add_labels = False,
                cmap= cc.cm.rainbow4,
                extend="neither",
                yscale = 'log',
                ylim = (1000, 1),
                xlim = (-89, 89),
                ax = axes[i + 1,k])
            cs = xr.plot.contour(seasonal['ta'].sel(season = season),
                x = 'lat',
                y = 'plev', 
                yincrease =  False,
                add_colorbar= False,
                add_labels = False,
                linewidths = 0.5,
                colors ="k",
                levels = boundaries,
                yscale = 'log',
                ylim = (1000, 1),
                ax = axes[i + 1, k])
            plt.clabel(cs, cs.levels, fontsize=10)
            seasonal.close()

            axes[i+1, k].set_ylabel('Pressure, hPa', fontsize = 15)
            axes[i+1, k].set_title(season, fontsize = 15)

            cbar = cf.colorbar  # Get the colorbar object
            cbar.ax.tick_params(length=0)
            #cbar.ax.set_ylabel('Temperature, K', fontsize=12) 

        axes[4,k].set_xlabel('Latitude, °N', fontsize = 15)
        k+=1

    # plot difference
    boundaries = [-50,-30, -20,-18, -16,-14, -12, -10, -8, -6, -4, -2, -1, 1, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20,30, 50]
    cf = xr.plot.contourf(annual_diff['ta'],
            x = 'lat',
            y = 'plev', 
            yincrease =  False,
            add_colorbar=True,
            cbar_kwargs= {'label':'Temperature Difference, K', 'drawedges':True, 'ticks':boundaries},
            levels = boundaries,
            add_labels = False,
            cmap= cc.cm.CET_D9,
            extend="neither",
            yscale = 'log',
            ylim = (1000, 1),
            xlim = (-89, 89),
            ax = axes[0,k])
    cs = xr.plot.contour(annual_diff['ta'],
            x = 'lat',
            y = 'plev', 
            yincrease =  False,
            add_colorbar= False,
            add_labels = False,
            linewidths = 0.5,
            colors ="k",
            levels = boundaries,
            yscale = 'log',
            ylim = (1000, 1),
            xlim = (-89, 89),
            ax = axes[0,k])
    plt.clabel(cs, cs.levels, fontsize=10)
    annual_diff.close()
    axes[0,k].set_title('Difference \nAnnual', fontsize = 15)
    axes[0,k].set_ylabel('Pressure, hPa', fontsize = 15)


    cbar = cf.colorbar  # Get the colorbar object
    cbar.ax.tick_params(length=0)
    #cbar.ax.set_ylabel('Temperature Difference, K', fontsize=12) 

    for i, season in enumerate(("DJF", "MAM", "JJA", "SON")):
        cf = xr.plot.contourf(seasonal_diff['ta'].sel(season=season), 
            x = 'lat',
            y = 'plev', 
            yincrease =  False,
            add_colorbar=True,
            cbar_kwargs= {'label':'Temperature Difference, K', 'drawedges':True, 'ticks':boundaries},
            levels = boundaries,
            add_labels = False,
            cmap= cc.cm.CET_D9,
            extend="neither",
            yscale = 'log',
            ylim = (1000, 1),
            xlim = (-89, 89),
            ax = axes[i + 1,k])
        cs = xr.plot.contour(seasonal_diff['ta'].sel(season = season),
            x = 'lat',
            y = 'plev', 
            yincrease =  False,
            add_colorbar= False,
            add_labels = False,
            linewidths = 0.5,
            colors ="k",
            levels = boundaries,
            yscale = 'log',
            ylim = (1000, 1),
            xlim = (-89, 89),
            ax = axes[i + 1, k])
        plt.clabel(cs, cs.levels, fontsize=10)
        seasonal_diff.close()

        axes[i+1,k].set_title(season, fontsize = 15)
        axes[i+1,k].set_ylabel('Pressure, hPa', fontsize = 15)


        cbar = cf.colorbar  # Get the colorbar object
        cbar.ax.tick_params(length=0)
    axes[4,k].set_xlabel(f'Latitude, °N', fontsize = 15)

    print(f'saving to... {savename}')
    plt.savefig(savename, dpi = 400)
    plt.close()
    return

if __name__ == '__main__':
    start = datetime.now()
    model = 'JRA-55'
    time_range = ('1980','1999')
    data, maximum, minimum = load_reans(time_range)
    savename = f'/home/siw2111/cmip6_reanalyses_comp/model_plots/04-03-2025/{model}_plots_{time_range[0]}-{time_range[1]}_{maximum}{minimum}.png'
    compare_rean(data, savename, time_range)
        
    end = datetime.now()
        
    print(f'finished at {end}, runtime: {end - start}')