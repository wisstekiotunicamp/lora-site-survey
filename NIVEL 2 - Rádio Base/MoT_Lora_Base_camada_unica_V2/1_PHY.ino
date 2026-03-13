//==================================================================================================================
//======================= PACOTE DOWN LINK - PACOTE VINDO DO PYTHON PARA SER ENVIADO AO NÓ SENSOR ===========================
//==================================================================================================================
// Pacote proveniente do Python pela serial deve ser enviado para o nó sensor. Primeiro o pacote é recebido pela serial USB e depois é encaminhado para o RF95
// ----------------------LEITURA DO BUFFER RX DA SERIAL PACOTE VINDO DA MAC DO PYTHON PARA DL----------------------------------------------------------------------------------------------------//

void Phy_serial_receive_DL() {  // Funcao de recepcao de pacote da Camada Física
  
  //===================== RECEPCAO DO PACOTE DL
  if (Serial.available() >= TAMANHO_PACOTE) {  // Testa se tem 52 bytes na serial

    for (byte i = 0; i < TAMANHO_PACOTE; i++)  // PacoteUL[#] é preenchido com zero e PacoteDL[#] recebe os bytes do buffer
    {
      PacoteDL[i] = Serial.read();  // Zera o pacote de transmissão
      //delay(1);                     // Intervalo de 1 ms para cada ciclo do for para estabilidade
    }
    
    // ADICIONADO Variáveis de recebimento do valores de rádio LoRa
    valor_new_SF = PacoteDL[0]; // Byte DL[0] valor de rádio LoRa de Spreading Spectrum
    valor_new_BW = PacoteDL[1]; // Byte DL[1] valor de rádio LoRa de Bandwidth

    // Configura Valor de Bandwidth de acordo com o valor recebido no Byte[1]
    if (valor_new_BW == 3){
      valor_new_BW = 500E3;
    }
    else if (valor_new_BW == 2){
      valor_new_BW = 250E3;
    }
    else if (valor_new_BW == 1){
      valor_new_BW = 125E3;
    }

    valor_new_CR = PacoteDL[2]; // Byte DL[2] valor de rádio LoRa de CodingRate
    valor_new_PW = PacoteDL[3]; // Byte DL[3] valor de rádio LoRa de Potência de Rádio LoRa
    cmd_new_config = PacoteDL[4]; // Byte DL[11] Receb comando de reconfiguração de Rádio LoRa

    // Primeiro ciclo
    // Caso comando de reconfiguração da rádio LoRa, Base LoRa confirma recebimento do Comando
    if (cmd_new_config == 1){
      confirm_new_config = 1;
    }
    // Segundo Ciclo
    // Caso incremento do comando de reconfiguração da rádio LoRa, Nível 3 recebeu confirmação do primeiro ciclo dos dois Devices
    // Base LoRa confirma recebimento do Comando do segundo ciclo e controla se há modificações de config. de rádio
    if ((cmd_new_config == 2) & ((valor_new_SF != valor_run_SF) || (valor_new_BW != valor_run_BW) || (valor_new_CR != valor_run_CR) || (valor_new_PW != valor_run_PW))){
        confirm_new_config = 2;
        valor_run_SF = valor_new_SF;
        valor_run_BW = valor_new_BW;
        valor_run_CR = valor_new_CR;
        valor_run_PW = valor_new_PW;
    }
    // Terceiro Ciclo
    // Caso novo incremento do comando de reconfiguração da rádio LoRa, Nível 3 recebeu confirmação do segundo ciclo dos dois Devices
    // Base LoRa confirma recebimento do Comando do terceiro ciclo e confirma as modificações de config. de rádio
    if (cmd_new_config == 3){
      confirm_new_config = 3;
    }
    

// ----------------------ENVIO DO PACOTE DE DOWN LINK ATRAVÉS DO RF95----------------------------------------------------------------------------------------------------//
    Phy_radio_send_DL();  // chama a funcao de recepcao da camada de controle de acesso ao meio
  }
}

//========================= ENVIA PACOTE DL PARA NÓ SENSOR ATRAVÉS DO RF95
//O pacote DL recebido pela serial proveniente do Nível 3 é enviado para o RF95
void Phy_radio_send_DL() {
  //#ifdef DEBUG
  //Serial.println("Inicia envio de pacote");
  //#endif
  LoRa.beginPacket();                   // start packet
  for (int i = 0; i < TAMANHO_PACOTE; i++) {
    LoRa.write(PacoteDL[i]);              // add data to packet
  }
  LoRa.endPacket();                     // finish packet and send it
  // Pisca LED azul do NodeMCU
  digitalWrite(LED_BUILTIN, LOW);  // Liga o LED (nível LOW acende no NodeMCU)
  delay(1);                      // Espera 500ms
  digitalWrite(LED_BUILTIN, HIGH); // Desliga o LED
  delay(1);                      // Espera 1ms
}

//==================================================================================================================
//======================= PACOTE UL LINK - PACODE VINDO NÓ SENSOR ENCAMINHADO PARA PYTHON===========================
//==================================================================================================================
// Pacote que chega no RF95 vindo do nó sensor e é passado para o buffer de TX da serial
//--------------------------- RECEBE PACOTE UL VINDO DO NÓ SENSOR ATRAVÉS DO MÓDULO RF95

