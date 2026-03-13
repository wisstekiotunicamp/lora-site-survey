#include <SPI.h>
#include <LoRa.h>

//#define DEBUG


#define MY_ID 1 
#define TAXA_SERIAL 115200
#define TAMANHO_PACOTE 52
#define MODO_DO_DISPOSITIVO SENSOR

/*Configurações LoRa*/
#define csPin 15                 // LoRa radio chip select
#define resetPin 0               // LoRa radio reset
#define irqPin 5                 // change for your board; must be a hardware interrupt pin

// Led Vermelho - ENVIO e RECEBIMENTO
const int PIN_LED_ONBOARD = D4; 

#define FREQUENCY_IN_HZ 915E6    // LoRa Frequency
#define txPower 17               // TX power in dBm, defaults to 17
#define spreadingFactor 12        // ranges from 6-12,default 7 see API docs
#define signalBandwidth 125E3    // signal bandwidth in Hz, Supported values are 7.8E3, 10.4E3, 15.6E3, 20.8E3, 31.25E3, 41.7E3, 62.5E3, 125E3, 250E3, and 500E3.
#define codingRateDenominator 5  // denominator of the coding rate, Supported values are between 5 and 8, these correspond to coding rates of 4/5 and 4/8. The coding rate numerator is fixed at 4.
//#define loraCRC                // Enable or disable CRC usage, by default a CRC is not used.


byte PacoteDL[TAMANHO_PACOTE];
byte PacoteUL[TAMANHO_PACOTE];
int contadorUL;
int contadorDL;
int RSSI_dBm_DL, RSSI_DL, LQI_DL;
int tipo, saltos, saltosTotal, dataInitAddress; // Variáveis utilizadas para o roteamento
float SNR_DL;
int lum;



// # Configuração Inicial Rádio LoRa
int valor_init_SF = 12; // # Spreading Factor inicial = Maior espalhamento possível 12 (de 7 a 12)
int valor_init_BW = 1; // # Bandwidth inicial = 125kHz (1 = 125kHz | 2 = 250kHz | 3 = 500kHz)
int valor_init_CR = 5; // # CodingRate Denominator = 5/4 (5/4 | 6/4 | 7/4 | 8/4)
int valor_init_PW = 17; // # TX Power = 1 a 17???
int cmd_init_config = 0; // # Comando de Downlink de mudança de configuração de rádio LoRa

// # Configuração Atual Rádio LoRa
int valor_run_SF = 12; // # Spreading Factor inicial = Maior espalhamento possível 12 (de 7 a 12)
int valor_run_BW = 1; // # Bandwidth inicial = 125kHz (1 = 125kHz | 2 = 250kHz | 3 = 500kHz)
int valor_run_CR = 5; // # CodingRate Denominator = 5/4 (5/4 | 6/4 | 7/4 | 8/4)
int valor_run_PW = 17; // # TX Power = 1 a 17???
int cmd_run_config = 0; // # Comando de Downlink de mudança de configuração de rádio LoRa

// # Configuração Nova Rádio LoRa
int valor_new_SF = 12; // # Spreading Factor inicial = Maior espalhamento possível 12 (de 7 a 12)
int valor_new_BW = 1; // # Bandwidth inicial = 125kHz (1 = 125kHz | 2 = 250kHz | 3 = 500kHz)
int valor_new_CR = 5; // # CodingRate Denominator = 5/4 (5/4 | 6/4 | 7/4 | 8/4)
int valor_new_PW = 17; // # TX Power = 1 a 17???
int cmd_new_config = 0; // # Comando de Downlink de mudança de configuração de rádio LoRa

int start_teste_site_suvey = 0;
int confirm_new_config = 0;
int confirm_sensor_recev_modif = 0;

int modif_radio_lora = 0;

enum bytes_do_pacote{


};
