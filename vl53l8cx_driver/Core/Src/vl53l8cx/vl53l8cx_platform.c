#include "vl53l8cx/vl53l8cx_platform.h"

// Write one byte
int32_t VL53L8CX_WrByte(VL53L8CX_Platform *p, uint16_t reg, uint8_t data)
{
    return (int32_t)HAL_I2C_Mem_Write(p->hi2c, p->address, reg,
                                      I2C_MEMADD_SIZE_16BIT, &data, 1, HAL_MAX_DELAY);
}

// Read one byte
int32_t VL53L8CX_RdByte(VL53L8CX_Platform *p, uint16_t reg, uint8_t *data)
{
    return (int32_t)HAL_I2C_Mem_Read(p->hi2c, p->address, reg,
                                     I2C_MEMADD_SIZE_16BIT, data, 1, HAL_MAX_DELAY);
}

// Write multiple bytes
int32_t VL53L8CX_WrMulti(VL53L8CX_Platform *p, uint16_t reg, uint8_t *pdata, uint32_t count)
{
    return (int32_t)HAL_I2C_Mem_Write(p->hi2c, p->address, reg,
                                      I2C_MEMADD_SIZE_16BIT, pdata, count, HAL_MAX_DELAY);
}

// Read multiple bytes
int32_t VL53L8CX_RdMulti(VL53L8CX_Platform *p, uint16_t reg, uint8_t *pdata, uint32_t count)
{
    return (int32_t)HAL_I2C_Mem_Read(p->hi2c, p->address, reg,
                                     I2C_MEMADD_SIZE_16BIT, pdata, count, HAL_MAX_DELAY);
}

// Swap buffer (big-endian <-> little-endian, 4 bytes at a time)
void VL53L8CX_SwapBuffer(uint8_t *pbuffer, int size)
{
    for (int i = 0; i < size; i += 4) {
        uint8_t tmp;
        tmp = pbuffer[i];     pbuffer[i]   = pbuffer[i+3]; pbuffer[i+3] = tmp;
        tmp = pbuffer[i+1];   pbuffer[i+1] = pbuffer[i+2]; pbuffer[i+2] = tmp;
    }
}

// Delay in milliseconds
int32_t VL53L8CX_WaitMs(VL53L8CX_Platform *p, int32_t wait_ms)
{
    (void)p;  // unused
    HAL_Delay(wait_ms);
    return 0;
}