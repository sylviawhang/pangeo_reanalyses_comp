import xarray as xr
import matplotlib.pyplot as plt

# Plot zonal mean temperatures for ERA-5, MERRA_2, JRA-55 side by side.

fig, axes = plt.subplots(nrows = 1, ncols = 2, figsize = (12,6))

#ERA-5
print('reading ERA-5...')

era5 = xr.open_dataset('/dx02/siw2111/ERA-5/ERA5_TEMP_ALL-TIME.nc')
era5 = era5.sel(valid_time = slice('1980-01-01', '2024-11-01')) # select time 1980-2024
era5_zonal_mean = era5.mean(dim = ['longitude', 'valid_time']) #average over longitudes, and time 
print(era5_zonal_mean)

#xr.plot.contour(era5_zonal_mean['t'], x = 'latitude', y = 'pressure_level', yincrease = False, add_colorbar = False, vmin = 190, vmax = 270, cmap = 'turbo', robust = False, extend = 'neither', levels =17, ax = axes[0], yscale = 'log') 
xr.plot.contourf(era5_zonal_mean['t'], x = 'latitude', y = 'pressure_level', yincrease = False, add_colorbar = False, vmin = 190, vmax = 270,  cmap = 'turbo', robust = False, extend = 'neither',  levels =17, ax = axes[0], yscale = 'log') 
axes[0].set_xlabel('latitude (°N)')
axes[0].set_title('ERA-5')

#MERRA-2
print('reading MERRA-2...')

merra2 = xr.open_dataset('/dx02/siw2111/MERRA-2/MERRA-2_TEMP_ALL-TIME.nc4')
merra2 = merra2.sel(lev = slice(1.00000000e+02, 1.00000000e+00)) # select pressure levels 100hPA - 1hPA for MERRA2
merra2_zonal_mean = merra2.mean(dim = ['lon', 'time']) #average over longitudes, and time 
print(merra2_zonal_mean)

#xr.plot.contour(merra2_zonal_mean['T'], x = 'lat', y = 'lev', yincrease = False, add_colorbar = True, vmin = 190, vmax = 270, cmap = 'turbo', robust = False, extend = 'neither', levels =17, ax = axes[1], yscale = 'log') 
xr.plot.contourf(merra2_zonal_mean['T'], x = 'lat', y = 'lev', yincrease = False, add_colorbar = True, vmin = 190, vmax = 270,  cmap = 'turbo', robust = False, extend = 'neither',  levels =17, ax = axes[1], yscale = 'log') 
axes[1].set_xlabel('latitude (°N)')
#axes[1].set_ylabel('pressure (hPa)')
axes[1].set_title('MERRA-2')

plt.suptitle('Zonal mean temperature')
plt.savefig('/home/siw2111/reanalyses_plots/zonal_temp.png', dpi = 400)