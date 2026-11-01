; 100 - 58 = 42 (ligue a chave do display em "com sinal" para ver negativos)
        LDA x
        SUB y
        OUT
        HLT
x:      DB 100
y:      DB 58
