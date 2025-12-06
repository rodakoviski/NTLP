import numpy as np
import matplotlib.pyplot as plt

def T_profile(z, T0, zi, dTdzBL, dTdzFA):
    """
    Piecewise linear temperature profile:
      - Below zi:  T = T0 + dTdzBL * z
      - Above zi: T = T0 + Tinv + dTdzFA * (z - zi)
        where Tinv = T(zi) from the lower branch
    """
    T = np.zeros_like(z)
    # Temperature at inversion height
    Tinv = T0 + dTdzBL * zi
    # Below zi
    mask_BL = z <= zi
    T[mask_BL] = T0 + dTdzBL * z[mask_BL]
    # Above zi
    mask_FA = z > zi
    T[mask_FA] = Tinv + dTdzFA * (z[mask_FA] - zi)
    return T

def RH_profile(z, RH0, zi, amp, dRHdzFA):
    RH = np.zeros_like(z)
    # Below zi
    mask_BL = z <= zi
    RH[mask_BL] = RH0-amp*np.sin(2.*np.pi*z[mask_BL]/zi)
    # Above zi
    mask_FA = z > zi
    RH[mask_FA] = RH0-dRHdzFA*(z[mask_FA]-zi)
    return RH

def es_clausius(T):
    """Saturation vapor pressure (Pa) at T (K) via integrated Clausius-Clapeyron."""
    Lv = 2.5e6        # J/kg
    Rv = 461.5        # J/(kg K)
    T0 = 273.15
    es0 = 611.65      # Pa
    T = np.asarray(T)
    return 610.94*np.exp((17.6257*(T-273.15))/(243.04+(T-273.15)))
#    return es0 * np.exp((Lv/Rv)*(1.0/T0 - 1.0/T))

def q_from_e(e, p):
    """Specific humidity (kg/kg) from vapor pressure e (Pa) and ambient pressure p (Pa)."""
    eps = 0.622
    return (eps * e) / (p - (1.0 - eps) * e)

def e_from_q(q, p):
    """Vapor pressure e (Pa) from specific humidity q (kg/kg) and ambient pressure p (Pa)."""
    eps = 0.622
    return (q * p) / (eps + (1.0 - eps) * q)

def pressure(z, p0, T0, zi, dTdzBL, dTdzFA):
    g = 9.81           # m/s2
    Rd = 287.          # J/(kg K)
    cp = 1004.         # J/(kg K)
    GBL = dTdzBL-(g/cp)
    GFA = dTdzFA-(g/cp)
    p = np.zeros_like(z)
    # Below zi
    mask_BL = z <= zi
    p[mask_BL] = p0*(1.+GBL*z[mask_BL]/T0)**(-g/(Rd*GBL))
    # Above zi
    mask_FA = z > zi
    p[mask_FA] = p0*((1.+GBL*zi/T0)**(-g/(Rd*GBL)))*((1.+GFA*(z[mask_FA]-zi)/(T0+GBL*zi))**(-g/(Rd*GFA)))
    return p

def exner(p,theta,p0):
    Rd = 287.          # J/(kg K)
    cp = 1004.         # J/(kg K)
    temp = np.zeros_like(p)
    temp = theta*(p/p0)**(Rd/cp)
    return temp

########################################
# Variable Parameters
########################################

T0 = 280.0             # K
p0 = 101325.0          # Pa
zi = 70.0              # m
zl = 128.0             # m
dTdzFA = 36 / 1000.0   # K/m (convert from K/km)
dTdzBL_values = [0, 4/1000, 12/1000]   # K/m
RH0 = 1.00             # multiply by 100 for surface RH in %
amp = 0.003            # maximum supersaturation within BL (multiply by 100 to have it in %)
dRHdzFA = 0.003        # multiply by 100 to have FA slope of RH(z) in %/m
Mw = 0.018015  #kg/mol
Ru = 8.3144    #J/mol-K Universal gas constant
Rd = 287.          # J/(kg K)


#####################################################################################################
###################### PLOTTING STUFF ###############################################################
#####################################################################################################

# z grid
z = np.linspace(0, zl, 500)

# --- Make side-by-side figure ---
fig, axes = plt.subplots(1, 3, figsize=(15, 6), sharey=True)

# ---- (1) Potential temperature profiles ----
for dTdzBL in dTdzBL_values:
    T = T_profile(z, T0, zi, dTdzBL, dTdzFA)
    axes[0].plot(T, z, label=f"dTdzBL = {dTdzBL*1000:.0f} K/km")

axes[0].set_xlabel("Potential temperature (K)")
axes[0].set_ylabel("Height z (m)")
axes[0].set_title("Temperature Profile")
axes[0].grid(True)
axes[0].legend()

# ---- (2) Specific humidiy profiles ----
for dTdzBL in dTdzBL_values:
    T = T_profile(z, T0, zi, dTdzBL, dTdzFA) # potential temperature
    RH = RH_profile(z, RH0, zi, amp, dRHdzFA)
    p = pressure(z, p0, T0, zi, dTdzBL, dTdzFA)
    temp = exner(p,T,p0)
    rhoa = pressure(z, p0,T0,zi,dTdzBL,dTdzFA)/(Rd*temp)
    q=RH*Mw*es_clausius(temp)/(Ru*temp*rhoa)
    #e = RH*es_clausius(temp)
    #q = q_from_e(e, p)
    axes[1].plot(q*1000., z, label=f"dTdzBL = {dTdzBL*1000:.0f} K/km")
axes[1].set_xlabel("WV specific humidity q (g/kg)")
axes[1].set_title("Water Vapor Specific Humidity")
axes[1].grid(True)
axes[1].legend()

# ---- (3) RH profile ----
RH = RH_profile(z, RH0, zi, amp, dRHdzFA)
axes[2].plot(RH*100., z)    # convert to %
axes[2].set_xlabel("Relative Humidity (%)")
axes[2].set_title("RH Profile")
axes[2].grid(True)

plt.tight_layout()
plt.savefig("thermodyn_profiles.png", dpi=150, bbox_inches="tight")
plt.close()

T = T_profile(z, T0, zi, 0.0, dTdzFA)
p = pressure(z, p0, T0, zi, 0.0, dTdzFA)
temp = exner(p,T,p0)
rhoa = pressure(z, p0,T0,zi,0.0,dTdzFA)/(Rd*temp)
q=RH*Mw*es_clausius(temp)/(Ru*temp*rhoa)
data = np.column_stack([z, RH*100., q*1000., T])   # convert units
np.savetxt("original_ic_profiles.dat", data, fmt="%14.7e",
           header="z(m) RH(%) qwv(g/kg) theta(K)", comments="")
