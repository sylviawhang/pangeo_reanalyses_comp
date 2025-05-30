import intake
from intake import open_catalog
import xarray as xr
from matplotlib import pyplot as plt
import numpy as np
from reanalyses_plots import plot_annual
from ncf_funct import sort_coordinate, area_weighted_mean, concat_era
from matplotlib.ticker import MultipleLocator

# Sylvia Whang siw2111@barnard.edu, Spring 2025. 
# function pangeo_pull to access models from panGeo database -- made to access one dataset at a time. 
# trend_plot used to make time series of all models together as in Figs 6-17 of phonebook.

def pangeo_pull(source_id = 'GISS-E2-1G', institution_id = 'NASA-GISS', variable_id = 'ta', experiment_id = 'historical', grid_label = 'gn', table_id = 'Amon', dict = False):
# Load the catalog
    url = 'https://storage.googleapis.com/cmip6/pangeo-cmip6.json'
    #print(url)
    cat = intake.open_esm_datastore(url, progressbar = True) # cat = catalogue
    #print(cat)
    cat_subset = cat.search(
        experiment_id = experiment_id,
        variable_id = variable_id,
        #grid_label = grid_label,
        table_id = table_id,
        source_id = source_id,
        #institution_id = institution_id, 
        member_id = 'r1i1p1f1'
    )
    print(cat_subset)
    print(cat_subset.df.head())
    unique = cat_subset.unique()
    print(unique) # prints unique parameters among the datasets
    print(unique['source_id'])

    # convert to dictionary of xarray datasets. 
    cat.esmcat.aggregation_control
    dset_dict = cat_subset.to_dataset_dict(
        xarray_open_kwargs={"consolidated": True, "decode_times": True, "use_cftime": True}
    )
    print(dset_dict)
    print(f' number of files: {len(dset_dict)}')
    
    if dict:
        return dset_dict
        
    name = list(dset_dict.keys())[0]
    xrds = dset_dict[name]

    return(xrds)

# make a plot
def group_year(xrds, time, lat, lon, model = True): # pre-process data for each pressure level
    xrds = xrds.groupby(f'{time}.year').mean()
    xrds = area_weighted_mean(xrds, lat, lon)
    if model:
        xrds = xrds.sel(member_id = 'r1i1p1f1')
    return xrds

def line_plot():
    model = pangeo_pull('GISS-E2-1-G')
    plev = model.coords['plev'].values
    model = model.assign_coords(plev = np.divide(plev,100).round(1)) # convert from pa to hpa
    
    model = model.sel(time = slice('1980-01-01', '2014-01-12'))
    model.coords['time'] = model.coords['time'].to_index()
    
    model = area_weighted_mean(model, 'lat', 'lon')
    model = model.sel(plev = 1e+01)
    model = model.sel(member_id  = 'r1i1p1f1')

    print(model)
    xr.plot.line(model['ta'], x = 'time', color = 'b', label = 'GISS-E2-1-G monthly mean' , zorder = 5)

    merra2 = xr.open_dataset('/dx02/siw2111/MERRA-2/MERRA-2_TEMP_ALL-TIME.nc4', chunks = 'auto')
    merra2 = sort_coordinate(merra2) # sort time    
    merra2 = area_weighted_mean(merra2, 'lat', 'lon')
    merra2 = merra2.sel(lev =1e+01)
    merra2 - merra2.sel(time = slice('1980-01-01', '2014-01-12'))
    merra2.coords['time'] = merra2.coords['time'].to_index()

    print(merra2)
    xr.plot.line(merra2['T'], x = 'time', label = 'MERRA2 monthly mean', color = 'lightsteelblue', zorder = 0)

    merra2.close()
    plt.yticks(np.arange(228, 231, 0.5))
    plt.title('Temperature as a Function of Time')
    plt.legend()
    plt.savefig('/home/siw2111/cmip6_reanalyses_comp/model_plots/04-03-2025/GISS_MERRA_line.png')


