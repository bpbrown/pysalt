################################# LICENSE ##################################
# Copyright (c) 2009, South African Astronomical Observatory (SAAO)        #
# All rights reserved.                                                     #
#                                                                          #
# Redistribution and use in source and binary forms, with or without       #
# modification, are permitted provided that the following conditions       #
# are met:                                                                 #
#                                                                          #
#     * Redistributions of source code must retain the above copyright     #
#       notice, this list of conditions and the following disclaimer.      #
#     * Redistributions in binary form must reproduce the above copyright  #
#       notice, this list of conditions and the following disclaimer       #
#       in the documentation and/or other materials provided with the      #
#       distribution.                                                      #
#     * Neither the name of the South African Astronomical Observatory     #
#       (SAAO) nor the names of its contributors may be used to endorse    #
#       or promote products derived from this software without specific    #
#       prior written permission.                                          #
#                                                                          #
# THIS SOFTWARE IS PROVIDED BY THE SAAO ''AS IS'' AND ANY EXPRESS OR       #
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED           #
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE   #
# DISCLAIMED. IN NO EVENT SHALL THE SAAO BE LIABLE FOR ANY                 #
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL       #
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS  #
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)    #
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,      #
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN #
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE          #
# POSSIBILITY OF SUCH DAMAGE.                                              #
############################################################################

"""SALTFIT is a Module to provide general fitting of arrays by SALT talks.   
The task will provide non-interactiving fitting of 1- and 2-D arrays and 
allow fitting of general functions to the parameters.

It will provide an easy function to call to fit 1-D arrays of data including
fitting with errors in both dimensions, iterative fitting, and fitting
an array of functions.  The functions to allow fitting include
legendry, chebyshev, polynomial, and spline functions.


Author                 Version      Date
-----------------------------------------------
S. M. Crawford (SAAO)    1.0       10 Oct 2009

TODO
----
1.  Add 2-D fitting options
2.  SALTBIAS uses poly and this should be updated and renamed

LIMITATIONS
-----------

1.



"""

import numpy as np
from salterror import SaltError
from scipy import optimize, interpolate 
from scipy.special import legendre, chebyt


class power:
   """A class to produce a polynomial term of power n.  

      This has similar behavior to scipy.special.legendre

   """
 
   def __init__(self, n):
       self.n=int(n)

   def __call__(self, x):
       return x**self.n

#These Generalized parameter and fitting code are from the 
#scipy cookbook 

class Parameter:
    def __init__(self, value):
            self.value = value

    def set(self, value):
            self.value = value

    def __call__(self):
            return self.value

def fit(function, parameters, y, x = None, var=1, warn=False):
    def f(params):
        i = 0
        for p in parameters:
            p.set(params[i])
            i += 1
        return (y - function(x))/var

    if x is None: x = np.arange(y.shape[0])
    p = [param() for param in parameters] 
    #depreciated because no longer warning keyword?
    #return optimize.leastsq(f, p, full_output=1, warning=warn)
    return optimize.leastsq(f, p, full_output=1)




class curfit: 
   """Given an x and y data arrays,  find the best fitting curve
 
   * x - list or array of x data
   * y - list or array of y data
   * yerr - error on y data
   * coef - Initial coefficients for fit
   * function - function to be fit to the data:
                options include polynomial, legendre, chebyshev, or spline
   * order - order of the function that is fit


   """
   def __init__(self, x, y, yerr=None, coef=None, function='poly', order=3):

       #set up the variables
       self.x=x
       self.y=y
       if yerr is None:
           self.yerr=1
       else:
           self.yerr=yerr
       self.order=order

       self.set_func(function)
       self.set_coef(coef)



   def set_coef(self, coef=None):
       """Set the coefficients for the fits for poly, legendre, and chebyshev"""
       if coef is None: coef=np.ones(self.order+1)
       self.coef=coef


   def set_func(self, function):
       """Set the function that will be used. 
       * function - name of function to be used

       It will throw an error if an inappropriate function is given
       """
       self.function=function
       if self.function=='poly' or self.function=='polynomial' or self.function=='power':
           self.func=power
       elif self.function=='legendre':
           self.func=legendre
       elif self.function=='chebyshev':
           self.func=chebyt
       elif self.function=='spline':
           self.func=None
       else:
           msg='%s is not a valid function' % self.function
           raise SaltError(msg)

   def set_weight(self, err):
       """Set the weighting for spline fitting """
       if isinstance(err, np.ndarray):
          if err.any()!=0:
             self.weight=1/err
             return 
       self.weight=None

   def __call__(self, x):
       """Return the value of the function evaluated at x"""
       if self.function=='spline':
           return interpolate.splev(x, self.coef, der=0)
       v=x*0.0
       for i in range(self.order+1):
           v += self.coef[i]*self.func(i)(x)
       return v

   def erf(self, coef, x, y, v):
       """Error function to be minimized in least-squares fit"""
       self.set_coef(coef)
       return (y-self.__call__(x))/v

   def sigma(self, x, y):
       """Return the RMS of the fit """
       return (((y-self(x))**2).mean())**0.5

   def chisq(self, x, y, err):
       """Return the chi^2 of the fit"""
       return (((y-self(x))/err)**2).sum()

   def fit(self, task=0, s=None, t=None, full_output=1, warn=False):
       """Fit the function to the data"""
       if self.function=='spline':
          self.set_weight(self.yerr)
          self.results=interpolate.splrep(self.x, self.y, w=self.weight,  task=0, s=None, t=None, k=self.order, full_output=full_output)
          #w=None, k=self.order, s=s, t=t, task=task, 
          # full_output=full_output)
          self.set_coef(self.results[0])
               
       else:
           self.results=optimize.leastsq(self.erf, self.coef,
               args=(self.x, self.y, self.yerr), 
               full_output=full_output)
           self.set_coef(self.results[0])

