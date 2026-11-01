; Sequencia de Fibonacci (0 1 1 2 3 5 8 13 21 34 55 89 144 233 ...) - repete apos estourar 8 bits
inicio: LDI 0
        STA x
        LDI 1
        STA y
laco:   LDA x
        OUT
        ADD y
        STA z       ; z = x + y
        LDA y
        STA x       ; x = y
        LDA z
        STA y       ; y = z
        JMP laco
x:      DB 0
y:      DB 0
z:      DB 0
