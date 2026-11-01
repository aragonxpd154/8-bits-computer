; Contador infinito: 0, 1, 2, ... 255, 0, 1 ...
        LDI 0
laco:   OUT
        ADD um
        JMP laco
um:     DB 1
