; Teste - XOR: 11001100 XOR 10101010
; Resultado esperado no display: 102
        LDA a
        XOR b
        OUT
        HLT
a:      DB 0b11001100
b:      DB 0b10101010