def trend_plot(level, savename):
    # set color map
    fig = plt.figure(figsize = (7,5))
    ax = fig.add_subplot()
    '''number_models = 20
    colormap = plt.cm.nipy_spectral
    colors = colormap(np.linspace(0, 1, number_models))
    ax.set_prop_cycle('color', colors)'''
    
    hi_model_li = ['EC-Earth3',
                    'EC-Earth3-CC',  
                    'EC-EARTH3-Veg',
                    'E3SM-1-1', 
                    'MRI-ESM2-0',
                    'IPSL-CM6A-LR',
                    'GISS-E2-1-H', 
                    'GISS-E2-1-G',
                    'INM-CM5-0',
                    'CESM2-WACCM', 
                    'MPI-ESM1-2-HR', 
                    'MPI-ESM1-2-LR',
                    'IITM-ESM',
                    'AWI-CM-1-1-MR', 
                    'ACCESS-CM2',
                    'KACE-1-0-G', 
                    'MIROC6'] 
         
    lo_model_li = ['ACCESS-ESM1-5',
                'BCC-CSM2-MR', 
                'CAMS-CSM1-0',
                'CanESM5',
                'CAS-ESM2-0',
                'CESM2',
                'CIESM',
                'CMCC-CM2-SR5', 
                'CMCC-ESM2',
                'EC-Earth3-Veg-LR',
                'FGOALS-f3-L',
                'FGOALS-g3', 
                'FIO-ESM-2-0',
                'GFDL-CM4',
                'GFDL-ESM4', 
                'INM-CM4-8',
                'KIOST-ESM',
                'MIROC-ES2L',
                'NESM3',
                'NorESM2-LM',
                'NorESM2-MM',
                'TaiESM1']
    i = 0
    for id in lo_model_li:
        try:
            print(f'plotting {id}----------------------------------')
            model = pangeo_pull(id, '')
            plev = model.coords['plev'].values
            model = model.assign_coords(plev = np.divide(plev,100).round(1)) # convert from pa to hpa
                        
            model_10 = group_year(model.sel(plev = level), time = 'time', lon = 'lon', lat = 'lat') # annual mean, mean over latitude, longitude
            
            if i == 0:
                ax.plot(model_10['year'], model_10['ta'], label = 'low-top', linewidth = 0.75, color = 'b', zorder = 5, linestyle = 'dotted')
                model.close()
            else: 
                ax.plot(model_10['year'], model_10['ta'], linewidth = 0.75, color = 'b', linestyle = 'dotted')
        
        except:
            print(f'error: unable to plot {id}')
            continue
        i+= 1
    
    i = 0
    for id in hi_model_li:
        try: 
            print(f'plotting {id}----------------------------------')
            model = pangeo_pull(id, '')
            plev = model.coords['plev'].values
            model = model.assign_coords(plev = np.divide(plev,100).round(1)) # convert from pa to hpa
            
            model_10 = group_year(model.sel(plev = level), time = 'time', lon = 'lon', lat = 'lat') # annual mean, mean over latitude, longitude
            if i == 0:
                ax.plot(model_10['year'], model_10['ta'], label = 'high-top', linewidth = 0.75, color = 'r', zorder = 1)
                model.close()
            else: 
                ax.plot(model_10['year'], model_10['ta'], linewidth = 0.75, color = 'r')
        except:
            print(f'error: unable to plot {id}')
            continue
        i+=1

    era5 = concat_era()
    era5_10 = group_year(era5.sel(pressure_level = level), time = 'valid_time', lon = 'longitude', lat = 'latitude', model = False)
    xr.plot.line(era5_10['t'], x = 'year', label = 'reanalysis', color = 'k', linewidth = 0.75, zorder = 10)
    era5.close()

    merra2 = xr.open_dataset('/dx02/siw2111/MERRA-2/MERRA-2_TEMP_ALL-TIME.nc4', chunks = 'auto')
    merra2 = sort_coordinate(merra2) # sort time
    merra2_10 = group_year(merra2.sel(lev = level), time = 'time', lon = 'lon', lat = 'lat', model = False)
    xr.plot.line(merra2_10['T'], x = 'year', color = 'k', linewidth = 0.75)
    merra2.close()

    jra55 = xr.open_dataset('/dx02/siw2111/JRA-55/JRA-55_T_interpolated.nc', chunks = 'auto')
    jra55_10 = group_year(jra55.sel(pressure_level = level), time = 'initial_time0_hours', lon = 'longitude', lat = 'latitude', model = False)
    xr.plot.line(jra55_10['TMP_GDS4_HYBL_S123'], x = 'year', color = 'k', linewidth = 0.75)
    jra55.close()

    plt.title(f'Temperature as a Function of Time at {level} hpa ')
   
    plt.xlabel('time YYYY')
    plt.xlim(1980,2014)

    ax.set_ylabel('temperature K')
    print(f'saving to...{savename}')
    
    fig.subplots_adjust(right=0.8) # 0.7 normally
    fig.legend(ncols = 1, fontsize = 'small', loc = 7)
    ax.yaxis.set_major_locator(MultipleLocator(5))  # Tick every 5 on y-axis
    ax.yaxis.set_minor_locator(MultipleLocator(1))  # Tick every 5 on y-axis
    ax.yaxis.set_ticks_position('both')  

    plt.savefig(savename, dpi = 300)

    plt.close()


# make a climatoligcal plot
def plot_climatology(xrds, savename):
    xrds_zonal = xrds.sel(time = slice('1980-01-01', '2014-12-01'))
    xrds_zonal = xrds_zonal.sel(member_id = 'r1i1p1f1')
    plev = xrds_zonal.coords['plev'].values
    xrds_zonal = xrds_zonal.assign_coords(plev  = np.divide(plev,100))
    xrds_zonal = xrds_zonal.mean(dim = ['dcpp_init_year'])
    print(xrds_zonal)
    plot_annual(xrds_zonal,
                savename = savename, 
                lat = 'lat', 
                lon = 'lon', 
                lev = 'plev', 
                time = 'time',
                variable = 'ta')

if __name__ == '__main__':
    trend_plot(10, '/home/siw2111/cmip6_reanalyses_comp/model_plots/05-22-2025/10_line_1980-2014.png')





