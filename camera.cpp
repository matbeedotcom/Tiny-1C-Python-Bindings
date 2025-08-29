#include "camera.h"

uint8_t is_streaming = 0;
int stream_time = 1000;  //unit:s
int fps;

int auto_gain_switch_frame_cnt = 0;
int overexposure_frame_cnt = 0;

//get specific device via pid&vid from all devices
int get_dev_index_with_pid_vid(int vid, int pid, DevCfg_t devs_cfg[])
{
    int cur_dev_index = 0;
    for (int i = 0; i < 64; i++)
    {
        if (devs_cfg[i].vid == vid && devs_cfg[i].pid == pid)
        {
            cur_dev_index = i;
            printf("name=%s\n", devs_cfg[i].name);
            return  cur_dev_index;
        }
    }
    return -1;
}

//set the camera_param from camera_stream_info and stream_index
CameraParam_t camera_para_set(DevCfg_t dev_cfg, int stream_index, CameraStreamInfo_t camera_stream_info[])
{
    CameraParam_t camera_param = { 0 };
    camera_param.dev_cfg = dev_cfg;
    camera_param.format = camera_stream_info[stream_index].format;
    camera_param.width = camera_stream_info[stream_index].width;
    camera_param.height = camera_stream_info[stream_index].height;
    camera_param.frame_size = camera_param.width * camera_param.height * 2;
    camera_param.fps = camera_stream_info[stream_index].fps[0];
    camera_param.timeout_ms_delay = 1000;

    return camera_param;
}

//open camera device by camera_param
int ir_camera_open(CameraParam_t* camera_param)
{
    DevCfg_t devs_cfg[64] = { 0 };
    CameraStreamInfo_t camera_stream_info[32] = { 0 };

    int rst = uvc_camera_init();
    if (rst < 0)
    {
        printf("uvc_camera_init:%d\n", rst);
        return rst;
    }

    memset(devs_cfg, 0, sizeof(DevCfg_t) * 64); //clear the device list before get list
    rst = uvc_camera_list(devs_cfg);
    if (rst < 0)
    {
        printf("uvc_camera_list:%d\n", rst);
        return rst;
    }

    int dev_index = 0;
    int pid, vid, resolution_idx = 0;

    pid = 0x5840;
    vid = 0x0BDA;
#if defined(IMAGE_AND_TEMP_OUTPUT)
    resolution_idx = 1;
#elif defined(IMAGE_OUTPUT) || defined(TEMP_OUTPUT)
    resolution_idx = 0;
#endif
    dev_index = get_dev_index_with_pid_vid(vid, pid, devs_cfg);
    if (dev_index < 0)
    {
        printf("can not get this device!\n");
        return dev_index;
    }
    printf("cur_index=%d\n", dev_index);

    rst = uvc_camera_info_get(devs_cfg[dev_index], camera_stream_info);
    if (rst < 0)
    {
        printf("uvc_camera_info_get:%d\n", rst);
        return rst;
    }

    rst = uvc_camera_open(devs_cfg[dev_index]);
    if (rst < 0)
    {
        printf("uvc_camera_open:%d\n", rst);
        return rst;
    }

    int i = 0;
    while (camera_stream_info[i].width != 0 && camera_stream_info[i].height != 0)
    {
        printf("width: %d,height: %d\n", camera_stream_info[i].width, camera_stream_info[i].height);
        i++;
    }
    *camera_param = camera_para_set(devs_cfg[dev_index], resolution_idx, camera_stream_info);

    return 0;
}

//close the device
int ir_camera_close(void)
{
    int rst = 0;
    if (is_streaming)
    {
        rst = uvc_camera_stream_close(KEEP_CAM_SIDE_PREVIEW);
        if (rst < 0)
            return rst;
        else
            is_streaming = 0;
    }
    uvc_camera_close();
    uvc_camera_release();
    return rst;
}

//stream start by stream_frame_info
int ir_camera_stream_on(StreamFrameInfo_t* stream_frame_info)
{
    int rst;

    init_pthread_sem();

    rst = uvc_camera_stream_start(stream_frame_info->camera_param, NULL);
    if (rst < 0)
    {
        printf("uvc_camera_stream_start:%d\n", rst);
        return rst;
    }
#if defined(TEMP_OUTPUT)
    rst = y16_preview_start(PREVIEW_PATH0, Y16_MODE_TEMPERATURE);
    if (rst < 0)
    {
        printf("y16_preview_start:%d\n", rst);
        return rst;
    }
#endif

    is_streaming = 1;
    return rst;
}

//stream stop
int ir_camera_stream_off(StreamFrameInfo_t* stream_frame_info)
{
    int rst = 0;

    rst = uvc_camera_stream_close(KEEP_CAM_SIDE_PREVIEW);
    if (rst < 0)
    {
        return rst;
    }

    destroy_data_demo(stream_frame_info);
    destroy_pthread_sem();
    is_streaming = 0;

    return rst;
}

