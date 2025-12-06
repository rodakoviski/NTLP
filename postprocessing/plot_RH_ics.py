#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
import netCDF4 as nc
import os

# ---------------------------------------------------------
# Directories containing the LES runs
# ---------------------------------------------------------
run_dirs = ["../test0", "../test1"]   # skip if missing
nc_filename = "history.nc"

# For storing profiles
profiles = {}
z_coords = {}

# ---------------------------------------------------------
# Load LES runs (NetCDF)
# ---------------------------------------------------------
for rd in run_dirs:
    path = os.path.join(rd, nc_filename)
    if not os.path.exists(path):
        print(f"Skipping {rd}: {path} not found")
        continue

    ds = nc.Dataset(path)

    # vertical coordinate
    zu = ds.variables["zu"][:]                 # shape Nz
    rh = ds.variables["RHxym"][0, :]    # first time index

    profiles[rd] = rh
    z_coords[rd] = zu

    ds.close()


# ---------------------------------------------------------
# Load separate original IC profile from .dat
# ---------------------------------------------------------
dat_file = "original_ic_profiles.dat"
if os.path.exists(dat_file):
    dat = np.loadtxt(dat_file, skiprows=1)
    z_sep = dat[:, 0]
    rh_sep = dat[:, 1]        # already in %

    profiles["original_separate"] = rh_sep
    z_coords["original_separate"] = z_sep
else:
    print(f"Warning: {dat_file} not found; skipping separate original profile.")


# ---------------------------------------------------------
# Plot
# ---------------------------------------------------------
plt.figure(figsize=(6, 8))

for name in profiles:
    plt.plot(profiles[name], z_coords[name], label=name)

plt.xlabel("Relative Humidity (%)")
plt.ylabel("z (m)")
plt.title("Initial Condition RH Profiles")
plt.grid(True)
plt.legend()
plt.tight_layout()

plt.savefig("RH_ic_profile.png", dpi=150)

