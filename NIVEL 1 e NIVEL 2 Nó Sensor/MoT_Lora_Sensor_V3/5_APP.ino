void App_Initialize() {
  pinMode(D2, OUTPUT);
  pinMode(PIN_LED_ONBOARD, OUTPUT);
  digitalWrite(PIN_LED_ONBOARD, LOW);
  Serial.println("LoRa NODE SENSOR Init OK.");
}
void App_radio_receive_DL() {


  App_radio_send_UL();  // Chama a função da camada de Aplicação de UL

}

void App_radio_send_UL() {
  // Neste ponto zeramos o pacote de UL para garantir que ele não está carregando nenhuma informação de comunicação anterior.
  for (int i = 0; i < TAMANHO_PACOTE; i++) {
    PacoteUL[i] = 0;
  }

  // Armazene as informações no PacoteUL[] ele é que será enviado
  lum = analogRead(A0); // trocar para o App_radio_send
  PacoteUL[16] = 44; // Aqui está o tipo de sensor, no caso 44 é um LDR
  PacoteUL[17] = (lum/256);
  PacoteUL[18] = (lum%256);
  Serial.println(PacoteUL[20]);
  Serial.println(PacoteUL[21]);
  
  Transp_radio_send_UL();
}
