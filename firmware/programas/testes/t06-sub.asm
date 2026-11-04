; Teste - SUB: 90 - 25
; Resultado esperado no display: 65
        LDA a
        SUB b
        OUT
        HLT
a:      DB 90
b:      DB 25
