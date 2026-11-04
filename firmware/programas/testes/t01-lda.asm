; Teste - LDA: carrega um byte da RAM
; Resultado esperado no display: 77
        LDA dado
        OUT
        HLT
dado:   DB 77
