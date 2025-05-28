import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
from reanalyses_plots import seasonal_zonal_mean, seasonal_zonal_mean_detrended, annual_zonal_mean, annual_zonal_mean_detrended, annual_zonal_trend
from pangeo_pull import pangeo_pull
from ncf_funct import concat_era, area_weighted_mean_2
from matplotlib.ticker import MultipleLocator

# 5/26/2026 by Sylvia Whang siw2111@barnard.edu
# Summary Plots for model climatology and trends (see Figs 18, 19, 57 in phonebook). 

# first plot: Polar night (DJF 60-90) versus JJA (-60--90) in levels (500hPa, 1hPa). 
# second plot: Tropopause (200hPa, 10hPa) versus upper stratosphere (10hPa, 1hPa) in the tropics (-30 deg N, 30 deg N)
# high-top models in red, low-top models in blue, reanalyses in red. 

def poles(model):
 # extract poles
    model = model.sel(plev = slice(500,1))
    model = seasonal_zonal_mean_detrended(model, 'lon', 'time', 'ta')
    npole = model.sel(season = 'DJF', lat = slice(60, 90), plev = slice(800,1))
    npole = area_weighted_mean_2(npole, 'lat')
    npole = npole.mean(dim = 'plev').variables['ta'].values[0]
    print(f'npole: {npole}')
            
    spole = model.sel(season = 'JJA', lat = slice(-90, -60), plev = slice(800,1))
    spole = area_weighted_mean_2(spole, 'lat')
    spole = spole.mean(dim = 'plev').variables['ta'].values[0]
    print(f'spole: {spole}')

    return npole, spole

def poles_rean(model, detrend = True):
 # extract poles
    model = model.sel(plev = slice(500,1))
    if detrend:
        model = seasonal_zonal_mean_detrended(model, 'lon', 'time', 'ta')
    else:
        model = seasonal_zonal_mean(model, 'lon', 'time', 'ta')

    if model.lat[0] < model.lat[1]:
        npole = model.sel(season = 'DJF', lat = slice(60, 90), plev = slice(500,1))
        spole = model.sel(season = 'JJA', lat = slice(-90, -60), plev = slice(500,1))
    else:
        npole = model.sel(season = 'DJF', lat = slice(90, 60), plev = slice(500,1))
        spole = model.sel(season = 'JJA', lat = slice(-60, -90), plev = slice(500,1))

    npole = area_weighted_mean_2(npole, 'lat')
    npole = npole.mean(dim = 'plev').variables['ta'].values
    print(f'npole: {npole}')
            
    spole = area_weighted_mean_2(spole, 'lat')
    spole = spole.mean(dim = 'plev').variables['ta'].values
    print(f'spole: {spole}')

    return npole, spole

