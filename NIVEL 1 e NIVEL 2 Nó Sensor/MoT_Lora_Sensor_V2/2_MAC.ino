//================ RECEBE O PACOTE DA CAMADA FÍSICA ========
void Mac_radio_receive_DL() { 
  // Aqui colocaremos o set de configuração
  cmd_new_config = PacoteDL[4]; // Byte DL[4] Receb comando de reconfiguração de Rádio LoRa --> Jogar para MAC
      // Jogar tudo abaixo para a MAC
      // Imprime na Serial para DEBUG
      Serial.print("Valor SF: ");
      Serial.println(valor_new_SF);
      Serial.print("Valor BW: ");
      Serial.println(valor_new_BW);
      Serial.print("Valor CR: ");
      Serial.println(valor_new_CR);
      Serial.print("Valor PW: ");
      Serial.println(valor_new_PW);

      Serial.print("cmd_new_config: ");
      Serial.println(cmd_new_config);

      // Primeiro ciclo
      // Caso comando de reconfiguração da rádio LoRa, Base LoRa confirma recebimento do Comando
      if (cmd_new_config == 1){
        confirm_new_config = 1;
      }

      // Segundo Ciclo
      // Caso incremento do comando de reconfiguração da rádio LoRa, Nível 3 recebeu confirmação do primeiro ciclo dos dois Devices
      // Nó Sensor LoRa confirma recebimento do Comando do segundo ciclo e controla se há modificações de config. de rádio      
      if ((cmd_new_config == 2) & ((valor_new_SF != valor_run_SF) || (valor_new_BW != valor_run_BW) || (valor_new_CR != valor_run_CR) || (valor_new_PW != valor_run_PW))){
        confirm_new_config = 2;
        valor_run_SF = valor_new_SF;
        valor_run_BW = valor_new_BW;
        valor_run_CR = valor_new_CR;
        valor_run_PW = valor_new_PW;
      }
    
      // Terceiro Ciclo
      // Caso novo incremento do comando de reconfiguração da rádio LoRa, Nível 3 recebeu confirmação do segundo ciclo dos dois Devices
      // Nó Sensor LoRa confirma recebimento do Comando do terceiro ciclo e confirma as modificações de config. de rádio      
      if (cmd_new_config == 3){
        confirm_new_config = 3;
      }
 
  Net_radio_receive_DL();
}

//================ ENVIA O PACOTE À CAMADA FÍSICA ========
void Mac_radio_send_UL() {
  // Aqui pode ser adicionado o Sleep Mode
  //Jogar tudo para MAC
  // Caso Nó Sensor Devices recebeu comando de alteração de config. de rádio escreve no Byte[11] para a Base LoRa
  // confirmação do primeiro ciclo  
  if (confirm_new_config == 1){
    PacoteUL[4] = 1;
    Serial.print("PacoteUL[4] =: ");
    Serial.println(confirm_new_config);
    modif_radio_lora = 0;
  }
  else if (confirm_new_config == 2){
    // Confirmação do segundo ciclo para alteração das config. de rádio do Nó Sensor
    PacoteUL[4] = 2;
    Serial.print("PacoteUL[4] =: ");
    Serial.println(confirm_new_config);
    modif_radio_lora = 1; // Habilita Nó Sensor a alterar as configurações de Rádio
  }
  else if (confirm_new_config == 3){
    //  Confirmação do terceiro ciclo confirmando a alteração das config. de rádio do Nó Sensor
    PacoteUL[4] = 3;
    Serial.print("PacoteUL[4] =: ");
    Serial.println(confirm_new_config);
    modif_radio_lora = 0;
    confirm_new_config = 0;
  }
  else {
    // Sem necessidade de alteração, ou confirmação de alteração
    PacoteUL[4] = 0;
    modif_radio_lora = 0;
    confirm_new_config = 0;
    Serial.print("PacoteUL[4] =: ");
    Serial.println(confirm_new_config);
  }
  Phy_radio_send_UL();
}
