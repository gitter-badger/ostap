#!/usr/bin/env python
# -*- coding: utf-8 -*-
# =============================================================================
## @file data.py 
#
#  Useful utilities to get access to datafiles & chains
#  Actualy it is just a little bit modified version (with globbing) of
#  original ``Ostap'' code by Alexander BARANOV
#
#  @code
#
#  >>> data  = Data('Bc/MyTree', '*.root' )
#  >>> chain = data.chain
#  >>> flist = data.files 
#
#  @endcode
# 
#  @author Vanya BELYAEV Ivan.Belyaev@itep.ru
#  @author Alexander BARANOV a.baranov@cern.ch
#  @date   2014-06-08
#
# =============================================================================
""" Useful utilities to get access to datafiles & chains

Actualy it is a little bit modified version (with globbing) of
the original ``Ostap'' code by Alexander BARANOV

>>> data  = Data('Bc/MyTree', '*.root' )
>>> chain = data.chain
>>> flist = data.files 

>>> data  = Data('Bc/MyTree', 'a.root' )
>>> chain = data.chain
>>> flist = data.files 

>>> data  = Data('Bc/MyTree', [ 'a.root' , 'b.root' ] )
>>> chain = data.chain
>>> flist = data.files 

>>> data  = DataAndLumi('Bc/MyTree', '*.root' )
>>> chain = data.chain
>>> flist = data.files 
>>> lumi  = data.lumi
>>> print data.getLumi() 

>>> data  = DataAndLumi('Bc/MyTree', [ 'A/*.root' , 'B/B/D/*.root' ] )
>>> chain = data.chain
>>> flist = data.files 
>>> lumi  = data.lumi
>>> print data.getLumi() 

"""
# =============================================================================
__version__ = "$Revision$"
__author__  = "Vanya BELYAEV Ivan.Belyaev@itep.ru"
__date__    = "2014-06-08"
__all__     = (
    'Files'       , ## collect files  
    'Data'        , ## collect files and create     TChain
    'Data2'       , ## collect files and create two TChain objects 
    )
# =============================================================================
import ROOT, glob 
# =============================================================================
# logging 
# =============================================================================
from   ostap.logger.logger import getLogger 
if '__main__' ==  __name__ : logger = getLogger ( 'ostap.trees.data' )
else                       : logger = getLogger ( __name__     )
# =============================================================================
if not hasattr ( ROOT.TTree , '__len__' ) :  
    ROOT.TTree. __len__ = lambda s : s.GetEntries()
# =============================================================================
## @class Files
#  Simple utility to pickup the list of files 
#  @author Vanya BELYAEV Ivan.Belyaev@itep.ru
#  @author Alexander BARANOV a.baranov@cern.ch
#  @date   2014-06-08  
class Files(object):
    """Simple utility to pickup the list of files     
    >>> data  = Files( '*.root' )
    >>> files = data.files 
    """    
    def __init__( self                  ,
                  files                 ,
                  description = ""      ,
                  maxfiles    = 1000000 ,
                  silent      = False   ) :  
        #
        self.files        = []
        self.patterns     = files
        self.description  = description
        self.maxfiles     = maxfiles
        self.silent       = silent 
        # 
        if isinstance ( files , str ) : files = [ files ]
        #
        _files = set() 
        for pattern in files :
            _fs = self.globPattern ( pattern )
            for _f in _fs : _files.add ( _f )
                
        if not self.silent :
            logger.info ('Loading: %s  #patterns/files: %s/%d' % ( self.description ,
                                                                   len(  files )    , 
                                                                   len( _files )    ) )
        from Ostap.progress_bar import ProgressBar 
        with ProgressBar ( max_value = len(_files) , silent = self.silent ) as bar :
            self.progress = bar 
            for f in _files : 
                if len ( self.files ) < self.maxfiles : self.treatFile  ( f )
                else :
                    logger.warning ('Maxfiles limit is reached %s ' % self.maxfiles )
                    break

        if not self.silent :
            logger.info ('Loaded: %s' % self )

    ## 
    def globPattern ( self , pattern ) :
        return [ f in glob.iglob ( pattern ) ]
        
    ## the specific action for each file 
    def treatFile ( self, the_file ) :
        self.files.append ( the_file )
        self.progress += 1
        
    ## printout 
    def __str__(self):
        """
        The specific printout
        """
        return "<#files: %4d>" % len ( self.files ) 
    
    def __repr__( self )  : return self.__str__()
    
