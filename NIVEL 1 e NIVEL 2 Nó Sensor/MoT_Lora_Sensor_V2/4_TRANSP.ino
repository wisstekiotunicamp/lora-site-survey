//================ RECEBE O PACOTE DE DL DA CAMADA DE REDE ========
void Transp_radio_receive_DL() { 
  // implementar a decisão de enviar ou não um pacote por perda em Time Division Multiplex
  //neste ponto pode ser implementado um controle relacionado ao recebimento não sequencial de pacotes de DL
  App_radio_receive_DL();
}


//================ ENVIA O PACOTE DE UL À CAMADA DE REDE ========
void Transp_radio_send_UL() { 
  contadorUL = contadorUL + 1;  // Incrementa o contador de pacote de UL 
  //Confirm_LoRa++;
  PacoteUL[14] =(byte)contadorUL/256;
  PacoteUL[15] = (byte)contadorUL%256;// retirar isso daqui para ontem
  //Serial.println(contadorUL);
  Net_radio_send_UL();
}
