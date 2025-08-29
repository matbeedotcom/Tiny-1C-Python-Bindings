#include "temperature.h"


//温度修正相关的参数
EnvParam_t org_env_param = { 0,0,0,0 };             //原始环境变量
EnvParam_t new_env_param = { 0,0,0,0 };             //新的环境变量
uint8_t gain_flag = 1;

NucFactor_t nuc_factor = { 0,0,0 };                  //温度映射二次函数系数
EnvFactor_t org_env_factor = { 0 };                 //原始修正参数
EnvFactor_t new_env_factor = { 0 };                 //新的修正参数
uint16_t nuc_table[NUCT_LEN] = { 0 };               //温度映射表
uint16_t correct_table[4 * 14 * 64 + 128];				//环境变量修正表


TempCalInfo_t temp_cal_info = { &org_env_param, &new_env_param, gain_flag, &nuc_factor,\
                                & org_env_factor, &new_env_factor, nuc_table };

TempCalInfo_t* get_temp_cal_info(void)
{
    return &temp_cal_info;
}


//temperature value to actual temp(Celsius)
float temp_value_converter(uint16_t temp_val)
{
    return ((double)temp_val / 64 - 273.15);
}


//该函数的功能是计算新的环境变量校正参数
// ems: 目标发射率(0.01-1)
// ta:大气温度(单位:摄氏度)
// tu:反射温度(单位:摄氏度)
// dist:目标距离(0.25-49.99,单位:m)
// hum: 环境相对湿度(0-1)
//calculate the new environmental variable correction parameters
int calculate_new_env_cali_parameter(uint16_t* correct_table, double ems, double ta, double tu, double dist, double hum)
{
    uint16_t tau = 0;
    if (read_tau(correct_table, hum, ta, dist, &tau) != IRTEMP_SUCCESS)
    {
        printf("read tau failed\n");
        return -1;
    }
    printf("tau=%d\n", tau);
    new_env_param.EMS = ems * (1 << 14);
    new_env_param.TAU = tau;
    new_env_param.Ta = (ta + 273.15) * (1 << 4);
    new_env_param.Tu = (tu + 273.15) * (1 << 4);
    if (calculate_new_KE_and_BE_with_nuc_t(&new_env_param, nuc_table, gain_flag, &new_env_factor) != IRTEMP_SUCCESS)
    {
        printf("calculate_KE_and_BE failed\n");
        return -1;
    }
    return 0;
}


//reverse temp data to nuc
int reverse_temp_frame_to_nuc(uint16_t* org_temp, NucFactor_t* nuc_factor, int pix_num, uint16_t* nuc_data)
{
    int ret = 0;
    int i = 0;
    while (i < pix_num)
    {
        double temp = *org_temp / 16;
        ret = reverse_calc_NUC_with_env_correct(nuc_factor, temp, nuc_data);
        if (ret != IRTEMP_SUCCESS)
        {
            printf("reverse_calc_NUC_with_env_correct failed\n");
            return -1;
        };
        org_temp++;
        nuc_data++;
        i++;
    }
    return 0;
}


// recalibrate the temperature with new environment parameters
// org_temp,unit:K    new_temp,unit:K
int temp_calc_with_new_env_calibration(TempCalInfo_t* temp_cal_info, double org_temp, double* new_temp)
{
    uint16_t nuc_cal = 0;
    uint16_t nuc_org = 0;
    irtemp_error_t ret;
    uint16_t temp_data = 0;

    ret = reverse_calc_NUC_with_nuc_t(temp_cal_info->nuc_table, org_temp - 273.15, &nuc_cal);
    printf("nuc_cal=%d\n", nuc_cal);
    if (ret != IRTEMP_SUCCESS)
    {
        printf("reverse_calc_NUC_with_nuc_t failed\n");
        return -1;
    };
    ret = reverse_calc_NUC_without_env_correct(temp_cal_info->org_env_factor, nuc_cal, &nuc_org);
    printf("nuc_org=%d\n", nuc_org);
    printf("K_E=%d,B_E=%d\n", temp_cal_info->org_env_factor->K_E, temp_cal_info->org_env_factor->B_E);
    if (ret != IRTEMP_SUCCESS)
    {
        printf("reverse_calc_NUC_without_env_correct failed\n");
        return -1;
    };
    ret = recalc_NUC_with_env_correct(temp_cal_info->new_env_factor, nuc_org, &nuc_cal);
    printf("nuc_cal=%d\n", nuc_cal);
    printf("K_E=%d,B_E=%d\n", temp_cal_info->new_env_factor->K_E, temp_cal_info->new_env_factor->B_E);
    if (ret != IRTEMP_SUCCESS)
    {
        printf("recalc_NUC_with_env_correct failed\n");
        return -1;
    };
    ret = remap_temp(temp_cal_info->nuc_table, nuc_cal, &temp_data);
    if (ret != IRTEMP_SUCCESS)
    {
        printf("remap_temp failed\n");
        return -1;
    };
    *new_temp = (double)temp_data / 16;
    return 0;
}

