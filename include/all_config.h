#pragma once

#define		THERMAL_CAM_CMD

#if defined(linux) || defined(unix)
#define LINUX_I2C_SUPPORT
#endif

/**
 * @file
 *
 * @brief Header file of Configuration
 *
 */

#if defined(_WIN32)
#define DLLEXPORT __declspec(dllexport)
#include <windows.h>
#elif defined(linux) || defined(unix)
#define DLLEXPORT
#include <unistd.h>
#endif

#if defined(THERMAL_CAM_CMD)
	#define PRODUCT_TYPE  "THERMAL_CAM"
#else
	#define PRODUCT_TYPE  "NULL"
#endif

 /**
  * @brief Restore defaut config types
  */
enum vdcmd_driver_type 
{
	/// send command by USB
	VDCMD_USB_VDCMD = 0,
	/// send command by I2C_USB
	VDCMD_I2C_USB_VDCMD,
	/// send command by I2C(linux with i2c port only)
	VDCMD_I2C_VDCMD,
	/// send command by UART
	VDCMD_UART_VDCMD
};

/**
 * @brief Return error's type
 */
typedef enum{
	/// success
	IRUVC_SUCCESS						= 0,
	/// parameters error
	IRUVC_ERROR_PARAM					= -1,
	/// libiruvc's service context initialize failed
	IRUVC_UVC_INIT_FAIL					= -2,
	/// get device list failed
	IRUVC_GET_DEVICE_LIST_FAIL			= -3,
	/// find device via pid/vid/name failed
	IRUVC_FIND_DEVICE_FAIL				= -4,
	/// find device via pid/vid/name failed
	IRUVC_NOT_GET_DEVICE_INFO			= -5,
	/// open device fail
	IRUVC_DEVICE_OPEN_FAIL				= -6,
	/// get device's descriptor failed
	IRUVC_GET_DEVICE_DESCRIPTOR_FAIL	= -7,
	/// device already opened
	IRUVC_DEVICE_OPENED					= -8,
	/// device doesn't provide a matching stream
	IRUVC_GET_FORMAT_FAIL				= -9,
	/// user's callback fucntion is empty
	IRUVC_USER_CALLBACK_EMPTY			= -10,
	/// device start streaming failed
	IRUVC_START_STREAMING_FAIL			= -11,
	/// over time when getting frame
	IRUVC_GET_FRAME_OVER_TIME			= -12,
	/// vdcmd not registered
	IRUVC_VDCMD_NOT_REGISTER			= -13,
	/// vdcmd register failed
	IRUVC_VDCMD_REGISTER_FAIL			= -14,
	/// control transter failed
	IRUVC_CONTROL_TRANSFER_FAIL			= -15,
	/// checking vdcmd send failed
	IRUVC_CHECK_DONE_FAIL				= -16,
	/// vdcmd's length is too long
	IRUVC_VDCMD_TOO_LONG				= -17,
	/// reset device fail
	IRUVC_RESET_DEVICE_FAIL				= -18,
	/// clear halt fail
	IRUVC_CLEAR_HALT_FAIL				= -19,
	/// unsupported command
	IRUVC_UNSUPPORTED_CMD				= -20,
	/// i2c transfer fail
	IRUVC_I2C_TRANSFER_FAIL				= -21,
	/// i2c device open fail
	IRUVC_I2C_DEVICE_OPEN_FAIL			= -22,
	/// i2c get register fail
	IRUVC_I2C_GET_REGISTER_FAIL			= -23,
	/// i2c set register fail
	IRUVC_I2C_SET_REGISTER_FAIL			= -24,
	/// memory allocation fail
	IRUVC_MEM_ALLOC_FAIL				= -25,
	/// command excute fail				
	IRUVC_CMD_EXECUTE_FAIL				= -26
}iruvc_error_t;

/**
 * @brief Log message levels
 */
typedef enum{
	/// all debug&error infomation
	IRUVC_LOG_DEBUG						= 0,
	/// all error infomation
	IRUVC_LOG_ERROR						= 1,
	/// no print infomation(default)
	IRUVC_LOG_NO_PRINT					= 2
}iruvc_log_level_t;


#if defined(_WIN32)
#define IRUVC_DEBUG(format, ...) iruvc_debug_print("libiruvc debug [%s:%d/%s] " format "\n", \
												 __FILE__,__LINE__, __FUNCTION__, __VA_ARGS__)
#elif defined(linux) || defined(unix)
#include <libgen.h>
#define IRUVC_DEBUG(format, ...) iruvc_debug_print("libiruvc debug [%s:%d/%s] " format "\n", \
												 basename(__FILE__), __LINE__, __FUNCTION__, ##__VA_ARGS__)
#endif

#if defined(_WIN32)
#define IRUVC_ERROR(format, ...) iruvc_error_print("libiruvc error [%s:%d/%s] " format "\n", \
												 __FILE__,__LINE__, __FUNCTION__, __VA_ARGS__)
#elif defined(linux) || defined(unix)
#include <libgen.h>
#define IRUVC_ERROR(format, ...) iruvc_error_print("libiruvc error [%s:%d/%s] " format "\n", \
												 basename(__FILE__), __LINE__, __FUNCTION__, ##__VA_ARGS__)
#endif

/// Print debug infomation
extern void (*iruvc_debug_print)(const char* fmt, ...);

/// Print error infomation
extern void (*iruvc_error_print)(const char* fmt, ...);

