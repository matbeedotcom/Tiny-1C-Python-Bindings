#pragma once
#define HAVE_STRUCT_TIMESPEC

#include <stdio.h>
#include <stdint.h>
#include <malloc.h>
#include <pthread.h>
#include "libiruvc.h"
#include "libirtemp.h"

#if defined(_WIN32)
    #include <Windows.h>
#elif defined(linux) || defined(unix)
    #include <unistd.h>
    #include <semaphore.h>
    #include <sys/time.h>
#endif
//thread's semaphore
#if defined(_WIN32)
    extern HANDLE image_sem, temp_sem, image_done_sem, temp_done_sem;
#elif defined(linux) || defined(unix)
    extern sem_t image_sem, temp_sem, image_done_sem, temp_done_sem;
#endif
//thread's semaphore

extern uint8_t is_streaming;
extern int stream_time;  //unit:s
extern int fps;
typedef enum
{
    NO_ROTATE = 0,
    LEFT_90D,
    RIGHT_90D,
    ROTATE_180D
}RotateSide_t;

typedef enum
{
    STATUS_NO_MIRROR_FLIP = 0,
    STATUS_ONLY_MIRROR,
    STATUS_ONLY_FLIP,
    STATUS_MIRROR_FLIP
}MirrorFlipStatus_t;

typedef enum
{
    INPUT_FMT_Y14 = 0,
    INPUT_FMT_Y16,
    INPUT_FMT_YUV422,
    INPUT_FMT_YUV444,
    INPUT_FMT_RGB888
}InputFormat_t;

typedef enum
{
    OUTPUT_FMT_Y14 = 0,
    OUTPUT_FMT_YUV422,
    OUTPUT_FMT_YUV444,
    OUTPUT_FMT_RGB888,
    OUTPUT_FMT_BGR888,
}OutputFormat_t;

typedef enum
{
    PSEUDO_COLOR_ON=0,
    PSEUDO_COLOR_OFF,
}PseudoColor_t;

typedef enum
{
    IMG_ENHANCE_ON = 0,
    IMG_ENHANCE_OFF,
}ImgEnhance_t;

typedef struct {
    int cur_detected_low_cnt;
    int cur_detected_high_cnt;
    int switch_frame_cnt;
    uint8_t switched_flag;
    int cur_switched_cnt;
    int waiting_frame_cnt;
}AutoGainSwitchInfo_t;

typedef struct {
    EnvParam_t* org_env_param;
    EnvParam_t* new_env_param;
    uint8_t gain_flag;
    NucFactor_t* nuc_factor;
    EnvFactor_t* org_env_factor;
    EnvFactor_t* new_env_factor;
    uint16_t* nuc_table;
}TempCalInfo_t;

typedef struct {
    uint32_t width;
    uint32_t height;
    uint32_t byte_size;
    RotateSide_t rotate_side;
    MirrorFlipStatus_t mirror_flip_status;
    InputFormat_t  input_format;
    OutputFormat_t  output_format;
    PseudoColor_t  pseudo_color_status;
    ImgEnhance_t   img_enhance_status;
}FrameInfo_t;

typedef struct {
    uint8_t* raw_frame;
    uint8_t* image_frame;
    uint32_t image_byte_size;
    uint8_t* temp_frame;
    uint32_t temp_byte_size;
    FrameInfo_t image_info;
    FrameInfo_t temp_info;
    CameraParam_t camera_param;
}StreamFrameInfo_t;

//initial the pthread's cond and mutex
int init_pthread_sem();

//release the pthread's cond and mutex
int destroy_pthread_sem();

//create space for getting frames
int create_data_demo(StreamFrameInfo_t* stream_frame_info);

//destroy the space
int destroy_data_demo(StreamFrameInfo_t* stream_frame_info);