import intake
import intake_esm
from intake import open_catalog
import xarray as xr
from matplotlib import pyplot as plt
import numpy as np
from reanalyses_plots import plot_zonal_means, seasonal_zonal_mean, annual_zonal_mean
from ncf_funct import sort_coordinate, interpolate, cdf_merge

'''cat = open_catalog("https://raw.githubusercontent.com/pangeo-data/pangeo-datastore/master/intake-catalogs/climate.yaml")
print(cat.walk(depth = 4))'''

def pangeo_pull(source_id, institution_id, variable_id = 'ta', experiment_id = 'historical', grid_label = 'gn', table_id = 'Amon'):
# Load the catalog
    url = 'https://storage.googleapis.com/cmip6/pangeo-cmip6.json'
    print(url)
    cat = intake.open_esm_datastore(url, progressbar = True) # cat = catalogue
    print(cat)
    print(cat.df.head())
    cat_subset = cat.search(
        experiment_id = experiment_id,
        variable_id = variable_id,
        grid_label = grid_label,
        table_id = table_id,
        source_id = source_id,
        institution_id = institution_id
    )
    print(cat_subset)
    print(cat_subset.df.head())
    unique = cat_subset.unique()
    print(unique) # prints unique parameters among the datasets
    print(unique['member_id'])
    print(unique['version'])

    # convert to dictionary of xarray datasets. 
    cat.esmcat.aggregation_control
    dset_dict = cat_subset.to_dataset_dict(
        xarray_open_kwargs={"consolidated": True, "decode_times": True, "use_cftime": True}
    )
    print(dset_dict)
    print(f' number of files: {len(dset_dict)}')
    
    name = f'CMIP.{institution_id}.{source_id}.{experiment_id}.{table_id}.{grid_label}'
    print(name)
    xrds = dset_dict[name]
    
    print(xrds)
    return(xrds)

# make a plot

# plot multiple pressure levels
def group_year(xrds, time, lat, lon, model = True): # pre-process data for each pressure level
    print('mean over year, latitude, longitude...')
    xrds = xrds.groupby(f'{time}.year').mean()
    xrds = xrds.mean(dim = [lon, lat])
    #xrds = xrds.drop_dims('dcpp_init_year') this is problematic -- drops dims and all variables associated with them i.e, temperature
    if model:
        xrds = xrds.sel(member_id = 'r10i1p1f1')
    xrds = xrds.sel(year = slice(1980,2024))
    print(xrds)
    return xrds

def trend_plot():
    cesm2 = pangeo_pull('CESM2', 'NCAR') # pull down from pangeo 
    plev = cesm2.coords['plev'].values
    cesm2 = cesm2.assign_coords(plev = np.divide(plev,100)) # convert from pa to hpa
    cesm2_10 = group_year(cesm2.sel(plev = 1e+01), time = 'time', lon = 'lon', lat = 'lat') # annual mean, mean over latitude, longitude
    xr.plot.line(cesm2_10['ta'], x = 'year', label = 'CESM2')
    cesm2.close()

    #era5 = xr.open_dataset('/dx02/siw2111/ERA-5/ERA-5_T.nc', chunks = 'auto')
    era5 = cdf_merge('/dx02/siw2111/ERA-5/unmerged/*.nc', concat_dim = 'valid_time', variable = 't')
    era5_10 = group_year(era5.sel(pressure_level = 1e+01), time = 'valid_time', lon = 'longitude', lat = 'latitude', model = False)
    print(era5_10.variables['t'].values)
    xr.plot.line(era5_10['t'], x = 'year', label = 'ERA5')
    era5.close()

    merra2 = xr.open_dataset('/dx02/siw2111/MERRA-2/MERRA-2_TEMP_ALL-TIME.nc4', chunks = 'auto')
    merra2 = sort_coordinate(merra2) # sort time
    merra2_10 = group_year(merra2.sel(lev = 1e+01), time = 'time', lon = 'lon', lat = 'lat', model = False)
    xr.plot.line(merra2_10['T'], x = 'year', label = 'MERRA2')
    merra2.close()

    jra55 = xr.open_dataset('/dx02/siw2111/JRA-55/JRA-55_T.nc', chunks = 'auto')
    jra55 = interpolate(jra55, era5)
    jra55_10 = group_year(jra55.sel(pressure_level = 1e+01), time = 'initial_time0_hours', lon = 'longitude', lat = 'latitude', model = False)
    xr.plot.line(jra55_10['TMP_GDS4_HYBL_S123'], x = 'year', label = 'JRA55')
    jra55.close()

    plt.title('Temperature as a function of time at 10hpa')
    plt.legend()
    plt.xlabel('time YYYY')
    plt.ylabel('temperature K')
    plt.xlim(1980,2014)
    savename = '/home/siw2111/model_plots/model_obs_comparison_1980-2014.png'
    print(f'saving to...{savename}')
    plt.savefig(savename)



'''plev = xrds.coords['plev'].values
xrds = xrds.assign_coords(plev  = np.divide(plev,100))

xrds1000 = group_year(xrds.sel(plev = 1e+03))
#xrds100 = group_year(xrds.sel(plev = 1e+02))
#xrds10 = group_year(xrds.sel(plev = 1e+01))
#xrds1 = group_year(xrds.sel(plev = 1e+00))

# plot single pressure level temperature versus time
xr.plot.line(xrds1000['ta'], x = 'year')
plt.title('CEMS2 Temperature as a function of time at 1000hPA')
plt.xlabel('time (YYYY)')
plt.ylabel('temperature (K)')
plt.savefig('/home/siw2111/model_plots/CEMS2_1000hpa.png')'''

# make a climatoligcal plot
'''xrds_zonal = xrds.sel(time = slice('2000-01-01', '2014-12-01'))
xrds_zonal = xrds_zonal.sel(member_id = 'r10i1p1f1')
plev = xrds_zonal.coords['plev'].values
xrds_zonal = xrds_zonal.assign_coords(plev  = np.divide(plev,100))
xrds_zonal = xrds_zonal.mean(dim = ['dcpp_init_year'])
print(xrds_zonal)
plot_zonal_means(xrds_zonal,
                  savename = '/home/siw2111/model_plots/CEMS2_climatology.png', 
                  lat = 'lat', 
                  lon = 'lon', 
                  lev = 'plev', 
                  time = 'time',
                variable = 'ta', 
                title = 'CESM2 Years 2000-2014')'''

if __name__ == '__main__':
    #pangeo_pull(source_id = 'CESM2', institution_id = 'NCAR')
    trend_plot()