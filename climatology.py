import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
from ncf_funct import cdf_merge, replace_coordinate
import colorcet as cc
from reanalyses_plots import annual_zonal_mean, seasonal_zonal_mean, plot_annual
from pangeo_pull import pangeo_pull
from datetime import datetime


# plots to compare model and reanalysis climatology

def load_models(source_id, institution_id):
    # load model
    model_xrds = pangeo_pull(source_id, institution_id)

    model_xrds =model_xrds.sel(time = slice('1980-01-01', '2014-12-01'))
    model_xrds = model_xrds.sel(member_id = 'r1i1p1f1')
    plev = model_xrds.coords['plev'].values
    model_xrds = model_xrds.assign_coords(plev  = np.divide(plev,100))
    model_xrds = model_xrds.sel(plev = slice(1000,1))
    model_xrds = model_xrds.mean(dim = ['dcpp_init_year'])

    annual_model = annual_zonal_mean(model_xrds, 'lon', 'time', 'ta')
    seasonal_model = seasonal_zonal_mean(model_xrds, 'lon', 'time', 'ta')

    # load reanalysis
    rean_xrds = xr.open_dataset('/dx02/siw2111/MERRA-2/MERRA-2_TEMP_ALL-TIME.nc4', chunks = 'auto')

    rean_xrds = rean_xrds.rename({'lat':'lat', 'lon':'lon', 'lev':'plev', 'time': 'time', 'T':'ta'})
    rean_xrds = rean_xrds.sortby('time')
    rean_xrds = rean_xrds.sel(time = slice('1980-01-01', '2014-12-01'))
    rean_xrds = rean_xrds.sel(plev = slice(1000,1))

    annual_rean = annual_zonal_mean(rean_xrds, 'lon', 'time', 'ta')
    seasonal_rean = seasonal_zonal_mean(rean_xrds, 'lon', 'time', 'ta')

    # select common pressure levels
    common_plev = np.intersect1d(annual_rean['plev'], annual_model['plev'])
    annual_rean = annual_rean.sel(plev = common_plev)
    annual_model = annual_model.sel(plev = common_plev)
    seasonal_rean = seasonal_rean.sel(plev = common_plev)
    seasonal_model = seasonal_model.sel(plev = common_plev)


    # interpolate to common latitude grid
    model_lat = annual_model['lat']
    annual_rean = annual_rean.interp(lat = model_lat)
    seasonal_rean = seasonal_rean.interp(lat = model_lat)

    annual_diff = annual_model - annual_rean
    seasonal_diff = seasonal_model - seasonal_rean

    maximum = max(float(annual_diff['ta'].max()), float(seasonal_diff['ta'].max()))
    minimum = max(float(annual_diff['ta'].min()), float(seasonal_diff['ta'].min()))
    
    print(f'maximum difference: {maximum} \n minimum difference: {minimum}')

    data = (source_id, annual_model, annual_rean, annual_diff, seasonal_model, seasonal_rean, seasonal_diff)

    return data