// recalibrate the temperature with new environment parameters
// org_temp,unit:K    new_temp,unit:K
int temp_calc_without_any_correct(TempCalInfo_t* temp_cal_info, double org_temp, double* new_temp)
{
    uint16_t nuc_cal = 0;
    uint16_t nuc_org = 0;
    irtemp_error_t ret;
    uint16_t temp_data = 0;
    ret = reverse_calc_NUC_with_nuc_t(temp_cal_info->nuc_table, org_temp - 273.15, &nuc_cal);
    if (ret != IRTEMP_SUCCESS)
    {
        printf("reverse_calc_NUC_with_nuc_t failed\n");
        return -1;
    };
    ret = reverse_calc_NUC_without_env_correct(temp_cal_info->org_env_factor, nuc_cal, &nuc_org);
    if (ret != IRTEMP_SUCCESS)
    {
        printf("reverse_calc_NUC_without_env_correct failed\n");
        return -1;
    };
    ret = remap_temp(temp_cal_info->nuc_table, nuc_org, &temp_data);
    if (ret != IRTEMP_SUCCESS)
    {
        printf("remap_temp failed\n");
        return -1;
    };
    *new_temp = (double)temp_data / 16;
    return 0;
}

void print_cali_info(TempCalInfo_t* temp_cal_info)
{
    printf("origin ems = %d \n", temp_cal_info->org_env_param->EMS);
    printf("origin tau = %d \n", temp_cal_info->org_env_param->TAU);
    printf("origin ta =  %d \n", temp_cal_info->org_env_param->Ta);
    printf("origin tu =  %d \n", temp_cal_info->org_env_param->Tu);
    printf("origin K_E =  %d \n", temp_cal_info->org_env_factor->K_E);
    printf("origin B_E =  %d \n", temp_cal_info->org_env_factor->B_E);

    printf("nuc param P0 =  %d \n", temp_cal_info->nuc_factor->P0);
    printf("nuc param P1 =  %d \n", temp_cal_info->nuc_factor->P1);
    printf("nuc param P2 =  %d \n", temp_cal_info->nuc_factor->P2);
    printf("nuc param nuc_table[0] =  %d \n", temp_cal_info->nuc_table[0]);

    printf("new ems =  %d \n", temp_cal_info->new_env_param->EMS);
    printf("new tau  =  %d \n", temp_cal_info->new_env_param->TAU);
    printf("new ta  =  %d \n", temp_cal_info->new_env_param->Ta);
    printf("new tu =  %d \n", temp_cal_info->new_env_param->Tu);

    printf("new K_E =  %d \n", temp_cal_info->new_env_factor->K_E);
    printf("new B_E =  %d \n", temp_cal_info->new_env_factor->B_E);
}
//detect the point's temperature
void point_temp_demo(uint16_t* temp_data, TempDataRes_t temp_res)
{
    Dot_t point = { 128,96 };
    uint16_t temp = 0;
    if (get_point_temp(temp_data, temp_res, point, &temp) == IRTEMP_SUCCESS)
    {
        printf("point(%d,%d)temp:%f\n", point.x, point.y, temp_value_converter(temp));
    }
}


void line_temp_demo(uint16_t* temp_data, TempDataRes_t temp_res)
{
    Line_t line = { 128,191, 128,0, };
    //Line_t line = { 191,128,0,128 };
    //Line_t line = { 20,50,128,30, };
    TempInfo_t temp_info = { 0 };

    if (get_line_temp(temp_data, temp_res, line, &temp_info) == IRTEMP_SUCCESS)
    {
        printf("current line temp: max=%f, min=%f, avr=%f\n", \
            temp_value_converter(temp_info.max_temp), \
            temp_value_converter(temp_info.min_temp), \
            temp_value_converter(temp_info.avr_temp));
        //printf("maxtemp_cord(%d,%d)\n", temp_info.max_cord.x, temp_info.max_cord.y);
        //printf("mintemp_cord(%d,%d)\n", temp_info.min_cord.x, temp_info.min_cord.y);
    }
}

//detect the rectangle's temperature
void rect_temp_demo(uint16_t* temp_data, TempDataRes_t temp_res)
{
    Area_t rect = { 50,50,20,20 };
    TempInfo_t temp_info = { 0 };

    if (get_rect_temp(temp_data, temp_res, rect, &temp_info) == IRTEMP_SUCCESS)
    {
        printf("rectangle temp: max=%f, min=%f, avr=%f\n", \
            temp_value_converter(temp_info.max_temp), \
            temp_value_converter(temp_info.min_temp), \
            temp_value_converter(temp_info.avr_temp));
    }
}


//temperature thead function
void* temperature_function(void* threadarg)
{
    StreamFrameInfo_t* stream_frame_info;
    stream_frame_info = (StreamFrameInfo_t*)threadarg;
    if (stream_frame_info == NULL)
    {
        return NULL;
    }

    TempDataRes_t temp_res = { stream_frame_info->temp_info.width, stream_frame_info->temp_info.height };
    int timer = 0;
    int i = 0;
    while (is_streaming || (i <= stream_time * fps))
    {
#if defined(_WIN32)
        WaitForSingleObject(temp_sem, INFINITE);	//waitting for temp singnal 
#elif defined(linux) || defined(unix)
        sem_wait(&temp_sem);
#endif
        if (timer % 25 == 0)	//colect one frame at an interval of 25 frames 
        {
            if (stream_frame_info->temp_byte_size > 0)
            {
                point_temp_demo((uint16_t*)stream_frame_info->temp_frame, temp_res);
                //line_temp_demo((uint16_t*)stream_frame_info->temp_frame, temp_res);
                //rect_temp_demo((uint16_t*)stream_frame_info->temp_frame, temp_res);
            }
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
    printf("temperature thread exit!!\n");
    return NULL;
}