# libirsample program structure and user's manual



## 1. Program structure

![](./irsample_structure.png)

As shown, the sample includes these modules: sample, camera, display, temperature, cmd. The function of each module as follows:

**sample module**: After configuring the relevant parameters in sample.cpp, call the camera module to establish a connection with the infrared camera, and stream the image. Later sample module will create 4 threads: stream, display,  temperature, and cmd, to process the corresponding information.

**camera module**: Used to obtain the information of infrared cameras. When stream thread obtains the original infrared frames, the raw frames will be divided into the image information(image frame) and temperature information(temp frame).At the same time, the signals will be transmitted to the corresponding modules. When image frame and temp frame's processing is compete, the signals will be transmitted back to camera thread, to continue the next loop.

**display module**: After obtaining the image frame information, according to the configuration of the parameters in frame_info, the image will be processed by data format conversion, flipping, mirroring, rotation and so on. In the end, it calls opencv to display the processed image.

**temperature module**: After obtaining the temperature frame information, according to the configuration of the parameters in frame_info, the image will be processed by data format conversion, flipping, mirroring, rotation and so on.

**cmd module**: Sending the corresponding command to the infrared camera.



## 2. Program compilation method

On windows, a complete VS2019 project is provided in the libir_sample folder, the opencv library and pthreadVC2.dll are required to run the example (already placed).

On linux, there are `Makefile` and `CMakeLists.txt` files in libir_sample, you need to remove the opencv2 folder at compile time (Linux needs to install it separately). If you don't need opencv, you can comment `#define OPENCV_ENABLE` in the display.h file, and comment opencv related content in the `Makefile` or `CMakeLists.txt` before compiling.





## 3. User's manual

### 3.1 Camera connection

In the main function of sample.cpp, the corresponding camera is selected by calling ir_camera_oepn, and get the relevant parameters information(stream_frame_info) from the camera.

After obtaining the parameter information, it is required to call load_stream_frame_info function to supplement  the settings for display and temperature modules, such as: width and height information, rotation/mirror/flip settings, pseudo color included in the library enable switch, input and output frame format, apply for buffer space, and so on.

```c
        stream_frame_info->image_info.width = stream_frame_info->camera_param.width;
        stream_frame_info->image_info.height = stream_frame_info->camera_param.height / 2;
        stream_frame_info->image_info.rotate_side = LEFT_90D;
        stream_frame_info->image_info.mirror_flip_status = STATUS_MIRROR_FLIP;
        stream_frame_info->image_info.pseudo_color_status = PSUEDO_COLOR_ON;
		stream_frame_info->image_info.img_enhance_status = IMG_ENHANCE_OFF;
        stream_frame_info->image_info.input_format = INPUT_FMT_YUV422; 	//only Y14 or Y16 mode can use enhance and pseudo color
        stream_frame_info->image_info.output_format = OUTPUT_FMT_BGR888; //if display on opencv,please select BGR888

        stream_frame_info->temp_info.width = stream_frame_info->camera_param.width;
        stream_frame_info->temp_info.height = stream_frame_info->camera_param.height / 2;
        stream_frame_info->temp_info.rotate_side = NO_ROTATE;
        stream_frame_info->temp_info.mirror_flip_status = STATUS_NO_MIRROR_FLIP;
        stream_frame_info->image_byte_size = stream_frame_info->image_info.width * stream_frame_info->image_info.height * 2;
        stream_frame_info->temp_byte_size = stream_frame_info->temp_info.width * stream_frame_info->temp_info.height * 2;
```

The following is the definition of the StreamFrameInfo_t structure. Note these parameters:

FrameInfo_t-width/height: width and height parameters, need to be filled in.

FrameInfo_t-byte_size: byte size of current frame_info, the display_image_process function in display.cpp will be filled in automatic according to the data format while streaming. 

FrameInfo_t-rotate_side/mirror_flip_status: flip/mirror/rotate and so on status, need to be filled in.

