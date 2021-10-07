
#include <stdio.h>
#include <stdlib.h>
#include "instructions.h"


int main(int argc, char *argv[])
{
  FILE *arquivo;
  
  arquivo = fopen("EEPROM2.bin","wb");
  fwrite(&EEPROM_2,1,sizeof(EEPROM_2),arquivo);
  fclose(arquivo);
  
  arquivo = fopen("EEPROM1.bin","wb");
  fwrite(&EEPROM_1,1,sizeof(EEPROM_1),arquivo);
  fclose(arquivo);
  
  arquivo = fopen("EEPROM0.bin","wb");
  fwrite(&EEPROM_0,1,sizeof(EEPROM_0),arquivo);
  fclose(arquivo);
  
  printf("Arquivos bin\xA0rios gerados com sucesso!\n");
  
  
  
  system("PAUSE");	
  return 0;
} //end main
