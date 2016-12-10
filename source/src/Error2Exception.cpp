// Include files
// ============================================================================
// ROOT 
// ============================================================================
#include "TError.h"
// ============================================================================
// Ostap
// ============================================================================
#include "Ostap/StatusCode.h"
#include "Ostap/Error2Exception.h"
// ============================================================================
// Python
// ============================================================================
// #include "Python.h"
// ============================================================================
// local 
// ============================================================================
#include "Exception.h"
// ============================================================================
/** Implementation file
 * 
 *  @date 2016-12-10 
 *  @author Vanya Belyaev Ivan.Belyaev@itep.ru
 */
// ============================================================================
namespace 
{
  // ==========================================================================
  /// (previous) error  handler 
  ErrorHandlerFunc_t s_handler    = nullptr   ;
  // ==========================================================================
  void errorHandler ( int         level    , 
                      Bool_t      abort    , 
                      const char* location , 
                      const char* message  ) 
  {
    //
    if ( gErrorIgnoreLevel == kUnset ) 
    { ::DefaultErrorHandler( kUnset - 1, kFALSE, "", "" ); }    
    // silently ignore ...
    if ( level  < gErrorIgnoreLevel ) { return ; }
    // error: throw exception 
    if      ( kError   <= level ) 
    {
      std::string msg  = location && location[0] ?
        message + std::string( " in " ) + location : std::string ( message ) ;
      std::string tag = 
        kError    == level ? "ROOT/Error"    :
        kBreak    == level ? "ROOT/Break"    :
        kSysError == level ? "ROOT/SysError" :
        kFatal    == level ? "ROOT/Fatal"    : "ROOT/error" ;
      Ostap::throwException ( tag + ": " + msg  , 
                              tag               , 
                              Ostap::StatusCode ( 10000 + level ) ) ;
    }
    // else if ( kWarning <= level ) 
    // {
    //  // python warning here 
    //  PyErr_WarnExplicit( NULL, (char*)msg, (char*)location, 0, (char*)"ROOT", NULL );
    // }
    else if ( nullptr != s_handler ) 
    { (*s_handler) ( level , abort , location , message ) ; }
    else 
    { ::DefaultErrorHandler( level , abort , location , message ); } 
  }
  // ==========================================================================
}
// ============================================================================
// use local error handler for ROOT 
// ============================================================================
bool Ostap::Utils::useErrorHandler ( const bool use ) 
{
  if      ( !use && GetErrorHandler() == &errorHandler ) 
  {
    if  ( nullptr != s_handler  && s_handler != &errorHandler ) 
    { SetErrorHandler ( s_handler ) ; return true ; }             // RETURN 
  }
  else if (  use && GetErrorHandler() != &errorHandler ) 
  {
    s_handler = GetErrorHandler() ; 
    SetErrorHandler ( &errorHandler ) ; 
    return true ;                                                  // RETURN 
  }
  return false ;
}  
// ============================================================================
// constructor: make use of local error handler
// ============================================================================
Ostap::Utils::ErrorSentry::ErrorSentry  () 
  : m_previous      ( Ostap::Utils::useErrorHandler ( true ) ) 
{}
// ============================================================================
// destructor: stop local error handler
// ============================================================================
Ostap::Utils::ErrorSentry::~ErrorSentry () 
{ if ( m_previous )  { Ostap::Utils::useErrorHandler ( false ) ; } }

// ============================================================================
// The END 
// ============================================================================
