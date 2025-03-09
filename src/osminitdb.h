/* @file osminitdb.h 
 * @brief initial  database  
 * @copyright(c) 2025  AGPL-3.0 License -  Umar Ba <jUmarB@protonmail.com> github.com/Jukoo  
 */

#if !defined(__OSM_DB_H) 
#define  __OSM_DB_H 
 
#include <sqlite3.h> 
#include <stdio.h> 
#include <err.h> 

//!TODO :  Should be moved outside not hardcoded  in source file 
#define  SQL_CREATE_TABLE \
  "CREATE TABLE IF NOT EXISTS usage_history ("\
      "id INTEGER PRIMARY KEY AUTOINCREMENT,"\
      "timestamp DATETIME NOT NULL,"\
      "cpu_usage REAL NOT NULL,"\
      "ram_usage REAL NOT NULL,"\
      "disk_usage REAL NOT NULL)"


#define hdl_err(error_code , jmp_lablel, fcall , ...)\
  do {warn(#fcall __VA_ARGS__);goto jmp_lablel;}while(0) 

typedef int (*__user_sqlite3_cb) (void * ,  int , char** , char ** )   ; 
#define  __user_sqlite3_cb  user_callback  

char  *errmsg = (void *)0  ; 

/* @fn __initial_record(sqlite3 * ,  const char *) 
 * @bref make a record to file data base with sql statement 
 * @param sqlite3 *     -  instance  
 * @param const char *  -  SQL statement to execute  
 * @return int   SQLITE_OK(ok) otherwise failure 
 **/
extern __inline__  int __initial_record(sqlite3 *  __sql3 ,  const char *__restrict__ __SQL_STATEMENT)   
{ 
  int status = sqlite3_exec(__sql3, __SQL_STATEMENT , (void*)0 , (void*)0 , &errmsg ); 
  
  sqlite3_free(errmsg) ; 
  return status ; 
}
/* @fn init_db(const char *) 
 * @brief  initialize the database the file db will be created if not exists automaticly 
 * @param  const char *  - database file name 
 * @return int  status   - SQLITE_OK (ok) otherwise failure 
 */
extern  __inline__ int  init_db(const char * __restrict__ __database_filename) 
{
  int init_db_status= SQLITE_OK ;  
  sqlite3 * lightquery  ;  
   
   if(SQLITE_OK != (sqlite3_open_v2(__database_filename , &lightquery ,  SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE, (void *)0 )))  
   { 
     hdl_err(pstatus =~0 , __init_db_out ,init_db,"Fail to  open database %s", sqlite3_errmsg(lightquery)) ; 
   } 

   if (SQLITE_OK != __initial_record(lightquery  ,SQL_CREATE_TABLE)) 
   { 
     sqlite3_close(lightquery) ; 
     hdl_err(pstatus =~0 , __init_db_out ,__initial_record, "Fail to  put initial record  %s", sqlite3_errmsg(lightquery)) ; 
   }


  sqlite3_close(lightquery) ; 
__init_db_out:
   return  init_db_status; 

}





#endif //! __OSM_DB_H 
