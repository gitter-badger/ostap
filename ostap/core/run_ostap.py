#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# =============================================================================
## @file run_ostap.py
#  
#     .oooooo.                .                        
#    d8P'  `Y8b             .o8                        
#   888      888  .oooo.o .o888oo  .oooo.   oo.ooooo.  
#   888      888 d88(  "8   888   `P  )88b   888' `88b 
#   888      888 `"Y88b.    888    .oP"888   888   888 
#   `88b    d88' o.  )88b   888 . d8(  888   888   888 
#    `Y8bood8P'  8""888P'   "888" `Y888""8o  888bod8P' 
#                                            888       
#                                           o888o      
#                                                    
#  Simple interactive PyRoot-based analysis environment to provide access
#  to zillions useful decorators for ROOT (and not only ROOT!) objects&classes  
# 
#  This file is a part of 
#  <a href="http://cern.ch/lhcb-comp/Analysis/Bender/index.html">Bender project</a>
#  <b>``Python-based Interactive Environment for Smart and Friendly Physics Analysis''</b>
#
#  The package has been designed with the kind help from
#  Pere MATO and Andrey TSAREGORODTSEV. 
#  And it is based on the 
#  <a href="http://cern.ch/lhcb-comp/Analysis/LoKi/index.html">LoKi project:</a>
#  <b>``C++ ToolKit for Smart and Friendly Physics Analysis''</b>
#
#  @date   2012-02-15
#  @author Vanya BELYAEV Ivan.Belyaev@itep.ru
#
# =============================================================================

""" Simple interactive PyRoot-based analysis environment
to provide access to zillions useful decorators for ROOT
(and not only ROOT) objects&classes

This file is a part of BENDER project:

``Python-based Interactive Environment for Smart and Friendly Physics Analysis''

The project has been designed with the kind help from Pere MATO and Andrey TSAREGORODTSEV.

And it is based on the LoKi project: ``C++ ToolKit for Smart and Friendly Physics Analysis''
"""
# =============================================================================
__author__  = 'Vanya BELYAEV Ivan.Belyaev@itep.ru'
__date__    = "2012-09-10"
__version__ = '$Revision$'
# =============================================================================
import ROOT, os  
ROOT.PyConfig.IgnoreCommandLineOptions = True
# =============================================================================