def plot_clim(data, savename):
    model, annual_model, annual_rean, annual_diff, seasonal_model, seasonal_rean, seasonal_diff = data
    fig, axes = plt.subplots(nrows = 5, ncols = 3, figsize = (25, 20), 
                             sharex = True, sharey = False, layout = 'constrained')

    fig.suptitle(f' {model} Zonal Mean Temperature in 1980-2024', fontsize = 20)
    
    # plot model
    boundaries = [180, 185, 190, 195, 200, 205, 210, 215, 220, 225, 230, 235, 240, 245, 250, 255, 260, 265, 270, 275, 280, 285, 290, 295, 300]
    cf = xr.plot.contourf(annual_model['ta'],
            x = 'lat',
            y = 'plev', 
            yincrease =  False,
            add_colorbar=False,
            #cbar_kwargs= {'label':'Temperature, K', 'drawedges':True, 'ticks':boundaries},
            levels = boundaries,
            add_labels = False,
            cmap= cc.cm.CET_L20,
            extend="neither",
            yscale = 'log',
            ylim = (1000, 1),
            ax = axes[0,0])
    cs = xr.plot.contour(annual_model['ta'],
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
            ax = axes[0,0])
    plt.clabel(cs, cs.levels, fontsize=10)
    annual_model.close()

    axes[0,0].set_ylabel('Pressure, hPa', fontsize = 15)
    axes[0,0].set_title(f'{model} \nAnnual', fontsize = 15)

    #cbar = cf.colorbar  # Get the colorbar object
    #cbar.ax.tick_params(length=0)
    #cbar.ax.set_ylabel('Temperature, K', fontsize=12) 

    for i, season in enumerate(("DJF", "MAM", "JJA", "SON")):
        cf = xr.plot.contourf(seasonal_model['ta'].sel(season=season), 
            x = 'lat',
            y = 'plev', 
            yincrease =  False,
            add_colorbar=False,
            #cbar_kwargs= {'label':'Temperature, K', 'drawedges':True, 'ticks':boundaries},
            levels = boundaries,
            add_labels = False,
            cmap= cc.cm.CET_L20,
            extend="neither",
            yscale = 'log',
            ylim = (1000, 1),
            ax = axes[i + 1,0])
        cs = xr.plot.contour(seasonal_model['ta'].sel(season = season),
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
            ax = axes[i + 1, 0])
        plt.clabel(cs, cs.levels, fontsize=10)
        seasonal_model.close()

        axes[i+1, 0].set_ylabel('Pressure, hPa', fontsize = 15)
        axes[i+1, 0].set_title(season, fontsize = 15)

        #cbar = cf.colorbar  # Get the colorbar object
        #cbar.ax.tick_params(length=0)
        #cbar.ax.set_ylabel('Temperature, K', fontsize=12) 

    axes[4,0].set_xlabel('Latitude, °N', fontsize = 15)
    # plot reanalysis (MERRA2)
    cf = xr.plot.contourf(annual_rean['ta'],
            x = 'lat',
            y = 'plev', 
            yincrease =  False,
            add_colorbar=True,
            cbar_kwargs= {'label':'Temperature, K', 'drawedges':True, 'ticks':boundaries},
            levels = boundaries,
            add_labels = False,
            cmap= cc.cm.CET_L20,
            extend="neither",
            yscale = 'log',
            ylim = (1000, 1),
            ax = axes[0,1])
    cs = xr.plot.contour(annual_rean['ta'],
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
            ax = axes[0,1])
    plt.clabel(cs, cs.levels, fontsize=10)
    annual_rean.close()

    axes[0,1].set_title('MERRA-2 \nAnnual', fontsize = 15)

    cbar = cf.colorbar  # Get the colorbar object
    cbar.ax.tick_params(length=0)
    cbar.ax.set_ylabel('Temperature, K', fontsize=12) 

    for i, season in enumerate(("DJF", "MAM", "JJA", "SON")):
        cf = xr.plot.contourf(seasonal_rean['ta'].sel(season=season), 
            x = 'lat',
            y = 'plev', 
            yincrease =  False,
            add_colorbar=True,
            cbar_kwargs= {'label':'Temperature, K', 'drawedges':True, 'ticks':boundaries},
            levels = boundaries,
            add_labels = False,
            cmap= cc.cm.CET_L20,
            extend="neither",
            yscale = 'log',
            ylim = (1000, 1),
            ax = axes[i + 1,1])
        cs = xr.plot.contour(seasonal_rean['ta'].sel(season = season),
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
            ax = axes[i + 1, 1])
        plt.clabel(cs, cs.levels, fontsize=10)
        seasonal_rean.close()

        axes[i+1,1].set_title(season, fontsize = 15)

        cbar = cf.colorbar  # Get the colorbar object
        cbar.ax.tick_params(length=0)
        cbar.ax.set_ylabel('Temperature, K', fontsize=12) 

    axes[4,1].set_xlabel(f'Latitude, °N', fontsize = 15)

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
            ax = axes[0,2])
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
            ax = axes[0,2])
    plt.clabel(cs, cs.levels, fontsize=10)
    annual_diff.close()
    axes[0,2].set_title('Difference \nAnnual', fontsize = 15)

    cbar = cf.colorbar  # Get the colorbar object
    cbar.ax.tick_params(length=0)
    cbar.ax.set_ylabel('Temperature Difference, K', fontsize=12) 

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
            ax = axes[i + 1,2])
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
            ax = axes[i + 1, 2])
        plt.clabel(cs, cs.levels, fontsize=10)
        seasonal_diff.close()

        axes[i+1,2].set_title(season, fontsize = 15)

        cbar = cf.colorbar  # Get the colorbar object
        cbar.ax.tick_params(length=0)
        cbar.ax.set_ylabel('Temperature Difference, K', fontsize=12) 
    axes[4,2].set_xlabel(f'Latitude, °N', fontsize = 15)

    print(f'saving to... {savename}')
    plt.savefig(savename, dpi = 400)

if __name__ == '__main__':
    model_li = ['ACCESS-CM2', 'AWI-CM-1-1-MR' , 'CESM2-WACCM', 'GISS-E2-1-H','IITM-ESM','MIROC6', 'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0']
    
    for model in model_li:
        print(f'plotting... {model} -----------------------------------------------')
        try:
            start = datetime.now()
        
            model = 'GISS-E2-1-G'
            #institution = 'NASA-GISS'

            data = load_models(model, institution = '')
            savename = f'/home/siw2111/cmip6_reanalyses_comp/model_plots/03-20-2025/{model}_plots_1980-2014.png'
            plot_clim(data, savename)
        
            end = datetime.now()
            print(f'{model} finished at {end}, runtime: {end - start}')
        except:
            print(f'error: unable to plot {model}')
            continue
    
    
    '''start = datetime.now()
    
    model = 'GISS-E2-1-G'
    institution = 'NASA-GISS'

    data = load_models(model, institution)
    savename = '/home/siw2111/cmip6_reanalyses_comp/model_plots/03-20-2025/GISS-E2-1-G_plots_1980-2014_1.png'
    plot_clim(data, savename)
    
    end = datetime.now()
    print(f'finished at {end}, runtime: {end - start}')'''

