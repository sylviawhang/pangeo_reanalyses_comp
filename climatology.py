import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
import colorcet as cc
from datetime import datetime
from reanalyses_plots import annual_zonal_mean_detrended, seasonal_zonal_mean_detrended
from pangeo_pull import pangeo_pull
from ncf_funct import detrend_fct, difference


# plots to compare model and reanalysis climatology

def load_models(source_id, institution_id, time_range:tuple):
    # load model
    time_slice = slice(f'{time_range[0]}-01-01', f'{time_range[1]}-12-01')

    model_xrds = pangeo_pull(source_id, institution_id)

    model_xrds =model_xrds.sel(time = time_slice)

    model_xrds = model_xrds.sel(member_id = 'r1i1p1f1')
    plev = model_xrds.coords['plev'].values
    model_xrds = model_xrds.assign_coords(plev  = np.divide(plev,100).round(2))
    model_xrds = model_xrds.sel(plev = slice(1000,1))
    model_xrds = model_xrds.mean(dim = ['dcpp_init_year'])

    # load reanalysis
    rean_xrds = xr.open_dataset('/dx02/siw2111/MERRA-2/MERRA-2_TEMP_ALL-TIME.nc4', chunks = 'auto')
    rean_xrds = rean_xrds.rename({'lat':'lat', 'lon':'lon', 'lev':'plev', 'time': 'time', 'T':'ta'})
    rean_xrds = rean_xrds.sel(plev = slice(1000,1))
    rean_xrds = rean_xrds.sortby('time')
    
    rean_xrds = rean_xrds.sel(time = time_slice)

    annual_model = annual_zonal_mean_detrended(model_xrds, 'lon', 'time', 'ta')
    seasonal_model = seasonal_zonal_mean_detrended(model_xrds, 'lon', 'time', 'ta')

    annual_rean = annual_zonal_mean_detrended(rean_xrds, 'lon', 'time', 'ta')
    seasonal_rean = seasonal_zonal_mean_detrended(rean_xrds, 'lon', 'time', 'ta')

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

    data = (source_id, annual_model, annual_rean, annual_diff, seasonal_model, seasonal_rean, seasonal_diff)

    return data, maximum, minimum
    
def plot_clim(data, savename, time_range):
    model, annual_model, annual_rean, annual_diff, seasonal_model, seasonal_rean, seasonal_diff = data
    fig, axes = plt.subplots(nrows = 5, ncols = 2, figsize = (18, 20), 
                             sharex = True, sharey = False, layout = 'constrained')

    fig.suptitle(f' {model} Temperature \n in {time_range[0]}-{time_range[1]}', fontsize = 20)
    
    # plot model
    boundaries = [175, 180, 185, 190, 195, 200, 205, 210, 215, 220, 225, 230, 235, 240, 245, 250, 255, 260, 265, 270, 275, 280, 285, 290, 295, 300]
    cf = xr.plot.contourf(annual_model['ta'],
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
            xlim = (-89, 89),
            ax = axes[0,0])
    plt.clabel(cs, cs.levels, fontsize=10)
    annual_model.close()

    axes[0,0].set_ylabel('Pressure, hPa', fontsize = 15)
    axes[0,0].set_title('Zonal Mean Temperature \nAnnual', fontsize = 15)

    cbar = cf.colorbar  # Get the colorbar object
    cbar.ax.tick_params(length=0)
    cbar.ax.set_ylabel('Temperature, K', fontsize=15) 

    for i, season in enumerate(("DJF", "MAM", "JJA", "SON")):
        cf = xr.plot.contourf(seasonal_model['ta'].sel(season=season), 
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
            xlim = (-89, 89),
            ax = axes[i + 1, 0])
        plt.clabel(cs, cs.levels, fontsize=10)
        seasonal_model.close()

        axes[i+1, 0].set_ylabel('Pressure, hPa', fontsize = 15)
        axes[i+1, 0].set_title(season, fontsize = 15)

        cbar = cf.colorbar  # Get the colorbar object
        cbar.ax.tick_params(length=0)
        cbar.ax.set_ylabel('Temperature, K', fontsize=12) 

    axes[4,0].set_xlabel('Latitude, °N', fontsize = 15)
    
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
            ax = axes[0,1])
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
            ax = axes[0,1])
    plt.clabel(cs, cs.levels, fontsize=10)
    annual_diff.close()
    axes[0,1].set_title('Difference in Mean \nAnnual', fontsize = 15)
    #axes[0,1].set_ylabel('Pressure, hPa', fontsize = 15)


    cbar = cf.colorbar  # Get the colorbar object
    cbar.ax.tick_params(length=0)
    cbar.ax.set_ylabel('Temperature Difference, K', fontsize=15) 

    for i, season in enumerate(("DJF", "MAM", "JJA", "SON")):
        cf = xr.plot.contourf(seasonal_diff['ta'].sel(season=season), 
            x = 'lat',
            y = 'plev', 
            yincrease =  False,
            add_colorbar=True,
            cbar_kwargs= {'label':'K', 'drawedges':True, 'ticks':boundaries},
            levels = boundaries,
            add_labels = False,
            cmap= cc.cm.CET_D9,
            extend="neither",
            yscale = 'log',
            ylim = (1000, 1),
            xlim = (-89, 89),
            ax = axes[i + 1,1])
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
            ax = axes[i + 1, 1])
        plt.clabel(cs, cs.levels, fontsize=10)
        seasonal_diff.close()

        axes[i+1,1].set_title(season, fontsize = 15)
        #axes[i+1,1].set_ylabel('Pressure, hPa', fontsize = 15)


        cbar = cf.colorbar  # Get the colorbar object
        cbar.ax.tick_params(length=0)
        cbar.ax.set_ylabel('K', fontsize=15) 
    axes[4,1].set_xlabel(f'Latitude, °N', fontsize = 15)

    print(f'saving to... {savename}')
    plt.savefig(savename, dpi = 400)
    plt.close()

