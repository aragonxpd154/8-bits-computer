; Soma 28 + 14 = 42 e mostra no display.  (Marcos Silva dos Santos)
        LDA x       ; A <- 28
        ADD y       ; A <- A + 14
        OUT         ; display = 42
        HLT
x:      DB 28
y:      DB 14
