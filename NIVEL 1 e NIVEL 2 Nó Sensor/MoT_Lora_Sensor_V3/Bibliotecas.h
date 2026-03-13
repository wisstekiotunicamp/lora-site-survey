#include <SPI.h>
#include <LoRa.h>

//#define DEBUG

/*Configurações LoRa*/
#define csPin 15                 // LoRa radio chip select
#define resetPin 0               // LoRa radio reset
#define irqPin 5                 // change for your board; must be a hardware interrupt pin

// Led Vermelho - ENVIO e RECEBIMENTO
const int PIN_LED_ONBOARD = D4; 


// # Configuração Inicial Rádio LoRa
int valor_init_SF = 12; // # Spreading Factor inicial = Maior espalhamento possível 12 (de 7 a 12)
int valor_init_BW = 1; // # Bandwidth inicial = 125kHz (1 = 125kHz | 2 = 250kHz | 3 = 500kHz)
int valor_init_CR = 8; // # CodingRate Denominator = 5/4 (5/4 | 6/4 | 7/4 | 8/4)
int valor_init_PW = 17; // # TX Power = 1 a 17???
int cmd_init_config = 0; // # Comando de Downlink de mudança de configuração de rádio LoRa

// # Configuração Atual Rádio LoRa
int valor_run_SF = 12; // # Spreading Factor inicial = Maior espalhamento possível 12 (de 7 a 12)
int valor_run_BW = 1; // # Bandwidth inicial = 125kHz (1 = 125kHz | 2 = 250kHz | 3 = 500kHz)
int valor_run_CR = 8; // # CodingRate Denominator = 5/4 (5/4 | 6/4 | 7/4 | 8/4)
int valor_run_PW = 17; // # TX Power = 1 a 17???
int cmd_run_config = 0; // # Comando de Downlink de mudança de configuração de rádio LoRa

// # Configuração Nova Rádio LoRa
int valor_new_SF = 12; // # Spreading Factor inicial = Maior espalhamento possível 12 (de 7 a 12)
int valor_new_BW = 1; // # Bandwidth inicial = 125kHz (1 = 125kHz | 2 = 250kHz | 3 = 500kHz)
int valor_new_CR = 8; // # CodingRate Denominator = 5/4 (5/4 | 6/4 | 7/4 | 8/4)
int valor_new_PW = 17; // # TX Power = 1 a 17???
int cmd_new_config = 0; // # Comando de Downlink de mudança de configuração de rádio LoRa

int start_teste_site_suvey = 0;
int confirm_new_config = 0;
int confirm_sensor_recev_modif = 0;

int modif_radio_lora = 0;

enum bytes_do_pacote{
};