class interfit(curfit):
   """Given an x and y data arrays,  find the best fitting curve.  
       After the initial fit, iterate on the solution to reject any 
       points which are away from the solution 
 
   * x - list or array of x data
   * y - list or array of y data
   * yerr - error on y data
   * coef - Initial coefficients for fit
   * function - function to be fit to the data:
                options include polynomial, legendre, chebyshev, or spline
   * order - order of the function that is fit
   * thresh - threshold for rejection
   * niter - number of times to iterate


   """
   def __init__(self, x, y, yerr=None, coef=None, function='poly', order=3, 
                thresh=3, niter=5):
       #set up the variables
       self.x_orig=x
       self.y_orig=y
       self.npts=len(self.x_orig)
       if yerr is None:
           self.yerr_orig=np.ones(self.npts)
       else:
           self.yerr_orig=yerr

       self.order=order
       self.thresh=thresh
       self.niter=niter

       self.set_func(function)
       self.set_coef(coef)
       self.set_mask(init=True)
       self.set_arrays(self.x_orig, self.y_orig, self.mask, err=self.yerr_orig)

   def set_mask(self, init=False):
       """Set the mask according to the values for rejecting points"""
       self.mask=np.ones(self.npts, dtype=bool)
       if init: return

       #difference the arrays
       diff=self.y_orig-self(self.x_orig)
       sigma=self.sigma(self.x, self.y)
       self.mask=(abs(diff)<self.thresh*sigma)
       

   def set_arrays(self, x, y, mask, err=None):
       """set the arrays using a mask"""
       self.x=x[mask]
       self.y=y[mask]
       if err is not None:
          self.yerr=err[mask]
 

   def interfit(self):
       """Fit a function and then iterate it to reject possible outlyiers"""
       self.fit()
       for i in range(self.niter):
           self.set_mask()
           self.set_arrays(self.x_orig, self.y_orig, self.mask, err=self.yerr_orig)
           self.fit()





def poly(x,y,order,rej_lo,rej_hi,niter):
    """linear least square polynomial fit with sigma-clipping

    * x = list of x data
    * y = list of y data
    * order = polynomial order
    * rej_lo = lower rejection threshold (units=sigma)
    * rej_hi = upper rejection threshold (units=sugma)
    * niter = number of sigma-clipping iterations

    This is currently used in SALTBIAS and should be made obselete
    """

    npts = []
    iiter = 0
    iterstatus = 1

# sigma-clipping iterations
    while (iiter < niter and iterstatus > 0):
        iterstatus = 0
        tmpx = []
        tmpy = []
        npts.append(len(x))
        coeffs = np.polyfit(x,y,order)
        fit = np.polyval(coeffs,x)
# calculate sigma of fit

        sig = 0
        for ix in range(npts[iiter]):
            sig = sig + (y[ix] - fit[ix])**2
        sig = math.sqrt(sig / (npts[iiter] - 1))
# point-by-point sigma-clipping test

        for ix in range(npts[iiter]):
            if (y[ix] - fit[ix] < rej_hi * sig and
                fit[ix] - y[ix] < rej_lo * sig):
                tmpx.append(x[ix])
                tmpy.append(y[ix])
            else:
                iterstatus = 1
        x = tmpx
        y = tmpy
        iiter += 1

# coeffs = best fit coefficients
# iiter = number of sigma clipping iteration before convergence

    return coeffs, iiter
