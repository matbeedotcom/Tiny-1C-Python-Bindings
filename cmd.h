#ifndef _CMD_H_
#define _CMD_H_


#define  _CRT_SECURE_NO_WARNINGS

#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#if defined(_WIN32)
#include <io.h>
#elif defined(linux) || defined(unix)
#include <unistd.h>
#endif

#include "libiruvc.h"
#include "libirtemp.h"
#include "data.h"
#include "temperature.h"

#define DEV_STATUS_NULL 0
#define DEV_STATUS_ROM 1
#define DEV_STATUS_CACHE 2

#define MXIC_MANU_ID 0xC2
#define WINBOND_MANU_ID 0xEF
#define GIGADEVICE_MANU_ID 0xC8
#define SECTOR_LEN 4096


#define KT_LEN 1201
#define SUCCESS 0
#define FAIL   -1

//init the command
void command_init(void);

//select the command
void command_sel(int cmd_type);

//command thread, get the input and select the command
void* cmd_function(void* threadarg);

//download firmware
void update_fw_cmd(const char* file_path);

#endif


