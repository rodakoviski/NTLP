# histograms.py
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")

# ----------------------------------------------------------------
def plot_histogram(ds, histvar, binsvar, time_index, outfile=None):
    """
    Plot DSD at a given time index.
    
    ds        : xarray.Dataset
    histvar   : name of histogram variable, e.g. 'radhist'
    binsvar   : name of bin coordinate variable, e.g. 'radbins'
    time_index can be:
       - an int  → single plot
       - a list/tuple of ints → multiple curves in one figure
    outfile   : filename to save
    """

    # Normalize time_index into a list
    if isinstance(time_index, int):
        time_indices = [time_index]
    else:
        time_indices = list(time_index)

    if outfile is None:
        outfile = f"{histvar}_histogram.png"

    bins = ds[binsvar]

    plt.figure(figsize=(7,4))
    for idx in time_indices:
        hist = ds[histvar].isel(time=idx)
        tval = float(ds["time"].isel(time=idx))
        label = f"t = {tval/3600.:.2f} h"
        plt.plot(bins, hist, linewidth=1., label=label)

    plt.xlim(bins.min(), bins.max())
    plt.xlabel(f"{binsvar}")
    plt.ylabel(f"{histvar}")
    plt.title(ds[histvar].attrs.get("title", histvar))

    plt.grid(True, which="both")
    plt.legend()
    plt.tight_layout()
    plt.savefig(outfile, dpi=150)
    plt.close()
    print(f"Saved {outfile}")
# ----------------------------------------------------------------

ds = xr.open_dataset('../histograms.nc')
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

plot_histogram(ds,'radhist','radbins',[0,49,249,608])
plot_histogram(ds,'reshist','resbins',[0,49,249,608])

# ----------------------------------------------------------------
# EOF
# ----------------------------------------------------------------
#
#

