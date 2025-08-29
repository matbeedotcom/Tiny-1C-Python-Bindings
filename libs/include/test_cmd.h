#pragma once
#include "thermal_cam_cmd.h"


#ifdef __cplusplus
extern "C" {
#endif

    /**
     * @brief Read ddr data from ISP chip
     *
     * @param[in] memory address
     * @param[in] data length
     * @param[out] the data read from memory
     *
     * @return see iruvc_error_t
     */
    DLLEXPORT iruvc_error_t ddr_read(uint32_t addr, uint16_t wlen, uint8_t* pbyData);


    /**
     * @brief Write ddr data to ISP chip
     *
     * @param[in] memory address
     * @param[in] data length
     * @param[in] the data write to memory
     *
     * @return see iruvc_error_t
     */
    DLLEXPORT iruvc_error_t ddr_write(uint32_t addr, uint16_t wlen, uint8_t* pbyData);



    /**
     * @brief read flash to memory with DMA
     * @param[in] dwAddr1 dest address in memory
     * @param[in] dwAddr2 src address in flash
     * @param[in] len data length
     *
     * @return see iruvc_error_t
     */
    DLLEXPORT iruvc_error_t spi_dma_read(uint32_t dwAddr1, uint32_t dwAddr2, uint16_t len);


    /**
     * @brief write memory to flash with DMA
     * @param[in] dwAddr1 src address in memory
     * @param[in] dwAddr2 dest address in flash
     * @param[in] len data length
     *
     * @return see iruvc_error_t
     */
    DLLEXPORT iruvc_error_t spi_dma_write(uint32_t dwAddr1, uint32_t dwAddr2, uint16_t len);



    /**
     * @brief add pseudo dead pixel
     * @param[in] x horizontal coordinate,start from 1, must satisfy x=4*n+2;
     * @param[in] y vertical coordinate,start from 1
     *
     * @return see iruvc_error_t
     */
    DLLEXPORT iruvc_error_t add_pseudo_dead_pixel(uint16_t x, uint16_t y);
#ifdef __cplusplus
}
#endif