FrameInfo_t-input_format/output_format: the data format of input and output frame, such as Y14 data input, RGB888 output, and so on, need to be filled in.

FrameInfo_t-pseudo_color_status: the switch of pseudo color. The pseudo color mapping table in the libirprocess library will be called, if the switch is turned on. Need to be filled in.

FrameInfot-imgenhance_status:If the switch of image stretch. The image stretching algorithm in libirprocess library will be called to stretch Y14 / Y16 data, Need to be filled in.

StreamFrameInfo_t-image_byte_size/temp_byte_size: the byte size of the input frame. If it is filled in 0, then no data can be received. Fill it in according to the size of the data that needs to be split.

```c
typedef struct {
    uint32_t width;
    uint32_t height;
    uint32_t byte_size;
    RotateSide_t rotate_side;
    MirrorFlipStatus_t mirror_flip_status;
    InputFormat_t  input_format;
    OutputFormat_t  output_format;
    PsuedoColor_t  pseudo_color_status;
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
```



### 3.2 Streaming control

After opening the device and getting the relevant parameter information, and filling in the configuration of display and temperature modules, you can call ir_camera_stream_on or ir_camera_stream_on_with_callback(open the macro USER_FUNCTION_CALLBACK to call the custom callback function)  function to stream.In the display_function of display.cpp, display_one_frame will be called after waiting for the signal of one frame to arrive.

```c
	while (is_streaming)
	{
#if defined(_WIN32)
		WaitForSingleObject(image_sem, INFINITE);	//waitting for image singnal 
#elif defined(linux) || defined(unix)
		sem_wait(&image_sem);
#endif
		display_one_frame(stream_frame_info);
#if defined(_WIN32)
		ReleaseSemaphore(image_done_sem, 1, NULL);
#elif defined(linux) || defined(unix)
		sem_post(&image_done_sem);
#endif
		i++;
	}
```



In the display_one_frame fucntion, display_image_process will be called to process the image data format. According to the input and output data formats (input_format, output_format) and pseudo-color settings (pseudo_color_status ) of stream_frame_info->image_info, the libirparse will be called to do corresponding conversion. And do flip, mirror, rotation operations according to the mirror_flip_status and rotate_side of stream_frame_info->image_info. Finally, it is displayed by the imshow function of opencv.

```c
	display_image_process(stream_frame_info->image_frame, pix_num, &stream_frame_info->image_info);
	if ((stream_frame_info->image_info.rotate_side == LEFT_90D)|| \
		(stream_frame_info->image_info.rotate_side == RIGHT_90D))
	{
		width = stream_frame_info->image_info.height;
		height = stream_frame_info->image_info.width;
	}

	mirror_flip_demo(&stream_frame_info->image_info, image_tmp_frame2, \
					stream_frame_info->image_info.mirror_flip_status);
	rotate_demo(&stream_frame_info->image_info, image_tmp_frame2, \
				stream_frame_info->image_info.rotate_side);

	cv::Mat image = cv::Mat(height, width, CV_8UC3, image_tmp_frame2);
	putText(image, frameText, cv::Point(11, 11), cv::FONT_HERSHEY_PLAIN, 1, cv::Scalar::all(0), 1, 8);
	putText(image, frameText, cv::Point(10, 10), cv::FONT_HERSHEY_PLAIN, 1, cv::Scalar::all(255), 1, 8);
	cv::imshow("Test", image);
	cvWaitKey(5);
```



In the stream_function function, you can control the duration of the graph by setting the value of stream_time. The sample is set to 100*fps display time. Without frame loss or timeout, the expected time of display  is 100 seconds.

        int stream_time = 100;  //unit:s
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


### 3.3 Command send

In the command_sel function of cmd.cpp, the corresponding commands are triggered by input different numbers.

```c
//command thread function
void* cmd_function(void* threadarg)
{
	int cmd = 1;
	while (is_streaming)
	{
		scanf("%d", &cmd);
		if (is_streaming)
		{
			command_sel(cmd);
		}
	}
	printf("cmd thread exit!!\n");
	return NULL;
}
```



