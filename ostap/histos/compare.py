#!/usr/bin/env python
# -*- coding: utf-8 -*-
# =============================================================================
## Copyright (c) Ostap developpers.
# =============================================================================  
## @file
#  Module with utilities for specific comparison of histograms/functions/shapes 
#  @date   2014-05-10
# =============================================================================
"""Module with utilities for specific comparison of histograms/functions/shapes
"""
# =============================================================================
__version__ = "$Revision$"
__author__  = "Vanya BELYAEV Ivan.Belyaev@itep.ru"
__date__    = "2011-06-07"
__all__     = () 
# =============================================================================
import ROOT             ## attention here!!
# =============================================================================
# logging 
# =============================================================================
from ostap.logger.logger import getLogger 
if '__main__' ==  __name__ : logger = getLogger( 'ostap.histos.compare' )
else                       : logger = getLogger( __name__ )
# =============================================================================
logger.debug ( 'Some specific comparison of histo-objects')
# =============================================================================
from   ostap.core.core     import hID,VE 
import ostap.histos.histos 
import ostap.histos.param
# =============================================================================
## Can 1D-histogram can be considered as ``constant'' ?
#  @code
#  histo = ...
#  print 'Is constant? %s ' % histo.is_constant( prob = 0.01 )
#  @endcode 
def _h1_constant_ ( h1 , prob = 0.10 , opts = '0Q' , rescale = False ) :
    """Can  1D-histogram be considered as constant ?
    >>> histo = ...
    >>> print 'Is constant? %s ' % histo.is_constant( prob = 0.01 ) 
    """
    #
    if rescale :
        h1_ = h1.rescale_bins(1)
        res = _h1_constant_ ( h1_ , prob , opts , rescale = False )
        del h1_
        return res
    
    if not isinstance ( h1 , ( ROOT.TH1D , ROOT.TH1F ) ) : return False 
    #
    r  = h1.Fit ( 'pol0', 'S' + opts )
    if 0 != r.Status() : 
        logger.warning("Can't fit with constant function %s" % r.Status() )
        r  = h1.Fit ( 'pol0', 'S' + opts )
        if 0 != r.Status() : return False
    #
    return prob <= r.Prob()

ROOT.TH1D.is_constant = _h1_constant_
ROOT.TH1F.is_constant = _h1_constant_

# =============================================================================
## compare the 1D-histograms trying to fit one with other
def _h1_cmp_fit_ ( h1              ,
                   h2              ,
                   rescale = False ,  
                   opts    = '0Q'  ) :
    """Compare histograms by refit of the first with functions,
    extracted from the second one

    >>> h1 = ... ## the first histo
    >>> h2 = ... ## the second histo
    >>> r  = h1.cmp_fit ( h2 )
    >>> if r : print r.Prob()    
    """    
    if rescale :
        h1_ = h1.rescale_bins   ( 1.0 )
        h2_ = h2.rescale_bins   ( 1.0 )
        res = _h1_cmp_fit_ ( h1_ , h2_ ,  rescale = False , opts = opts )
        del h1_, h2_
        return res 
    
    f2 = h2.asTF () 
    f2.ReleaseParameter ( 0 ) 

    rf = h1.Fit ( f2 , 'S' + opts ) 
    if 0 != rf.Status() :
        logger.warning("Can't fit with function " % rf.Status() )
        return None

    return rf

ROOT.TH1D.cmp_fit = _h1_cmp_fit_
ROOT.TH1F.cmp_fit = _h1_cmp_fit_ 


