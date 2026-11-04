; Teste - ADD: 100 + 55
; Resultado esperado no display: 155
        LDA a
        ADD b
        OUT
        HLT
a:      DB 100
b:      DB 55