### 3.4 Temperature measurement

In the temperature_function function of temperature.cpp, when got one frame signal arrived, the counter add 1. Every 25 frames call the temperature measurement once, which supports 3 measurement modes: point, line and area.

```c
	while (is_streaming)
	{
#if defined(_WIN32)
		WaitForSingleObject(temp_sem, INFINITE);	//waitting for temp singnal 
#elif defined(linux) || defined(unix)
		sem_wait(&temp_sem);
#endif
		if (timer % 25 == 0)	//colect one frame at an interval of 25 frames 
		{
			//point_temp_demo(temp_frame, *image_res);
			line_temp_demo((uint16_t*)stream_frame_info->temp_frame, temp_res);
			//rect_temp_demo(temp_frame, *image_res);
			timer = 0;
		}
		timer++;
		i++;
#if defined(_WIN32)
		ReleaseSemaphore(temp_done_sem, 1, NULL);	//release temp singnal  
#elif defined(linux) || defined(unix)
		sem_post(&temp_done_sem);
#endif
	}
```

It should be noted that if commands are sent in multi-thread, you may need to add the mutex lock, otherwise the commands will crosstalk each other.



### 3.5 End program

In the main function of the sample, call `destroy_pthread_sem`to turn off the signal, and call `uvc_camera_close` to disconnect the device connection.



### 3.6 Update firmware

In the cmd.cpp of the sample, call `update_fw_cmd` function to update the firmware. After passing the file path, the function can update the new firmware  through control command.

Step1: Check the current state of the device, whether it is in rom mode(the smallest mode that can keep the burning function) or cache mode(normal mode), switch to rom mode and check  to confirm.

```c
//1)check current device status is rom mode or cache mode
	status = device_status_get();
	if (status == DEV_STATUS_CACHE)
	{
		rst = sys_reset_to_update_fw();
		if (rst < 0)
		{
			printf("sys_reset_to_update_fw failed!\n");
			return;
		}

		status = device_status_get();
		for (int j = 0; j < 100; j++)
		{
			if (status == DEV_STATUS_ROM)
			{
				break;
			}
#if defined(_WIN32)
			Sleep(1);
#elif defined(linux) || defined(unix)
			sleep(0.001);
#endif
		}
	}
```



Step 2: Configure the flash register state.

```c
//2) reset spi status before spi access
	rst = flash_status_check();
	if (rst < 0)
	{
		printf("flash status check failed!\n");
		return;
	}
```



Step 3: Erase the flash area to be burned, with a firmware flash starting address of 0 and a length of 256k (64 sectors, each 4k in size).

```c
	//3)erase and check erase area
	uint32_t start_addr = 0;
	uint16_t sector_num = 64;		//  256K/4k = 64
	uint8_t erase_read_buff[SECTOR_LEN] = { 0 };

	rst = spi_erase_sector(start_addr, sector_num);
	if (rst < 0)
	{
		printf("spi_erase_sector failed!\n");
		return;
	}

		//check first 4k
	rst = spi_read(start_addr, SECTOR_LEN, erase_read_buff);
	if (rst < 0)
	{
		printf("spi_read first 4k failed!\n");
		return;
	}
	for (int j = 0; j < SECTOR_LEN; j++)
	{
		if (erase_read_buff[j] != 0xFF)
		{
			printf("flash first 4k check failed!\n");
			return;
		}
	}

		//check last 4k
	rst = spi_read(start_addr + (sector_num - 1) * SECTOR_LEN, SECTOR_LEN, erase_read_buff);
	if (rst < 0)
	{
		printf("spi_read last 4k failed!\n");
		return;
	}
	for (int j = 0; j < SECTOR_LEN; j++)
	{
		if (erase_read_buff[j] != 0xFF)
		{
			printf("flash last 4k check failed!\n");
			return;
		}
	}
```



