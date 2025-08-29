#if defined(_WIN32)
#define  _CRT_SECURE_NO_WARNINGS
#include <Windows.h>

#elif defined(linux) || defined(unix)
#include <unistd.h>
#include <sys/time.h>    
#include <sys/resource.h>
#endif

#include <stdio.h>

#include "cmd.h"
#include "camera.h"
#include "display.h"
#include "temperature.h"

#define IR_SAMPLE_VERSION "libirsample 1.2.5"


typedef enum {
    DEBUG_PRINT = 0,
    ERROR_PRINT,
    NO_PRINT,
}log_level_t;

//#define USER_FUNCTION_CALLBACK
//#define LOOP_TEST
//#define UPDATE_FW
