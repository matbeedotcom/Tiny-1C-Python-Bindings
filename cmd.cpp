#include "cmd.h"

//command init.it need to be called before sending command.
void command_init(void)
{
    vdcmd_init();
}

//获取某个文件的长度
int get_file_len(const char* p_path)
{
    int f_len = 0;
    if (NULL == p_path)
        return f_len;
    FILE* pf = fopen(p_path, "rb");
    if (NULL == pf)
        return f_len;
    fseek(pf, 0, SEEK_END); //先将指针偏移到文件尾    
    f_len = ftell(pf);
    fclose(pf);
    return f_len;
}

//使用新的环境变量修正温度
//1.关闭模组中的距离修正算法，NUC映射系数(P0,P1,P2)。
//2.读取模组中的环境变量参数(EMS, TAU, Ta, Tu)，计算固件中的环境变量校正系数K_E和B_E。
//2.计算更高精度并且使用新的环境变量参数(目标发射率,距离,大气温度,反射温度,湿度)下的校正系数K_E和B_E
//3.重新修正温度结果

//该函数的功能是读取固件中的测温参数
int read_nuc_parameter(TempCalInfo_t* temp_cal_info)
{
    int i = 0;
    uint8_t temp = 0;


    uint8_t data[0x4000] = { 0 };
    if (spi_read(0xda000, 0x4000, data) != IRUVC_SUCCESS)//high gain is 0xda000 / low gain is 0xd3000
    {
        printf("get nuc-t table failed\n");
        return FAIL;
    }
    for (i = 0; i < sizeof(data);)
    {
        temp = data[i];
        data[i] = data[i + 1];
        data[i + 1] = temp;
        i = i + 2;
    }
    memcpy(temp_cal_info->nuc_table, data, 0x4000);
    return FAIL;
}

//该函数的功能是计算固件中环境变量校正的参数
int calculate_org_env_cali_parameter()
{
    uint8_t gain_flag = HIGH_GAIN;
    uint8_t data[4] = { 0 };
    TempCalInfo_t* temp_cal_info = get_temp_cal_info();
    if (get_prop_tpd_params(TPD_PROP_EMS, (uint16_t*)&temp_cal_info->org_env_param->EMS) != IRUVC_SUCCESS)
    {
        printf("get EMS failed\n");
        return FAIL;
    }
    if (get_prop_tpd_params(TPD_PROP_TAU, (uint16_t*)&temp_cal_info->org_env_param->TAU) != IRUVC_SUCCESS)
    {
        printf("get TAU failed\n");
        return FAIL;
    }
    if (get_prop_tpd_params(TPD_PROP_TA, (uint16_t*)&temp_cal_info->org_env_param->Ta) != IRUVC_SUCCESS)
    {
        printf("get TA failed\n");
        return FAIL;
    }
    if (get_prop_tpd_params(TPD_PROP_TU, (uint16_t*)&temp_cal_info->org_env_param->Tu) != IRUVC_SUCCESS)
    {
        printf("get TU failed\n");
        return FAIL;
    }
    if (calculate_org_KE_and_BE_with_nuc_t(temp_cal_info->org_env_param, temp_cal_info->nuc_table, \
        temp_cal_info->gain_flag, temp_cal_info->org_env_factor) != IRTEMP_SUCCESS)
    {
        printf("calculate_KE_and_BE failed\n");
        return FAIL;
    }
    return SUCCESS;
}

int get_compitible_correct_table(uint16_t* correct_table, uint16_t** valid_correct_table)
{
    if (correct_table == NULL)
    {
        printf("correct_table is null\n");
        return -1;
    }
    if ((correct_table[2] == 0xFFFF) && (correct_table[3] == 0xFFFF))
    {
        *valid_correct_table = correct_table + HEAD_SIZE;
    }
    else
    {
        *valid_correct_table = correct_table;
    }
    return 0;
}

uint16_t new_nuc_table[NUC_T_SIZE] = { 0 };
uint16_t new_kt[KT_SIZE] = { 0 };
int16_t new_bt[BT_SIZE] = { 0 };

