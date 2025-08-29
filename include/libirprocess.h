#ifndef _LIBIRPROCESS_H_
#define _LIBIRPROCESS_H_

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>
#include <stdio.h>
#include <stdarg.h>
#include <string.h>
#include <stdlib.h>
#include <math.h>


/**
* @brief Image resulution
*/
typedef struct {
    uint16_t width;    ///< resolution width
    uint16_t height;   ///< resolution height
}ImageRes_t;


/**
* @brief AGC stretch parameters
*/
typedef struct {
    uint8_t enable;
    uint16_t lower_limit;   ///< lower limit of the stretched image
    uint16_t upper_limit;   ///< upper limit of the stretched image
}AgcStretchParam_t;


/**
* @brief AGC algorithm parameter
*/
typedef struct {
    float highDiscardRatio;     ///< high discard pixel ration
    float lowDiscardRatio;      ///< low discard pixel ration
    float maxStepThdRatio;      ///< maximum step pixel threshold ration of accumlated graph
    float minStepThdRatio;      ///< minimum step pixel threshold ration of accumlated graph
    uint32_t rangeGain;         ///< range gain 
    float  alphaRatio;          ///< alpha ratio
    float  offsetRatio;         ///< offset ration
    AgcStretchParam_t stretch_param;
}AgcParam_t;


/**
* @brief DDE algorithm parameter
*/
typedef struct {
    float startCoef;        ///< start coefficient of dde algorithm
    float maxCoef;        ///< maximum coefficient of dde algorithm
    float endCoef;      ///< end coefficient of dde algorithm
    int startMinThd;    ///< start minimum threshold of difference between origin image and blured image
    int startMaxThd;    ///< start maximum threshold of difference between origin image and blured image
    int endMaxThd;      ///< end maximum threshold of difference between origin image and blured image
    int endMinThd;      ///< end minimum threshold of difference between origin image and blured image
}DdeParam_t;


/**
* @brief DDE algorithm parameters
*/
typedef struct {
    AgcParam_t agc_param;    ///< AGC algorithm parameter
    DdeParam_t dde_param;    ///< DDE algorithm parameter
}ImgEnhanceParam_t;


/**
* @brief Gain switch detect parameters
*/
typedef struct {
    float above_pixel_prop;     ///< above pixel proportion
    int above_temp_data;           ///< above temp data, in y14 format
    float below_pixel_prop;     ///< below pixel proportion
    int below_temp_data;           ///< below temp data, in y14 format
}GainSwitchParam_t;


/**
* @brief Log level definition in libirprocess library
*/
typedef enum {
    IRPROC_LOG_DEBUG            = 0,    ///< print debug and error infomation
    IRPROC_LOG_ERROR            = 1,    ///< only print error infomation
    IRPROC_LOG_NO_PRINT         = 2     ///< don't print debug and error infomation
}irproc_log_level_t;


/**
* @brief Error type in libirprocess library
*/
typedef enum {
    IRPROC_SUCCESS              = 0,    ///< function excute success
    IRPROC_ERROR_PARAM          = -1,   ///< parameter is invalid
    IRPROC_FMT_NOT_SUPPORTED    = -2,    ///< image format not supported
    IRPROC_MALLOC_FAILED        = -3,     ///< alloc memory failed
    IRPROC_ERROR_SOURCE         = -4,     ///< error source image
}irproc_error_t;


/**
* @brief Supported image format in libirprocess library
*/
typedef enum {
    IRPROC_SRC_FMT_Y14 = 0,     ///< Y14 format of source image
    IRPROC_SRC_FMT_YUV422,      ///< YUV422 format of source image
    IRPROC_SRC_FMT_YUV444,      ///< YUV444 format of source image
    IRPROC_SRC_FMT_RGB888,      ///< RGB888 format of source image
    IRPROC_SRC_FMT_BGR888       ///< BGR888 format of source image
}irproc_src_fmt_t;