def summary_1(hi_model_li, lo_model_li, savename):
    fig = plt.figure(figsize = (7,5))
    ax = fig.add_subplot()

    # plot reanalyses

    merra2 = xr.open_dataset('/dx02/siw2111/MERRA-2/MERRA-2_TEMP_ALL-TIME.nc4', chunks = 'auto')
    merra2 = merra2.rename({'lat':'lat', 'lon':'lon', 'lev':'plev', 'time': 'time', 'T':'ta'})
    merra2 = merra2.sel(plev = slice(1000,1))
    merra2 = merra2.sortby('time')

    era5 = concat_era()
    era5 = era5.rename({'latitude':'lat', 'longitude':'lon', 'pressure_level':'plev', 'valid_time': 'time', 't':'ta'})

    jra55 = xr.open_dataset('/dx02/siw2111/JRA-55/JRA-55_T.nc', chunks = 'auto')
    jra55 = jra55.rename({'g4_lat_2':'lat', 'g4_lon_3':'lon', 'lv_HYBL1':'plev', 'initial_time0_hours': 'time', 'TMP_GDS4_HYBL_S123':'ta'})
    standard_lev = merra2['plev']
    jra55 = jra55.interp(plev = standard_lev)
    lat = jra55.coords['lat']
    jra55 = jra55.assign_coords(lat = lat.round(1)) # convert from pa to hpa
    
    rean_li = [era5, jra55, merra2]

    i = 0
    for rean in rean_li:
        print(rean)
        rean = rean.sel(time = slice('1980-01-01', '2014-01-12'))

        if i == 0:
            npole, spole = poles_rean(rean, detrend = False)
            ax.scatter(spole, npole, s = 35, c = 'k', marker = 'o', alpha = 0.5, label = 'reanalysis')
            print(f'plotted!')
        else:
            npole, spole = poles_rean(rean, detrend = True)
            ax.scatter(spole, npole, s = 35, c = 'k', marker = 'o', alpha = 0.5)
            print(f'plotted!')
        i +=1
        rean.close()

    # plot high-top models
    i = 0
    for id in hi_model_li:
        print(f'{id}')
        try: 
            model = pangeo_pull(id, '')
            model = model.sel(time = slice('1980-01-01', '2014-01-12'))
            plev = model.coords['plev'].values
            model = model.assign_coords(plev = np.divide(plev,100).round(1)) # convert from pa to hpa
            
            # extract poles
            npole, spole = poles(model)

            if i == 0:
                ax.scatter(spole, npole, s = 35, c = 'r', marker = 'o', alpha = 0.5, label = 'high-top')
            else: 
                ax.scatter(spole, npole, s = 35, c = 'r', marker = 'o', alpha = 0.5)
            i+=1
        except:
            print(f'unable to plot... {id}')
        
        model.close()

    # plot low-top models  
    i = 0
    for id in lo_model_li:
        print(f'{id}')
        try: 
            model = pangeo_pull(id, '')
            model = model.sel(time = slice('1980-01-01', '2014-01-12'))
            plev = model.coords['plev'].values
            model = model.assign_coords(plev = np.divide(plev,100).round(1)) # convert from pa to hpa
            
            # extract poles
            npole, spole = poles(model)

            if i == 0:
                ax.scatter(spole, npole, s = 35, c = 'b', marker = 'o', alpha = 0.5, label = 'low-top')
            else: 
                ax.scatter(spole, npole, s = 35, c = 'b', marker = 'o', alpha = 0.5)
            i+=1
        except:
            print(f'unable to plot... {id}')
        
        model.close()
          
    plt.title('CMIP6 Models Mean Temperature at the Poles')
    plt.xlabel('S Pole JJA')
    plt.ylabel('N Pole DJF')
    plt.legend()
    
    ax.yaxis.set_major_locator(MultipleLocator(2))  # Tick every 2 on y-axis
    ax.yaxis.set_minor_locator(MultipleLocator(1))  
    ax.xaxis.set_major_locator(MultipleLocator(2))  # Tick every 2 on x-axis
    ax.xaxis.set_minor_locator(MultipleLocator(1))  
    
    print(f'saving to...{savename}')
    plt.savefig(savename, dpi = 300)
    return

def tropics(model):
    model = model.sel(plev = slice(200,1))
    model = model.sel(lat = slice(-30,30))
    model = annual_zonal_mean_detrended(model, 'lon', 'time', 'ta')
    
    cold_point = model.sel(plev = slice(200,10))
    cold_point = area_weighted_mean_2(cold_point, 'lat')
    cold_point = cold_point.mean(dim = 'plev').variables['ta'].values[0]
    print(f'cold point: {cold_point}')
            
    upper_strat = model.sel(plev = slice(10,1))
    upper_strat = area_weighted_mean_2(upper_strat, 'lat')
    upper_strat = upper_strat.mean(dim = 'plev').variables['ta'].values[0]
    print(f'upper stratosphere: {upper_strat}')

    return cold_point, upper_strat

def tropics_rean(model, detrend = True):
    model = model.sel(plev = slice(200,1))
    if model.lat[0] < model.lat[1]:
        model = model.sel(lat = slice(-30,30))
    else: 
        model = model.sel(lat = slice(30, -30))
    
    if detrend:
        model = annual_zonal_mean_detrended(model, 'lon', 'time', 'ta')
    else: 
        model = annual_zonal_mean(model, 'lon', 'time', 'ta')
    
    cold_point = model.sel(plev = slice(200,10))
    cold_point = area_weighted_mean_2(cold_point, 'lat')
    cold_point = cold_point.mean(dim = 'plev').variables['ta'].values
    print(f'cold point: {cold_point}')
            
    upper_strat = model.sel(plev = slice(10,1))
    upper_strat = area_weighted_mean_2(upper_strat, 'lat')
    upper_strat = upper_strat.mean(dim = 'plev').variables['ta'].values
    print(f'upper stratosphere: {upper_strat}')

    return cold_point, upper_strat