void multi_point_calibration(uint16_t* correct_table, uint16_t* nuc_table, \
    uint16_t* org_kt, int16_t* org_bt, TempCalibParam_t* temp_calib_param)
{
    int i = 0;
    second_calibration_result_t second_cal_result = { new_kt,new_bt };

    second_calibration_param_t second_cal_param = { temp_calib_param->Ktemp, \
        temp_calib_param->Btemp, temp_calib_param->AddressCA,\
           KT_SIZE, BT_SIZE, NUC_T_SIZE };
    second_cal_param.setting_temp_high = 415.9;
    second_cal_param.setting_temp_low = 123.9;
    second_cal_param.high_vtemp = 8400;
    second_cal_param.low_vtemp = 8400;
    second_cal_param.object_temp_high = 341.15;
    second_cal_param.object_temp_low = 104.5;

    float ems = 0.95;
    float hum = 0.5;
    float dist = 0.25;
    float ta = 25;
    float tu = 25;

    EnvCorrectParam env_cor_param[] = { { dist,ems,hum,ta,tu },\
    { dist, ems, hum, ta, tu }, { dist,ems,hum,ta,tu } };


    MultiPointCalibTemp_t multi_point_temp[] = { { 6042.0 / 16 - 273.15,123.9  },\
    { 7776.5 / 16 - 273.15, 259.4  }, { 9828.8 / 16 - 273.15, 415.9} };
    MultiPointCalibNuc_t multi_point_nuc[] = { { 0,0 },{ 0,0}, { 0,0 } };

    MultiPointCalibParam_t multi_point_calib_param = { env_cor_param[0],
       second_cal_param,8400 };
    MultiPointCalibArray_t multi_point_calib_array = { org_kt, org_bt, nuc_table, correct_table };
    TwoPointCalibResult_t two_point_calib_result = { new_kt, new_bt };
    new_ktbt_recal_double_point_calculate(&multi_point_calib_param, P2, &multi_point_calib_array, &two_point_calib_result);
    printf("new_kt[0]= %d,new_bt[0]= %d\n", two_point_calib_result.new_kt_array[0], two_point_calib_result.new_bt_array[0]);
    for (i = 0; i < sizeof(multi_point_temp) / sizeof(multi_point_temp[0]); i++)
    {
        MultiPointCalibParam_t multi_point_calib_param = { env_cor_param[i],
                  second_cal_param,8400 };

        multi_point_calc_user_defined_nuc(&multi_point_calib_param, 0, \
            & multi_point_calib_array, &two_point_calib_result, \
            & multi_point_temp[i], &multi_point_nuc[i]);
        printf("setting_nuc=%d output_nuc=%d\n", multi_point_nuc[i].setting_nuc / 2, multi_point_nuc[i].output_nuc / 2);
    }

    multi_point_calc_new_nuc_table(nuc_table, multi_point_nuc,
        sizeof(multi_point_temp) / sizeof(multi_point_temp[0]), new_nuc_table);



    for (i = 0; i < NUC_T_SIZE; i++)
    {
        printf("new_nuc_table[%d]= %d %d\n", i, nuc_table[i], new_nuc_table[i]);
    }
    printf("new_nuc_table[%d]= %d\n", 0, new_nuc_table[0]);
}


//nuc_table 为从模组中读取的NUC-T表
//kt_array 为从模组中读取kt表
//bt_array 为从模组中读取bt表

