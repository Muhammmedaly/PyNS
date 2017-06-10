"""
#                                                       o ... scalars
#                          (n)                          - ... u velocities      
#                                                       | ... v velocities
#       +-------+-------+-------+-------+-------+          
#       |       |       |       |       |       |            
#       |   o   -   o   -   o   -   o   -   o   | j=ny-2     
#       |       |       |       |       |       | 
#       +---|---+---|---+---|---+---|---+---|---+     j=ny-1     
#       |       |       |       |       |       |
#       |   o   -   o   -   o   -   o   -   o   | ...
#       |       |       |       |       |       |
#  (w)  +---|---+---|---+---|---+---|---+---|---+    j=1        (e)
#       |       |       |       |       |       |
#       |   o   -   o   -   o   -   o   -   o   | j=1
#       |       |       |       |       |       |
#       +---|---+---|---+---|---+---|---+---|---+    j=0 (v-velocity)
#       |       |       |       |       |       |
#       |   o   -   o   -   o   -   o   -   o   | j=0   (scalar cell)
#       |       |       |       |       |       |
#       +-------+-------+-------+-------+-------+
#  y       i=0     i=1     ...     ...    i=nx-1      (scalar cells)
# ^            i=0      i=1    ...    i=nx-2      (u-velocity cells)
# |
# +---> x                  (s)
#  
"""

#!/usr/bin/python

# Standard Python modules
from pyns.standard import *

# ScriNS modules
from pyns.constants.all       import *
from pyns.operators.all       import *
from pyns.display.all         import *
from pyns.discretization.all  import *
from pyns.physical_models.all import *

def main(show_plot=True, time_steps=4800):
  
# =============================================================================
#
# Define problem
#
# =============================================================================

  # Node coordinates
  xn = nodes(0, 1,     256)
  yn = nodes(0, 0.125,  32)
  zn = nodes(0, 0.125,   4)
  
  # Cell coordinates
  xc = avg(xn)
  yc = avg(yn)
  zc = avg(zn)
  
  # Cell dimensions
  nx,ny,nz, dx,dy,dz, rc,ru,rv,rw = cartesian_grid(xn,yn,zn)
  
  # Set physical properties
  rho, mu, cap, kappa = properties_for_air(rc)
       
  # Time-stepping parameters
  dt  = 0.002      # time step
  ndt = time_steps # number of time steps
  
  # Create unknowns; names, positions and sizes
  uf = create_unknown('face-u-vel',  X, ru, DIRICHLET)
  vf = create_unknown('face-v-vel',  Y, rv, DIRICHLET)
  wf = create_unknown('face-w-vel',  Z, rw, DIRICHLET)
  p  = create_unknown('pressure',    C, rc, NEUMANN)
  
  # Specify boundary conditions
  uf.bnd[W].typ[:1,:,:] = DIRICHLET 
  for k in range(0,nz):
    uf.bnd[W].val[:1,:,k]  = par(0.1, yn)
  
  uf.bnd[E].typ[:1,:,:] = OUTLET 
  
  for j in (B,T):
    uf.bnd[j].typ[:] = NEUMANN     
    vf.bnd[j].typ[:] = NEUMANN     
    wf.bnd[j].typ[:] = NEUMANN     
  
  adj_n_bnds(p)
  
  obst = zeros(rc)
  for j in range(0, 24):
    for i in range(64+j, 64+24):
        for k in range(0,nz):
          obst[i,j,k] = 1

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
  
    print_time_step(ts)
    
    # -----------------
    # Store old values
    # -----------------
    uf.old[:] = uf.val[:]
    vf.old[:] = vf.val[:]
    wf.old[:] = wf.val[:]
    
    # ----------------------
    # Momentum conservation
    # ----------------------
    ef = zeros(ru), zeros(rv), zeros(rw)
      
    calc_uvw((uf,vf,wf), (uf,vf,wf), rho, mu,  \
             zeros(rc), ef, dt, (dx,dy,dz), obst)
    
    # ---------
    # Pressure
    # ---------
    calc_p(p, (uf,vf,wf), rho, dt, (dx,dy,dz), obst)
    
    # --------------------
    # Velocity correction
    # --------------------
    corr_uvw((uf,vf,wf), p, rho, dt, (dx,dy,dz), obst)
   
    # Compute volume balance for checking 
    err = vol_balance((uf,vf,wf), (dx,dy,dz), obst)
    print('Maximum volume error after correction: %12.5e' % abs(err).max())
  
    # Check the CFL number too 
    cfl = cfl_max((uf,vf,wf), dt, (dx,dy,dz))
    print('Maximum CFL number: %12.5e' % cfl)

# =============================================================================
#
# Visualisation
#
# =============================================================================
    if show_plot:
      if ts % 20 == 0:
        plot_isolines(p.val, (uf,vf,wf), (xn,yn,zn), Z)

if __name__ == '__main__':
    main()