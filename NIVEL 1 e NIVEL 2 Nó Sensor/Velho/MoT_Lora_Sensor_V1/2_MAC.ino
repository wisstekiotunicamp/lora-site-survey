//================ RECEBE O PACOTE DA CAMADA FÍSICA ========
void Mac_radio_receive_DL() { 
  // Aqui pode ser adicionado o Sleep Mode
  Net_radio_receive_DL();
}

//================ ENVIA O PACOTE À CAMADA FÍSICA ========
void Mac_radio_send_UL() {
  // Aqui pode ser adicionado o Sleep Mode
  
  Phy_radio_send_UL();
}
