#include "sample.h"

int frame_idx = 0;

//load the stream frame info
void load_stream_frame_info(StreamFrameInfo_t* stream_frame_info)
{
#if defined(IMAGE_AND_TEMP_OUTPUT)
    {
        stream_frame_info->image_info.width = stream_frame_info->camera_param.width;
        stream_frame_info->image_info.height = stream_frame_info->camera_param.height/2;
        stream_frame_info->image_info.rotate_side = NO_ROTATE;
        stream_frame_info->image_info.mirror_flip_status = STATUS_NO_MIRROR_FLIP;
        stream_frame_info->image_info.pseudo_color_status = PSEUDO_COLOR_OFF;
        stream_frame_info->image_info.img_enhance_status = IMG_ENHANCE_OFF;
        stream_frame_info->image_info.input_format = INPUT_FMT_YUV422; //only Y14 or Y16 mode can use enhance and pseudo color
        stream_frame_info->image_info.output_format = OUTPUT_FMT_BGR888; //if display on opencv,please select BGR888

        stream_frame_info->temp_info.width = stream_frame_info->camera_param.width;
        stream_frame_info->temp_info.height = stream_frame_info->camera_param.height/2;
        stream_frame_info->temp_info.rotate_side = NO_ROTATE;
        stream_frame_info->temp_info.mirror_flip_status = STATUS_NO_MIRROR_FLIP;
        stream_frame_info->image_byte_size = stream_frame_info->image_info.width * stream_frame_info->image_info.height*2;
        stream_frame_info->temp_byte_size = stream_frame_info->temp_info.width * stream_frame_info->temp_info.height * 2;  //no temp frame input
    }
#elif defined(IMAGE_OUTPUT)
    stream_frame_info->image_info.width = stream_frame_info->camera_param.width;
    stream_frame_info->image_info.height = stream_frame_info->camera_param.height;
    stream_frame_info->image_info.rotate_side = NO_ROTATE;
    stream_frame_info->image_info.mirror_flip_status = STATUS_NO_MIRROR_FLIP;
    stream_frame_info->image_info.pseudo_color_status = PSEUDO_COLOR_OFF;
    stream_frame_info->image_info.img_enhance_status = IMG_ENHANCE_OFF;
    stream_frame_info->image_info.input_format = INPUT_FMT_YUV422; //only Y14 or Y16 mode can use enhance and pseudo color
    stream_frame_info->image_info.output_format = OUTPUT_FMT_BGR888; //if display on opencv,please select BGR888

    stream_frame_info->image_byte_size = stream_frame_info->image_info.width * stream_frame_info->image_info.height * 2;
    stream_frame_info->temp_byte_size = 0;

#elif defined(TEMP_OUTPUT)
    stream_frame_info->image_info.width = stream_frame_info->camera_param.width;
    stream_frame_info->image_info.height = stream_frame_info->camera_param.height;
    stream_frame_info->image_info.rotate_side = NO_ROTATE;
    stream_frame_info->image_info.mirror_flip_status = STATUS_NO_MIRROR_FLIP;
    stream_frame_info->image_info.pseudo_color_status = PSEUDO_COLOR_OFF;
    stream_frame_info->image_info.img_enhance_status = IMG_ENHANCE_OFF;
    stream_frame_info->image_info.input_format = INPUT_FMT_Y16; //only Y14 or Y16 mode can use enhance and pseudo color
    stream_frame_info->image_info.output_format = OUTPUT_FMT_BGR888; //if display on opencv,please select BGR888

    stream_frame_info->image_byte_size = stream_frame_info->image_info.width * stream_frame_info->image_info.height * 2;
    stream_frame_info->temp_byte_size = 0;
#endif



    create_data_demo(stream_frame_info);
}
void log_level_register(log_level_t log_level)
{
    switch(log_level)
    {
        case(DEBUG_PRINT):
        {
            iruvc_log_register(IRUVC_LOG_DEBUG);
            irtemp_log_register(IRTEMP_LOG_DEBUG);
            irproc_log_register(IRPROC_LOG_DEBUG);
            irparse_log_register(IRPARSE_LOG_DEBUG);
            break;
        }
        case(ERROR_PRINT):
        {
            iruvc_log_register(IRUVC_LOG_ERROR);
            irtemp_log_register(IRTEMP_LOG_ERROR);
            irproc_log_register(IRPROC_LOG_ERROR);
            irparse_log_register(IRPARSE_LOG_ERROR);
            break;
        }
        case(NO_PRINT):
        default:
        {
            iruvc_log_register(IRUVC_LOG_NO_PRINT);
            irtemp_log_register(IRTEMP_LOG_NO_PRINT);
            irproc_log_register(IRPROC_LOG_NO_PRINT);
            irparse_log_register(IRPARSE_LOG_NO_PRINT);
            break;
        }
    }

}

