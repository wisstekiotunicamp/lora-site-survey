void Transp_initialize() {
 // colocar um contador de pacotes recebidos do nível 3
}

void Transp_radio_receive() {// colocar um contador de pacotes recebidos contador de downlink
  contadorDL = ((PacoteDL[12]*256) + PacoteDL[13]); 

  App_radio_receive();
}

void Transp_radio_send() {
  if (contadorDL == 0){
    contadorUL = 0;
  }
  contadorUL = contadorUL + 1;
  PacoteUL[UL_COUNTER_MSB] =(byte)contadorUL/256;
  PacoteUL[UL_COUNTER_LSB] = (byte)contadorUL%256;
  Serial.println(contadorUL);
  Net_radio_send();
}