if __name__ == '__main__':
    #model_li = ['CESM2-WACCM', 'ACCESS-CM2', 'AWI-CM-1-1-MR' , 'GISS-E2-1-G', 'GISS-E2-1-H','IITM-ESM','MIROC6', 'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'E3SM-1-1', 'EC-Earth3','EC-Earth3-CC', 'EC-Earth3-Veg', 'INM-CM5-0', 'IPSL-CM6A-LR' , 'KACE-1-0-G']
    
         
    model_li = ['ACCESS-ESM1-5','BCC-CSM2-MR', 'CAMS-CSM1-0','CanESM5','CAS-ESM2-0','CESM2', 'CIESM','CMCC-CM2-SR5', 'CMCC-ESM2', 'EC-Earth3-Veg-LR','FGOALS-f3-L', 'FGOALS-g3',
                'FIO-ESM-2-0', 'GFDL-CM4', 'GFDL-ESM4', 'INM-CM4-8', 'KIOST-ESM', 'MIROC-ES2L','NESM3', 'NorESM2-LM','NorESM2-MM ','TaiESM1' ]
    
    for model in model_li:
        for time_range in [('1980','2014')]:
            print(f'plotting... {model} -----------------------------------------------')
            try:
                start = datetime.now()

                data, maximum, minimum = load_models(model, '', time_range)
                savename = f'/home/siw2111/cmip6_reanalyses_comp/model_plots/04-20-2025/{model}_zonal-mean_{time_range[0]}-{time_range[1]}_{maximum}{minimum}.png'
                plot_clim(data, savename, time_range)
                model.close()
                end = datetime.now()
                print(f'{model} finished at {end}, runtime: {end - start}')
            except:
                print(f'error: unable to plot {model}')
                continue
    
    
    '''start = datetime.now()
    
    model = 'CESM2-WACCM'
    institution = ''
    time_range = ('1980', '2014')
    data, maximum, minimum = load_models(model, institution, time_range)
    savename = f'/home/siw2111/cmip6_reanalyses_comp/model_plots/04-10-2025/{model}_plots_{time_range[0]}-{time_range[1]}_{maximum}{minimum}.png'
    plot_clim(data, savename, time_range)
    
    end = datetime.now()
    print(f'finished at {end}, runtime: {end - start}')'''

