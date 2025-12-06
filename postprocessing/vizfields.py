# vizfields.py
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib
matplotlib.use("Agg")   # Important on clusters

# Remember to load ffmpeg module on cluster before running!

# ----------------------------------------------------------------
def animate_xz_field(ds, varname, x_name="x", z_name="zu",
                     time_name="time", outfile="anim.mp4", fps=10):
    """
    Animate a variable defined as (time, z, x).
    Saves animation as MP4.
    """
    da = ds[varname]               # (time, z, x)
    time_vals = ds[time_name].values
    x_vals = ds[x_name].values
    z_vals = ds[z_name].values

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.set_xlabel("x")
    ax.set_ylabel("z")
    ax.set_title(f"{varname} (time = {time_vals[0]:.2f})")

    # initial frame
    frame0 = da.isel(time=0)
    pcm = ax.pcolormesh(x_vals, z_vals, frame0, shading="auto")
    fig.colorbar(pcm, ax=ax)
    ax.grid(True)

    def update(frame):
        fdata = da.isel(time=frame)
        pcm.set_array(fdata.values.ravel())
        ax.set_title(f"{varname} (time = {time_vals[frame]:.2f})")
        return (pcm,)

    anim = animation.FuncAnimation(
        fig, update, frames=len(time_vals), blit=False
    )

    anim.save(outfile, dpi=150, fps=fps)
    plt.close(fig)
    print(f"Saved {outfile}")
    return outfile
# ----------------------------------------------------------------

ds = xr.open_dataset('../viz.nc')
print(ds)
# For more details, uncomment lines below
#print("\n--- Global Attributes ---")
#for k, v in ds.attrs.items():
#  print(f"{k}: {v}")
#print("\n--- Dimensions ---")
#for dim, size in ds.sizes.items():
#  print(f"{dim}: {size}")
#print("\n--- Variables ---")
#for var in ds.data_vars:
#  print(f"{var}: {ds[var].dims} -> {ds[var].shape}")

animate_xz_field(ds, "t_xz", outfile="t_xz_animation.mp4")

# ----------------------------------------------------------------
# EOF
# ----------------------------------------------------------------
#
#

