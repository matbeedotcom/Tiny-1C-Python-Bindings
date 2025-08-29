#include "data.h"

#if defined(_WIN32)
	HANDLE image_sem, temp_sem, image_done_sem, temp_done_sem;
#elif defined(linux) || defined(unix)
	sem_t image_sem, temp_sem, image_done_sem, temp_done_sem;
#endif

//init the semaphore
int init_pthread_sem()
{
#if defined(_WIN32)
	image_sem = CreateSemaphore(NULL, 1, 1, NULL);
	temp_sem = CreateSemaphore(NULL, 1, 1, NULL);
	image_done_sem = CreateSemaphore(NULL, 0, 1, NULL);
	temp_done_sem = CreateSemaphore(NULL, 0, 1, NULL);
#elif defined(linux) || defined(unix)
	sem_init(&image_sem, 0, 1);
	sem_init(&temp_sem, 0, 1);
	sem_init(&image_done_sem, 0, 0);
	sem_init(&temp_done_sem, 0, 0);
#endif 
	return 0;
}

//recycle the semaphore
int destroy_pthread_sem()
{
#if defined(_WIN32)
	CloseHandle(image_sem);
	CloseHandle(temp_sem);
	CloseHandle(image_done_sem);
	CloseHandle(temp_done_sem);
#elif defined(linux) || defined(unix)
	sem_destroy(&image_sem);
	sem_destroy(&temp_sem);
	sem_destroy(&image_done_sem);
	sem_destroy(&temp_done_sem);
#endif 
	return 0;
}

//create the raw frame/image frame/temperature frame's buffer
int create_data_demo(StreamFrameInfo_t* stream_frame_info)
{
	if (stream_frame_info != NULL)
	{
		if (stream_frame_info->raw_frame == NULL && stream_frame_info->image_frame == NULL && \
			stream_frame_info->temp_frame == NULL)
		{
			stream_frame_info->raw_frame = (uint8_t*)uvc_frame_buf_create(stream_frame_info->camera_param);
			stream_frame_info->image_frame = (uint8_t*)malloc(stream_frame_info->image_byte_size);
			stream_frame_info->temp_frame = (uint8_t*)malloc(stream_frame_info->temp_byte_size);
		}
	}
	return 0;
}

//recycle the raw frame/image frame/temperature frame's buffer
int destroy_data_demo(StreamFrameInfo_t* stream_frame_info)
{
	if (stream_frame_info != NULL)
	{
		if (stream_frame_info->raw_frame != NULL)
		{
			uvc_frame_buf_release(stream_frame_info->raw_frame);
		}

		if (stream_frame_info->image_frame != NULL)
		{
			free(stream_frame_info->image_frame);
			stream_frame_info->image_frame = NULL;
		}

		if (stream_frame_info->temp_frame != NULL)
		{
			free(stream_frame_info->temp_frame);
			stream_frame_info->temp_frame = NULL;
		}
	}
	return 0;
}