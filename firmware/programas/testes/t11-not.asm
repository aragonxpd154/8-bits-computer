; Teste - NOT: inverte 00001111
; Resultado esperado no display: 240
        LDA a
        NOT
        OUT
        HLT
a:      DB 0b00001111
