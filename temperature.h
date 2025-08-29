#ifndef _TEMPERATURE_H_
#define _TEMPERATURE_H_

#include <stdio.h>
#include "data.h"
#include "libirtemp.h"
#include "libirprocess.h"

#define NUCT_LEN 8192

#define HEAD_SIZE 128
extern TempCalInfo_t temp_cal_info;				
extern uint16_t correct_table[4 * 14 * 64+128];				
// get temperature calibration information
TempCalInfo_t* get_temp_cal_info(void);

// print temperature calibration information
void print_cali_info(TempCalInfo_t* temp_cal_info);

//convert temperature value to real temperature.
float temp_value_converter(uint16_t temp_val);

//calculate the new environmental variable correction parameters
int calculate_new_env_cali_parameter(uint16_t* correct_table, double ems, double ta, double tu, double dist, double hum);

//reverse temp data to nuc
int reverse_temp_frame_to_nuc(uint16_t* org_temp, NucFactor_t* nuc_factor, int pix_num, uint16_t* nuc_data);

// recalculate the temperature with new environment parameters
int temp_calc_with_new_env_calibration(TempCalInfo_t* temp_cal_info, double org_temp, double* new_temp);

// recalculate temperature with out any correct
int temp_calc_without_any_correct(TempCalInfo_t* temp_cal_info, double org_temp, double* new_temp);

//get line temperature's info
void line_temp_demo(uint16_t* temp_data, TempDataRes_t temp_res);

//get rectangle temperature's info
void rect_temp_demo(uint16_t* temp_data, TempDataRes_t temp_res);

//get point temperature's info
void point_temp_demo(uint16_t* temp_data, TempDataRes_t temp_res);

//temperature detection thread
void* temperature_function(void* threadarg);

#endif