# =============================================================================
## parse arguments 
def parse_args ( args = [] ) :
    """ Parse arguments 
    """
    # =========================================================================
    import argparse 
    ## @class Collect
    #  simple parsing action to collect multiple arguments
    #  @code
    #  parser =...
    #  parser.add_argument('--foo',
    #  ... action  = Collect ,
    #  ... nargs   = '*'     ,
    #  ... default = []      ,
    #  ...)
    #  print parser.parse_args('a.txt b.txt --foo 1 2 3 --foo 4 -foo 5 '.split())
    #  @encode
    class Collect(argparse.Action):
        """Simple parsing action to collect multiple arguments
        >>> parser =...
        >>> parser.add_argument('--foo',
        ... action  = Collect ,
        ... nargs   = '*'     ,
        ... default = []      ,
        ...)
        >>> print parser.parse_args('a.txt b.txt --foo 1 2 3 --foo 4 -foo 5 '.split())
        """
        def __init__(self            ,
                     option_strings  ,
                     dest            ,
                     nargs    =None  ,
                     const    =None  ,
                     default  =None  , 
                     type     =None  ,
                     choices  =None  ,
                     required =False ,
                     help     =None  ,
                     metavar  =None  ) :
            if nargs == 0:
                raise ValueError('nargs for Collect actions must be > 0; if arg '
                                 'strings are not supplying the value to append, '
                                 'the append const action may be more appropriate')
            if const is not None and nargs != argparse.OPTIONAL:
                raise ValueError('nargs must be %r to supply const' % argparse.OPTIONAL)
            super(Collect, self).__init__(
                option_strings = option_strings ,
                dest           = dest           ,
                nargs          = nargs          ,
                const          = const          ,
                default        = default        ,
                type           = type           ,
                choices        = choices        ,
                required       = required       ,
                help           = help           ,
                metavar        = metavar        )
            
        def __call__(self, parser, namespace, values, option_string=None):
            items = argparse._copy.copy(argparse._ensure_value(namespace, self.dest, []))
            ## the only one important line: 
            for v in values : items.append(v)
            setattr(namespace, self.dest, items)
            
    
    from argparse import ArgumentParser 
    parser = ArgumentParser ( prog = 'ostap' )
    #
    group1 = parser.add_mutually_exclusive_group()    
    group1.add_argument ( 
        "-q" , "--quiet"       ,
        dest    = 'Quiet'      , 
        action  = 'store_true' ,
        help    = "Quite processing [default: %(default)s]" ,
        default = False        )
    group1.add_argument ( 
        "--verbose"     ,
        dest    = 'Verbose'    , 
        action  = 'store_true' ,
        help    = "Verbose processing [default: %(default)s]" ,
        default = False        )
    #
    parser.add_argument (
        "files" ,
        metavar = "FILE"  ,
        nargs   = '*'     , 
        help    = "ROOT/python/macro files to be opened/processed [default: %(default)s]" ,
        default = []  )
    #
    parser.add_argument ( 
        '-c'        ,
        '--command' ,
        dest    = 'Commands'   ,
        nargs   = '*'          ,
        action  = Collect      , 
        help    = "The commands for ``exec'' [default: %(default)s]" , 
        default = []           )
    #
    parser.add_argument ( 
        "-m" , "--macros"      ,
        metavar = "MACROS"     ,
        dest    = 'Macros'     ,
        nargs   = '*'          ,
        action  = Collect      , 
        help    = "ROOT macros to be loaded [default: %(default)s]",
        default = []  )
    #
    parser.add_argument (
        '--no-context'           ,
        action  = "store_false"  ,
        dest    = 'WithContext'  ,
        help    = "Do not use global Ostap context for the scripts",
        default = True           )
    #
    parser.add_argument ( 
        '--no-canvas'           ,
        dest    = 'canvas'      , 
        action  = 'store_false' , 
        help    = "Do not create canvas", 
        default = True          )
    #
    parser.add_argument ( 
        '--no-color'     ,
        dest    = 'Color'      , 
        action  = 'store_false' , 
        help    = "Do not use colorization", 
        default = True          )    
    #
    parser.add_argument ( 
        '--profile'     ,
        dest    = 'Profile'         , 
        action  = 'store_true'      , 
        help    = "Invoke profiler" , 
        default = False             )
    # 
    parser.add_argument ( 
        '--no-mt'                     ,        
        dest    = 'NoImplicitMT'      , 
        action  = 'store_true'        , 
        help    = "DisableImplicitMT" , 
        default = False               )
    # 
    group2 = parser.add_mutually_exclusive_group()
    group2.add_argument ( '-i' ,  
                         '--interactive' , dest='batch', 
                         action = 'store_false' , default = False ,
                         help = "Interactive shell/start_ipython" )
    group2.add_argument ( '-e' ,
                         '--embed' , 
                         action = 'store_true' ,
                         help = "Interactive embedded shell" )
    group2.add_argument ( '-s' ,
                         '--simple' ,
                         action = 'store_true' ,
                         help = "Simple python shell" )
    group2.add_argument ( '-b' ,
                         '--batch' ,
                         action = 'store_true' , default = False , 
                         help = "Batch processing: execute files and exit" )

    if not args :
        import sys 
        args = sys.argv[1:]
    
    v = [ a for a in args ]
    if '--' in v : v.remove('--')
    
    return parser.parse_args( v )

# =============================================================================
## do we run IPython?
from ostap.utils.basic import with_ipython

# =============================================================================