/**
* @brief Psudocolor mode types in libirprocess library
*/
typedef enum {
    IRPROC_COLOR_MODE_1 = 1,    ///< white hot
    IRPROC_COLOR_MODE_2,        ///< reserved
    IRPROC_COLOR_MODE_3,        ///< color3
    IRPROC_COLOR_MODE_4,        ///< color4
    IRPROC_COLOR_MODE_5,        ///< color5
    IRPROC_COLOR_MODE_6,        ///< color6
    IRPROC_COLOR_MODE_7,        ///< color7
    IRPROC_COLOR_MODE_8,        ///< color8
    IRPROC_COLOR_MODE_9,        ///< color9
    IRPROC_COLOR_MODE_10,       ///< color10
    IRPROC_COLOR_MODE_11,       ///< black hot
    IRPROC_COLOR_MODE_12,       ///< reserved
    IRPROC_COLOR_MODE_13,       ///< reserved
    IRPROC_COLOR_MODE_14,       ///< reserved
    IRPROC_COLOR_MODE_15,       ///< reserved
    IRPROC_COLOR_MODE_16,       ///< user reserved
    IRPROC_COLOR_MODE_17,       ///< user reserved
    IRPROC_COLOR_MODE_18,       ///< user reserved
    IRPROC_COLOR_MODE_19,       ///< user reserved
    IRPROC_COLOR_MODE_20,       ///< user reserved
}irproc_color_mode_t;


#if defined(_WIN32)
#define DLLEXPORT __declspec(dllexport)
#elif defined(linux) || defined(unix)
#define DLLEXPORT
#endif


#if defined(_WIN32)
    #define IRPROC_DEBUG(format, ...) irproc_debug_print("libirprocess debug [%s:%d/%s] " format "\n", \
                                                        __FILE__,__LINE__, __FUNCTION__, __VA_ARGS__)
    #define IRPROC_ERROR(format, ...) irproc_error_print("libirprocess error [%s:%d/%s] " format "\n", \
                                                        __FILE__,__LINE__, __FUNCTION__, __VA_ARGS__)
#elif defined(linux) || defined(unix)
    #include <libgen.h>
    #define IRPROC_DEBUG(format, ...) irproc_debug_print("libirprocess debug [%s:%d/%s] " format "\n", \
                                                        basename(__FILE__), __LINE__, __FUNCTION__, ##__VA_ARGS__)
    #define IRPROC_ERROR(format, ...) irproc_error_print("libirprocess error [%s:%d/%s] " format "\n", \
                                                        basename(__FILE__), __LINE__, __FUNCTION__, ##__VA_ARGS__)
#endif

extern void (*irproc_debug_print)(const char* fmt, ...);
extern void (*irproc_error_print)(const char* fmt, ...);

/**
 * @brief Get current libirprocess library version
 *
 * @param NULL
 *
 * @return current libirprocess library version
 */
DLLEXPORT char* irproc_version(void);


/**
 * @brief Register log function depend on log level
 *
 * @param[in] log_level detail see irproc_log_level_t
 *
 */
DLLEXPORT void irproc_log_register(irproc_log_level_t log_level);


/**
 * @brief Rotate the frame left 90 degree
 *
 * @param[in] src source image frame 
 * @param[in] image_res imput image resulution, detail see ImageRes_t
 * @param[in] input_fmt imput image format, detail see irproc_src_fmt_t
 * @param[out] dst destination frame after rotate
 *
 * @return see irproc_error_t
 */
DLLEXPORT irproc_error_t rotate_left_90(uint8_t* src, ImageRes_t image_res, irproc_src_fmt_t input_fmt, uint8_t* dst);


/**
 * @brief Rotate the frame right 90 degree
 *
 * @param[in] src source image frame
 * @param[in] image_res imput image resulution, detail see ImageRes_t
 * @param[in] input_fmt imput image format, detail see irproc_src_fmt_t
 * @param[out] dst destination frame after rotate
 *
 * @return see irproc_error_t
 */
DLLEXPORT irproc_error_t rotate_right_90(uint8_t* src, ImageRes_t image_res, irproc_src_fmt_t input_fmt, uint8_t* dst);


