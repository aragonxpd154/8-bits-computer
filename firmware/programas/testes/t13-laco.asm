; Teste - Laco com JMP: soma 3 a cada volta
; Resultado esperado no display: 0, 3, 6, 9, 12 ... (laco infinito)
        LDI 0
volta:  OUT
        ADD tres
        JMP volta
tres:   DB 3
