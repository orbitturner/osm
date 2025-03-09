/* @file  osmanager.c 
 * @brief handle osm process 
 * @copyright(c) 2025  AGPL-3.0 License -  Umar Ba <jUmarB@protonmail.com> github.com/Jukoo  
 */ 

#define _GNU_SOURCE
#include <stdlib.h> 
#include <stdio.h> 
#include <string.h> 
#include <sys/types.h> 
#include <sys/wait.h> 
#include <unistd.h> 
#include <signal.h> 
#include <stdarg.h> 
#include <errno.h>
#include <err.h> 
#include <time.h> 

#include "config_parser.h"
#include "osminitdb.h"

struct __osm_cfg_t kv_attr[OSM_CONFIG_MAX_ALLOW_KEY] = {0} ; 

#define CFG_FILE "/etc/osm/osmconf.cfg"

#define  __OSM_MAGIC_CODE {0x6f,0x73,0x6d,0x00}
#define  __osm_argument_vector(__ident , __size) \
  char *__ident[__size] = {(char[]) __OSM_MAGIC_CODE} 

/*
 * The NO_BLOCKING_MODE allow the osm  manager  to do some 
 * other tasks in paralel while the osm programme  running  
 *  By default is disabled  but  it can be enable by setting 1  
 */

#if  defined(NO_BLOCKING_MODE) && NO_BLOCKING_MODE > 0  
# define  WPID_OPT WNOHANG|WUNTRACED 
# define  atomic_t   sig_atomic_t  
#else 
# define  WPID_OPT  0 
# define   atomic_t  int 
#endif 

struct __osmargs_vector{
  char args[10][100] ; 
  int argn;  
} argshandler={{0},0};  

#define  __arghsprintf(...)  \
  sprintf( *(argshandler.args+argshandler.argn),__VA_ARGS__ ) 

typedef struct  sigaction  sigact_t ; 
#define  __nptr (void *) 0x00   

sigact_t sa ;  
atomic_t status = ~0;   

//!  sleep function but in millisec 
void msleep(int __millis)  ;

/* @fn osm_manager(void) 
 * @brief the osm handler funtion 
 * */
int  osm_manager(void) ;

/* @fn osm_sigcatch (int) 
 * @brief  catch the signal registred in osm_multsigcatch  
 * @param int       -- the signal number 
 * @return atomic_t -- the signal status  
 * */
atomic_t   osm_sigcatch(int __signal);  

/* @fn osm_sighandler(atomic_t) 
 * @brief determine what type of signal is delivred  
 * @param atomic_t  --  signal status 
 * @return int      --  signal status 
 */
int  osm_sighandler(atomic_t  __atomic_signal_code)  ; 

/* @fn osm_multsigcatch(int  , ... ) 
 * @brief  allow to specify more than one signal to  handler 
 *         it's automaticly passed to sigaction  handler 
 * @param int  -- how many signal 
 * @param variadic arguments  1..to.. N signal number 
 * */
void osm_multsigcatch(int __nsig, ...) ; 

/* @fn argsfmt_builder(char *const , ... )
 * @brief build argument using  string formating like printf function  
 * @param  char *const  --- string formating e.g  "string  formation  %i", 10 ...  
 *         only  the indicator after the '%' is placed as argument  the reste is ignored 
 *         but   very usefull as commentary  
 * @param variadic arguments  --- the argument value 
 *  
 */
void argsfmt_builder(char * const __fmt , ...) ; 


/* @fn argsentry( char (*)[100] , char *[100] ) 
 * @brief  transform the arguments array to  array of pointer 
 *         Require by execvp function the array of pointer must be end with null 
 * @param  char (*)[100] --  argument from argsfmt_builder 
 * @param  char *[100]   --  the output  
 * */
void argsentry(char  (*__osmargs)[100]  , char  *__args[100]) ; 


/* @fn enhancing_environment(struct  __osm_cfg_t []   ,  int) 
 * @brief  enhancing the environment variables by adding the builted in and 
 *         the variables that come from the configuration file 
 * @param  struct __osm_cfg_t[]  - array of structure __osm_cfg_t  list of key=value 
 * @param  int                   - how many environment variable found on configfile  
 * */
void enhancing_environment(struct  __osm_cfg_t * __restrict__ __kv_attr ,  int __how_many_envar_found) ;  

