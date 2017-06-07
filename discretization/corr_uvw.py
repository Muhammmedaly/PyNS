"""
Projects velocity into a divergence-free velocity field with the pressure 
correction gradient (provided pressure correction is accuratelly solved).
"""

# Standard Python modules
from standard import *

# ScriNS modules
from constants.all      import *
from operators.all      import *

from discretization.obst_zero_val import obst_zero_val

# =============================================================================
def corr_uvw(uvw, p, rho, dt, dxyz, obst):
# -----------------------------------------------------------------------------
  """
  Args:
    uvw:  a tuple with three staggered or centered velocity components 
          (each component is created with "scrins.create_unknown" function.
    p:    unknown holding the pressure correction.     
    rho:  three-dimensional matrix holding density for all cells.
    dt:   time step
    dxyz: a tuple holding cell dimensions in "x", "y" and "z" directions.
          Each cell dimension is a three-dimensional array.
    obst: obstacle
    
  Returns:
    none, but input argument uvw is modified.
  """

  # Unpack received tuples
  dx, dy, dz = dxyz

  # Compute pressure correction gradients
  p_x = dif(X, p.val) / avg(X, dx)  
  p_y = dif(Y, p.val) / avg(Y, dy)  
  p_z = dif(Z, p.val) / avg(Z, dz)  
  
  # Set to zero in obst
  if obst.any() != 0:
    p_x = obst_zero_val(X, p_x, obst)
    p_y = obst_zero_val(Y, p_y, obst)
    p_z = obst_zero_val(Z, p_z, obst)
  
  # Pad with boundary values by expanding from interior 
  # (This is done only for collocated formulation)
  if uvw[X].pos == C:
    p_x = avg(X, cat(X, (p_x[:1,:,:], p_x, p_x[-1:,:,:])))
    p_y = avg(Y, cat(Y, (p_y[:,:1,:], p_y, p_y[:,-1:,:])))
    p_z = avg(Z, cat(Z, (p_z[:,:,:1], p_z, p_z[:,:,-1:])))
  
  # Correct the velocities
  uvw[X].val[:] = uvw[X].val[:] - dt / avg(uvw[X].pos, rho) * p_x
  uvw[Y].val[:] = uvw[Y].val[:] - dt / avg(uvw[Y].pos, rho) * p_y
  uvw[Z].val[:] = uvw[Z].val[:] - dt / avg(uvw[Z].pos, rho) * p_z
  
  return  # end of function