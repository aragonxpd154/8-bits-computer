; Teste - SUB com resultado negativo: 5 - 9 = -4 (252 sem sinal)
; Resultado esperado no display: 252
        LDA a
        SUB b
        OUT
        HLT
a:      DB 5
b:      DB 9