void multi_point_calibration_one_point_correct(uint16_t* correct_table, uint16_t* nuc_table, \
    uint16_t* kt_array, int16_t* bt_array, TempCalibParam_t* temp_calib_param)
{
    int i = 0;


    float ems = 0.95;
    float hum = 0.5;
    float dist = 0.25;
    float ta = 25;
    float tu = 25;
    uint16_t org_nuc_table[NUC_T_SIZE];
    EnvCorrectParam env_cor_param[] = { { dist,ems,hum,ta,tu },\
    { dist, ems, hum, ta, tu }, { dist,ems,hum,ta,tu } };

    second_calibration_param_t second_cal_param = { temp_calib_param->Ktemp, \
    temp_calib_param->Btemp, temp_calib_param->AddressCA,\
       KT_SIZE, BT_SIZE, NUC_T_SIZE };

    TwoPointCalibResult_t two_point_calib_result = { kt_array, bt_array };
    MultiPointCalibTemp_t multi_point_temp[] = { { 6042.0 / 16 - 273.15,123.9  },\
{ 7776.5 / 16 - 273.15, 259.4  }, { 7000 / 16 - 273.15, 180} };
    MultiPointCalibNuc_t multi_point_nuc[] = { { 0,0 },{ 0,0}, { 0,0 } };
    for (i = 0; i < sizeof(multi_point_temp) / sizeof(multi_point_temp[0]); i++)
    {
        MultiPointCalibParam_t multi_point_calib_param = { env_cor_param[i],
                  second_cal_param,8400 };
        MultiPointCalibArray_t multi_point_calib_array = { kt_array, bt_array, nuc_table, correct_table };
        multi_point_calc_user_defined_nuc(&multi_point_calib_param, P2, \
            & multi_point_calib_array, &two_point_calib_result, \
            & multi_point_temp[i], &multi_point_nuc[i]);
        printf("setting_nuc=%d output_nuc=%d\n", multi_point_nuc[i].setting_nuc / 2, multi_point_nuc[i].output_nuc / 2);
    }
    memcpy(org_nuc_table, nuc_table, NUC_T_SIZE * 2);
    multi_point_calc_one_point_correct(nuc_table, multi_point_nuc, 3, new_nuc_table);
    for (i = 0; i < NUC_T_SIZE; i++)
    {
        printf("new_nuc_table[%d]= %d %d\n", i, org_nuc_table[i], new_nuc_table[i]);
    }

    //uint8_t data[NUC_T_SIZE * 2] = { 0 };
    //FILE* fp = NULL;
    //irtemp_log_register(IRTEMP_LOG_DEBUG);
    //uint16_t org_nuc_table[NUC_T_SIZE] = { 0 };
    //uint16_t new_nuc_table[NUC_T_SIZE] = { 0 };
    //uint16_t correct_nuc_table[NUC_T_SIZE] = { 0 };
    //MultiPointCalibNuc_t multi_point_nuc[] = { { 0,0 },{ 0,0}, { 0,0 } };
    //fp = fopen("org_NUC-T.bin", "rb");
    //fread(data, 1, NUC_T_SIZE * 2, fp);
    //fclose(fp);
    //memcpy(org_nuc_table, data, 0x4000);

    //fp = fopen("new_NUC-T.bin", "rb");
    //fread(data, 1, NUC_T_SIZE * 2, fp);
    //fclose(fp);
    //memcpy(new_nuc_table, data, 0x4000);

    //multi_point_nuc[0].setting_nuc = 2290;
    //multi_point_nuc[0].output_nuc = 2290;
    //multi_point_nuc[1].setting_nuc = 5480;
    //multi_point_nuc[1].output_nuc = 5480;
    //multi_point_nuc[2].setting_nuc = 3488;
    //multi_point_nuc[2].output_nuc = 3412;
    //multi_point_calc_one_point_correct(org_nuc_table, multi_point_nuc, 3, correct_nuc_table);


    //for (int i = 0; i < NUC_T_SIZE; i++)
    //{
    //    printf("new_nuc_table[%d]=%d %d %d %d\n", i, org_nuc_table[i], correct_nuc_table[i], new_nuc_table[i], correct_nuc_table[i] - new_nuc_table[i]);
    //}
    //EXPECT_TRUE(true);
}

