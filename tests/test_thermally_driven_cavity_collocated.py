#!/usr/bin/python
"""
This program solves thermally driven cavity at Ra = 1.0e6, in dimensional
and non-dimensional forms, for collocated variable arrangement.

Equations in dimensional form:

D(rho u)/Dt = nabla(mu (nabla u)^T) - nabla p + g
D(rho cp T)/Dt = nabla(lambda (nabla T)^T)

Equations in non-dimensional form, for natural convection problems

DU/Dt = nabla(1/sqrt(Gr) (nabla U)^T) - nabla P + theta
D theta/Dt = nabla(1/(Pr*sqrt(Gr)) (nabla theta)^T)

For thermally driven cavity, with properties of air at 60 deg:

nu   =  1.89035E-05;
beta =  0.003;
dT   = 17.126;
L    =  0.1;
Pr   = 0.709;

Characteristic non-dimensional numbers are:
Gr = 1.4105E+06
Ra = 1.0000E+06
"""

from __future__ import division

# Standard Python modules
from pyns.standard import *

# PyNS modules
from pyns.constants      import *
from pyns.operators      import *
from pyns.discretization import *
from pyns.display        import plot, write
from pyns.physical       import properties

def main(show_plot=True, time_steps=1200, plot_freq=120):

# =============================================================================
#
# Define problem
#
# =============================================================================

    xn = nodes(0, 1,  64, 1.0/256, 1.0/256)
    yn = nodes(0, 1,  64, 1.0/256, 1.0/256)
    zn = nodes(0, 0.1, 5)

    # Cell dimensions
    nx,ny,nz, dx,dy,dz, rc,ru,rv,rw = cartesian_grid(xn,yn,zn)

    # Set physical properties
    grashof = 1.4105E+06
    prandtl = 0.7058
    rho   = zeros(rc)
    mu    = zeros(rc)
    kappa = zeros(rc)
    cap   = zeros(rc)
    rho  [:,:,:] = 1.0
    mu   [:,:,:] = 1.0 / sqrt(grashof)
    kappa[:,:,:] = 1.0 / (prandtl * sqrt(grashof))
    cap  [:,:,:] = 1.0

    # Time-stepping parameters
    dt  = 0.02        # time step
    ndt = time_steps  # number of time steps

    # Create unknowns; names, positions and sizes
    uc    = Unknown("cell-u-vel",     C, rc, DIRICHLET)
    vc    = Unknown("cell-v-vel",     C, rc, DIRICHLET)
    wc    = Unknown("cell-w-vel",     C, rc, DIRICHLET)
    uf    = Unknown("face-u-vel",     X, ru, DIRICHLET)
    vf    = Unknown("face-v-vel",     Y, rv, DIRICHLET)
    wf    = Unknown("face-w-vel",     Z, rw, DIRICHLET)
    t     = Unknown("temperature",    C, rc, NEUMANN)
    p     = Unknown("pressure",       C, rc, NEUMANN)
    p_tot = Unknown("total-pressure", C, rc, NEUMANN)

    # This is a new test
    t.bnd[W].typ[:] = DIRICHLET
    t.bnd[W].val[:] = -0.5

    t.bnd[E].typ[:] = DIRICHLET
    t.bnd[E].val[:] = +0.5

    for j in (B,T):
        uc.bnd[j].typ[:] = NEUMANN
        vc.bnd[j].typ[:] = NEUMANN
        wc.bnd[j].typ[:] = NEUMANN

# =============================================================================
#
# Solution algorithm
#
# =============================================================================

    # ----------
    #
    # Time loop
    #
    # ----------
    for ts in range(1,ndt+1):

        write.time_step(ts)

        # -----------------
        # Store old values
        # -----------------
        t.old[:]  = t.val[:]
        uc.old[:] = uc.val[:]
        vc.old[:] = vc.val[:]
        wc.old[:] = wc.val[:]

        # -----------------------
        # Temperature (enthalpy)
        # -----------------------
        calc_t(t, (uf,vf,wf), (rho*cap), kappa, dt, (dx,dy,dz))

        # ----------------------
        # Momentum conservation
        # ----------------------
        ext_f = zeros(rc), t.val, zeros(rc)

        calc_uvw((uc,vc,wc), (uf,vf,wf), rho, mu, dt, (dx,dy,dz),
                 pressure = p_tot,
                 force    = ext_f)

        # ---------
        # Pressure
        # ---------
        calc_p(p, (uf,vf,wf), rho, dt, (dx,dy,dz))

        p_tot.val += p.val

        # --------------------
        # Velocity correction
        # --------------------
        corr_uvw((uc,vc,wc), p, rho, dt, (dx,dy,dz))
        corr_uvw((uf,vf,wf), p, rho, dt, (dx,dy,dz))

        # Check the CFL number too
        cfl = cfl_max((uc,vc,wc), dt, (dx,dy,dz))

# =============================================================================
#
# Visualisation
#
# =============================================================================
        if show_plot:
            if ts % plot_freq == 0:
                plot.isolines(t.val, (uc, vc, wc), (xn, yn, zn), Z)
                plot.gmv("tdc-collocated-%6.6d" % ts, 
                         (xn, yn, zn), (uc, vc, wc, t))

if __name__ == "__main__":
    main()