# =============================================================================
## compare the 1D-histograms trying to fit one 
def _h1_cmp_pdf_ ( h1               ,
                   h2               ,
                   rescale1 = False , 
                   rescale2 = False , 
                   draw     = True  ,
                   silent   = True  ) :
    """Compare histograms by refit of the first with functions,
    extracted from the second one

    >>> h1 = ... ## the first histo
    >>> h2 = ... ## the second histo
    >>> r  = h1.cmp_fit ( h2 )
    >>> if r : print r.Prob()    
    """    
    if rescale1 :
        h1_    = h1.rescale_bins   ( 1.0 )
        result = _h1_cmp_pdf_ ( h1_ , h2 , False   , rescale2 , draw , silent )
        del h1_
        return result
    
    if rescale2 :
        h2_    = h2.rescale_bins   ( 1.0 )
        result = _h1_cmp_pdf_ ( h1 , h2_ , rescale1 , False   , draw , silent )
        del h2_
        return result
        
    from ostap.fitting.basic      import H1D_pdf, Fit1D
    from ostap.fitting.background import Bkg_pdf 


    pdf2   = H1D_pdf    ( '_H1', h2 , density   = True , silent = True )
    model2 = Fit1D ( signal = pdf2 , background = Bkg_pdf( '_B2' , mass = pdf2.mass , power = 0 , tau = 0 ) ) 
    model2.b.fix(0)

    from ostap.utils.utils import invisibleCanvas 
    with invisibleCanvas() : 
        r2 , f2 = model2.chi2fitTo ( h1  , silent = silent , draw = draw , density = False , sumw2 = True )

    return r2 , f2.chiSquare()

ROOT.TH1D.cmp_pdf = _h1_cmp_pdf_
ROOT.TH1F.cmp_pdf = _h1_cmp_pdf_ 

# =============================================================================
## compare the 1D-histograms by chi2 
def _h1_cmp_chi2_ ( h1              ,
                    h2              ,
                    rescale = False ) :
    """Compare histograms by chi2
    >>> h1 = ... ## the first histo
    >>> h2 = ... ## the second histo (or function or anything else) 
    >>> chi2ndf,prob  = h1.cmp_chi2 ( h2 )    
    """
    if rescale :
        h1_    = h1.rescale_bins   ( 1.0 )
        h2_    = h2.rescale_bins   ( 1.0 )
        hmean  = h1_.mean()             ## normalization point        
        h1    /= h1_( hmean )
        h2    /= h2_( hmean )
        res = _h1_cmp_chi2_ ( h1_ , h2_ ,  rescale = False )
        del h1_, h2_
        return res 

    c2  = 0
    ndf = 0  
    for entry in h1.iteritems() :
        
        x     = entry[1]
        y1    = entry[2]
        
        y2    = h2 ( x.value() )

        c2   += y1.chi2 ( y2 )
        ndf  += 1 

    c2ndf = c2/ndf 
    return c2ndf, ROOT.TMath.Prob( c2 , ndf ) 

ROOT.TH1D.cmp_chi2 = _h1_cmp_chi2_
ROOT.TH1F.cmp_chi2 = _h1_cmp_chi2_ 

# =============================================================================
## Calculate chi2 for historgam and ``function''
def _h1_chi2_cmp_ ( h1                                    ,
                    func                                  ,
                    integral = False                      ,
                    select   = lambda x,y,v : True        ,
                    chi2     = lambda v1,v2 : v1.chi2(v2) ) :
    """Calculate chi2 for histogram and ``function''
    >>> h1   = ... ## the first histo
    >>> func = ... ## the the function 
    >>> chi2ndf,prob  = h1.chi2_cmp ( func , integral = False )
    """
    c2  = 0
    ndf = 0

    _func_  = lambda x,xl,xr : func(x)
    if   integral and hasattr ( func , 'integral' ) :
        _func_  = lambda x,xl,xr : func.integral(xl,xr)/(xr-xl) 
    elif integral and hasattr ( func , 'Integral' ) :  
        _func_  = lambda x,xl,xr : func.Integral(xl,xr)/(xr-xl) 
    elif integral :
        ## use numerical integration from scipy
        from ostap.math.intergal import integral as _integral_
        _func_  = lambda x,xl,xr : _integral_ ( func , xl , xr )/(xr-xl)
        
    for entry in h1.iteritems() :
        
        x    = entry[1]
        y1   = entry[2]

        
        xv   = x.value()
        xe   = x.error()
        xl   = xv - xe
        xr   = xv + xe
        
        y2   = _func_ ( x , xl , xr )        
        if not select ( x, y1 , y2 ) : continue

        c2  += chi2 ( y1 , y2 )
        ndf += 1
        
    c2ndf = c2/ndf 
    return c2ndf, ROOT.TMath.Prob( c2 , ndf ) 

ROOT.TH1D.chi2_cmp = _h1_chi2_cmp_
ROOT.TH1F.chi2_cmp = _h1_chi2_cmp_ 