def summary_2(hi_model_li, lo_model_li, savename):
    fig = plt.figure(figsize = (7,5))
    ax = fig.add_subplot()

    # plot reanalyses
    '''era5 = concat_era()
    era5 = era5.rename({'latitude':'lat', 'longitude':'lon', 'pressure_level':'plev', 'valid_time': 'time', 't':'ta'})'''

    merra2 = xr.open_dataset('/dx02/siw2111/MERRA-2/MERRA-2_TEMP_ALL-TIME.nc4', chunks = 'auto')
    merra2 = merra2.rename({'lat':'lat', 'lon':'lon', 'lev':'plev', 'time': 'time', 'T':'ta'})
    merra2 = merra2.sel(plev = slice(1000,1))
    merra2 = merra2.sortby('time')

    jra55 = xr.open_dataset('/dx02/siw2111/JRA-55/JRA-55_T.nc', chunks = 'auto')
    jra55 = jra55.rename({'g4_lat_2':'lat', 'g4_lon_3':'lon', 'lv_HYBL1':'plev', 'initial_time0_hours': 'time', 'TMP_GDS4_HYBL_S123':'ta'})
    standard_lev = merra2['plev']
    jra55 = jra55.interp(plev = standard_lev)
    lat = jra55.coords['lat']
    jra55 = jra55.assign_coords(lat = lat.round(1)) # convert from pa to hpa
    
    rean_li = [jra55, merra2]

    i = 0
    for rean in rean_li:
        print(rean)
        rean = rean.sel(time = slice('1980-01-01', '2014-01-12'))

        if i == 0:
            cold_point, upper_strat = tropics_rean(rean, detrend = False)
            ax.scatter(cold_point, upper_strat, s = 35, c = 'k', marker = 'o', alpha = 0.5, label = 'reanalysis')
            print(f'plotted!')
        else: 
            cold_point, upper_strat = tropics_rean(rean, detrend = True)
            ax.scatter(cold_point, upper_strat, s = 35, c = 'k', marker = 'o', alpha = 0.5)
            print('plotted!')
        i +=1
        rean.close()

    # plot high-top models
    i = 0
    for id in hi_model_li:
        print(f'{id}')
        try: 
            model = pangeo_pull(id, '')
            model = model.sel(time = slice('1980-01-01', '2014-01-12'))
            plev = model.coords['plev'].values
            model = model.assign_coords(plev = np.divide(plev,100).round(1)) # convert from pa to hpa
            
            # extract means
            cold_point, upper_strat = tropics(model)

            if i == 0:
                ax.scatter(cold_point, upper_strat, s = 35, c = 'r', marker = 'o', alpha = 0.5, label = 'high-top')
            else: 
                ax.scatter(cold_point, upper_strat, s = 35, c = 'r', marker = 'o', alpha = 0.5)
            i+=1
        except:
            print(f'unable to plot... {id}')
        
        model.close()

    # plot low-top models  
    i = 0
    for id in lo_model_li:
        print(f'{id}')
        try: 
            model = pangeo_pull(id, '')
            model = model.sel(time = slice('1980-01-01', '2014-01-12'))
            plev = model.coords['plev'].values
            model = model.assign_coords(plev = np.divide(plev,100).round(1)) # convert from pa to hpa
            
            # extract means
            cold_point, upper_strat = tropics(model)

            if i == 0:
                ax.scatter(cold_point, upper_strat, s = 35, c = 'b', marker = 'o', alpha = 0.5, label = 'low-top')
            else: 
                ax.scatter(cold_point, upper_strat, s = 35, c = 'b', marker = 'o', alpha = 0.5)
            i+=1
        except:
            print(f'unable to plot... {id}')
        
        model.close()
          
    
    plt.title('CMIP6 Models Temperature Trends in the Tropics')
    plt.xlabel('Tropopause')
    plt.ylabel('Upper Stratosphere')
    plt.legend()
    
    ax.yaxis.set_major_locator(MultipleLocator(5))  # Tick every 2 on y-axis
    ax.yaxis.set_minor_locator(MultipleLocator(1))  
    ax.xaxis.set_major_locator(MultipleLocator(1))  # Tick every 2 on x-axis
    
    print(f'saving to...{savename}')
    plt.savefig(savename, dpi = 300)
    return

if __name__ == '__main__':
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
    
    summary_2(hi_model_li, lo_model_li, '/home/siw2111/cmip6_reanalyses_comp/model_plots/05-27-2025/summary_2_trends.png')