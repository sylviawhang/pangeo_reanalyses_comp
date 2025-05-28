import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
import cmasher as cmr
from datetime import datetime
from pangeo_pull import pangeo_pull
from ncf_funct import difference, find_trend
from dask.diagnostics import ProgressBar

# plots to compare model and reanalysis trends. As seen in Figures 58-95 of phonebook.

def seasonal_zonal_trend(xrds, lon, time, variable):
    print(f'finding seasonal trends...')
    xrds = xrds[[variable]]
    xrds = xrds.mean(dim = lon)
    seasonal_xrds = xrds.groupby(f"{time}.season").map(find_trend)    
    return seasonal_xrds

def annual_zonal_trend(xrds, lon, time, variable):
    print(f'finding annual trend...')
    xrds = xrds[[variable]]
    xrds = xrds.mean(dim = lon)
    xrds = find_trend(xrds)
    return xrds

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

    '''# load JRA-55 reanalysis
    rean_xrds = xr.open_dataset('/dx02/siw2111/JRA-55/JRA-55_T.nc', chunks = 'auto')
    rean_xrds = rean_xrds.rename({'g4_lat_2':'lat', 'g4_lon_3':'lon', 'lv_HYBL1':'plev', 'initial_time0_hours': 'time', 'TMP_GDS4_HYBL_S123':'ta'})
    model_lev = model_xrds['plev']
    rean_xrds = rean_xrds.interp(plev = model_lev)

    rean_xrds = rean_xrds.sel(plev = slice(1000,1))
    rean_xrds = rean_xrds.sortby('time')
    
    rean_xrds = rean_xrds.sel(time = time_slice)'''

    # load MERRA-2 reanalysis
    rean_xrds = xr.open_dataset('/dx02/siw2111/MERRA-2/MERRA-2_TEMP_ALL-TIME.nc4', chunks = 'auto')
    rean_xrds = rean_xrds.rename({'lat':'lat', 'lon':'lon', 'lev':'plev', 'time': 'time', 'T':'ta'})
    rean_xrds = rean_xrds.sel(plev = slice(1000,1))
    rean_xrds = rean_xrds.sortby('time')
    
    rean_xrds = rean_xrds.sel(time = time_slice)

    # group annually and seasonally
    annual_model = annual_zonal_trend(model_xrds, 'lon', 'time', 'ta')
    seasonal_model = seasonal_zonal_trend(model_xrds, 'lon', 'time', 'ta')

    annual_rean = annual_zonal_trend(rean_xrds, 'lon', 'time', 'ta')
    seasonal_rean = seasonal_zonal_trend(rean_xrds, 'lon', 'time', 'ta')

    print('computing difference...')
    xrds_li = [(annual_model, annual_rean), (seasonal_model, seasonal_rean)]
    diff_li = []

    for model, rean in xrds_li:
        diff = difference(model, rean)
        diff_li.append(diff)

    annual_diff = diff_li[0] 
    seasonal_diff = diff_li[1] 

    data = (source_id, annual_model, annual_rean, annual_diff, seasonal_model, seasonal_rean, seasonal_diff)

    return data
    