# =============================================================================
## parse arguments
# =============================================================================
arguments = parse_args()

# =============================================================================
# logging 
# =============================================================================
from ostap.logger.logger import getLogger
if arguments.Color and not arguments.batch :
    from ostap.logger.logger import make_colors
    make_colors()
    del make_colors
logger = getLogger( 'ostap' )
# =============================================================================

# =============================================================================
## suppress extra prints from logging  
# =============================================================================
if arguments.Quiet :
    
    import logging
    logger.info ( '(silent) Interactive Ostap session (steroid-enhanced PyROOT)')
    logging.disable ( logging.WARNING - 1 )

else:
    
    import logging
    level = logging.DEBUG-5  if arguments.Verbose else logging.INFO-1
    logging.disable ( level  )

    from ostap import banner
    logger.info ( "Welcome to Ostap\n" +  banner )
    logger.info ( __doc__ )
    del banner
    
    _vars = vars ( arguments )
    _keys = _vars.keys()
    _keys .sort() 
    logger.info ( 'Arguments  : ')
    for _k in _keys : logger.info ( '  %15s : %-s ' % ( _k , _vars[_k] ) )
    del _keys,_vars,_k,level  

# =============================================================================
## use profiling ?
if arguments.Profile :
    import cProfile as _profile
    _pr = _profile.Profile()
    
    def _end_profile_ ( prof ) :
        logger.debug ( 'End of profiling, generate profiling report' )
        prof.disable()
        import  cStringIO as StringIO 
        _sio   = StringIO.StringIO()
        sortby = 'cumulative'
        import pstats 
        _pstat = pstats.Stats( prof , stream=_sio).sort_stats('cumulative')
        _pstat.print_stats()
        print _sio.getvalue()
            

    import atexit 
    atexit.register ( _end_profile_ , _pr ) 
    _pr.enable()
    del _pr 
    logger.info ( 'Profiling is activated' )
    
# =============================================================================
## set ROOT into batch mode 
# =============================================================================
ROOT.gROOT.SetBatch ( arguments.batch )
if ROOT.gROOT.IsBatch() : logger.info ('Batch processing is activated') 


import ostap.fixes.fixes 

# =============================================================================
## Ostap startup: history, readlines, etc... 
# =============================================================================
import ostap.core.startup

# =============================================================================
## import everything from Ostap
# =============================================================================
if arguments.Quiet :
    from Ostap.Utils import mute
    with mute () : 
        from   ostap.core.load_ostap import *
    del mute
else :
    from ostap.core.load_ostap import *

    
# =============================================================================
## create default canvas
# =============================================================================
if arguments.canvas : 
    import ostap.plotting.canvas 
    logger.debug ( "Create the default canvas" )
    canvas    = ostap.plotting.canvas.getCanvas ()

# =============================================================================
## execute startup files 
# =============================================================================
## startup files to be executed:
_startups = ( '$OSTAPSTART'     ,  
              '$HOME/.ostap.py' ,
              '~/.ostap.py'     ,        
              './.ostap.py'     )
_executed = set() 
for _s in _startups : 
    import os
    _ss = _s 
    _ss =  os.path.expandvars ( _ss )
    _ss =  os.path.expandvars ( _ss )
    _ss =  os.path.expandvars ( _ss )
    _ss =  os.path.expanduser ( _ss )
    _ss =  os.path.expandvars ( _ss )
    if not os.path.exists     ( _ss ) : continue
    if not os.path.isfile     ( _ss ) : continue
    _ss =  os.path.abspath    ( _ss )
    if _ss in _executed           : continue
    ## execute it! 
    try :

        import runpy
        globs = runpy.run_path ( _ss , globals() , run_name = '__main__')
        globs = dict ( ( (k,v) for k,v in globs.items() if  not k.startswith('__') and not k.endswith('__')) )
        logger.debug('Symbols from %s: %s' % ( _s , globs.keys() ) )
        globals().update( globs )
        del globs
        
        _executed.add ( _ss )
        logger.info   ( "Startup file '%s' is executed"      % _s )
    except:
        logger.error  ( "Error in execution of '%s' startup" % _s , exc_info = True )
        

