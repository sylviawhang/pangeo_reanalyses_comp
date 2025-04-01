import intake
import intake_esm
from intake import open_catalog
import xarray as xr
from matplotlib import pyplot as plt
import numpy as np
from reanalyses_plots import plot_annual
from ncf_funct import sort_coordinate, interpolate, cdf_merge, area_weighted_mean, concat_era
import statistics

'''cat = open_catalog("https://raw.githubusercontent.com/pangeo-data/pangeo-datastore/master/intake-catalogs/climate.yaml")
print(cat.walk(depth = 4))'''

def pangeo_pull(source_id = 'GISS-E2-1G', institution_id = 'NASA-GISS', variable_id = 'ta', experiment_id = 'historical', grid_label = 'gn', table_id = 'Amon', dict = False):
# Load the catalog
    url = 'https://storage.googleapis.com/cmip6/pangeo-cmip6.json'
    print(url)
    cat = intake.open_esm_datastore(url, progressbar = True) # cat = catalogue
    print(cat)
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
    
    #name = f'CMIP.{institution_id}.{source_id}.{experiment_id}.{table_id}.{grid_label}'
    
    name = list(dset_dict.keys())[0]
    print(name)
    xrds = dset_dict[name]

    print(xrds)
    return(xrds)

# make a plot
def group_year(xrds, time, lat, lon, model = True): # pre-process data for each pressure level
    print('mean over year, latitude, longitude...')
    xrds = xrds.groupby(f'{time}.year').mean()
    xrds = area_weighted_mean(xrds, lat, lon)
    if model:
        xrds = xrds.sel(member_id = 'r1i1p1f1')
    #xrds = xrds.sel(year = slice(1980,2014))
    print(xrds)
    return xrds

def trend_plot_2():
    # get models (start with 10)
    model_dict = pangeo_pull( variable_id = 'ta', experiment_id = 'historical', grid_label = 'gn', table_id = 'Amon', dict = True)
    i = 0
    for key, xrds in model_dict.items():
        if i >10:
            break
        print('----------------------')
        print(key)
        name = key.split('.')[2]
        print(f'label: {name}')
        plev = xrds.coords['plev'].values
        xrds = xrds.assign_coords(plev = np.divide(plev,100)) # convert from pa to hpa
        print(f'pressure levels: {len(plev)}')
        
        top = xrds.coords['plev'].values[-1]
        print(f'model top: {top}')
        
        xrds_10 = group_year(xrds.sel(plev = 1e+01), time = 'time', lon = 'lon', lat = 'lat', model = True)
        xr.plot.line(xrds_10['ta'], x = 'year', label = name)
        i +=1

    merra2 = xr.open_dataset('/dx02/siw2111/MERRA-2/MERRA-2_TEMP_ALL-TIME.nc4', chunks = 'auto')
    merra2 = sort_coordinate(merra2) # sort time
    merra2_10 = group_year(merra2.sel(lev = 1e+01), time = 'time', lon = 'lon', lat = 'lat', model = False)
    xr.plot.line(merra2_10['T'], x = 'year', label = 'MERRA2', color = 'darkblue')
    merra2.close()

    plt.title('Temperature as a Function of Time at 10hpa')
    plt.legend()
    plt.xlabel('time YYYY')
    plt.ylabel('temperature K')
    plt.xlim(1850,2014)
    savename = '/home/siw2111/cmip6_reanalyses_comp/model_plots/03-03-2025/40model_3obs_1850-2014_.png'
    print(f'saving to...{savename}')
    plt.savefig(savename, dpi = 300)

def trend_plot():
    # set color map
    fig = plt.figure()
    ax = fig.add_subplot()
    number_models = 17
    colormap = plt.cm.nipy_spectral
    colors = colormap(np.linspace(0, 1, number_models))
    ax.set_prop_cycle('color', colors) 
    
    #models
    model_li = ['ACCESS-CM2', 'AWI-CM-1-1-MR' , 'CESM2-WACCM', 'GISS-E2-1-G', 'GISS-E2-1-H','IITM-ESM','MIROC6', 'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'E3SM-1-1', 'EC-Earth3','EC-Earth3-CC', 'EC-Earth3-Veg', 'INM-CM5-0', 'IPSL-CM6A-LR' , 'KACE-1-0-G']
    for id in model_li:
        print(f'plotting {id}----------------------------------')
        model = pangeo_pull(id, '')
        plev = model.coords['plev'].values
        model = model.assign_coords(plev = np.divide(plev,100).round(1)) # convert from pa to hpa
        model_10 = group_year(model.sel(plev = 1e+03), time = 'time', lon = 'lon', lat = 'lat') # annual mean, mean over latitude, longitude
        ax.plot(model_10['year'], model_10['ta'], label = id, linewidth = 0.7)
        model.close()

    era5 = concat_era()
    era5_10 = group_year(era5.sel(pressure_level = 1e+03), time = 'valid_time', lon = 'longitude', lat = 'latitude', model = False)
    print(era5_10.variables['t'].values)
    xr.plot.line(era5_10['t'], x = 'year', label = 'ERA5.1', color = 'lightgray', linewidth = 0.7)
    era5.close()

    merra2 = xr.open_dataset('/dx02/siw2111/MERRA-2/MERRA-2_TEMP_ALL-TIME.nc4', chunks = 'auto')
    merra2 = sort_coordinate(merra2) # sort time
    merra2_10 = group_year(merra2.sel(lev = 1e+03), time = 'time', lon = 'lon', lat = 'lat', model = False)
    xr.plot.line(merra2_10['T'], x = 'year', label = 'MERRA2', color = 'k', linewidth = 0.7)
    merra2.close()

    jra55 = xr.open_dataset('/dx02/siw2111/JRA-55/JRA-55_T_interpolated.nc', chunks = 'auto')
    jra55_10 = group_year(jra55.sel(pressure_level = 1e+03), time = 'initial_time0_hours', lon = 'longitude', lat = 'latitude', model = False)
    xr.plot.line(jra55_10['TMP_GDS4_HYBL_S123'], x = 'year', label = 'JRA55', color = 'grey', linewidth = 0.7)
    jra55.close()

    plt.title('Temperature as a Function of Time at 1000hpa')
    plt.legend()
    plt.xlabel('time YYYY')
    plt.ylabel('temperature K')
    plt.xlim(1850,2014)
    savename = '/home/siw2111/cmip6_reanalyses_comp/model_plots/03-20-2025/temp-time_1000_1850-2014.png'
    print(f'saving to...{savename}')
    plt.savefig(savename, dpi = 300)

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
    trend_plot()
    #savename = '/home/siw2111/cmip6_reanalyses_comp/model_plots/03-20-2025/GISS-E2-1-G_climatology_1980-2014_1.png'
    #plot_climatology(xrds, savename)




