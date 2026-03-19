void App_radio_receive_DL() {
  //Nesta camada são feitos os acionamentos ou ajustes enviados pela base no pacote de DL
  

  App_radio_send_UL();  // Chama a função da camada de Aplicação de UL

}

void App_radio_send_UL() {
  // Neste ponto zeramos o pacote de UL para garantir que ele não está carregando nenhuma informação de comunicação anterior.
  for (int i = 0; i < TAMANHO_PACOTE; i++) {
    PacoteUL[i] = 0;
  }

  // Armazene as informações no PacoteUL[] ele é que será enviado

  // ====== Leitura do sensor de luminosidade (LDR) ======
  luminosidade = analogRead(A0);
  Serial.println(luminosidade);
  PacoteUL[16] = 44; // Aqui está o tipo de sensor, no caso 44 é um LDR
  PacoteUL[17] = (luminosidade/256);
  PacoteUL[18] = (luminosidade%256);

  // ====== Leitura do sensor DHT22 (Temperatura e Umidade) ======
  dht22.read2(&temperatura, &umidade, NULL);

  // Multiplica por 100 para transformar o float em inteiro (ex: 25.39 -> 2539)
  int temp_x100 = (int)(temperatura * 100);
  int umid_x100 = (int)(umidade * 100);

  // Empacota a temperatura no payload (mesmo padrão da luminosidade)
  PacoteUL[19] = 22;                // Flag: tipo de sensor DHT22
  PacoteUL[20] = (temp_x100 / 256); // Temperatura - byte alto
  PacoteUL[21] = (temp_x100 % 256); // Temperatura - byte baixo

  // Empacota a umidade no payload (mesmo padrão da luminosidade)
  PacoteUL[22] = 22;                // Flag: tipo de sensor DHT22
  PacoteUL[23] = (umid_x100 / 256); // Umidade - byte alto
  PacoteUL[24] = (umid_x100 % 256); // Umidade - byte baixo

  // Mostra os valores lidos no Serial Monitor
  Serial.print("Temp: ");
  Serial.print(temperatura);
  Serial.print(" *C | Umid: ");
  Serial.print(umidade);
  Serial.println(" %");

  Transp_radio_send_UL();
}
