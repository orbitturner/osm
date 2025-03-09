/* @file config_parser.h 
 * @brief  basic configuration parse
 * @copyright(c) 2025  AGPL-3.0 License -  Umar Ba <jUmarB@protonmail.com> github.com/Jukoo  
 */
#if !defined (__osm_parseconfig_h )
#define  __osm_parseconfig_h 

#include <stdlib.h>
#include <stdio.h>
#include <unistd.h> 
#include <fcntl.h> 
#include <string.h> 

#define  __assign_symbole  "=" 

#if defined(ALLOW_OVERIDE_ENVAR) && ALLOW_OVERIDE_ENVAR  
# define  SHOULD_BE_OVERIDED  1 
#else  
# define  SHOULD_BE_OVERIDED  0 
#endif 

#define IS_EMPTY(__eline)(\
    (strlen(__eline) == 1)&&\
    ((0xa ==  *(eachline))& 0xff)\
    )

#define IS_COMMENT(__eline) (\
    (0x23 == *(eachline)& 0xff) ||\
    (0x3b == *(eachline)& 0xff)\
    )

#define  ESC(__char, __token) ({\
    char *_scape_character = strchr(__token , __char);\
    if(_scape_character) *_scape_character=0; \
    })

#define  OSM_CONFIG_MAX_ALLOW_KEY 0x80

extern char cfg_data[OSM_CONFIG_MAX_ALLOW_KEY][0xff] ;  

typedef struct __osm_cfg_t  osm_cfg_t;  
extern struct __osm_cfg_t 
{
  char _key_attr[0xff]; 
  char _val_attr[0xff]; 
} kv_attr[OSM_CONFIG_MAX_ALLOW_KEY] ; 
 

/* @fn read_config_file(const char *)
 * @brief read the config file 
 * @param  const char *  config filename 
 * @return int - 0 OK - otherwise error 
 */
extern  __inline__ int enhancing_envars (const char * __restrict__ __osm_config_file,
                                         struct __osm_cfg_t * __restrict__ __kv_attr)  
{
  int  fd  =  open(__osm_config_file, O_RDONLY) ; 
  if(~0 == fd) return  ~0 ; 

  if (dup2(fd , STDIN_FILENO))
  {
     close(fd) ; 
     return ~0 ; 
  }
 
  int items =0 ; 
  char eachline[0xff]={0}; 
  int  index = 0 ;  
  while((void *)0 != fgets( eachline, 0xff , stdin )) 
  { 
    //!NOTICE :Empty line  and comment lines are ignored # ; 
    if (IS_EMPTY(eachline) ||  IS_COMMENT(eachline)) continue ;  
     
    int index = 0,
       scan_current_line = 1 ; 

    char *token = (void *) 0 , 
         *current_line = eachline ,
         *sep   = __assign_symbole ; 

    while ((void*)0  !=  ( token =strtok(current_line,  sep))) 
    {
       if(scan_current_line == 1 ) 
       {
         scan_current_line^=1 ; 
         current_line = (void *)0 ;  
         strcpy((__kv_attr+index)->_key_attr , token) ; 
       }else 
       {
         ESC(0xa,  token) ; 
         strcpy((__kv_attr+index)->_val_attr , token);
         setenv((__kv_attr+index)->_key_attr,  (__kv_attr+index)->_val_attr, SHOULD_BE_OVERIDED /*?*/); 
         index=-~index ; 
       }
       
    }
    items=-~items ; 
  }

  close(fd) ; 
  return items  ;  
}

#endif 
