#pragma once

#ifdef __cplusplus
extern "C" {
#endif

#include "all_config.h"

#if defined(THERMAL_CAM_CMD)
#include "thermal_cam_cmd.h"
#endif

/**
* @file
*
* @brief Libiruvc library header file
*
*/

#define FORMAT_YUY2 "YUY2"
#define FORMAT_MJPEG "MJPEG"

#define FPS_CNT_MAX 32


/**
* @brief Device's configuration
*/
typedef struct {
	unsigned int    pid;	///< pid
	unsigned int    vid;	///< vid
	char*			name;	///< device name
}DevCfg_t;


/**
* @brief Camera's supported stream information
*/
typedef struct
{
	char*			format;				///< format
	unsigned int	width;				///< resolution width
	unsigned int	height;				///< resolution height
	unsigned int	frame_size;			///< frame byte size
	unsigned int	fps[FPS_CNT_MAX];	///< frame per second
}CameraStreamInfo_t;


/**
* @brief Camera's one stream parameter
*/
typedef struct {
	DevCfg_t		dev_cfg;				///< device's configuration 
	char*			format;					///< format
	unsigned int	width;					///< resolution width
	unsigned int    height;					///< resolution height
	unsigned int	frame_size;				///< frame byte size
	unsigned int    fps;					///< frame per second
	unsigned int	timeout_ms_delay;		///< frame get's timeout timer(ms)
}CameraParam_t;


/**
* @brief User's callback function and parameters
*/
typedef struct {
	void* usr_func;			///< user's function
	void* usr_param;		///< parameters of user's function
}UserCallback_t;


/**
* @brief Control camera side's preview
*/
typedef enum {
	CLOSE_CAM_SIDE_PREVIEW = 0,	///< close camera side's preview
	KEEP_CAM_SIDE_PREVIEW = 1	///< keep camera side's preview
}cam_side_preview_ctl;

/**
 * @brief Get libiruvc library's version
 *
 * @param NULL
 *
 * @return version's string
 */
DLLEXPORT char* libiruvc_version(void);

/**
 * @brief Get libiruvc library's version number
 *
 * @param NULL
 *
 * @return supported device's type string
 */
DLLEXPORT const char* iruvc_version_number(void);


/**
 * @brief Get product type
 *
 * @param NULL
 *
 * @return supported device's type string
 */
DLLEXPORT char* product_type(void);


/**
 * @brief Initialize libiruvc's service context
 *
 * @param NULL
 *
 * @return see iruvc_error_t
 */
DLLEXPORT iruvc_error_t uvc_camera_init(void);


/**
 * @brief Return a devices' list with pid,vid and name
 *
 * @param[out] devs_cfg devices' configuration
 *
 * @return see iruvc_error_t
 */
DLLEXPORT iruvc_error_t uvc_camera_list(DevCfg_t devs_cfg[]);


/**
 * @brief Using a devices' configuration to find it, and list its supported stream infomation
 *
 * @param[in] dev_cfg devices' configuration
 * @param[out] camera_stream_info camera's supported stream infomation
 *
 * @return see iruvc_error_t
 */
DLLEXPORT iruvc_error_t uvc_camera_info_get(DevCfg_t dev_cfg, CameraStreamInfo_t camera_stream_info[]);


/**
 * @brief Open a camera device with its configuration
 *
 * @param[in] dev_cfg devices' configuration
 *
 * @return see iruvc_error_t
 */
DLLEXPORT iruvc_error_t uvc_camera_open(DevCfg_t dev_cfg);


/**
 * @brief Open a camera device with its configuration, 
 * and distinguish the same device via same_dev_index
 *
 * @param[in] dev_cfg devices' configuration
 * @param[in] same_dev_index same device's index
 *
 * @return see iruvc_error_t
 */
DLLEXPORT iruvc_error_t uvc_camera_open_same(DevCfg_t dev_cfg, int same_dev_index);


/**
 * @brief set bandwidth foctor for some platform which has bandwidth limit,such as hisilicon
 *
 * @param[in] factor bandwidth factor,range from 0 to 1.
 *
 * @return see iruvc_error_t
 */
DLLEXPORT iruvc_error_t uvc_camera_set_bandwidth_factor(float factor);



/**
 * @brief get bandwidth foctor
 *
 * @param[out] factor bandwidth factor,range from 0 to 1.
 *
 * @return see iruvc_error_t
 */
DLLEXPORT iruvc_error_t uvc_camera_get_bandwidth_factor(float* factor);


/**
 * @brief Start stream with specific one stream parameter of the camera,
 * you can use user's callback function or polling frame(usr_callback=NULL)
 *
 * @param[in] camera_param camera's one selected stream parameter
 * @param[in] usr_callback user's callback function
 *
 * @return see iruvc_error_t
 */
DLLEXPORT iruvc_error_t uvc_camera_stream_start(CameraParam_t camera_param, UserCallback_t* usr_callback);


/**
 * @brief Close camera's stream
 *
 * @param[in] cam_preview control camera side's preview
 */
DLLEXPORT iruvc_error_t uvc_camera_stream_close(cam_side_preview_ctl cam_preview);


/**
 * @brief Disconnect the camera's device connection
 *
 * @param NULL
 */
DLLEXPORT void uvc_camera_close(void);


/**
 * @brief Release libiruvc's service context
 *
 * @param NULL
 */
DLLEXPORT void uvc_camera_release(void);


/**
 * @brief Create one frame's buffer for frame_get
 *
 * @param[in] camera_param camera's one selected stream parameter
 */
DLLEXPORT void* uvc_frame_buf_create(CameraParam_t camera_param);


/**
 * @brief Release the frame's buffer created before
 *
 * @param[in] frame_buf the frame's buffer created before
 */
DLLEXPORT void uvc_frame_buf_release(void* frame_buf);


/**
 * @brief Polling frame transfered from uvc camera.
 * User can't recieve data when use user callback function
 *
 * @param[out] raw_data raw frame data that transfered from camera
 *
 * @return see iruvc_error_t
 */
DLLEXPORT iruvc_error_t uvc_frame_get(void *raw_data);


/**
 * @brief Send control command to uvc camera
 *
 * @param[in] request_type command's request type
 * @param[in] bRequest command's bRequest
 * @param[in] wValue command's wValue
 * @param[in] wIndex command's wIndex
 * @param data command's data pointer
 * @param[in] wLength command's data length
 * @param[in] timeout command's timeout timer(ms)
 *
 * @return see iruvc_error_t
 */
DLLEXPORT iruvc_error_t uvc_control_cmd(unsigned char request_type, unsigned char bRequest, unsigned short wValue,
	unsigned short wIndex, unsigned char *data, unsigned short wLength, unsigned int timeout);


/**
 * @brief Register log print via log_level
 *
 * @param[in] log_level debug information level
 *
 */
DLLEXPORT void iruvc_log_register(iruvc_log_level_t log_level);


/**
 * @brief Register i2c device node
 *
 * @param[in] node_name i2c device node name
 *
 * @return see iruvc_error_t
 */
DLLEXPORT iruvc_error_t register_i2c_device_node(const char* node_name);


/**
 * @brief Register log print via log_level
 *
 * @param[in] log_level debug information level
 *
 */
DLLEXPORT void iruvc_log_register(iruvc_log_level_t log_level);


/**
 * @brief Start stream by i2c.Will be deleted in 2.0.0
 *
 * @param[in] path stream path
 * @param[in] src stream source
 * @param[in] width stream frame width
 * @param[in] height stream  frame height
 * @param[in] fps stream  frame fps
 * @param[in] mode stream mode
 *
 */
DLLEXPORT int i2c_start_stream(uint8_t path, uint8_t src, uint16_t width, uint16_t height,\
							   uint8_t fps, uint8_t mode);


/**
 * @brief Stop stream by i2c.Will be deleted in 2.0.0
 *
 * @param[in] path stream path
 *
 */
DLLEXPORT int i2c_stop_stream(uint8_t path);


#ifdef __cplusplus
}
#endif
