#include <SPI.h>
#include <LoRa.h>

//#define DEBUG

#define MY_ID 0
#define TAXA_SERIAL 115200
#define TAMANHO_PACOTE 52
#define MODO_DO_DISPOSITIVO BASE

/*Configurações LoRa*/
#define csPin 15                 // LoRa radio chip select
#define resetPin 0               // LoRa radio reset
#define irqPin 5                 // change for your board; must be a hardware interrupt pin

#define FREQUENCY_IN_HZ 919E6    // LoRa Frequency
#define txPower 17               // TX power in dBm, defaults to 17
#define spreadingFactor 7        // ranges from 6-12,default 7 see API docs
#define signalBandwidth 125E3    // signal bandwidth in Hz, Supported values are 7.8E3, 10.4E3, 15.6E3, 20.8E3, 31.25E3, 41.7E3, 62.5E3, 125E3, 250E3, and 500E3.
#define codingRateDenominator 5  // denominator of the coding rate, Supported values are between 5 and 8, these correspond to coding rates of 4/5 and 4/8. The coding rate numerator is fixed at 4.
//#define loraCRC                // Enable or disable CRC usage, by default a CRC is not used. (uncomment to Enable)


byte PacoteDL[TAMANHO_PACOTE];
byte PacoteUL[TAMANHO_PACOTE];
int contadorUL;
int contadorDL;
int RSSI_dBm_UL, RSSI_UL, LQI_UL;
float SNR_UL;

enum bytes_do_pacote{
  /* Physical Layer */
  RSSI_UPLINK   = 0,
  LQI_UPLINK    = 1,
  RSSI_DOWNLINK = 2,
  LQI_DOWNLINK  = 3,

  /* MAC Layer */
  MAC_COUNTER_MSB = 4, 
  MAC_COUNTER_LSB = 5,
  MAC3 = 6,
  MAC4 = 7,

  /* Network Layer */
  RECEIVER_ID     = 8,
  NET2            = 9,
  TRANSMITTER_ID  = 10,
  NET4            = 11,

  /* Transport Layer */
  DL_COUNTER_MSB = 12,
  DL_COUNTER_LSB = 13,
  UL_COUNTER_MSB = 14,
  UL_COUNTER_LSB = 15,

  /* Application Layer */
  APP1 = 16,
  APP2 = 17,
  APP3 = 18,
  APP4 = 19,
  APP5 = 20,
  APP6 = 21,
  APP7 = 22,
  APP8 = 23,
  APP9 = 24,
  APP10 = 25,
  APP11 = 26,
  APP12 = 27,
  APP13 = 28, 
  APP14 = 29,
  APP15 = 30,
  APP16 = 31,
  APP17 = 32,
  APP18 = 33,
  APP19 = 34,
  APP20 = 35,
  APP21 = 36,
  APP22 = 37,
  APP23 = 38,
  APP24 = 39,
  APP25 = 40,
  APP26 = 41,
  APP27 = 42,
  APP28 = 43,
  APP29 = 44,
  APP30 = 45,
  APP31 = 46,
  APP32 = 47,
  APP33 = 48,
  APP34 = 49,
  APP35 = 50,
  APP36 = 51,
};
