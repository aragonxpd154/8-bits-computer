//Store vectors with Instructions

#include "defines.c"

char EEPROM_2[] = {
     
     MAI_2|PCO_2, RMO_2|IRI_2|PCI_2, 0,           0,           0,             0,0,0,          // 0000 -> NOP
     MAI_2|PCO_2, RMO_2|IRI_2|PCI_2, IRO_2|MAI_2, RMO_2|ACI_2, 0,             0,0,0,          // 0001 -> LDA
     MAI_2|PCO_2, RMO_2|IRI_2|PCI_2, 0, 0, 0,   0,0,0,          // 0010 -> 
     MAI_2|PCO_2, RMO_2|IRI_2|PCI_2, 0, 0, 0,   0,0,0,          // 0011 -> 
     MAI_2|PCO_2, RMO_2|IRI_2|PCI_2, IRO_2|MAI_2, RMO_2|BRI_2, ALU_2|ACI_2,   0,0,0,          // 0100 -> ADD
     MAI_2|PCO_2, RMO_2|IRI_2|PCI_2, 0, 0, 0,   0,0,0,          // 0101 -> 
     MAI_2|PCO_2, RMO_2|IRI_2|PCI_2, 0, 0, 0,   0,0,0,          // 0110 -> 
     MAI_2|PCO_2, RMO_2|IRI_2|PCI_2, 0, 0, 0,   0,0,0,          // 0111 -> 
     MAI_2|PCO_2, RMO_2|IRI_2|PCI_2, 0, 0, 0,   0,0,0,          // 1000 -> 
     MAI_2|PCO_2, RMO_2|IRI_2|PCI_2, 0, 0, 0,   0,0,0,          // 1001 -> 
     MAI_2|PCO_2, RMO_2|IRI_2|PCI_2, 0, 0, 0,   0,0,0,          // 1010 -> 
     MAI_2|PCO_2, RMO_2|IRI_2|PCI_2, 0, 0, 0,   0,0,0,          // 1011 -> 
     MAI_2|PCO_2, RMO_2|IRI_2|PCI_2, 0, 0, 0,   0,0,0,          // 1100 -> 
     MAI_2|PCO_2, RMO_2|IRI_2|PCI_2, 0, 0, 0,   0,0,0,          // 1101 -> 
     MAI_2|PCO_2, RMO_2|IRI_2|PCI_2, ACO_2|ORI_2, 0,            0,            0,0,0,          // 1110 -> OUT 
     MAI_2|PCO_2, RMO_2|IRI_2|PCI_2, HLT_2,       0,            0,            0,0,0,          // 1111 -> HLT
     
     
     };


char EEPROM_1[] = {
     
     MAI_1|PCO_1, RMO_1|IRI_1|PCI_1, 0,           0,           0,             0,0,0,          // 0000 -> NOP
     MAI_1|PCO_1, RMO_1|IRI_1|PCI_1, IRO_1|MAI_1, RMO_1|ACI_1, 0,             0,0,0,          // 0001 -> LDA
     MAI_1|PCO_1, RMO_1|IRI_1|PCI_1, 0, 0, 0,   0,0,0,          // 0010 -> 
     MAI_1|PCO_1, RMO_1|IRI_1|PCI_1, 0, 0, 0,   0,0,0,          // 0011 -> 
     MAI_1|PCO_1, RMO_1|IRI_1|PCI_1, IRO_1|MAI_1, RMO_1|BRI_1, ALU_1|ACI_1,   0,0,0,          // 0100 -> ADD
     MAI_1|PCO_1, RMO_1|IRI_1|PCI_1, 0, 0, 0,   0,0,0,          // 0101 -> 
     MAI_1|PCO_1, RMO_1|IRI_1|PCI_1, 0, 0, 0,   0,0,0,          // 0110 -> 
     MAI_1|PCO_1, RMO_1|IRI_1|PCI_1, 0, 0, 0,   0,0,0,          // 0111 -> 
     MAI_1|PCO_1, RMO_1|IRI_1|PCI_1, 0, 0, 0,   0,0,0,          // 1000 -> 
     MAI_1|PCO_1, RMO_1|IRI_1|PCI_1, 0, 0, 0,   0,0,0,          // 1001 -> 
     MAI_1|PCO_1, RMO_1|IRI_1|PCI_1, 0, 0, 0,   0,0,0,          // 1010 -> 
     MAI_1|PCO_1, RMO_1|IRI_1|PCI_1, 0, 0, 0,   0,0,0,          // 1011 -> 
     MAI_1|PCO_1, RMO_1|IRI_1|PCI_1, 0, 0, 0,   0,0,0,          // 1100 -> 
     MAI_1|PCO_1, RMO_1|IRI_1|PCI_1, 0, 0, 0,   0,0,0,          // 1101 -> 
     MAI_1|PCO_1, RMO_1|IRI_1|PCI_1, ACO_1|ORI_1, 0,            0,            0,0,0,          // 1110 -> OUT 
     MAI_1|PCO_1, RMO_1|IRI_1|PCI_1, HLT_1,       0,            0,            0,0,0,          // 1111 -> HLT
     
     
     };
     
     
char EEPROM_0[] = {
     
     MAI_0|PCO_0, RMO_0|IRI_0|PCI_0, 0,           0,           0,             0,0,0,          // 0000 -> NOP
     MAI_0|PCO_0, RMO_0|IRI_0|PCI_0, IRO_0|MAI_0, RMO_0|ACI_0, 0,             0,0,0,          // 0001 -> LDA
     MAI_0|PCO_0, RMO_0|IRI_0|PCI_0, 0, 0, 0,   0,0,0,          // 0010 -> 
     MAI_0|PCO_0, RMO_0|IRI_0|PCI_0, 0, 0, 0,   0,0,0,          // 0011 -> 
     MAI_0|PCO_0, RMO_0|IRI_0|PCI_0, IRO_0|MAI_0, RMO_0|BRI_0, ALU_0|ACI_0,   0,0,0,          // 0100 -> ADD
     MAI_0|PCO_0, RMO_0|IRI_0|PCI_0, 0, 0, 0,   0,0,0,          // 0101 -> 
     MAI_0|PCO_0, RMO_0|IRI_0|PCI_0, 0, 0, 0,   0,0,0,          // 0110 -> 
     MAI_0|PCO_0, RMO_0|IRI_0|PCI_0, 0, 0, 0,   0,0,0,          // 0111 -> 
     MAI_0|PCO_0, RMO_0|IRI_0|PCI_0, 0, 0, 0,   0,0,0,          // 1000 -> 
     MAI_0|PCO_0, RMO_0|IRI_0|PCI_0, 0, 0, 0,   0,0,0,          // 1001 -> 
     MAI_0|PCO_0, RMO_0|IRI_0|PCI_0, 0, 0, 0,   0,0,0,          // 1010 -> 
     MAI_0|PCO_0, RMO_0|IRI_0|PCI_0, 0, 0, 0,   0,0,0,          // 1011 -> 
     MAI_0|PCO_0, RMO_0|IRI_0|PCI_0, 0, 0, 0,   0,0,0,          // 1100 -> 
     MAI_0|PCO_0, RMO_0|IRI_0|PCI_0, 0, 0, 0,   0,0,0,          // 1101 -> 
     MAI_0|PCO_0, RMO_0|IRI_0|PCI_0, ACO_0|ORI_0, 0,            0,            0,0,0,          // 1110 -> OUT 
     MAI_0|PCO_0, RMO_0|IRI_0|PCI_0, HLT_0,       0,            0,            0,0,0,          // 1111 -> HLT
     
     
     };    
     
     
     
     
     
     
     