# =============================================================================
## cleanup a bit the context 
# =============================================================================
del parse_args, getLogger
del _startups,_executed,_s,_ss 

# =============================================================================
## execute the files, defined as arguments
# =============================================================================
root_files     = {}
root_macros    = []
python_scripts = []
PARAMETERS     = []
## _Load roo macro
def _load_macro_ ( macro , silent = True ) :
    """Load ROOT macro"""
    logger.debug  ("Try to load macro '%s'" % macro )
    if silent :
        from Ostap.Utils import rootError
        with rootError() : sc = ROOT.gROOT.LoadMacro ( macro )
    else :
        sc = ROOT.gROOT.LoadMacro ( macro )
        
    if sc :
        # - Interactive mode: print traceback and continue
        if arguments.batch :
            raise RuntimeError, 'Failure to load macro "%s" code:%d' % ( m , sc ) 
        else :
            logger.error       ('Failure to load macro "%s" code:%d' % ( m , sc ) )
            return False
        
    logger.debug ("Loaded macro   '%s'" % macro )
    del sc
    return True
    
## Load root macro/pattern
def load_macro ( pattern ) :
    """ Load root macro/pattern
    """
    ## expand the actual file name 
    pattern  = os.path.expandvars ( pattern )
    pattern  = os.path.expanduser ( pattern )
    pattern  = os.path.expandvars ( pattern )
    patetrn  = os.path.expandvars ( pattern )
    ##
    patterns = [ (pattern,'') ]
    if   pattern.endswith ( '++' ) : patterns += [ ( pattern [:-2] , '++' ) ]
    elif pattern.endswith ( '+'  ) : patterns += [ ( pattern [:-1] , '+'  ) ]

    import glob
    _glob   = False 
    _loaded = 0
    from  Ostap.Utils import rootError
    
    for pat,ext in patterns :
        
        for m in glob.iglob ( pat ) :

            _glob = True 
            if m in root_macros  : continue

            loaded = _load_macro_ ( m )
            if loaded : root_macros.append ( m )
            _loaded += loaded 
            
    if not _glob and not pattern in root_macros :
        m = pattern
        if _load_macro_ ( m ) : 
            root_macros.append ( m )
            _loaded += 1 
        
    return _loaded 