int main(int ac, char **av , char**env) 
{

  int  pstatus = EXIT_SUCCESS ; 
  //!Disable buffering on stdout for quick log 
  (void) setvbuf(stdout ,  __nptr ,  _IONBF , 0) ;

  //!NOTICE: Load the configuration file and dope the environement variable   
  int  __attribute__((unused)) how_many_envar_found = enhancing_envars(CFG_FILE, kv_attr);  

  //!NOTICE: initialize the database 
  char * db_file  =  getenv("DB_FILE") ;
  if (init_db(db_file)) 
  {
     pstatus =  EXIT_FAILURE ; 
     goto __eplg ;
  }
  /* !NOTICE  : Register signal action   for the handler */
  *(void**) &sa.sa_handler= osm_sigcatch ; 
  osm_multsigcatch(4, SIGTERM , SIGCHLD, SIGKILL , SIGINT);  
  
  pid_t  osm_spawn = fork() ; 
  if (~0 == osm_spawn) 
  {
     pstatus = EXIT_FAILURE ; 
     goto __eplg ; 
  }

  if(0 == osm_spawn) 
  {
    __osm_argument_vector(args_v , 100) ; 
    argsfmt_builder("Get the pid of the programme  %i", getpid()) ; 
    char pid[10]={0}; 
    sprintf(pid , "%i", getpid()); 
    setenv("OSM_PID" ,  pid, 0 ) ;
    argsentry(argshandler.args ,  args_v) ;  
    if (execvp(*(args_v) , args_v)) 
    {
       errx(errno, "having trouble to lauch osm application %s", strerror(*__errno_location())) ; 
       exit(EXIT_FAILURE) ; 
    }else  
    return status   ;  
  }else
  {
    osm_sighandler(status) ;  
    pstatus = osm_manager(); 
  }

__eplg: 
  return pstatus ;
} 


atomic_t  osm_sigcatch( int signal ) 
{  
 
  waitpid(~0,  &status, WPID_OPT)  ;  
  return status ;
}

int osm_manager(void) 
{
  int  how=0  ; 
#if  NO_BLOCKING_MODE
  /*  NOTICE : If you want to perform some other tasks in background  at the same time 
   *  while the osm programme running  you can put it in the  loop
   */
  int  proceed = 1 ;  
  while(proceed)
  { 
    if(status>=0) 
    { 
      osm_sighandler(status) ; 
      proceed^=1 ;  
    } 
      
    //! NOTICE : uncomment this code bellow to see how osm manager keep running in background  
    //msleep(1000); 
    //printf("."); 
   
  } 
  
  how = 0 ; 

#else 
  waitpid(~0 , &status ,  WPID_OPT) ;
  //msleep(100); 
  how= osm_sighandler(status) ;  
#endif 
    return how ; 
} 

int  osm_sighandler(atomic_t  sigatom) 
{  
 
  if(WIFEXITED(sigatom)) 
  {
    return WEXITSTATUS(sigatom) ; 
  }
  
  if(WIFSIGNALED(sigatom))
  {
    return  WSTOPSIG(sigatom) ;  
  }

  if(WIFSTOPPED(sigatom)) 
  {
    return WSTOPSIG(sigatom) ; 
  }
  
  return ~0 ; 
}

void osm_multsigcatch(int nsigs ,  ...) 
{
   va_list ap ; 
   va_start(ap , nsigs) ; 
   
   int nsig= ~0 ; 
   while(++nsig <  nsigs)
   {
     int signalnumber =  va_arg(ap , int) ; 
     sigaction(signalnumber ,  &sa , __nptr); 
   }
   va_end(ap);  
}

void argsfmt_builder (char * const fmt , ...) 
{
  va_list ap ;
  va_start(ap, fmt) ; 
  int i  = 0 ;  
  while ( *(fmt+i) !=0  ) 
  {  
    if( (*(fmt+i) & 0xff) == 0x25)  
    {
       char c =  *(fmt+(i+1))  ;  
       switch(c) 
       {
         case 'i':
         case 'd': 
           __arghsprintf("%i" ,(int) va_arg(ap,int)) ; 
           break ; 
         case 's':
           __arghsprintf("%s" , va_arg(ap,char *)) ; 
           break; 
       }
       argshandler.argn=-~argshandler.argn; 
    }
    i=-~i ; 
  }


  va_end(ap) ; 
}
void argsentry(char (*osmargs)[100]  , char  *args[100])  
{
   int  i = ~0 ; 
   while(++i < argshandler.argn ) 
     *(args+i+1) =   *(osmargs+i) ; 

   *(args+i+1) = __nptr ; 
}


void msleep(int millisec) 
{
  struct  timespec ts = { 
    .tv_sec  = ( millisec  / 1000 ) , 
    .tv_nsec = (millisec  % 10000) / 100000000UL 
  };
  
  while((clock_nanosleep(CLOCK_REALTIME, 0  , &ts  , __nptr)) !=0) ; 
}