def plot_trend(data, savename, time_range):
    model, annual_model, annual_rean, annual_diff, seasonal_model, seasonal_rean, seasonal_diff = data
    fig, axes = plt.subplots(nrows = 5, ncols = 2, figsize = (18, 20), 
                             sharex = False, sharey = False, layout = 'constrained')

    fig.suptitle(f' {model} Temperature in {time_range[0]}-{time_range[1]}', fontsize = 20, fontweight = "medium")
    
    # plot model
    print('plotting trends...')
    print('annual model...')
    boundaries = [-5,-3.0, -2, -1.8,-1.6, -1.4, -1.2, -1, -0.8, -0.6, -0.4, -0.2, 0.2, 0.4, 0.6, 0.8, 1, 1.2, 1.4, 1.6, 1.8, 2.0, 3.0, 5]
    with ProgressBar():
        cf = xr.plot.contourf(annual_model['ta'],
                x = 'lat',
                y = 'plev', 
                yincrease =  False,
                add_colorbar=True,
                cbar_kwargs= {'drawedges':True, 'ticks':boundaries},
                levels = boundaries,
                add_labels = False,
                cmap= cmr.prinsenvlag_r,
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

    axes[0,0].set_ylabel('Pressure, hPa', fontsize = 15, fontweight = "medium")
    axes[0,0].set_title('Trend (Kelvin per decade) \nAnnual', fontsize = 15, fontweight = "medium")

    cbar = cf.colorbar  # Get the colorbar object
    cbar.ax.tick_params(length=0)

    for i, season in enumerate(("DJF", "MAM", "JJA", "SON")):
        print(f'{i}..............')
        cf = xr.plot.contourf(seasonal_model['ta'].sel(season=season), 
            x = 'lat',
            y = 'plev', 
            yincrease =  False,
            add_colorbar=True,
            cbar_kwargs= {'drawedges':True, 'ticks':boundaries},
            levels = boundaries,
            add_labels = False,
            cmap= cmr.prinsenvlag_r,
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
            #levels = 10,
            yscale = 'log',
            ylim = (1000, 1),
            xlim = (-89, 89),
            ax = axes[i + 1, 0])
        plt.clabel(cs, cs.levels, fontsize=10)
        seasonal_model.close()

        axes[i+1, 0].set_ylabel('Pressure, hPa', fontsize = 15, fontweight = "medium")
        axes[i+1, 0].set_title(season, fontsize = 15, fontweight = "medium")

        cbar = cf.colorbar  # Get the colorbar object
        cbar.ax.tick_params(length=0)

    axes[4,0].set_xlabel('Latitude, °N', fontsize = 15, fontweight = "medium")
    
    # plot difference
    print('plotting difference...')
    boundaries = [-5,-3.0, -2, -1.8,-1.6, -1.4, -1.2, -1, -0.8, -0.6, -0.4, -0.2, 0.2, 0.4, 0.6, 0.8, 1, 1.2, 1.4, 1.6, 1.8, 2.0, 3.0, 5]
    cf = xr.plot.contourf(annual_diff['ta'],
            x = 'lat',
            y = 'plev', 
            yincrease =  False,
            add_colorbar=True,
            cbar_kwargs= {'drawedges':True, 'ticks':boundaries},
            levels = boundaries,
            add_labels = False,
            cmap= cmr.prinsenvlag_r,
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
    axes[0,1].set_title('Difference from MERRA-2 \nAnnual', fontsize = 15, fontweight = "medium")

    cbar = cf.colorbar  # Get the colorbar object
    cbar.ax.tick_params(length=0)
    for i, season in enumerate(("DJF", "MAM", "JJA", "SON")):
        print(f'{i}.................')
        cf = xr.plot.contourf(seasonal_diff['ta'].sel(season=season), 
            x = 'lat',
            y = 'plev', 
            yincrease =  False,
            add_colorbar=True,
            cbar_kwargs= { 'drawedges':True, 'ticks':boundaries},
            levels = boundaries,
            add_labels = False,
            cmap= cmr.prinsenvlag_r,
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

        axes[i+1,1].set_title(season, fontsize = 15, fontweight = "medium")

        cbar = cf.colorbar  # Get the colorbar object
        cbar.ax.tick_params(length=0)
    axes[4,1].set_xlabel(f'Latitude, °N', fontsize = 15, fontweight = "medium")

    print(f'saving to... {savename}')
    plt.savefig(savename, dpi = 400)
    plt.close()

if __name__ == '__main__':
    lo_model_li = ['ACCESS-ESM1-5','BCC-CSM2-MR', 'CAMS-CSM1-0','CanESM5','CAS-ESM2-0','CESM2', 'CIESM','CMCC-CM2-SR5', 'CMCC-ESM2', 'EC-Earth3-Veg-LR','FGOALS-f3-L', 'FGOALS-g3',
'FIO-ESM-2-0', 'GFDL-CM4', 'GFDL-ESM4', 'INM-CM4-8', 'KIOST-ESM', 'MIROC-ES2L','NESM3', 'NorESM2-LM','NorESM2-MM ','TaiESM1' ]
    model_li = ['CESM2-WACCM', 'ACCESS-CM2', 'AWI-CM-1-1-MR' , 'GISS-E2-1-G', 'GISS-E2-1-H','IITM-ESM','MIROC6', 'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'E3SM-1-1', 'EC-Earth3','EC-Earth3-CC', 'EC-Earth3-Veg', 'INM-CM5-0', 'IPSL-CM6A-LR' , 'KACE-1-0-G']
    model_li = model_li + lo_model_li
    for model in model_li:
        for time_range in [('1980','2014')]:
            print(f'plotting... {model} -----------------------------------------------')
            try:
                start = datetime.now()

                data, maximum, minimum = load_models(model, '', time_range)
                savename = f'/home/siw2111/cmip6_reanalyses_comp/model_plots/05-21-2025/{model}_trend_{time_range[0]}-{time_range[1]}_MERRA2.png'
                plot_trend(data, savename, time_range)
                model.close()
                
                end = datetime.now()
                print(f'{model} finished at {end}, runtime: {end - start}')
            except:
                print(f'error: unable to plot {model}')
                continue