void auto_gain_switch(uint16_t* temp_frame, FrameInfo_t* temp_info, \
    AutoGainSwitchInfo_t* auto_gain_switch_info)
{
    int rst = 0;
    uint16_t cur_gain = 0;
    uint8_t detect_flag = 0;
    ImageRes_t image_res = { temp_info->width, temp_info->height };
    GainSwitchParam_t gain_switch_param = { 0.1, (int)((130 + 273.15) * 16 * 4), \
                                            0.95, (int)((110 + 273.15) * 16 * 4) };

    //just switched, waiting for sensor loading
    if (auto_gain_switch_info->switched_flag)
    {
        //printf("just switched\n");
        auto_gain_switch_info->cur_switched_cnt++;
        if (auto_gain_switch_info->cur_switched_cnt > auto_gain_switch_info->waiting_frame_cnt)
        {
            auto_gain_switch_info->switched_flag = 0;
            auto_gain_switch_info->cur_switched_cnt = 0;
        }
        return;
    }

    rst = gain_switch_detect(temp_frame, image_res, gain_switch_param, &detect_flag);
    if (rst < IRPROC_SUCCESS)
    {
        printf("error\n");
        return;
    }

    if (detect_flag == 1)    //this frame needs switch to low
    {
        auto_gain_switch_info->cur_detected_low_cnt++;
        auto_gain_switch_info->cur_detected_high_cnt = 0;
    }
    else if (detect_flag == 2)    //this frame needs switch to high
    {
        auto_gain_switch_info->cur_detected_high_cnt++;
        auto_gain_switch_info->cur_detected_low_cnt = 0;
    }
    else    //clear switch flag
    {
        auto_gain_switch_info->cur_detected_low_cnt = 0;
        auto_gain_switch_info->cur_detected_high_cnt = 0;
    }

    //start to switch
    if ((auto_gain_switch_info->cur_detected_low_cnt > auto_gain_switch_info->switch_frame_cnt) || \
        (auto_gain_switch_info->cur_detected_high_cnt > auto_gain_switch_info->switch_frame_cnt))
    {
        auto_gain_switch_info->cur_detected_low_cnt = 0;
        auto_gain_switch_info->cur_detected_high_cnt = 0;
        auto_gain_switch_info->switched_flag = 1;
        auto_gain_switch_info->cur_switched_cnt = 0;

        rst = get_prop_tpd_params(TPD_PROP_GAIN_SEL, &cur_gain);
        if (rst < IRPROC_SUCCESS)
        {
            printf("error\n");
            return;
        }
        printf("temp_frame[100]:%d,%d,gain:%d,detect_flag:%d\n", temp_frame[100], temp_frame[100] / 64 - 273, cur_gain, detect_flag);

        if ((detect_flag == 1) && (cur_gain != 0))
        {
            printf("switch to low gain!\n");
            set_prop_tpd_params(TPD_PROP_GAIN_SEL, 0);//high->low
        }
        else if ((detect_flag == 2) && (cur_gain != 1))
        {
            printf("switch to high gain!\n");
            set_prop_tpd_params(TPD_PROP_GAIN_SEL, 1);//low->high
        }


    }
}

void avoid_overexposure(uint16_t* temp_frame, FrameInfo_t* temp_info, int close_frame_cnt)
{
    int rst = 0;
    uint16_t cur_gain = 0;
    uint8_t detect_flag = 0;
    static uint8_t last_detect_flag = 0;
    ImageRes_t image_res = { temp_info->width, temp_info->height };
    int low_gain_over_temp_data = (550 + 273) * 16 * 4;
    int high_gain_over_temp_data = (105 + 273) * 16 * 4;
    int over_temp_data = 0;
    float pixel_above_prop = 0.02;

    overexposure_frame_cnt++;
    if (overexposure_frame_cnt % 10 != 0)
    {
        return;
    }

    rst = get_prop_tpd_params(TPD_PROP_GAIN_SEL, &cur_gain);
    if (rst < IRPROC_SUCCESS)
    {
        printf("error\n");
        return;
    }

    if (cur_gain == 1)
    {
        over_temp_data = high_gain_over_temp_data;
    }
    else if (cur_gain == 0)
    {
        over_temp_data = low_gain_over_temp_data;
    }

    rst = overexposure_detect(temp_frame, image_res, over_temp_data, pixel_above_prop, \
        & detect_flag);
    if (rst < IRPROC_SUCCESS)
    {
        printf("error\n");
        return;
    }
    //printf("temp_frame[100]:%d,%d,gain:%d,detect_flag:%d\n", temp_frame[100], temp_frame[100] / 64 - 273, cur_gain, detect_flag);

    if (detect_flag == 1)
    {

        printf("OVEREXPOSURE, close shutter!!!\n");
        shutter_manual_switch(SHUTTER_CLOSE);
        shutter_sta_set(SHUTTER_CTL_DIS);
        last_detect_flag = 1;
        return;

    }
    if (overexposure_frame_cnt > close_frame_cnt)
    {
        if (last_detect_flag == 1)
        {
            printf("open shutter!!!\n");
            shutter_sta_set(SHUTTER_CTL_EN);
            shutter_manual_switch(SHUTTER_OPEN);
            last_detect_flag = 0;
        }
        overexposure_frame_cnt = 0;
        return;
    }
}

