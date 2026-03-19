//================ RECEBE O PACOTE DE DL DA CAMADA DE REDE ========
void Transp_radio_receive_DL() { 
  //neste ponto pode ser implementado um controle relacionado ao recebimento não sequencial de pacotes de DL
  App_radio_receive_DL();
}


//================ ENVIA O PACOTE DE UL À CAMADA DE REDE ========
void Transp_radio_send_UL() { 
  // neste ponto pode ser implementado um controle relacionado ao recebimento não sequencial de pacotes de DL
  Net_radio_send_UL();
}
