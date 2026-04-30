#ifndef VL53L8CX_PLATFORM_H_
#define VL53L8CX_PLATFORM_H_

#include "stm32u5xx_hal.h"
#include <stdint.h>

#ifndef VL53L8CX_NB_TARGET_PER_ZONE
#define VL53L8CX_NB_TARGET_PER_ZONE    1U
#endif

typedef struct
{
    I2C_HandleTypeDef *hi2c;
    uint8_t address;
} VL53L8CX_Platform;

// Functions called by VL53L8CX API
int32_t VL53L8CX_WrByte(VL53L8CX_Platform *p, uint16_t reg, uint8_t data);
int32_t VL53L8CX_RdByte(VL53L8CX_Platform *p, uint16_t reg, uint8_t *data);
int32_t VL53L8CX_WrMulti(VL53L8CX_Platform *p, uint16_t reg, uint8_t *pdata, uint32_t count);
int32_t VL53L8CX_RdMulti(VL53L8CX_Platform *p, uint16_t reg, uint8_t *pdata, uint32_t count);
void VL53L8CX_SwapBuffer(uint8_t *pbuffer, int size);
int32_t VL53L8CX_WaitMs(VL53L8CX_Platform *p, int32_t wait_ms);

#endif