Step 4: Write and proofread the new firmware.

```c
//4) write fw, read and compare
	FILE* fp;
	if (_access(file_path, 0)==0)
	{
		fp = fopen(file_path, "rb");
	}
	else
	{
		printf("file doesn't exist!\n");
		return;
	}
	
	uint32_t addr = 0;
	uint8_t write_data[SECTOR_LEN] = { 0 };
	uint8_t read_data[SECTOR_LEN] = { 0 };
	for (int k = 0; k < sector_num; k++)
	{
		printf("k:%d\n", k);
		fread(write_data, SECTOR_LEN, 1, fp);
		spi_write(addr, SECTOR_LEN, write_data);

		spi_read(addr, SECTOR_LEN, read_data);
		for (int i = 0; i < SECTOR_LEN; i++)
		{
			if (write_data[i] != read_data[i])
			{
				printf("data compare failed!\n");
				return;
			}
		}
		addr += SECTOR_LEN;
	}
	fclose(fp);
```



Step 5: Write the cache tag, which means the check result is correct and the camera chip can switch to cache mode.

```c
	//5)write cache tag
	spi_write_tag();
```



Step 6: Restart the rom mode, if Step 5 's tag is correct, it will automatically switch to cache mode, and the update is finished.

```c
//6)reboot rom
	sys_reset_to_rom();

	printf("update finished!\n");
```



### 3.7 Secondary correction of temperature measurement

see cmp.cpp In case16 function read_nuc_parameter() reads the relevant NUC parameter and   function calculate_org_env_cali_parameter() calculates the temperature measurement correction coefficient in the device.
```c
    case 16:
		read_nuc_parameter();
		printf("read_nuc_parameter\n");
		printf("nuc_table[0]=%d\n", nuc_table[0]);
		printf("P0=%x\n", nuc_factor.P0);
		printf("P1=%x\n", nuc_factor.P1);
		printf("P2=%x\n", nuc_factor.P2);
		calculate_org_env_cali_parameter();
		printf("EMS=%d\n", org_env_param.EMS);
		printf("TAU=%d\n", org_env_param.TAU);
		printf("TA=%d\n", org_env_param.Ta);
		printf("Tu=%d\n", org_env_param.Tu);
		break;
```
In case 17, by reading tau.bin and new target emissivity, atmospheric temperature, reflection temperature, distance and humidity are set to calculate the new temperature measurement correction coefficient,and tpd_get_point_temp_info function reads the original temperature of a point in the device, converts it into Kelvin temperature, and temp_calc_with_new_env_calibration function is used to correct the temperature and output the corrected temperature.
```c
	case 17:
		calculate_new_env_cali_parameter("tau.bin", 1, 40, 40, 2, 0.8);
		tpd_get_point_temp_info(point_pos, &temp);
		org_temp = (double)temp / 16;
		printf("org_temp=%f\n", org_temp);
		temp_calc_with_new_env_calibration(org_temp, &new_temp);
		printf("new_temp=%f\n", new_temp);
		break;
```

### 3.7 Overexposure and auto gain switch function

See stream_function in camera.cpp. The overexposure and auto gain switch functions are two independent functions, which are based on the temperature data `stream_frame_info->temp_frame`.

```c
        if (stream_frame_info->raw_frame != NULL)
        {
            raw_data_cut((uint8_t*)stream_frame_info->raw_frame, stream_frame_info->image_byte_size, \
                        stream_frame_info->temp_byte_size, (uint8_t*)stream_frame_info->image_frame, \
                        (uint8_t*)stream_frame_info->temp_frame);
            if (stream_frame_info->temp_byte_size > 0)
            {
                avoid_overexposure((uint16_t*)stream_frame_info->temp_frame, &stream_frame_info->temp_info, 10 * fps);
                auto_gain_switch((uint16_t*)stream_frame_info->temp_frame, &stream_frame_info->temp_info, &auto_gain_switch_info);
            }
        }
```

