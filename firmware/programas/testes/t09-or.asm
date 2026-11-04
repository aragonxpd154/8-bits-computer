; Teste - OR: 11110000 OR 00001111
; Resultado esperado no display: 255
        LDA a
        OR b
        OUT
        HLT
a:      DB 0b11110000
b:      DB 0b00001111
