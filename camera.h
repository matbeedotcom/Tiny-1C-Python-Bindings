#ifndef _CONFIG_H_
#define _CONFIG_H_

#include <stdio.h>
#include <string.h>
#include "data.h"
#include "libiruvc.h"
#include "libirparse.h"

#include "display.h"
#include "cmd.h"

#define IMAGE_AND_TEMP_OUTPUT	//normal mode:get 1 image frame and temp frame at the same time 
//#define IMAGE_OUTPUT	//only image frame
//#define TEMP_OUTPUT		//only temp frame


//open the ir camera,and get its parameter(width,height,fps,and so on)
int ir_camera_open(CameraParam_t* camera_param);

//close the ir camera 
int ir_camera_close(void);

//stream the ir camera by the stream info
int ir_camera_stream_on(StreamFrameInfo_t* stream_frame_info);

//stop the ir camera streaming by the stream info
int ir_camera_stream_off(StreamFrameInfo_t* stream_frame_info);

//stream thread,get the raw frame, cut to temperature and image, and then send to other thread
void* stream_function(void* threadarg);

//stream the ir camera by the camera parameter, and call the user's callback function.
int ir_camera_stream_on_with_callback(StreamFrameInfo_t* stream_frame_info, void* test_func);

//stop stream
int ir_camera_stream_off_with_callback(StreamFrameInfo_t* stream_frame_info);

#endif
