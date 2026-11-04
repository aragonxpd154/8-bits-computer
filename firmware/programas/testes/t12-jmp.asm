; Teste - JMP: pula a instrucao LDI 9
; Resultado esperado no display: 1
        LDI 1
        JMP fim
        LDI 9
fim:    OUT
        HLT
