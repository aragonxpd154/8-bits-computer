; Teste - ADD com estouro: 200 + 100 = 300 - 256
; Resultado esperado no display: 44
        LDA a
        ADD b
        OUT
        HLT
a:      DB 200
b:      DB 100
