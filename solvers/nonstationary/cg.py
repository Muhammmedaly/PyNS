"""
Preconditioned Conjugate Gradient (CG) solver.

Source:
  http://www.netlib.org/templates/templates.pdf
"""

from __future__ import print_function

# Standard Python modules
from pyns.standard import *

# PyNS modules
from pyns.constants      import *
from pyns.display        import write
from pyns.discretization import Unknown

# Sisters from this module
from pyns.solvers.mat_vec_bnd import mat_vec_bnd
from pyns.solvers.vec_vec     import vec_vec
from pyns.solvers.norm        import norm

# =============================================================================
def cg(a, phi, b, tol, 
       verbose = False,
       max_iter = -1):
# -----------------------------------------------------------------------------
    """
    Args:
      a: ...... Object of the type "Matrix", holding the system matrix.
      phi: .... Object of the type "Unknown" to be solved.
      b: ...... Three-dimensional array holding the source term.
      tol: .... Absolute solver tolerance
      verbose:  Logical variable setting if solver will be verbose (print
                info on Python console) or not.
      max_iter: Maxiumum number of iterations.

    Returns:
      x: Three-dimensional array with solution.
    """

    if verbose is True:
        write.at(__name__)

    # Helping variable
    x = phi.val

    # Intitilize arrays
    p = Unknown("vec_p", phi.pos, x.shape, -1, per=phi.per, verbose=False)
    q = zeros(x.shape)
    r = zeros(x.shape)
    z = zeros(x.shape)

    # r = b - A * x
    r[:,:,:] = b[:,:,:] - mat_vec_bnd(a, phi)

    # ---------------
    # Iteration loop
    # ---------------
    if max_iter == -1:
        max_iter = prod(phi.val.shape)
        
    for i in range(1, max_iter):

        if verbose is True:
            print("  iteration: %3d:" % (i), end = "" )

        # Solve M z = r
        z[:,:,:] = r[:,:,:] / a.C[:,:,:]

        # rho = r * z
        rho = vec_vec(r, z)

        if i == 1:
            # p = z
            p.val[:,:,:] = z[:,:,:]

        else:
            # beta = rho / rho_old
            beta = rho / rho_old

            # p = z + beta p
            p.val[:,:,:] = z[:,:,:] + beta * p.val[:,:,:]

        # q = A * p
        q[  :,  :,  :]  = mat_vec_bnd(a, p)

        # alfa = rho / (p * q)
        alfa = rho / vec_vec(p.val, q)

        # x = x + alfa p
        x[:,:,:] += alfa * p.val[:,:,:]

        # r = r - alfa q
        r[:,:,:] -= alfa * q[:,:,:]

        # Compute residual
        res = norm(r)

        if verbose is True:
            print("%12.5e" %res)

        # If tolerance has been reached, get out of here
        if res < tol:
            return x

        # Prepare for next iteration
        rho_old = rho

    return x  # end of function