void print_and_record_version(void)
{
    puts(IR_SAMPLE_VERSION);
    puts(irproc_version());
    puts(irparse_version());
    puts(irtemp_version());
    puts(libiruvc_version());
#if defined(_WIN32)
    FILE* fp = fopen("..\\libs_version.txt", "wb");
#elif defined(linux) || defined(unix)
    FILE* fp = fopen("../libs_version.txt", "wb");
#endif
    fputs(IR_SAMPLE_VERSION, fp);fputs("\n", fp);
    fputs(irproc_version(), fp);fputs("\n", fp);
    fputs(irparse_version(), fp);fputs("\n", fp);
    fputs(irtemp_version(), fp);fputs("\n", fp);
    fputs(libiruvc_version(), fp);fputs("\n", fp);
    fclose(fp);
}


//user's call back function
void usr_test_func(void* frame, void* usr_param)
{
    //write your own callback code here

    StreamFrameInfo_t* stream_frame_info;
    stream_frame_info = (StreamFrameInfo_t*)usr_param;

    if (stream_frame_info == NULL)
    {
        return;
    }

    if ((frame != NULL) && (stream_frame_info->raw_frame != NULL))
    {
        memcpy(stream_frame_info->raw_frame, frame, stream_frame_info->camera_param.frame_size);
    }

    if (stream_frame_info->raw_frame != NULL)
    {
        raw_data_cut((uint8_t*)stream_frame_info->raw_frame, stream_frame_info->image_byte_size, \
            stream_frame_info->temp_byte_size, (uint8_t*)stream_frame_info->image_frame, \
            (uint8_t*)stream_frame_info->temp_frame);
        display_one_frame(stream_frame_info);
    }

    //printf("test_func:%d\n", ((unsigned short*)frame)[10]);
    printf("frame_idx:%d\n", frame_idx);
    frame_idx++;
}


int main(void)
{
    //set priority to highest level
#if defined(_WIN32)
    SetPriorityClass(GetCurrentProcess(), HIGH_PRIORITY_CLASS);
#elif defined(linux) || defined(unix)
    setpriority(PRIO_PROCESS, 0, -20);
#endif

    //version
    print_and_record_version();
    log_level_register(ERROR_PRINT);
#if defined(LOOP_TEST)
    for (int i = 0;i < 100;i++)
    {
#endif
        int rst;
        StreamFrameInfo_t stream_frame_info = { 0 };

        rst = ir_camera_open(&stream_frame_info.camera_param);
        if (rst < 0)
        {
            puts("ir camera open failed!\n");
            getchar();
            return 0;
        }
        vdcmd_set_polling_wait_time(10000);
        command_init();

#ifdef UPDATE_FW
        log_level_register(DEBUG_PRINT);
        FILE* fp = NULL;
        uint8_t firmware_data[256 * 1024] = { 0 };
        fp=fopen("AC010_FW_new.bin", "rb");
        fread(firmware_data, 1, sizeof(firmware_data), fp);
        fclose(fp);
        update_fw(firmware_data,sizeof(firmware_data));
        uvc_camera_close(); 
        puts("firmware updated");
        getchar();
        return 0;
#endif

        load_stream_frame_info(&stream_frame_info);

//user function callback mode
#ifdef USER_FUNCTION_CALLBACK
        display_init(&stream_frame_info);
        rst = ir_camera_stream_on_with_callback(&stream_frame_info, usr_test_func);

        //if (rst < 0)
        //{
        //    puts("ir camera stream on failed!\n");
        //    getchar();
        //    return 0;
        //}
        puts("ir camera stream on!\n");
        getchar();
        //Sleep(10000);
        //while (1);
        ir_camera_stream_off_with_callback(&stream_frame_info);
        display_release();

//multiple thread function mode
#else
        rst = ir_camera_stream_on(&stream_frame_info);
        if (rst < 0)
        {
            puts("ir camera stream on failed!\n");
            getchar();
            return 0;
        }

        pthread_t tid_stream, tid_display, tid_temperature, tid_cmd;

        pthread_create(&tid_temperature, NULL, temperature_function, &stream_frame_info);
        pthread_create(&tid_display, NULL, display_function, &stream_frame_info);
        pthread_create(&tid_stream, NULL, stream_function, &stream_frame_info);
        pthread_create(&tid_cmd, NULL, cmd_function, NULL);


        pthread_join(tid_stream, NULL);
        pthread_cancel(tid_display);
        pthread_cancel(tid_temperature);
        pthread_cancel(tid_cmd);
#endif

        uvc_camera_close();
#if defined(LOOP_TEST)
        printf("test cycle=%d\n",i);
    }
#endif
    puts("EXIT");
    getchar();
    return 0;
}