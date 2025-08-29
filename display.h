#ifndef _DISPALAY_H_
#define _DISPALAY_H_
#define  _CRT_SECURE_NO_WARNINGS
#include <stdint.h>
#include <data.h>
#include "libirparse.h"
#include "libirprocess.h"
#include "cmd.h"
#include "temperature.h"

#define OPENCV_ENABLE
#ifdef OPENCV_ENABLE
#include <opencv2/imgproc.hpp>
#include <opencv2/highgui.hpp> 
#include <opencv2/highgui/highgui_c.h> 
//using namespace cv;
#endif

//initial the parameters for displaying
void display_init(StreamFrameInfo_t* stream_frame_info);

//release the parameters
void display_release(void);

//display one frame
void display_one_frame(StreamFrameInfo_t* stream_frame_info);

//display thread
void* display_function(void* threadarg);


#endif
