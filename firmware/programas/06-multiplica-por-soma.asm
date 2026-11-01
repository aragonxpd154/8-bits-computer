; Tabuada do 7 (soma repetida): 7, 14, 21, 28 ... (sem flags o laco nao tem fim)
        LDI 0
laco:   ADD sete
        OUT
        JMP laco
sete:   DB 7
