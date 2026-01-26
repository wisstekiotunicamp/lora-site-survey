void App_initialize() {
  pinMode(D2, OUTPUT);
  pinMode(D4, OUTPUT);
}

void App_radio_receive() {
  
  // Para não gravar sobre RSSI inicie a armazenar os dados da aplicação a partir de PacoteUL[dataInitAddress];
  // Armazene as informações no PacoteUL[] ele é que será enviado
 digitalWrite(D2, HIGH); // colocar na camada física posteriormente
 delay(10);
 digitalWrite(D2, LOW);
 digitalWrite(D4, HIGH);
 delay(10);
 digitalWrite(D4, LOW); 
 lum = analogRead(A0); // trocar para o App_radio_send
 PacoteUL[20] = (lum/256);
 PacoteUL[21] = (lum%256);
 delay(10);

  App_radio_send();
}

void App_radio_send() {
  
  Transp_radio_send();
}
