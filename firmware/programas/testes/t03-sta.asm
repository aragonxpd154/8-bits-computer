; Teste - STA: grava o acumulador na RAM e le de volta
; Resultado esperado no display: 7
        LDI 7
        STA 15
        LDI 0
        LDA 15
        OUT
        HLT
