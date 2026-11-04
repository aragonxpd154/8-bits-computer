; Teste - AND: 11110000 AND 10101010
; Resultado esperado no display: 160
        LDA a
        AND b
        OUT
        HLT
a:      DB 0b11110000
b:      DB 0b10101010