# =============================================================================
## compare the 1D-historgams (as functions)
#  calculate
# \f$cos \theta = \frac{ f_1 \cdot f_2 } { \left|f_1\right|\left|f_2\right| }\f$
def _h1_cmp_costheta_ ( h1              ,
                        h2              ,
                        rescale = False ) :  
    """Compare the 1D-historgams (as functions)
    Calculate scalar product and get ``the angle'' from it
    
    >>> h1 = ... ## the first histo
    >>> h2 = ... ## the second histo
    >>> cos_theta  = h1.cmp_costheta ( h2 )
    
    """
    if rescale :
        h1_ = h1.rescale_bins   ( 1.0 )
        h2_ = h2.rescale_bins   ( 1.0 )
        res = _h1_cmp_costheta_ ( h1_ , h2_ , rescale = False )
        del h1_, h2_
        return res 
        
    f1 = h1.asFunc   ()
    f2 = h2.asFunc   ()

    lims = h1.xminmax()
    
    from ostap.math.integral import integral as _integral_
    vr1   = _integral_ ( lambda x : f1( x )**2    , lims[0] , lims[1] , limit = 200 , err = True )
    vr2   = _integral_ ( lambda x : f2( x )**2    , lims[0] , lims[1] , limit = 200 , err = True )
    vr12  = _integral_ ( lambda x : f1( x )*f2(x) , lims[0] , lims[1] , limit = 200 , err = True )

    return vr12 / ( vr1 * vr2 ) ** 0.5 

ROOT.TH1D.cmp_cos = _h1_cmp_costheta_
ROOT.TH1F.cmp_cos = _h1_cmp_costheta_ 

# =============================================================================
## calculate the norm of difference of scaled histograms/functions 
#  \f$ d = \left| f_1^{*} - f_2^{*}\right| \f$,
#  where \f$ f^* \f$-are scaled functions, such \f$ \left| f^*\right| = 1 \f$ 
def _h1_cmp_dist_ ( h1              ,
                    h2              ,
                    rescale = False ) : 
    """Calculate the norm of difference of scaled histograms/functions 
    |f1-f2|, such |f1|=1 and |f2|=1
    
    >>> h1 = ... ## the first histo
    >>> h2 = ... ## the second histo
    >>> diff = h1.cmp_dist ( h2 )
    
    """
    if rescale :
        h1_ = h1.rescale_bins   ( 1.0 )
        h2_ = h2.rescale_bins   ( 1.0 )
        res = _h1_cmp_dist_ ( h1_ , h2_ , rescale = False )
        del h1_, h2_
        return res 
    
    f1 = h1.asFunc   ()
    f2 = h2.asFunc   ()

    lims = h1.xminmax()
    
    from ostap.math.integral import integral as _integral_
    r1   = _integral_ ( lambda x : f1 ( x )**2    , lims[0] , lims[1] , limit = 200 , err = True )
    r2   = _integral_ ( lambda x : f2 ( x )**2    , lims[0] , lims[1] , limit = 200 , err = True )
    
    import math 
    
    sf1  = 1.0 / math.sqrt ( r1.value() ) 
    sf2  = 1.0 / math.sqrt ( r2.value() ) 
    
    d12  = _integral_ ( lambda x : (sf1*f1(x)-sf2*f2(x))**2 , lims[0] , lims[1] , limit = 200 , err = True )

    return d12 

ROOT.TH1D.cmp_dist = _h1_cmp_dist_
ROOT.TH1F.cmp_dist = _h1_cmp_dist_ 