# =============================================================================    
## perform treatment of the file 
def treat_file ( f ) :
    """Perform treatment of the file 
    """
    fok = os.path.exists ( f ) and os.path.isfile ( f ) 
    name,dot,ext  = f.rpartition('.')
    if  name and dot and ext in ('root', 'ROOT' ) :
        
        logger.debug  ("Try  to open file '%s'" % f )
        try :
            from Ostap.TFileDeco import ROOTCWD 
            with ROOTCWD() :
                _f = ROOT.TFile.Open(  f , 'READ')
                root_files [ name ] = _f 
                logger.info ("Open ROOT file '%s'" % f )
                _f.ls()
        except :
            
            # - Batch mode:       just re-raise exception
            if arguments.batch :  raise
            
            # - Interactive mode: print traceback and continue 
            logger.error ('Failure to open ROOT file "%s"'  % f  , exc_info = True ) 
            
    ## execute python file 
    elif fok and name and dot and 'py' == ext  :  
        
        logger.debug  ("Try    to execute '%s'" % f )
        
        try :

            import runpy 
            globs = runpy.run_path (
                f , globals() if arguments.WithContext else {}  ,
                run_name = '__main__' )
            globs = dict ( ( (k,v) for k,v in globs.items() if  not k.startswith('__') and not k.endswith('__')) )
            logger.debug('Symbols from %s: %s' % ( f , globs.keys() ) )
            globals().update ( globs )
            del globs 
                
            logger.info  ("Executed       '%s'" % f )
            python_scripts.append ( f )
            
        except :
            
            # - Batch mode:       just re-raise exception
            if arguments.batch :  raise
            
            # - Interactive mode: print traceback and continue 
            logger.error ('Failure to execute "%s"'     % f  , exc_info = True ) 
            
    elif name and dot and ext.upper() in ( 'C'   ,   'C+' ,   'C++' ,
                                           'CPP' , 'CPP+' , 'CPP++' ,
                                           'CXX' , 'CXX+' , 'CXX++' ) :
        
        if not load_macro ( f )  :
            if arguments.batch :
                raise RuntimeError, "No macros are loaded for '%s' pattern" % f 
            else :
                logger.error       ("No macros are loaded for '%s' pattern" % f )

    ## execute Ostap-script 
    elif fok and name and dot and ext in ( 'ost' , 'ostp' , 'ostap' ) :
        
        logger.debug  ("Try    to execute '%s'" % f )
        
        try :
            
            ## this one is always executed with the context!!!
            import runpy
            globs = runpy.run_path ( f , globals() , run_name = '__main__')
            globs = dict ( ( (k,v) for k,v in globs.items() if  not k.startswith('__') and not k.endswith('__')) )
            logger.debug('Symbols from %s: %s' % ( f , globs.keys() ) ) 
            globals().update ( globs )
            del globs 
            
            python_scripts.append ( f , run_name = '__main__' )
            logger.info  ("Executed       '%s'" % f )
            
        except :
                
            # - Batch mode:       just re-raise exception
            if arguments.batch :  raise
            
            # - Interactive mode: print traceback and continue 
            logger.error ('Failure to execute "%s"'     % f  , exc_info = True ) 
            
    else :
                
        ## collect the argument as parameters
        PARAMETERS.append ( f )
        logger.debug ( 'Add argument %s to PARAMETERS' % f )

# =============================================================================
## load ROOT macros 
for pattern in arguments.Macros :
    if not load_macro ( pattern )  :
        if arguments.batch :
            raise RuntimeError, "No macros are loaded for '%s' pattern" % pattern 
        else :
            logger.error       ("No macros are loaded for '%s' pattern" % pattern )

# =============================================================================
## treat all input arguments/files 
for pattern in arguments.files :
    import glob
    _glob = False
    ##
    pattern  = os.path.expandvars ( pattern )
    pattern  = os.path.expanduser ( pattern )
    pattern  = os.path.expandvars ( pattern )
    patetrn  = os.path.expandvars ( pattern )
    ##
    for _f in glob.iglob ( pattern ) :
        _glob = True
        treat_file ( _f      )
    if not _glob :
        treat_file ( pattern )
del treat_file

    
# =============================================================================
## list names of opened ROOT files 
if root_files :
    logger.info("ROOT FILES    : %d (with '.root' extension)" % len ( root_files ) )
    keys = root_files.keys()
    keys.sort()
    _n = 0  
    for k in keys :
        _n +=  1
        rfile = root_files [k]
        okeys = rfile.keys ()
        okeys.sort()
        logger.info('%2d: %s #keys: %d: %s' % ( _n , k , len(okeys) , okeys ) )

# =============================================================================
## list all loaded root macros
if root_macros    : 
    logger.info ('ROOT MACROS   : %s' % root_macros    )
# =============================================================================
## list all executed ostap/python scripts 
if python_scripts :
    logger.info ('OSTAP SCRIPTS : %s' % python_scripts )
    
# =============================================================================
## dump all loaded 'parameters'
if PARAMETERS : 
    logger.info ('PARAMETERS    : %s' % PARAMETERS )

# =============================================================================
if '__main__' == __name__ : logger.info ( 'Ostap is ready'  ) 
else                      : logger.info ( 'Ostap is loaded' )

# =============================================================================
# The END 
# =============================================================================