//stream thread.this function can get the raw frame and cut it to image frame and temperature frame
//and send semaphore to image/temperature thread
void* stream_function(void* threadarg)
{
    StreamFrameInfo_t* stream_frame_info;
    stream_frame_info = (StreamFrameInfo_t*)threadarg;
    if (stream_frame_info == NULL)
    {
        return NULL;
    }

    fps = stream_frame_info->camera_param.fps;

    printf("fps=%d\n", fps);
    int i = 0;
    int r = 0;
    int overtime_cnt = 0;
    int overtime_threshold = 3;
    AutoGainSwitchInfo_t auto_gain_switch_info = { 0 };
    auto_gain_switch_info.switch_frame_cnt = 5 * fps;
    auto_gain_switch_info.waiting_frame_cnt = 7 * fps;

    while (is_streaming && (i <= stream_time * fps))//display stream_time seconds
    {
#if defined(_WIN32)
        WaitForSingleObject(image_done_sem, INFINITE);
        WaitForSingleObject(temp_done_sem, INFINITE);
#elif defined(linux) || defined(unix)
        sem_wait(&image_done_sem);
        sem_wait(&temp_done_sem);
#endif
        r = uvc_frame_get(stream_frame_info->raw_frame);
        if (r < 0)
        {
            overtime_cnt++;
        }
        else
        {
            overtime_cnt = 0;
        }
        while (r < 0 && overtime_cnt >= overtime_threshold)
        {
#if defined(_WIN32)
            ReleaseSemaphore(image_sem, 1, NULL);
            ReleaseSemaphore(temp_sem, 1, NULL);
#elif defined(linux) || defined(unix)
            sem_post(&image_sem);
            sem_post(&temp_sem);
#endif
            ir_camera_stream_off(stream_frame_info);
            printf("uvc_frame_get failed\n ");
            return NULL;
        }

        if (stream_frame_info->raw_frame != NULL)
        {
            raw_data_cut((uint8_t*)stream_frame_info->raw_frame, stream_frame_info->image_byte_size, \
                stream_frame_info->temp_byte_size, (uint8_t*)stream_frame_info->image_frame, \
                (uint8_t*)stream_frame_info->temp_frame);
            if (stream_frame_info->temp_byte_size > 0)
            {
                //avoid_overexposure((uint16_t*)stream_frame_info->temp_frame, &stream_frame_info->temp_info, 10 * fps);
                //auto_gain_switch((uint16_t*)stream_frame_info->temp_frame, &stream_frame_info->temp_info, &auto_gain_switch_info);
            }
        }
#if defined(_WIN32)
        ReleaseSemaphore(image_sem, 1, NULL);
        ReleaseSemaphore(temp_sem, 1, NULL);
#elif defined(linux) || defined(unix)
        sem_post(&image_sem);
        sem_post(&temp_sem);
#endif
        //printf("raw data\n");
        i++;
        if (i == stream_time * fps)
        {
            is_streaming = 0;
            break;
        }
    }

#if defined(_WIN32)
    WaitForSingleObject(image_done_sem, INFINITE);
    WaitForSingleObject(temp_done_sem, INFINITE);
#elif defined(linux) || defined(unix)
    sem_wait(&image_done_sem);
    sem_wait(&temp_done_sem);
#endif

    ir_camera_stream_off(stream_frame_info);

    printf("stream thread exit!!\n");
    return NULL;
}

//stream start by stream_frame_info and callback the user's function while receiving the frame
int ir_camera_stream_on_with_callback(StreamFrameInfo_t* stream_frame_info, void* test_func)
{
    int rst;

    static UserCallback_t user_callback = { test_func, (void*)stream_frame_info };
    rst = uvc_camera_stream_start(stream_frame_info->camera_param, &user_callback);
    printf("uvc_camera_stream_start:%d\n", rst);
    if (rst < 0)
    {
        return rst;
    }
    is_streaming = 1;
#if defined(TEMP_OUTPUT)
    rst = y16_preview_start(PREVIEW_PATH0, Y16_MODE_TEMPERATURE);
    if (rst < 0)
    {
        printf("y16_preview_start:%d\n", rst);
        return rst;
    }
#endif
    //display 100s
#if defined(_WIN32)
    //while (1);
    //Sleep(100000);
#elif defined(linux) || defined(unix)
    sleep(100);
#endif

#ifdef OPENCV_ENABLE
    //cv::destroyAllWindows();
#endif

    return rst;
}

//stop stream
int ir_camera_stream_off_with_callback(StreamFrameInfo_t* stream_frame_info)
{
    int rst;
    rst = uvc_camera_stream_close(KEEP_CAM_SIDE_PREVIEW);
    if (rst < 0)
    {
        return rst;
    }
    is_streaming = 0;

    destroy_data_demo(stream_frame_info);
    return rst;
}