# =============================================================================
## @class Data
#  Simple utility to access to certain chain in the set of ROOT-files
#  @author Vanya BELYAEV Ivan.Belyaev@itep.ru
#  @author Alexander BARANOV a.baranov@cern.ch
#  @date   2014-06-08  
class Data(Files):
    """Simple utility to access to certain chain in the set of ROOT-files
    >>> data  = Data('Bc/MyTree', '*.root' )
    >>> chain = data.chain
    >>> flist = data.files 
    """
    
    def __init__( self                  ,
                  chain                 ,
                  files       = []      ,
                  description = ''      , 
                  maxfiles    = 1000000 ,
                  silent      = False   ) :  
        
        self.e_list1    = set()  
        self.chain      = ROOT.TChain ( chain )
        if not description :
            description = self.chain.GetName()
        Files.__init__( self , files , description  , maxfiles , silent )
        
    ## the specific action for each file 
    def treatFile ( self, the_file ) :
        """Add the file to TChain
        """
        Files.treatFile ( self , the_file )
        
        ## suppress Warning/Error messages from ROOT 
        from ostap.logger.utils import rootError
        with rootError() :
            
            tmp = ROOT.TChain ( self.chain.GetName() )
            tmp.Add ( the_file )
        
            ##if 0 < tmp.GetEntries() and 0 < tmp.GetEntry(0) : self.chain.Add ( the_file )
            if 0 < tmp.GetEntries() : self.chain.Add ( the_file )
            else                  :
                logger.warning("No/empty chain '%s' in file '%s'" % ( self.chain.GetName() , the_file ) ) 
                self.e_list1.add ( the_file ) 
                
    ## printout 
    def __str__(self):
        return  "<#files: {}; Entries: {}>".format ( len ( self.files ) ,
                                                     len ( self.chain ) )
    
# =============================================================================
## @class Data2
#  Simple utility to access two chains in the set of ROOT-files
#  @author Vanya BELYAEV Ivan.Belyaev@itep.ru
#  @author Alexander BARANOV a.baranov@cern.ch
#  @date   2014-06-08  
class Data2(Data):
    """Simple utility to access to certain chain in the set of ROOT-files    
    >>> data  = Data('Bc/MyTree', '*.root' )
    >>> chain = data.chain
    >>> flist = data.files 
    """
    
    def __init__( self                  ,
                  chain1                ,
                  chain2                , 
                  files       = []      ,
                  description = ''      ,
                  maxfiles    = 1000000 ,
                  silent      = False   ) :  
        
        self.e_list2 = set()
        self.chain2  = ROOT.TChain ( chain2 )
        if not description :
            description = chain1.GetName() if hasattr ( chain1 , 'GetName' ) else str(chain1)
            description = "%s&%s" % ( description , self.chain2.GetName() )
        Data.__init__( self , chain1 , files , description , maxfiles , silent )
        self.chain1  = self.chain 
        
    ## the specific action for each file 
    def treatFile ( self, the_file ) :
        """
        Add the file to TChain
        """
        Data.treatFile ( self , the_file )

        ## suppress Warning/Error messages from ROOT 
        from ostap.logger.utils import rootError
        with rootError() :
            
            tmp = ROOT.TChain ( self.chain2.GetName() )
            tmp.Add ( the_file )
        
            ##if 0 < tmp.GetEntries() and 0 < tmp.GetEntry(0) : self.chain2.Add ( the_file ) 
            if 0 < tmp.GetEntries() : self.chain2.Add ( the_file ) 
            else                  :
                logger.warning("No/empty chain '%s' in file '%s'" % ( self.chain2.GetName() , the_file ) ) 
                self.e_list2.add ( the_file ) 
        
    ## printout 
    def __str__(self):    
        return  "<#files: {}; Entries1: {}; Entries2: {}>".format ( len ( self.files  ) ,
                                                                    len ( self.chain  ) ,
                                                                    len ( self.chain2 ) )
    
    
# =============================================================================
if '__main__' == __name__ :
    
    from ostap.utils.docme import docme
    docme ( __name__ , logger = logger )
    
# =============================================================================
# The END 
# =============================================================================
