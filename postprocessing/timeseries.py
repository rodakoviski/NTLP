# timeseries.py
import os
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter

zl = 128.0
verbose = False
outdir_time = 'fig_timeseries'
outdir_prof = 'fig_colorprofiles'
outdir_anim = 'fig_animations'

# TO-DO LIST
# 1) insert units in netCDF dataset
# 2) plot animated profiles
# 3) include cbrange & cmap as arguments in functions

os.makedirs(outdir_time, exist_ok=True)
os.makedirs(outdir_prof, exist_ok=True)
os.makedirs(outdir_anim, exist_ok=True)

# ----------------------------------------------------------------
def plot_timeseries(ds, varname, time_name="time", outfile=None):
    global outdir_time
    """
    Plot a 1D timeseries variable from an xarray dataset.

    Parameters
    ----------
    ds : xarray.Dataset
        The dataset containing the variable.
    varname : str
        Variable to plot (e.g., "dt").
    time_name : str
        Name of the time coordinate (default: "time").
    outfile : str
        Output PNG file. If None, uses "<varname>_vs_<time>.png".
    """
    time = ds[time_name]
    var = ds[varname]

    if outfile is None:
        outfile = f"{varname}_vs_time.png"

    plt.figure()
    plt.plot(time/3600., var, linewidth=.8)
    plt.xlabel(r'$t$ (h)')
    plt.ylabel(varname)
    plt.title(var.attrs.get("title", varname))
    plt.grid(True)

    plt.savefig(os.path.join(outdir_time,outfile), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved {outfile}")


def plot_profile_timecolor(ds, varname, z_name, time_name='time',
                           figsize=(10, 4),cmap='viridis',outfile=None):
    global outdir_prof
    """
    Make a colorplot of variable(varname) with dimensions (time, z):
    horizontal axis = time
    vertical axis   = z
    color levels    = variable values
    """
    if outfile is None:
        outfile = f"{varname}_profile_color.png"

    # --- Axis coordinates ---
    t = ds[time_name].values
    z = ds[z_name].values
    vals = ds[varname].values

    # --- Plot ---
    fig, ax = plt.subplots(figsize=figsize)
    T, Z = np.meshgrid(t/3600., z, indexing='ij')
    c = ax.pcolormesh(T, Z, vals, cmap=cmap, shading='auto')
    ax.set_xlabel(r'$t$ (h)')
    ax.set_ylabel(r'$z$ (m)')
    cb = fig.colorbar(c, ax=ax)
    ax.set_title(ds[varname].attrs.get('title', varname))
    ax.grid(True, linestyle='--', alpha=0.5)

    plt.savefig(os.path.join(outdir_prof,outfile), dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved {outfile}")

def animate_vertical_profiles(ds, varname, z_name, time_name='time',
                              figsize=(5,6), dpi=150, outfile=None):
    global outdir_anim, zl
    """
    Animate vertical profiles var(z) over time and save as MP4.
    ds        : xarray.Dataset
    varname   : variable of shape (time, z)
    z_name    : vertical coordinate
    time_name : time coordinate
    outfile   : mp4 filename
    """
    if outfile is None:
        outfile = f"{varname}_animated.mp4"
    # --- Read data ---
    t = ds[time_name].values / 3600.0   # convert to hours
    z = ds[z_name].values
    vals = ds[varname].values           # shape (Nt, Nz)
    Nt, Nz = vals.shape

    # --- Prepare figure ---
    fig, ax = plt.subplots(figsize=figsize)
    line, = ax.plot(vals[0, :], z, lw=1.5)
#    ax.set_xlabel(ds[varname].attrs.get("units", varname))
    ax.set_ylabel(z_name)
    ax.grid(True)
    ax.set_title(f"{ds[varname].attrs.get('title', varname)}   t = {t[0]:.2f} h")

    # --- Adjust axes limits ---
    ax.set_xlim(np.nanmin(vals), np.nanmax(vals))
    ax.set_ylim(0.0, zl)

    # --- Frame update function ---
    def update(frame):
        line.set_xdata(vals[frame, :])
        ax.set_title(f"{ds[varname].attrs.get('title', varname)}   t = {t[frame]:.2f} h")
        return line,

    # --- Animation ---
    anim = FuncAnimation(fig, update, frames=Nt, blit=True)
    writer = FFMpegWriter(fps=30, bitrate=2000)
    anim.save(os.path.join(outdir_anim,outfile), writer=writer, dpi=dpi)
    plt.close(fig)
    print(f"Saved animation to {outfile}")
# ----------------------------------------------------------------

ds = xr.open_dataset('../history.nc')
print(ds)
if verbose:
  print("\n--- Global Attributes ---")
  for k, v in ds.attrs.items():
    print(f"{k}: {v}")
  print("\n--- Dimensions ---")
  for dim, size in ds.sizes.items():
    print(f"{dim}: {size}")
  print("\n--- Variables ---")
  for var in ds.data_vars:
    print(f"{var}: {ds[var].dims} -> {ds[var].shape}")

animate_vertical_profiles(ds,'RHxym','zu')
animate_vertical_profiles(ds,'tempxym','zu')

plot_timeseries(ds,'dt')
plot_timeseries(ds,'utau')
plot_timeseries(ds,'uwsfc')
plot_timeseries(ds,'tnumpart')
plot_timeseries(ds,'tnumdrop')
plot_timeseries(ds,'tnumaerosol')
plot_timeseries(ds,'tnum_destroy')
plot_timeseries(ds,'tdenum')
plot_timeseries(ds,'tactnum')
plot_timeseries(ds,'tnum100')
plot_timeseries(ds,'tnumimpos')
plot_timeseries(ds,'tot_reintro')
plot_timeseries(ds,'Tsfc')
plot_timeseries(ds,'qsfc')
plot_timeseries(ds,'wtsfc')
plot_timeseries(ds,'wqsfc')
plot_timeseries(ds,'Swall')
plot_timeseries(ds,'meanRH')
plot_timeseries(ds,'varRH')
plot_timeseries(ds,'radavg')
plot_timeseries(ds,'radmsqr')
plot_timeseries(ds,'twmass')
plot_timeseries(ds,'tpmass')
plot_timeseries(ds,'tpvol')

plot_profile_timecolor(ds,'uxym','zu')
plot_profile_timecolor(ds,'vxym','zu')
plot_profile_timecolor(ds,'wxym','zw')
####################################
# these have 2 variables combined
plot_profile_timecolor(ds["txym"].isel(nscl=0).to_dataset(name="txym0"),'txym0','zu')
plot_profile_timecolor(ds["txym"].isel(nscl=1).to_dataset(name="txym1"),'txym1','zu')
plot_profile_timecolor(ds["tps"].isel(nscl=0).to_dataset(name="tps0"),'tps0','zu')
plot_profile_timecolor(ds["tps"].isel(nscl=1).to_dataset(name="tps1"),'tps1','zu')
plot_profile_timecolor(ds["wtle"].isel(nscl=0).to_dataset(name="wtle0"),'wtle0','zw')
plot_profile_timecolor(ds["wtle"].isel(nscl=1).to_dataset(name="wtle1"),'wtle1','zw')
plot_profile_timecolor(ds["wtsb"].isel(nscl=0).to_dataset(name="wtsb0"),'wtsb0','zw')
plot_profile_timecolor(ds["wtsb"].isel(nscl=1).to_dataset(name="wtsb1"),'wtsb1','zw')
####################################
plot_profile_timecolor(ds,'exym','zw')
plot_profile_timecolor(ds,'RHxym','zu')
plot_profile_timecolor(ds,'RHmsqr','zu')
plot_profile_timecolor(ds,'tempxym','zu')
plot_profile_timecolor(ds,'ups','zu')
plot_profile_timecolor(ds,'vps','zu')
plot_profile_timecolor(ds,'wps','zw')
plot_profile_timecolor(ds,'uwle','zw')
plot_profile_timecolor(ds,'uwsb','zw')
plot_profile_timecolor(ds,'vwle','zw')
plot_profile_timecolor(ds,'vwsb','zw')
plot_profile_timecolor(ds,'t_rprod','zw')
plot_profile_timecolor(ds,'t_sprod','zw')
plot_profile_timecolor(ds,'t_tran','zw')
plot_profile_timecolor(ds,'t_buoy','zw')
plot_profile_timecolor(ds,'t_diss','zw')
plot_profile_timecolor(ds,'zconc','zu')
plot_profile_timecolor(ds,'pflux','zw')
plot_profile_timecolor(ds,'pfluxdiff','zw')
plot_profile_timecolor(ds,'pmassflux','zw')
plot_profile_timecolor(ds,'penegflux','zw')
plot_profile_timecolor(ds,'vp1mean','zu')
plot_profile_timecolor(ds,'vp2mean','zu')
plot_profile_timecolor(ds,'vp3mean','zu')
plot_profile_timecolor(ds,'vp1msqr','zu')
plot_profile_timecolor(ds,'vp2msqr','zu')
plot_profile_timecolor(ds,'vp3msqr','zu')
plot_profile_timecolor(ds,'uf1mean','zu')
plot_profile_timecolor(ds,'uf2mean','zu')
plot_profile_timecolor(ds,'uf3mean','zu')
plot_profile_timecolor(ds,'uf1msqr','zu')
plot_profile_timecolor(ds,'uf2msqr','zu')
plot_profile_timecolor(ds,'uf3msqr','zu')
plot_profile_timecolor(ds,'m1src','zu')
plot_profile_timecolor(ds,'m2src','zu')
plot_profile_timecolor(ds,'m3src','zu')
plot_profile_timecolor(ds,'Tpsrc','zu')
plot_profile_timecolor(ds,'TEpsrc','zu')
plot_profile_timecolor(ds,'Hpsrc','zu')
plot_profile_timecolor(ds,'Tpmean','zu')
plot_profile_timecolor(ds,'Tpmsqr','zu')
plot_profile_timecolor(ds,'Tfmean','zu')
plot_profile_timecolor(ds,'qfmean','zu')
plot_profile_timecolor(ds,'radmean','zu')
plot_profile_timecolor(ds,'rad2mean','zu')
plot_profile_timecolor(ds,'qstarm','zu')
plot_profile_timecolor(ds,'Nc','zu')
plot_profile_timecolor(ds,'ql','zu')
plot_profile_timecolor(ds,'radsrc','zu')
plot_profile_timecolor(ds,'rho_base','zu')
plot_profile_timecolor(ds,'p_base','zu')
plot_profile_timecolor(ds,'T_base','zu')
plot_profile_timecolor(ds,'theta_base','zu')

# ----------------------------------------------------------------
# EOF
# ----------------------------------------------------------------
#
#