# =============================================================================
## calculate the norm of difference of scaled histograms/functions 
#  \f$ d = \left| (f_1^{*}-f_2^{*})^2/(f_1^{*}f_2^*(x))\right| \f$,
#  where \f$ f^* \f$-are scaled functions, such \f$ \left| f^*\right| = 1 \f$ 
def _h1_cmp_dist2_ ( h1              ,
                     h2              ,
                     rescale = False ) :   
    """Calculate the norm of difference of scaled histograms/functions 
    |(f1-f2)*2/(f1*f2)|, such |f1|=1 and |f2|=1

    >>> h1 = ... ## the first histo
    >>> h2 = ... ## the second histo
    >>> diff = h1.cmp_dist2 ( h2 )
    
    """
    if rescale :
        h1_ = h1.rescale_bins   ( 1.0 )
        h2_ = h2.rescale_bins   ( 1.0 )
        res = _h1_cmp_dist2_ ( h1_ , h2_ , rescale = False )
        del h1_, h2_
        return res 

    f1 = h1.asFunc   ()
    f2 = h2.asFunc   ()

    lims = h1.xminmax()
         
    from ostap.math.integral import integral as _integral_
    r1   = _integral_( lambda x : f1 ( x )**2    , lims[0] , lims[1] , limit = 200 , err = True )
    r2   = _integral_( lambda x : f2 ( x )**2    , lims[0] , lims[1] , limit = 200 , err = True )
    
    import math 
    
    sf1 = 1.0 / math.sqrt ( r1.value() ) 
    sf2 = 1.0 / math.sqrt ( r2.value() ) 
    
    def  _func_   ( x ) :
        v1 =  sf1 * f1 ( x )
        v2 =  sf2 * f2 ( x )
        v  = (v1-v2)*(v1-v2)/abs(v1*v2)
        return v*v 
    
    d12  = _integral_ ( _func_ , lims[0] , lims[1] , limit = 200 , err = True )

    return d12 

ROOT.TH1D.cmp_dist2 = _h1_cmp_dist2_
ROOT.TH1F.cmp_dist2 = _h1_cmp_dist2_ 

# =============================================================================
## calculate and print some statistic for comparison
#  @code
#  h1 , h2 = ...
#  h1.cmp_prnt ( h2 )
#  @endcode 
def _h1_cmp_prnt_ ( h1              ,
                    h2              ,
                    head1   = ''    ,
                    head2   = ''    ,
                    title   = ''    ,
                    rescale = False ) : 
    """ Calculate and print some statistic information for two histos
    >>> h1 , h2 = ...
    >>> h1.cmp_prnt ( h2 ) 
    """
    if rescale :
        h1_ = h1.rescale_bins   ( 1.0 )
        h2_ = h2.rescale_bins   ( 1.0 )
        res = _h1_cmp_prnt_ ( h1_ , h2_ , head1 , head2 , title , rescale = False )
        del h1_, h2_
        return res 
    
    if not head1 : head1 = h1.GetName() 
    if not head2 : head2 = h1.GetName()
    
    logger.info ( ' %-15s |            | %-20s | %-20s | ' % ( title , head1 , head2 ) )
    
    logger.info ( ' %-15s | -MEAN-     | %20s | %20s | ' %
                  ( title    ,
                    h1  .mean     ().toString ('%+8.4g+-%-8.4g ') ,
                    h2  .mean     ().toString ('%+8.4g+-%-8.4g ') ) ) 
    logger.info ( ' %-15s | -RMS-      | %20s | %20s | ' %
                  ( title    ,
                    h1  .rms      ().toString ('%+8.4g+-%-8.4g ') ,
                    h2  .rms      ().toString ('%+8.4g+-%-8.4g ') ) )
    logger.info ( ' %-15s | -SKEWNESS- | %20s | %20s | ' %
                  ( title    ,
                    h1  .skewness ().toString ('%+8.4g+-%-8.4g ') ,
                    h2  .skewness ().toString ('%+8.4g+-%-8.4g ') ) )
    logger.info ( ' %-15s | -KURTOSIS- | %20s | %20s | ' %
                  ( title    ,
                    h1  .kurtosis ().toString ('%+8.4g+-%-8.4g ') ,
                    h2  .kurtosis ().toString ('%+8.4g+-%-8.4g ') ) )
    
    
ROOT.TH1D.cmp_prnt = _h1_cmp_prnt_
ROOT.TH1F.cmp_prnt = _h1_cmp_prnt_ 

# =============================================================================
_decorated_classes_ = (
    ROOT.TH1  , 
    ROOT.TH1F , 
    ROOT.TH1D ,
    )
_new_methods_       = (
    _h1_constant_     ,
    _h1_cmp_fit_      ,
    _h1_cmp_chi2_     ,
    _h1_chi2_cmp_     ,
    _h1_cmp_costheta_ ,
    _h1_cmp_dist_     ,
    _h1_cmp_dist2_    ,
    _h1_cmp_prnt_     ,
    )
# =============================================================================
if '__main__' == __name__ :
    
    from ostap.utils.docme import docme
    docme ( __name__ , logger = logger )
    
# =============================================================================
# The END 
# =============================================================================
