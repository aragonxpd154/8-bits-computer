; Operacoes logicas: mostra 0xF0 AND 0x3C = 48, OR = 252, XOR = 204, NOT 0xF0 = 15
        LDA a
        AND b
        OUT         ; 48
        LDA a
        OR b
        OUT         ; 252
        LDA a
        XOR b
        OUT         ; 204
        LDA a
        NOT
        OUT         ; 15
        HLT
a:      DB 0xF0
b:      DB 0x3C
