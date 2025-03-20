import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
from ncf_funct import cdf_merge, replace_coordinate
import colorcet as cc
from reanalyses_plots import annual_zonal_mean, seasonal_zonal_mean, plot_annual
from pangeo_pull import pangeo_pull


# plots to compare model and reanalysis climatology

# load model
model_xrds = pangeo_pull(source_id = 'GISS-E2-1-G', institution_id = 'NASA-GISS')

model_xrds =model_xrds.sel(time = slice('1980-01-01', '2014-12-01'))
model_xrds = model_xrds.sel(member_id = 'r1i1p1f1')
plev = model_xrds.coords['plev'].values
model_xrds = model_xrds.assign_coords(plev  = np.divide(plev,100))
model_xrds = model_xrds.sel(plev = slice(1000,1))
model_xrds = model_xrds.mean(dim = ['dcpp_init_year'])

annual_model = annual_zonal_mean(model_xrds, 'lon', 'time', 'ta')

# load reanalysis
rean_xrds = xr.open_dataset('/dx02/siw2111/MERRA-2/MERRA-2_TEMP_ALL-TIME.nc4', chunks = 'auto')

rean_xrds = rean_xrds.rename({'lat':'lat', 'lon':'lon', 'lev':'plev', 'time': 'time', 'T':'ta'})
rean_xrds = rean_xrds.sortby('time')
rean_xrds = rean_xrds.sel(time = slice('1980-01-01', '2014-01-01'))
rean_xrds = rean_xrds.sel(plev = slice(1000,1))

annual_rean = annual_zonal_mean(rean_xrds, 'lon', 'time', 'ta')

# select common pressure levels
common_plev = np.intersect1d(annual_rean['plev'], annual_model['plev'])
annual_rean = annual_rean.sel(plev = common_plev)
annual_model = annual_model.sel(plev = common_plev)

# interpolate to common latitude grid
model_lat = annual_model['lat']
annual_rean = annual_rean.interp(lat = model_lat)

print('annual reanalysis')
print(annual_rean)
print('annual model')
print(annual_model)
print('difference')
annual_diff = annual_model - annual_rean
print(annual_diff)
print(annual_diff.variables['ta'].values)

# plot difference
boundaries = [-12, -10, -8, -6, -4, -2, -1, 1, 2, 4, 6, 8, 10, 12]
plt.figure(figsize = (12,6), layout = 'constrained')
xr.plot.contourf(annual_diff['ta'],
            x = 'lat',
            y = 'plev', 
            yincrease =  False,
            add_colorbar= True,
            cbar_kwargs= {'label':'Temperature Difference, K', 'drawedges':True, 'ticks':boundaries},
            levels = boundaries,
            add_labels = False,
            cmap= cc.cm.diverging_bwr_55_98_c37,
            extend="neither",
            yscale = 'log',
            ylim = (1000, 1))
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
            ylim = (1000, 1))
plt.clabel(cs, cs.levels, fontsize=10)
annual_diff.close()
    
cbar = plt.gca().collections[0].colorbar  # Get the colorbar object
cbar.ax.tick_params(length=0)
cbar.ax.set_ylabel('Temperature Difference, K', fontsize=12) 

plt.ylim(1000,1)
plt.ylabel('Pressure, hPa', fontsize = 12)
plt.xlabel('Latitude, deg N', fontsize = 12)
plt.title('GISS-E2-1-G Zonal Mean Temperature Difference (Annual 1980-2014)', fontsize = 15)

savename = '/home/siw2111/cmip6_reanalyses_comp/model_plots/03-20-2025/GISS-E2_1-G_difference.png'
print(f'saving to... {savename}')
plt.savefig(savename, dpi = 300)