void Phy_radio_receive_UL() {
  uint8_t packetSize = LoRa.parsePacket();
  if (packetSize > 0) {
    if (packetSize >= TAMANHO_PACOTE) {
      for (int i = 0; i < TAMANHO_PACOTE; i++) {
        PacoteUL[i] = LoRa.read();
      }
      
      RSSI_dBm_UL = LoRa.packetRssi();
      SNR_UL = LoRa.packetSnr();

//===================================== IMPORTANTE - OPÇÃO VERIFICAÇÃO DE ENDEREÇO OU MODO PROMÍSCUO========================
// Quando recebe o pacote a base pode verificar o endereço de destino ou trabalhar em modo promíscuo.
//===================== QUANDO A BASE  VERIFICA O ENDENREÇO DE DESTINO O PACOTE SÓ É ENVIADO PARA A SERIAL CASO A BASE SEJA O DESTINATÁRIO - nesse caso descomentar o bloco abaixo
// Esta é uma função originalmente da camada de rede, mas existe um cross-layer para verificação do endereço de destino, recebendo somente os pacotes que são destinados para a base

      if (PacoteUL[RECEIVER_ID] == MY_ID) {
        // Garante que Nó Sensor também recebeu comando de alteração de rádio e confirmou
        confirm_sensor_recev_modif = PacoteUL[4]; // PacoteUL[11] recebe confirmação do nó sensor do recebimento
        Phy_serial_send_UL();  //Chama a função de envio da Camada Física
      }

//===================== QUANDO A BASE TRABALHA EM MODO PROMÍSCUO - nesse caso descomentar o bloco abaixo
// neste caso não existe a verificação do endereço de destino e todos os pacotes recebidos pelo rádio são repassados para a serial, o controle do endereço, caso necessário, deverá ser executado no nível 3
     
      // Phy_serial_send();  //Chama a função de envio da Camada Física

//=========================================================================================================================


    }
  }
}

//===================== ESCREVE NA SERIAL PACOTE UL
void Phy_serial_send_UL() { // Funcao de envio de pacote de UL para o computador via buffer TX da serial do NodeMCU
//--- Bloco que faz adequação da leitura de RSSI para um byte ---


  if(RSSI_dBm_UL > -10.5)  // Caso a RSSI medida esteja acima do valor superior -10,5 dBm
  {
   RSSI_UL = 127; // equivalente a -10,5 dBm 
  }

  if(RSSI_dBm_UL <= -10.5 && RSSI_dBm_UL >= -74) // Caso a RSSI medida esteja no intervalo [-10,5 dBm e -74 dBm]
  {
   RSSI_UL = ((RSSI_dBm_UL +74)*2) ;
  }

  if(RSSI_dBm_UL < -74) // Caso a RSSI medida esteja no intervalo ]-74 dBm e -138 dBm]
  {
   RSSI_UL = (((RSSI_dBm_UL +74)*2)+256) ;
  }

  // =================Informações de gerência do pacote
  PacoteUL[RSSI_UPLINK] = RSSI_UL;  // aloca RSSI_UL
  PacoteUL[LQI_DOWNLINK] = (byte)SNR_UL%256;
  
  // Caso ambos Devices receberam comando de alteração de config. de rádio escreve no Byte[11] para Nível 3
  // confirmação do primeiro ciclo
  if ((confirm_new_config == 1) & (confirm_sensor_recev_modif == 1)){
    PacoteUL[4] = 2;
  }
  else if ((confirm_new_config == 2) & (confirm_sensor_recev_modif == 2)){
    // Confirmação do segundo ciclo de ambos devices
    PacoteUL[4] = 3;
    // Altera na Base as configurações de rádio para na próxima janela realizar comunicação já na nova configuração
    LoRa.setTxPower(valor_new_PW);                       // Potência de Transmissão (Configurado em bibliotecas.h)
    LoRa.setSpreadingFactor(valor_new_SF);       // Fator de Espalhamento  (Configurado em bibliotecas.h)
    LoRa.setSignalBandwidth(valor_new_BW);       // Banda do Sinal (Configurado em bibliotecas.h)
    LoRa.setCodingRate4(valor_new_CR);     // Coding Rate  (Configurado em bibliotecas.h)
  }
  else if ((confirm_new_config == 3) & (confirm_sensor_recev_modif == 3)){
    // Confirmação do terceiro ciclo de ambos devices já com Nova Configuração de Rádio
    PacoteUL[4] = 4;
  }
  else if ((confirm_new_config == 1) & (confirm_sensor_recev_modif == 0)){
    // Indica ao Nível 3 que apenas um dos Devices LoRa (Base) recebeu/processou o Comando de alteração
    PacoteUL[4] = 1;
  }
  else if ((confirm_new_config == 0) & (confirm_sensor_recev_modif == 1)){
    // Indica ao Nível 3 que apenas um dos Devices LoRa (Nó Sensor) recebeu/processou o Comando de alteração
    PacoteUL[4] = 1;
  }
  else {
    // Sem necessidade de alteração de Rádio
    PacoteUL[4] = 0;
  }
  // Transmissão do pacote pela serial do Arduino
  for (int i = 0; i < TAMANHO_PACOTE; i++) {
    Serial.write(PacoteUL[i]);
  }
}