//command selection
void command_sel(int cmd_type)
{
    int rst = 0;
    double  t_env = 0;


    uint8_t id_data[8] = { 0 };
    uint8_t flash_data[0x30] = { 0 };
    uint16_t temp_data = 0;
    uint8_t r_mirror_flip = 0;

    IruvcPoint_t point_1 = { 160,160 };
    IruvcRect_t rect1 = { 100, 100, 300, 300 };
    IruvcRect_t rect2 = { 10, 10, 100, 100 };
    TpdLineRectTempInfo_t rect1_temp_info = { 0 };

    IruvcPoint_t point_pos = { 80,60 };
    uint32_t file_len = 0;
    double org_temp, dev_temp, new_temp;
    uint16_t temp;
    TempCalInfo_t* temp_cal_info = get_temp_cal_info();
    FILE* fp;
    float ems = 1;
    float ta = 25;
    float new_temp1 = 0;
    float new_temp2 = 0;
    float d = 0;
    uint16_t tau;
    uint8_t ooc_data[0xd9c8] = { 0 };
    uint16_t* cur_correct_table = NULL;

    static uint16_t kt_array[1201] = { 0 };
    static int16_t bt_array[1201] = { 0 };
    static uint16_t nuct_array[8192] = { 0 };
    static TempCalibParam_t temp_calib_param = { 0 };
    switch (cmd_type)
    {
    case 0:
        get_device_info(DEV_INFO_PROJECT_INFO, id_data);
        printf("get_device_info:");
        for (int j = 0; j < 8; j++)
        {
            printf("0x%x ", id_data[j]);
        }
        printf("\n");
        break;
    case 1:
        shutter_sta_set(SHUTTER_CTL_EN);
        ooc_b_update(B_UPDATE);
        printf("shutter\n");
        break;
    case 2:
        shutter_sta_set(SHUTTER_CTL_DIS);
        shutter_manual_switch(SHUTTER_OPEN);
        ooc_b_update(B_UPDATE);
        shutter_sta_set(SHUTTER_CTL_EN);
        printf("shutter background\n");
        break;
    case 3:
        rst = zoom_center_up(PREVIEW_PATH0, ZOOM_STEP4);
        printf("zoom_center_up\n");
        break;
    case 4:
        rst = zoom_center_down(PREVIEW_PATH0, ZOOM_STEP4);
        printf("zoom_center_down\n");
        break;
    case 5:
        get_device_info(DEV_INFO_PROJECT_INFO, id_data);
        printf("get device info project info:");
        for (int j = 0; j < 4; j++)
        {
            printf("0x%x ", id_data[j]);
        }
        printf("\n");
        break;
    case 10:
        tpd_get_rect_temp_info(rect1, &rect1_temp_info);
        printf("tpd_get_rect_temp_info:min(%d,%d):%d, max(%d,%d):%d\n", \
            rect1_temp_info.min_temp_point.x, rect1_temp_info.min_temp_point.y, \
            rect1_temp_info.temp_info_value.min_temp, \
            rect1_temp_info.max_temp_point.x, rect1_temp_info.max_temp_point.y, \
            rect1_temp_info.temp_info_value.max_temp);
        break;
    case 11:
        cur_vtemp_get(&temp_data);
        printf("cur_vtemp_get:%d\n", temp_data);
        break;
    case 13:
        spi_read(0x28e000, 0x30, flash_data);
        for (int j = 0; j < 0x30; j++)
        {
            printf("0x%x ", flash_data[j]);
        }
        printf("spi_read 0x28e000\n");
        break;
    case 14:
        y16_preview_start(PREVIEW_PATH0, (y16_isp_stream_src_types)Y16_MODE_SNR);
        printf("y16_preview_start temp\n");
        break;
    case 15:
        y16_preview_stop(PREVIEW_PATH0);
        printf("y16_preview_stop\n");
        break;
    case 16:  //temperature correction with origin method
        read_nuc_parameter(temp_cal_info);
        printf("read_nuc_parameter\n");
        printf("nuc_table[0]=%d\n", temp_cal_info->nuc_table[0]);
        calculate_org_env_cali_parameter();
        printf("EMS=%d\n", temp_cal_info->org_env_param->EMS);
        printf("TAU=%d\n", temp_cal_info->org_env_param->TAU);
        printf("TA=%d\n", temp_cal_info->org_env_param->Ta);
        printf("Tu=%d\n", temp_cal_info->org_env_param->Tu);
        break;
    case 17: //temperature correction with origin method  for tc1c/wn256/tcbe
        fp = fopen("tau_H.bin", "rb");
        fread(correct_table, 1, sizeof(correct_table), fp);
        fclose(fp);
        calculate_new_env_cali_parameter(correct_table, 1, 27, 27, 0.25, 1);
        tpd_get_point_temp_info(point_pos, &temp);
        org_temp = (double)temp / 16;
        temp_calc_with_new_env_calibration(temp_cal_info, org_temp, &new_temp);
        printf("org_temp=%f\n", org_temp - 273.15);
        printf("new_temp=%f\n", new_temp - 273.15);
        break;
    case 18:  //temperature correction with new method for P2 module
        file_len = get_file_len("new_tau_H.bin");
        printf("file_len=%d\n", file_len);
        fp = fopen("new_tau_H.bin", "rb");
        fread(correct_table, 1, file_len, fp);
        fclose(fp);

        get_compitible_correct_table(correct_table, &cur_correct_table);//新旧版本的修正表兼容
        d = 5;
        tpd_get_point_temp_info(point_pos, &temp);  //获取固件中的点温度
        dev_temp = (double)temp / 16;  //
        temp_calc_without_any_correct(temp_cal_info, dev_temp, &org_temp);  //计算出未经任何修正的温度数据
        org_temp = org_temp - 273.15;
        printf("dev_temp=%f\n", dev_temp - 273.15);
        printf("org_temp=%f\n", org_temp);
        read_tau_with_target_temp_and_dist(cur_correct_table, org_temp, d, &tau); //根据目标温度和距离查找等效大气透过率
        temp_correct(ems, tau, ta, org_temp, &new_temp1);//第一次修正得到修正后的目标温度
        read_tau_with_target_temp_and_dist(cur_correct_table, new_temp1, d, &tau); //根据第一次修正的结果再次查找等效大气透过率
        temp_correct(ems, tau, ta, org_temp, &new_temp2);//迭代两次修正
        printf("new_temp=%f\n", new_temp2);
        break;
    case 19:
        set_prop_tpd_params(TPD_PROP_GAIN_SEL, 0);
        printf("set_prop_tpd_params to low\n");
        break;
    case 20:
        set_prop_tpd_params(TPD_PROP_GAIN_SEL, 1);
        printf("set_prop_tpd_params to high\n");
        break;
    case 23:
        dpc_auto_calibration(30);
        printf("dpc_auto_detect completed\n");
        break;
    case 24:
        restore_default_cfg(DEF_CFG_TPD);
        printf("dpc_auto_detect completed\n");
        break;
    case 25:
        zoom_position_up(PREVIEW_PATH0, ZOOM_STEP4, point_pos);
        printf("zoom_position_up completed\n");
        break;
    case 26:
        zoom_position_down(PREVIEW_PATH0, ZOOM_STEP4, point_pos);
        printf("zoom_center_down completed\n");
        break;
    case 27:
        set_prop_image_params(IMAGE_PROP_SEL_MIRROR_FLIP, 3);
        printf("IMAGE_PROP_SEL_MIRROR_FLIP completed\n");
        break;
    case 28:
        set_prop_image_params(IMAGE_PROP_SEL_MIRROR_FLIP, 2);
        printf("IMAGE_PROP_SEL_MIRROR_FLIP completed\n");
        break;
    case 29:
        set_prop_tpd_params(TPD_PROP_GAIN_SEL, 0);
        set_prop_tpd_params(TPD_PROP_EMS, 128);
        printf("set_prop_tpd_params to low gain\n");
        restore_default_cfg(DEF_CFG_TPD);
        get_tpd_kt_array((uint8_t*)kt_array);
        printf("get_tpd_kt_array completed\n");
        printf("kt_array[0]=%d kt_array[1200]=%d\n", kt_array[0], kt_array[1200]);
        get_tpd_bt_array((uint8_t*)bt_array);
        printf("get_tpd_bt_array completed\n");
        printf("bt_array[0]=%d bt_array[1200]=%d\n", bt_array[0], bt_array[1200]);
        get_tpd_nuc_t_array((uint8_t*)nuct_array);
        printf("get_tpd_nuc_t_array completed\n");
        printf("nuct_array[0]=%d nuct_array[8191]=%d\n", nuct_array[0], nuct_array[8191]);
        get_tpd_calib_param(&temp_calib_param);
        printf("get_tpd_calib_param completed\n");
        printf("Ktemp=%d Btemp=%d AddressCA=%d\n", temp_calib_param.Ktemp, temp_calib_param.Btemp, temp_calib_param.AddressCA);
        break;
    case 30:
        file_len = get_file_len("tau_L.bin");
        fp = fopen("tau_L.bin", "rb");
        fread(correct_table, 1, file_len, fp);
        fclose(fp);
        multi_point_calibration(correct_table, nuct_array, kt_array, bt_array, &temp_calib_param);
        break;
    case 31:
        printf("new_kt[0]=%d\n", new_kt[0]);
        set_tpd_kt_array((uint8_t*)new_kt);
        printf("set_tpd_kt_array completed new_kt[0]=%d\n", new_kt[0]);
        printf("new_bt[0]=%d\n", new_bt[0]);
        set_tpd_bt_array((uint8_t*)new_bt);
        printf("set_tpd_bt_array completed new_bt[0]=%d\n", new_bt[0]);
        printf("new_nuc_table[0]=%d\n", new_nuc_table[0]);
        set_tpd_nuc_t_array((uint8_t*)new_nuc_table);
        printf("set_tpd_bt_array completed new_nuc_table[0]=%d\n", new_nuc_table[0]);
        break;
    case 32:
        set_prop_tpd_params(TPD_PROP_GAIN_SEL, 0);
        set_prop_tpd_params(TPD_PROP_EMS, 128);
        printf("set_prop_tpd_params to low gain\n");
        get_tpd_kt_array((uint8_t*)kt_array);
        printf("get_tpd_kt_array completed\n");
        printf("kt_array[0]=%d kt_array[1200]=%d\n", kt_array[0], kt_array[1200]);
        get_tpd_bt_array((uint8_t*)bt_array);
        printf("get_tpd_bt_array completed\n");
        printf("bt_array[0]=%d bt_array[1200]=%d\n", bt_array[0], bt_array[1200]);
        get_tpd_nuc_t_array((uint8_t*)nuct_array);
        printf("get_tpd_nuc_t_array completed\n");
        printf("nuct_array[0]=%d nuct_array[8191]=%d\n", nuct_array[0], nuct_array[8191]);
        get_tpd_calib_param(&temp_calib_param);
        printf("get_tpd_calib_param completed\n");
        printf("Ktemp=%d Btemp=%d AddressCA=%d\n", temp_calib_param.Ktemp, temp_calib_param.Btemp, temp_calib_param.AddressCA);
        break;
    case 33:
        file_len = get_file_len("tau_L.bin");
        fp = fopen("tau_L.bin", "rb");
        fread(correct_table, 1, file_len, fp);
        fclose(fp);
        irtemp_log_register(IRTEMP_LOG_ERROR);
        multi_point_calibration_one_point_correct(correct_table, nuct_array, kt_array, bt_array, &temp_calib_param);
        break;
    case 34:
        printf("new_nuc_table[0]=%d\n", new_nuc_table[0]);
        set_tpd_nuc_t_array_to_ddr((uint8_t*)new_nuc_table);
        printf("set_tpd_bt_array completed new_nuc_table[0]=%d\n", new_nuc_table[0]);
        break;
    case 35:
        printf("new_nuc_table[0]=%d\n", new_nuc_table[0]);
        set_tpd_nuc_t_array((uint8_t*)new_nuc_table);
        printf("set_tpd_bt_array completed new_nuc_table[0]=%d\n", new_nuc_table[0]);
        break;
    default:
        break;

    }
    //printf("command rst:%d\n", rst);
}

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