/**
 * @brief Rotate the frame 180 degree
 *
 * @param[in] src source image frame
 * @param[in] image_res imput image resulution, detail see ImageRes_t
 * @param[in] input_fmt imput image format, detail see irproc_src_fmt_t
 * @param[out] dst destination frame after rotate
 *
 * @return see irproc_error_t
 */
DLLEXPORT irproc_error_t rotate_180(uint8_t* src, ImageRes_t image_res, irproc_src_fmt_t input_fmt, uint8_t* dst);


/**
 * @brief Mirror the frame (left and right side)
 *
 * @param[in] src source image frame
 * @param[in] image_res imput image resulution, detail see ImageRes_t
 * @param[in] input_fmt imput image format, detail see irproc_src_fmt_t
 * @param[out] dst destination frame after mirror
 *
 * @return see irproc_error_t
 */
DLLEXPORT irproc_error_t mirror(uint8_t* src, ImageRes_t image_res, irproc_src_fmt_t input_fmt, uint8_t* dst);


/**
 * @brief Flip the frame (up and down side)
 *
 * @param[in] src source image frame
 * @param[in] image_res imput image resulution, detail see ImageRes_t
 * @param[in] input_fmt imput image format, detail see irproc_src_fmt_t
 * @param[out] dst destination frame after mirror
 *
 * @return see irproc_error_t
 */
DLLEXPORT irproc_error_t flip(uint8_t* src, ImageRes_t image_res, irproc_src_fmt_t input_fmt, uint8_t* dst);


/**
 * @brief Y14 array map to YUV422 pseudocolor array
 *
 * @param[in] image_y14 source image frame with Y14 format
 * @param[in] pix_num pixel number of whole frame
 * @param[in] color_mode pseudo color mode type
 * @param[out] out_yuv destination frame after pseudo color mapping
 *
 * @return see irproc_error_t
 */
DLLEXPORT irproc_error_t y14_map_to_yuyv_pseudocolor(uint16_t* image_y14, uint32_t pix_num, \
                                                     irproc_color_mode_t color_mode, uint8_t* out_yuv);


/**
 * @brief Do spatial noise reduction to the y14 image
 *
 * @param[in] src source image frame with Y14 format
 * @param[in] image_res image resolution
 * @param[out] dst output frame after snr
 *
 * @return see irproc_error_t
 */
DLLEXPORT irproc_error_t y14_image_spatial_noise_reduction(uint16_t* src, ImageRes_t image_res, \
                                                  uint16_t* dst);


/**
 * @brief Enhance the y14 image
 *
 * @param[in] src source image frame with Y14 format
 * @param[in] image_res image resolution
 * @param[in] img_enhance_param enhance parameters
 * @param[out] dst output frame after enhance
 *
 * @return see irproc_error_t
 */
DLLEXPORT irproc_error_t y14_image_enhance(uint16_t* src, ImageRes_t image_res, \
                                           ImgEnhanceParam_t img_enhance_param, uint16_t* dst);


/**
 * @brief detect gain switch status
 *
 * @param[in] temp_data temperature frame data
 * @param[in] image_res image resolution
 * @param[in] gain_switch_param gain switch parameters
 * @param[out] detect_flag detect flag status. 0:normal, 1:high->low gain, 2:low->high gain
 *
 * @return see irproc_error_t
 */
DLLEXPORT irproc_error_t gain_switch_detect(uint16_t* temp_data, ImageRes_t image_res, \
                                           GainSwitchParam_t gain_switch_param, uint8_t* detect_flag);


/**
 * @brief detect overexposure status
 *
 * @param[in] temp_data temperature frame data, in y14 format
 * @param[in] image_res image resolution
 * @param[in] over_temp_data overexposure's temperature value data, in y14 format
 * @param[in] pixel_above_prop above over_temp's proportion
 * @param[out] detect_flag detect flag status. 0:noraml, 1:overexposure
 *
 * @return see irproc_error_t
 */
DLLEXPORT irproc_error_t overexposure_detect(uint16_t* temp_data, ImageRes_t image_res, int over_temp_data, \
                                             float pixel_above_prop, uint8_t* detect_flag);

#ifdef __cplusplus
}
#endif

#endif 
