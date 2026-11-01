"""Dicas de posicionamento das placas (linhas de cima para baixo).
'J' = linha de conectores; listas de refs = linhas de componentes."""
LAYOUTS = {
    'ACC': [['J1', 'J2', 'J3', 'J4', 'J5', 'J6'], ['U1', 'U2', 'U3'], 'LEDS'],
    'B': [['J1', 'J2', 'J3', 'J4', 'J5', 'J6'], ['U1', 'U2', 'U3'], 'LEDS'],
    'IR': [['J1', 'J2', 'J3', 'J4', 'J5'], ['U1', 'U2', 'U3'], 'LEDS'],
    'OUT': [['J1', 'J2', 'J3', 'J4', 'J5', 'J6'], ['U1', 'U2'], 'LEDS'],
    'PC': [['J1', 'J2', 'J3', 'J4', 'J5'], ['U1', 'U2'], 'LEDS'],
    'FETCH': [['J1', 'J2', 'J3'], ['U1', 'U2'], 'LEDS'],
    'RESET': [['J1', 'J2'], ['U1', 'R2'], ['SW1', 'R1', 'C1', 'LED1', 'R3']],
    'CLOCK': [['J1', 'J2'], ['U1', 'U3', 'U2'], ['R1', 'R2', 'R4', 'R5', 'C1', 'C2', 'C3', 'C4'],
              ['RV1', 'SW2', 'SW1', 'LED1']],
    'CD': [['J1', 'J2', 'J3', 'J4', 'J5', 'J6', 'J7', 'J8', 'J9'], ['U1', 'U2', 'U3'], ['R1', 'R2']],
    'DISPLAY': [['J1', 'J2', 'J3'], ['U2', 'U3', 'U4', 'U1'], ['R1', 'R10', 'C5', 'C6', 'SW1'],
                {'refs': ['R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'R9'], 'rot': 90}, ['DS1']],
    'ALU': [['J4', 'J5', 'J6', 'J7', 'J8', 'J9', 'J1', 'J2', 'J3'],
            ['U18', 'U4', 'U2', 'U3', 'U1', 'U5', 'U6'],
            ['U7', 'U8', 'U9', 'U11', 'U10', 'U12'],
            ['U13', 'U14', 'U15', 'U16', 'U17'], 'LEDS'],
    'RAM': [['J1', 'J2', 'J3', 'J4', 'J5'],
            ['U6', 'U7', 'U11', 'U10', 'U12'],
            ['U8', 'U9', 'U1', 'U2'],
            ['U3', 'U4', 'U5'],
            ['C13', 'R18', 'C14', 'R13', 'R16', 'R17', 'RN2', 'RN1'],
            {'refs': ['SW1', 'SW3', 'SW4', 'SW2', 'LED13', 'R14', 'LED14', 'R15'], 'rot': {'SW1': 270, 'SW3': 270, 'R14': 90, 'R15': 90}},
            'LEDS'],
    'BACKPLANE': None,  # layout proprio
}

# textos de serigrafia acima de componentes: placa -> [(ref, texto)]
NOTAS = {
    'RAM': [('SW1', 'END: A3 A2 A1 A0 (ON=1)'), ('SW3', 'DADO: D7 ... D0 (ON=1)'), ('SW4', 'GRAVAR'),
            ('SW2', 'PROG / RUN'), ('LED13', 'PROG'), ('LED14', 'RUN')],
    'CLOCK': [('SW1', 'PASSO'), ('SW2', 'AUTO / MANUAL'), ('RV1', 'VELOCIDADE')],
    'RESET': [('SW1', 'RESET')],
    'DISPLAY': [('SW1', 'COM SINAL / SEM SINAL'), ('DS1', 'CATODO COMUM')],
    'CD': [('U1', 'EEPROM2.bin'), ('U2', 'EEPROM1.bin'), ('U3', 'EEPROM0.bin')],
}

# espacamentos especiais (mm) para placas densas
PARAMS = {
    'ALU': {'gap_row': 13.0, 'ic_gap': 7.0},
    'RAM': {'gap_row': 8.0, 'ic_gap': 5.0},
    'DISPLAY': {'gap_row': 9.0, 'ic_gap': 7.0},
}
