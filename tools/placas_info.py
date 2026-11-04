"""Textos didaticos de cada placa do Computador 8 Bits v3.0.

Usado por tools/gerar_placas.py (paginas docs/placas/*.md) e pelo visualizador 3D.
Os dados eletricos (componentes, conectores, redes) vem de tools/gerador-kicad/designs.py;
aqui fica so a explicacao em portugues.

Projeto: Marcos Silva dos Santos (MarcosObel) - GPL-3.0
"""

# ordem = ordem de montagem/teste sugerida no manual
PLACAS = {
    'BACKPLANE': dict(
        ordem=1, nome='Backplane / Barramento', icone='🔌',
        resumo='Placa-mãe: entrada de 5 V protegida, barramento D0…D7 com LEDs e todos os sinais entre os módulos.',
        funcao=(
            'É a "placa-mãe" do computador. Não tem lógica: recebe a fonte de 5 V, protege e distribui a '
            'alimentação para os 12 módulos e liga entre si todos os sinais que precisam passar de uma placa '
            'para outra — o **barramento de dados D0…D7** e os **18 sinais de controle** que saem do '
            'Decodificador de Controle. Cada módulo se liga a ela com cabos de 4 vias retos.'),
        funcionamento=[
            '**Entrada de energia.** A fonte entra pelo jack J1 (5,5 × 2,1 mm, centro positivo) ou pelo borne J2. '
            'Passa pela chave LIGA/DESLIGA (SW1) e pelo fusível rearmável F1 (PTC 3 A).',
            '**Proteção contra inversão.** O diodo D1 (1N5822) fica *ao contrário* entre +5 V e GND. Com a polaridade '
            'certa ele não conduz. Se a fonte for ligada invertida, D1 conduz forte, a corrente sobe e o PTC abre — '
            'os CIs ficam protegidos. Depois de corrigir, o PTC volta sozinho em alguns segundos.',
            '**Reserva de energia.** C1 (470 µF) segura a tensão durante os picos de consumo (LEDs e saídas TTL '
            'chaveando juntos); C2 (100 nF) filtra ruído rápido. O LED1 verde indica 5 V presente.',
            '**Barramento.** As linhas D0…D7 passam por todos os conectores BL_* (D0…D3) e BH_* (D4…D7). '
            'Os 8 LEDs vermelhos (LED2…LED9) mostram o valor do barramento em tempo real — é a melhor ferramenta '
            'de depuração do computador: em cada passo do clock você vê quem está escrevendo no barramento.',
            '**Sinais de controle.** Os conectores CD_A…CD_E recebem os 18 sinais do microcódigo e os levam aos '
            'conectores C_* de cada módulo, sempre na mesma ordem de pinos impressa na serigrafia.',
        ],
        blocos=[('J1, J2', 'entrada de 5 V (jack ou borne)'), ('SW1', 'liga/desliga'),
                ('F1', 'fusível rearmável PTC 3 A'), ('D1', 'proteção contra inversão de polaridade'),
                ('C1, C2', 'reserva e filtro da alimentação'),
                ('J3…J14 (P_*)', 'alimentação para cada módulo (+5V +5V GND GND)'),
                ('J15…J28 (BL_*, BH_*)', 'barramento de dados para os 7 módulos que leem/escrevem nele'),
                ('J29…J46 (C_*, CD_*)', 'sinais de controle'), ('J47 (EXPANSAO)', 'saídas livres para futuras placas')],
        leds=[('LED1 (verde)', '5 V presente'), ('LED2…LED9 (vermelhos)', 'valor do barramento D7…D0 (aceso = 1)')],
        controles=[('SW1', 'liga/desliga o computador inteiro')],
        teste=['Sem nenhum módulo ligado, conecte a fonte: LED1 acende e o multímetro mostra 4,9…5,1 V em qualquer P_*.',
               'Meça a resistência entre +5 V e GND com a fonte desligada: deve ser alta (> 1 kΩ, carga dos capacitores).',
               'Com um fio de 1 kΩ, ligue D0 ao +5 V num conector BL_*: o LED de D0 acende. Repita para D1…D7.'],
        atencao=['Use somente fonte **regulada de 5 V** (2 A ou mais). A placa não tem regulador: 9 V ou 12 V queimam os CIs.',
                 'Os conectores estão agrupados por módulo, com o nome escrito ao lado — confira antes de encaixar o cabo.'],
    ),
    'CLOCK': dict(
        ordem=2, nome='Clock', icone='⏱️',
        resumo='Gera o "batimento" do computador: automático (0,7–140 Hz) ou passo a passo, e para no HLT.',
        funcao=(
            'Produz o sinal **CLK** que sincroniza todo o computador, e o seu inverso **/CLK**. Há dois modos: '
            '**AUTOMÁTICO**, com velocidade ajustável no potenciômetro, e **MANUAL**, em que cada toque no botão '
            'PASSO gera exatamente um pulso — ideal para ver cada passo da instrução nos LEDs. Quando o programa '
            'executa `HLT`, o sinal HLT chega aqui e trava o clock.'),
        funcionamento=[
            '**Metade 1 do NE556 — astável.** Oscila sozinho, carregando e descarregando C1 (10 µF) através de R1 (1 kΩ) '
            'e do potenciômetro RV1 (100 kΩ). A frequência é f ≈ 1,44 / ((R1 + 2·RV1) · C1): de **≈ 0,7 Hz** '
            '(RV1 no máximo) até **≈ 140 Hz** (RV1 no mínimo). R2 (10 Ω) evita curto quando o potenciômetro está em zero.',
            '**Metade 2 do NE556 — monoestável.** O botão PASSO (SW1) dispara um único pulso de '
            't ≈ 1,1 · R5 · C4 = 1,1 · 330 kΩ · 330 nF ≈ 0,12 s. Como o pulso tem duração fixa, o **repique** '
            '(bounce) do botão é ignorado: um toque = um pulso.',
            '**Seleção do modo.** A chave AUTO/MANUAL (SW2) é invertida duas vezes pelo 74LS04 (sinal MODE limpo). '
            'Três portas NAND do 74LS00 formam um multiplexador: quando MODE = 1 passa o astável, quando MODE = 0 '
            'passa o monoestável.',
            '**HLT.** A última porta NAND junta o clock escolhido com /HLT: com HLT = 1 a saída fica parada. '
            'Uma porta do 74LS04 gera o CLK final e a saída /CLK, que vai para o Contador de Passos.',
            'C2 e C3 (10 nF) estabilizam o pino de controle (CV) de cada 555; C5…C7 são desacoplamento dos CIs.',
        ],
        blocos=[('U1 NE556', 'dois temporizadores 555: astável (automático) e monoestável (passo manual)'),
                ('U2 74LS00', 'multiplexador AUTO/MANUAL e bloqueio por HLT'),
                ('U3 74LS04', 'inversores: limpa a chave de modo, gera CLK e /CLK, inverte HLT'),
                ('RV1 + C1', 'definem a velocidade do clock automático'),
                ('R5 + C4', 'definem a largura do pulso manual')],
        leds=[('LED1 (azul)', 'pisca no ritmo do CLK')],
        controles=[('RV1', 'velocidade do clock automático'), ('SW2', 'AUTO / MANUAL'),
                   ('SW1 PASSO', 'um pulso de clock por toque (modo manual)')],
        teste=['Ligue só esta placa ao backplane e ponha o pino HLT (J2-3) no GND com um fio — sem o Decodificador a entrada fica solta, e entrada TTL solta vale 1 (clock parado).',
               'Em AUTO, o LED azul pisca; girando RV1 a velocidade muda de ~1 a muitas piscadas por segundo.',
               'Em MANUAL, cada toque em PASSO acende o LED uma única vez.',
               'Passe o fio do HLT do GND para o +5 V: o clock para. Volte para o GND: funciona de novo.',
               'Com osciloscópio: CLK e /CLK são opostos, bordas limpas, nível alto > 3,5 V.'],
        atencao=['C1 é **tântalo polarizado**: o lado + fica no pino 2/6 do 556 (marcado na serigrafia).',
                 'Esta é a única placa já testada em bancada na versão anterior (2.1); a lógica não mudou.'],
    ),
    'RESET': dict(
        ordem=3, nome='Reset', icone='🔄',
        resumo='Reinicia o computador pelo botão ou ao ligar, e reinicia o contador de passos a cada instrução.',
        funcao=(
            'Gera **RST** (ativo em 1) e **/RST** (ativo em 0) para zerar o Contador de Programa, a MAR e os '
            'registradores. Também gera **/STCLR**, que zera o Contador de Passos ao fim de cada instrução '
            '(quando chega o sinal /Y5) ou durante o reset.'),
        funcionamento=[
            '**Botão com pull-up.** R1 (10 kΩ) mantém /BTN em 1; apertar RESET (SW1) leva /BTN a 0. '
            'A primeira porta do 74LS132 inverte: RST = 1 enquanto o botão estiver apertado.',
            '**Reset ao ligar.** C1 (10 µF) começa descarregado, então ao ligar /BTN fica em 0 por cerca de '
            'R1·C1 ≈ 0,1 s — o computador sempre começa zerado, sem precisar apertar nada.',
            '**Por que 74LS132?** É um NAND com entrada **Schmitt-trigger**: a subida lenta da tensão de C1 vira uma borda '
            'limpa. O 74LS00 tem a mesma pinagem e funciona, mas o 132 é recomendado.',
            '**/RST.** A segunda porta inverte RST. O LED1 vermelho acende enquanto o reset está ativo.',
            '**/STCLR = /RST AND /Y5.** As duas últimas portas fazem um AND: o Contador de Passos é zerado quando '
            'chega o passo 5 (fim da instrução, /Y5 = 0) **ou** durante o reset. R2 mantém /Y5 em 1 se o cabo estiver solto.',
        ],
        blocos=[('U1 74LS132', '4 portas NAND Schmitt: inverte o botão, gera /RST e o AND de /STCLR'),
                ('R1 + C1', 'pull-up do botão e atraso do reset ao ligar'), ('R2', 'pull-up de /Y5'),
                ('SW1', 'botão RESET')],
        leds=[('LED1 (vermelho)', 'reset ativo')],
        controles=[('SW1 RESET', 'zera o computador (PC, MAR, registradores e passo)')],
        teste=['Ligue a placa: o LED pisca rapidamente ao energizar (reset automático) e apaga.',
               'Segurando RESET o LED fica aceso; meça RST ≈ 5 V e /RST ≈ 0 V em J2.',
               'Solto o botão: RST ≈ 0 V, /RST ≈ 5 V e /STCLR ≈ 5 V.',
               'Ligue /Y5 (J2-3) ao GND com um fio: /STCLR vai a 0 V.'],
        atencao=['C1 é eletrolítico: a faixa "−" vai para o GND (lado indicado na serigrafia).',
                 'Esta placa não tinha PCB na versão antiga — é nova na v3.0.'],
    ),
    'PC': dict(
        ordem=4, nome='Contador de Programa (PC)', icone='🔢',
        resumo='Guarda o endereço da próxima instrução (0…15), conta +1 a cada busca e salta no JMP.',
        funcao=(
            'O **Program Counter** diz em qual endereço da RAM está a próxima instrução. No início de cada instrução '
            'ele coloca o endereço no barramento (/PCO) e, logo depois, conta +1 (PCI). Na instrução `JMP` ele '
            'carrega um novo endereço vindo do barramento (/JMP).'),
        funcionamento=[
            '**74LS161** é um contador binário síncrono de 4 bits. Com PCI = 1 (entradas ENP e ENT), ele soma 1 na '
            'borda de subida do CLK. Com /JMP = 0 (entrada /LOAD), em vez de contar ele copia D0…D3 do barramento.',
            '**/RST** vai na entrada /CLR: o reset zera o contador imediatamente, sem esperar o clock.',
            '**74LS245** é a "porta" para o barramento. Com /PCO = 0, as saídas P0…P3 vão para D0…D3 e as entradas '
            'aterradas colocam 0 em D4…D7. Com /PCO = 1 ele fica em alta impedância e não interfere no barramento.',
            'Os 4 LEDs mostram o endereço atual em binário.',
        ],
        blocos=[('U1 74LS161', 'contador de 4 bits com carga paralela (JMP) e clear (reset)'),
                ('U2 74LS245', 'buffer 3-state: coloca o endereço no barramento quando /PCO = 0')],
        leds=[('LED1…LED4', 'endereço atual P3…P0 (aceso = 1)')],
        controles=[],
        teste=['Com Clock e Reset ligados e PCI (J2-1) ligado ao +5 V por um fio: os LEDs contam 0, 1, 2 … 15, 0.',
               'Aperte RESET: os LEDs voltam a 0000.',
               'Com /PCO (J3-1) em 0 V, os LEDs do barramento no backplane mostram o mesmo valor do PC.'],
        atencao=['No computador montado, PCI, /JMP e /PCO vêm do Decodificador de Controle — não deixe fios de teste ligados.'],
    ),
    'RAM': dict(
        ordem=5, nome='RAM e MAR', icone='💾',
        resumo='16 bytes de memória, o registrador de endereço (MAR) e a programação manual por chaves DIP.',
        funcao=(
            'Guarda o **programa e os dados** (16 posições de 8 bits). A **MAR** (Memory Address Register) guarda o endereço '
            'que será lido ou escrito. Uma chave **PROG/RUN** escolhe quem manda: no modo PROG você escolhe endereço e dado '
            'nas chaves DIP e aperta GRAVAR; no modo RUN quem manda é o computador.'),
        funcionamento=[
            '**MAR (U6 74LS173).** Na borda do CLK, se /MAI = 0, copia D0…D3 do barramento. É zerada pelo RST.',
            '**Multiplexadores (U7…U10 74LS157).** Cada 74LS157 tem 4 chaves eletrônicas de 2 posições. '
            'Com RUN = 0 (modo PROG) eles passam as **chaves DIP** (endereço SW1, dado SW3, botão GRAVAR); '
            'com RUN = 1 passam a **MAR**, o **barramento** e o pulso de escrita automático.',
            '**Memória (U1, U2 74S189).** Cada chip guarda 16 × 4 bits; dois chips formam 16 × 8. '
            'As saídas do 74S189 são **invertidas**, por isso U3 e U4 (74LS04) desinvertem o dado.',
            '**Saída para o barramento (U5 74LS245).** Com /RMO = 0 o byte lido vai para D0…D7.',
            '**Pulso de escrita sincronizado.** Na instrução `STA` o microcódigo liga RMI. U11 (74LS00) bufferiza o CLK, '
            'e o diferenciador C13 (1 nF) + R18 (1 kΩ) transforma a subida do clock num pulso de ≈ 1 µs. '
            '/WE_RUN = NAND(pulso, RMI): a RAM é escrita só nesse instante, com endereço e dado já estáveis.',
            '**Chave PROG/RUN sem repique (U12 NE555).** O 555 trabalha como flip-flop SR: um lado da chave vai no '
            'TRIGGER (liga RUN), o outro no RESET (desliga RUN). A saída troca uma única vez, sem oscilar.',
            '**Chaves DIP.** Ligam ao +5 V, com pull-down de 1 kΩ (RN1, RN2): **chave LIGADA = bit 1**.',
        ],
        blocos=[('U6 74LS173', 'MAR — endereço de 4 bits'),
                ('U7 74LS157', 'escolhe o endereço: chaves (PROG) ou MAR (RUN)'),
                ('U8, U9 74LS157', 'escolhe o dado a gravar: chaves (PROG) ou barramento (RUN)'),
                ('U10 74LS157', 'escolhe o pulso de escrita: botão GRAVAR ou automático'),
                ('U1, U2 74S189', 'RAM 16 × 4 bits cada (nibble alto e baixo)'),
                ('U3, U4 74LS04', 'desinvertem as saídas da RAM'),
                ('U5 74LS245', 'coloca o byte lido no barramento (/RMO)'),
                ('U11 74LS00', 'buffer do clock e porta de escrita (RMI)'),
                ('U12 NE555', 'flip-flop da chave PROG/RUN (sem repique)'),
                ('SW1, SW3', 'chaves DIP de endereço (4) e dado (8)'), ('SW4', 'botão GRAVAR')],
        leds=[('LED1…LED8', 'conteúdo da posição atual Q7…Q0'), ('LED9…LED12 (amarelos)', 'endereço atual A3…A0'),
              ('LED13 (vermelho)', 'modo PROG'), ('LED14 (verde)', 'modo RUN')],
        controles=[('SW2 PROG/RUN', 'programação manual × execução'), ('SW1 ENDEREÇO', 'endereço em modo PROG'),
                   ('SW3 DADO', 'byte a gravar em modo PROG'), ('SW4 GRAVAR', 'grava o byte das chaves no endereço das chaves')],
        teste=['Modo PROG: mude SW1 — os LEDs amarelos acompanham. Os LEDs vermelhos mostram o conteúdo (aleatório ao ligar).',
               'Coloque 1010 0101 em SW3 e aperte GRAVAR: os LEDs de dado mostram 1010 0101. Mude o endereço e volte: o valor continua lá.',
               'Grave valores diferentes em 2–3 endereços e confira cada um.',
               'Modo RUN: os LEDs amarelos passam a mostrar a MAR (0000 depois do reset).'],
        atencao=['O 74S189 é série **S** (Schottky) e esquenta mais que os LS — é normal.',
                 'A memória é volátil: ao desligar, o programa se perde. Reprograme pelas chaves (ou use o emulador para planejar).'],
    ),
    'IR': dict(
        ordem=6, nome='Registrador de Instrução (IR)', icone='📥',
        resumo='Guarda a instrução atual: o opcode vai para o Controle, o operando volta ao barramento.',
        funcao=(
            'Cada instrução tem 8 bits: os **4 de cima são o opcode** (qual instrução) e os **4 de baixo são o operando** '
            '(um endereço ou um número de 0 a 15). O IR guarda a instrução lida da RAM durante toda a sua execução.'),
        funcionamento=[
            '**Dois 74LS173** guardam o byte: U1 o nibble alto, U2 o nibble baixo. Carregam na borda do CLK quando '
            '/IRI = 0 (passo T1 de toda instrução) e são zerados por RST.',
            '**Opcode.** O nibble alto sai direto pelo conector OPCODE (J5) para o Decodificador de Controle, '
            'com OP3 no pino 1 — cabo reto.',
            '**Operando.** O 74LS245 coloca **só o nibble baixo** no barramento quando /IRO = 0 (as outras 4 entradas '
            'estão no GND, então D4…D7 = 0). É assim que `LDA 14` manda o endereço 14 para a MAR.',
        ],
        blocos=[('U1, U2 74LS173', 'registrador de 8 bits (opcode + operando)'),
                ('U3 74LS245', 'devolve o operando ao barramento (/IRO)')],
        leds=[('LED1…LED4', 'opcode (bits 7…4)'), ('LED5…LED8', 'operando (bits 3…0)')],
        controles=[],
        teste=['Coloque um valor no barramento (por exemplo pela RAM em RUN com /RMO), aplique /IRI = 0 e dê um pulso de clock: os LEDs copiam o valor.',
               'Com /IRO = 0, os LEDs do barramento mostram 0000 + nibble baixo.', 'RESET zera todos os LEDs.'],
        atencao=['A placa é igual à do Registrador A e B, mudando os sinais de controle e o conector OPCODE.'],
    ),
    'CD': dict(
        ordem=7, nome='Decodificador de Controle', icone='🧠',
        resumo='O "cérebro": 3 EEPROMs com o microcódigo ligam os 18 sinais certos em cada passo de cada instrução.',
        funcao=(
            'Transforma **opcode + passo** em **sinais de controle**. É uma tabela gravada em 3 EEPROMs 28C16: '
            'o endereço da EEPROM é formado pelo opcode (do IR), pelo passo T0…T2 (do Contador de Passos) e pelas '
            'flags; o byte guardado naquele endereço diz quais sinais ligar. Cada EEPROM fornece 8 sinais.'),
        funcionamento=[
            '**Endereço:** A0…A2 = passo (T0…T2), A3…A6 = opcode (OP0…OP3), A7 = flag de carry (CF), A8 = flag zero (ZF), '
            'A9 e A10 no GND. As EEPROMs ficam sempre lendo (/CE e /OE no GND, /WE em +5 V).',
            '**EEPROM2 (U1):** /IRI, /RMO, RMI, /MAI, /PCO, /JMP, PCI, HLT. '
            '**EEPROM1 (U2):** NOT, /ALUO, AL0, AL1, SUB, /ACI, /ACO, /IRO. '
            '**EEPROM0 (U3):** /BRI, /ORI e duas saídas livres (E0_4, E0_5) para expansão.',
            '**Busca (igual para todas as instruções):** T0 = PCO + MAI (endereço do PC vai para a MAR); '
            'T1 = RMO + IRI + PCI (a instrução vai da RAM para o IR e o PC soma 1).',
            '**Execução:** T2…T4 dependem do opcode. Exemplo `ADD 15`: T2 = IRO + MAI (o operando 15 vai para a MAR), '
            'T3 = RMO + BRI (RAM[15] vai para o registrador B), T4 = ALUO + ACI (A + B volta para A).',
            '**Sinais ativos em 0.** Vários sinais (/PCO, /MAI, /IRI…) ligam em nível baixo. O gerador do microcódigo já '
            'grava esses bits invertidos, então nos passos vazios todas as saídas ficam desligadas.',
            '**Flags.** O conector FLAGS (J4) tem pull-down (R1, R2): sem a futura placa de flags, CF = ZF = 0 e `JC`/`JZ` não saltam.',
            '**Sem placa inversora.** Os 11 sinais ativos em 0 já saem invertidos das EEPROMs, então não é preciso nenhum '
            '74LS04 entre o Decodificador e os módulos. Para ver os sinais em LEDs, use a placa opcional '
            '[Palavra de Controle](cw-palavra-de-controle.md), que só repete os sinais (não inverte).',
        ],
        blocos=[('U1 AT28C16', 'EEPROM2 — sinais de memória, PC e HLT'),
                ('U2 AT28C16', 'EEPROM1 — sinais da ULA, registrador A e IR'),
                ('U3 AT28C16', 'EEPROM0 — registrador B e saída'),
                ('R1, R2', 'pull-down das flags CF e ZF')],
        leds=[],
        controles=[],
        teste=['Grave as EEPROMs (capítulo 6) e confira com `minipro` que a leitura bate com o .bin.',
               'Ligue IR e Contador de Passos e use o clock MANUAL. Com o opcode 0000 (NOP), em T0 os sinais /PCO e /MAI devem ir a 0 V e em T1 /RMO e /IRI a 0 V e PCI a 5 V.',
               'Mude o opcode para 1110 (OUT) e confira em T2: /ACO = 0 V e /ORI = 0 V.',
               'No PC, rode `python3 firmware/ferramentas/testar.py`: os 14 programas de teste devem dar OK.'],
        atencao=['Encaixe cada EEPROM no soquete certo: **U1 = EEPROM2.bin, U2 = EEPROM1.bin, U3 = EEPROM0.bin** (etiquete os chips).',
                 'O pino 1 (marca/chanfro) de cada EEPROM fica para o lado indicado na serigrafia. Use soquete de 24 pinos.'],
    ),
    'CW': dict(
        ordem=8, nome='Palavra de Controle', icone='💡',
        resumo='Placa opcional: 18 LEDs mostram, em cada passo, quais sinais de controle o microcódigo ligou.',
        funcao=(
            'Mostra a **palavra de controle** — os 18 sinais que o Decodificador liga em cada passo de cada instrução. '
            'Com o clock em MANUAL dá para ver, passo a passo, por que cada registrador carrega ou escreve no barramento. '
            'De quebra, os 3 buffers reforçam os sinais que saem das EEPROMs. É **opcional**: sem ela os cabos do '
            'Decodificador vão direto ao backplane, como antes, e o backplane não muda em nada.'),
        funcionamento=[
            '**Onde fica.** Entre o Decodificador e o backplane. Os 5 cabos CTRL_A…CTRL_E do Decodificador entram em '
            'ENTRADA_A…E (J2…J6); as saídas SAIDA_A…E (J7…J11) vão para CD_A…CD_E no backplane, com a mesma pinagem.',
            '**Alimentação sem mexer no backplane.** O cabo do conector P_CD do backplane chega em J1 desta placa, e J12 '
            '(ALIM_DECODIF) repassa os 5 V para o J1 do Decodificador.',
            '**Buffers (3× 74HCT541).** Cada canal copia a entrada na saída, sem inverter. A família HCT tem entradas '
            'compatíveis com TTL e saídas CMOS fortes: a EEPROM passa a alimentar só uma entrada CMOS (quase nenhuma '
            'corrente), e o 74HCT541 é quem aciona os módulos e os LEDs. /OE1 e /OE2 no GND = sempre ligados.',
            '**LED aceso = sinal ativo.** Nos sinais com barra (ativos em 0) o LED vai do +5 V (via 1 kΩ) até a saída: '
            'acende quando a saída vai a 0 V. Nos sinais ativos em 1 (HLT, PCI, RMI, SUB, AL0, AL1, NOT) o LED vai da saída '
            'ao GND (via 1 kΩ). Assim todos os LEDs seguem a mesma regra, sem pensar em polaridade.',
            '**Não inverte nada.** Os sinais ativos em 0 já saem invertidos das EEPROMs; esta placa só repete e mostra. '
            'E0_4 e E0_5 (saídas livres da EEPROM0) passam pela placa sem LED.',
            '**O que esperar.** Em T0 acendem PCO e MAI; em T1, RMO, IRI e PCI — em toda instrução. Em `ADD`: T2 IRO+MAI, '
            'T3 RMO+BRI, T4 ALUO+ACI. No `HLT` fica aceso só o HLT.',
        ],
        blocos=[('U1 74HCT541', 'repete CTRL_A e CTRL_B: /IRI /RMO RMI /MAI /PCO /JMP PCI HLT'),
                ('U2 74HCT541', 'repete CTRL_C e CTRL_D: NOT /ALUO AL0 AL1 SUB /ACI /ACO /IRO'),
                ('U3 74HCT541', 'repete CTRL_E: /BRI /ORI E0_5 E0_4 (4 canais livres no GND)'),
                ('LED1…LED18 + R1…R18', 'um LED por sinal de controle, 1 kΩ cada'),
                ('J2…J6 / J7…J11', 'entradas do Decodificador / saídas para o backplane'),
                ('J1 / J12', 'entrada de 5 V (P_CD) / repasse para o Decodificador')],
        leds=[('LED1…LED4', '/IRI /RMO RMI /MAI'), ('LED5…LED8', '/PCO /JMP PCI HLT'),
              ('LED9…LED12', 'NOT /ALUO AL0 AL1'), ('LED13…LED16', 'SUB /ACI /ACO /IRO'),
              ('LED17, LED18', '/BRI /ORI'), ('todos', 'aceso = sinal ATIVO naquele passo')],
        controles=[],
        teste=['Só a alimentação (J1 em P_CD), sem cabos de sinal: confira 5 V em J12 e no pino 20 dos três CIs. Com as entradas soltas os LEDs podem acender ao acaso — é normal; por isso **nunca** ligue as saídas no backplane sem o Decodificador conectado nas entradas.',
               'Com um fio, ponha J2 pino 1 (/IRI) no GND: o LED do /IRI acende. No +5 V: apaga. Repita para alguns sinais ativos em 1 (ex.: HLT, J3 pino 4): acende no +5 V.',
               'Monte o computador com o Decodificador e o Contador de Passos, clock em MANUAL e RESET: em T0 acendem PCO e MAI, em T1 RMO, IRI e PCI.',
               'Rode `t04-add.asm` passo a passo e confira os LEDs com a tabela de instruções (capítulo 1).'],
        atencao=['Use **74HCT541** (não 74LS541): a família HCT tira quase nenhuma corrente da EEPROM e acende bem os LEDs azuis.',
                 'Lembre de passar o cabo de alimentação: backplane P_CD → J1 desta placa, e J12 → J1 do Decodificador.',
                 'Sem esta placa, ligue o Decodificador direto no backplane (J1 → P_CD e J5…J9 → CD_A…CD_E): funciona igual, só sem os LEDs.'],
    ),
    'FETCH': dict(
        ordem=9, nome='Contador de Passos', icone='👣',
        resumo='Conta os passos T0…T4 de cada instrução e avisa (/Y5) quando a instrução terminou.',
        funcao=(
            'Toda instrução é executada em até 5 passos (T0 a T4), um por pulso de clock. Esta placa conta o passo atual, '
            'manda o número (T0…T2 em binário) para o Decodificador de Controle e mostra nos LEDs em qual passo o '
            'computador está.'),
        funcionamento=[
            '**74LS161** conta na borda de **/CLK**, ou seja, na **descida** do CLK. Assim o passo muda no meio do ciclo e os '
            'sinais de controle já estão estáveis quando chega a próxima subida do CLK (quando os registradores carregam).',
            '**74LS138** é um decodificador 3→8: transforma o número binário em uma linha ativa. /S0…/S4 acendem os LEDs '
            'de passo; /Y5 vai para a placa de Reset.',
            '**Fim da instrução:** quando o contador chega a 5, /Y5 vai a 0, a placa de Reset gera /STCLR = 0 e o 74LS161 '
            'volta imediatamente a 0. O estado 5 dura poucos nanossegundos — na prática a sequência é T0…T4, T0…',
        ],
        blocos=[('U1 74LS161', 'contador do passo (conta na descida do CLK)'),
                ('U2 74LS138', 'decodifica o passo em linhas /S0…/S4 e /Y5')],
        leds=[('LED1…LED3 (amarelos)', 'passo em binário T2 T1 T0'), ('LED4…LED8 (verdes)', 'passo atual T0…T4 (um aceso por vez)')],
        controles=[],
        teste=['Ligue Clock (com HLT no GND), Reset e esta placa. Em clock MANUAL, cada toque avança um LED verde: T0 → T1 → T2 → T3 → T4 → T0.',
               'Os LEDs amarelos mostram 000, 001, 010, 011, 100.', 'RESET volta para T0 a qualquer momento.'],
        atencao=['Sem a placa de Reset ligada o contador vai até T7 (não há quem gere /STCLR) — monte as duas juntas.'],
    ),
    'ACC': dict(
        ordem=10, nome='Registrador A (Acumulador)', icone='🅰️',
        resumo='Registrador principal de 8 bits: guarda o resultado das contas e alimenta a ULA.',
        funcao=(
            'O **acumulador** guarda o operando principal e o resultado das operações. Sua saída está sempre ligada à '
            'entrada A da ULA (conectores ALU_L e ALU_H) e pode ser colocada no barramento para gravar na RAM (`STA`) '
            'ou mostrar no display (`OUT`).'),
        funcionamento=[
            '**Dois 74LS173** (4 bits cada) formam 8 bits. Carregam o barramento na subida do CLK quando /ACI = 0. RST zera.',
            '**74LS245** coloca o valor no barramento quando /ACO = 0.',
            '**Saída permanente:** A0…A7 saem pelos conectores J5/J6 direto para a ULA (cabos diretos, sem passar pelo backplane).',
        ],
        blocos=[('U1, U2 74LS173', 'registrador de 8 bits'), ('U3 74LS245', 'saída para o barramento (/ACO)')],
        leds=[('LED1…LED8', 'valor de A, bit 7 à esquerda')],
        controles=[],
        teste=['Coloque um valor no barramento, /ACI = 0 e um pulso de clock: os LEDs copiam.',
               'Com /ACO = 0 o valor aparece nos LEDs do barramento.', 'RESET zera.'],
        atencao=['Placa idêntica ao Registrador B e ao IR — confira o nome na serigrafia antes de soldar os conectores.'],
    ),
    'B': dict(
        ordem=11, nome='Registrador B', icone='🅱️',
        resumo='Segundo operando da ULA: recebe o valor da RAM nas contas ADD, SUB, AND, OR e XOR.',
        funcao=(
            'Guarda o **segundo operando** das operações. O valor vem da RAM (passo T3 de ADD/SUB/AND/OR/XOR) e fica '
            'ligado permanentemente à entrada B da ULA.'),
        funcionamento=[
            'Mesma placa do Registrador A: dois 74LS173 carregam o barramento quando /BRI = 0, e saem para a ULA por J5/J6.',
            'O 74LS245 está na placa, mas no backplane **/BRO fica fixo em +5 V**: o registrador B nunca escreve no '
            'barramento (nenhuma instrução precisa disso). Fica disponível para expansões.',
        ],
        blocos=[('U1, U2 74LS173', 'registrador de 8 bits'), ('U3 74LS245', 'saída para o barramento (desabilitada no backplane)')],
        leds=[('LED1…LED8', 'valor de B, bit 7 à esquerda')],
        controles=[],
        teste=['Coloque um valor no barramento, /BRI = 0 e um pulso de clock: os LEDs copiam.', 'RESET zera.'],
        atencao=[],
    ),
    'ALU': dict(
        ordem=12, nome='ULA (Unidade Lógica e Aritmética)', icone='➕',
        resumo='Faz soma, subtração, AND, OR, XOR e NOT entre A e B; resultado vai ao barramento.',
        funcao=(
            'Calcula, **o tempo todo**, o resultado da operação escolhida entre o registrador A e o registrador B. '
            'O resultado só vai para o barramento quando o microcódigo liga /ALUO, e então é guardado de volta em A.'),
        funcionamento=[
            '**Soma e subtração (U1, U2 74LS283 + U3, U4 74LS86).** Dois somadores de 4 bits em cascata formam 8 bits. '
            'Para subtrair, os XOR invertem todos os bits de B e o carry de entrada recebe 1: A + (NOT B) + 1 = **A − B** '
            '(complemento de 2).',
            '**AND (U5, U6 74LS08)** e **OR (U7, U8 74LS32)** bit a bit.',
            '**XOR e NOT (U9…U12).** X = A XOR (B OR NOT). Com NOT = 0 é o XOR normal; com NOT = 1 o lado B vira tudo 1 '
            'e o resultado é **NOT A**.',
            '**Seletor (U13…U16 74LS153).** Quatro multiplexadores 4→1 duplos escolhem, bit a bit, qual resultado sai: '
            'AL1 AL0 = **00 soma/sub · 01 AND · 10 OR · 11 XOR/NOT**.',
            '**Saída (U17 74LS245)** coloca o resultado no barramento com /ALUO = 0.',
            '**Buffer (U18 74LS04).** SUB e NOT acionam 8–9 entradas TTL cada, mais do que a EEPROM aguenta; '
            'duas inversões em série reforçam esses sinais.',
            '**CARRY** (vai-um do bit 7) sai no conector CTRL2 para a futura placa de flags.',
        ],
        blocos=[('U1, U2 74LS283', 'somador de 8 bits'), ('U3, U4 74LS86', 'inversor controlado de B (subtração)'),
                ('U5, U6 74LS08', 'A AND B'), ('U7, U8 74LS32', 'A OR B'),
                ('U9, U11 74LS32', 'B OR NOT (prepara o NOT)'), ('U10, U12 74LS86', 'A XOR (B OR NOT)'),
                ('U13…U16 74LS153', 'seletor da operação (AL1, AL0)'), ('U17 74LS245', 'saída para o barramento'),
                ('U18 74LS04', 'buffer de SUB e NOT')],
        leds=[('LED1…LED8', 'resultado da operação selecionada, bit 7 à esquerda')],
        controles=[],
        teste=['Ligue A, B e a ULA. Com AL1 AL0 = 00 e SUB = 0: coloque A = 5 e B = 3 → LEDs da ULA = 0000 1000 (8).',
               'SUB = 1 → 0000 0010 (2). AL = 01 → AND = 0000 0001. AL = 10 → OR = 0000 0111. AL = 11 → XOR = 0000 0110.',
               'AL = 11 e NOT = 1 → 1111 1010 (NOT 5).', 'Com /ALUO = 0 o resultado aparece no barramento.'],
        atencao=['É a placa com mais CIs (18). Use soquetes e confira o pino 1 de cada um — a serigrafia mostra o tipo de cada CI.',
                 'Na v3.0 foram corrigidos dois erros do projeto antigo (AL0/AL1 sem conector e saídas AND em curto com o GND).'],
    ),
    'OUT': dict(
        ordem=13, nome='Registrador de Saída', icone='📤',
        resumo='Guarda o valor que aparece no display (instrução OUT).',
        funcao=(
            'Guarda o número que o programa quer mostrar. Na instrução `OUT` o valor de A passa pelo barramento e é '
            'copiado aqui; a placa do Display lê estas saídas continuamente.'),
        funcionamento=[
            '**Dois 74LS173** carregam o barramento quando /ORI = 0 na subida do CLK. RST zera.',
            'Não há 74LS245: esta placa só lê o barramento. As saídas O0…O7 vão por cabos diretos (J5, J6) para o Display.',
        ],
        blocos=[('U1, U2 74LS173', 'registrador de 8 bits')],
        leds=[('LED1…LED8', 'valor mostrado no display, em binário')],
        controles=[],
        teste=['Coloque um valor no barramento, /ORI = 0 e um pulso de clock: os LEDs copiam e o display mostra o número em decimal.'],
        atencao=[],
    ),
    'DISPLAY': dict(
        ordem=14, nome='Display Decimal', icone='🔟',
        resumo='Mostra o valor do registrador de saída em decimal, 0…255 ou −128…127, em 4 dígitos.',
        funcao=(
            'Converte o número binário de 8 bits em **decimal** e mostra num display de 4 dígitos de 7 segmentos. '
            'A chave escolhe entre **sem sinal** (0…255) e **com sinal** (−128…127, complemento de 2).'),
        funcionamento=[
            '**Tabela na EEPROM (U1 28C16).** Em vez de lógica de conversão, uma EEPROM guarda o desenho de cada dígito: '
            'endereço = valor (A0…A7) + qual dígito (A8, A9) + modo com/sem sinal (A10); o byte lido são os segmentos a…g e o ponto.',
            '**Multiplexação.** Os 4 dígitos dividem os mesmos 8 fios de segmento. O 555 (U2) oscila a '
            'f ≈ 1,44 / ((R1 + 2·R10)·C5) ≈ 480 Hz; o 74LS161 (U3) conta 0…3 (DG0, DG1) e o 74LS139 (U4) acende um dígito '
            'por vez. Cada dígito pisca ≈ 120 vezes por segundo — o olho vê os 4 acesos.',
            '**Catodo comum.** O 74LS139 ativa o dígito puxando o catodo para 0 V. Os resistores de 100 Ω (R2…R9) '
            'limitam a corrente dos segmentos e protegem as saídas da EEPROM.',
        ],
        blocos=[('U1 AT28C16', 'tabela binário → 7 segmentos (DISPLAY.bin)'), ('U2 NE555', 'oscilador da varredura (~480 Hz)'),
                ('U3 74LS161', 'contador do dígito atual (0…3)'), ('U4 74LS139', 'seleciona um dos 4 dígitos'),
                ('DS1', 'display 4 dígitos, catodo comum, 0,4"'), ('R2…R9', 'resistores dos segmentos (100 Ω)')],
        leds=[],
        controles=[('SW1', 'SEM SINAL (0…255) / COM SINAL (−128…127)')],
        teste=['Grave DISPLAY.bin na EEPROM (capítulo 6).',
               'Com o Registrador de Saída zerado o display mostra "0". Coloque 1111 1111 no registrador: mostra 255 (sem sinal) ou −1 (com sinal).',
               'Se aparecerem segmentos trocados, confira se o display é mesmo de **catodo comum**.'],
        atencao=['Use display de **catodo comum** de 4 dígitos (tipo 5641AS / 3461AS). Anodo comum não funciona.'],
    ),
}

# chave da placa (designs.py) <-> pasta
PASTAS = {
    'BACKPLANE': 'backplane-barramento', 'CLOCK': 'clock-astavel-monoestavel', 'RESET': 'reset-circuito',
    'PC': 'pc-contador-programa', 'RAM': 'ram-mar-memoria', 'IR': 'ir-registrador-instrucao',
    'CD': 'cd-decodificador-controle', 'FETCH': 'fetch-contador-passos', 'ACC': 'acc-registrador-a',
    'B': 'b-registrador-b', 'CW': 'cw-palavra-de-controle', 'ALU': 'alu-unidade-logica-aritmetica', 'OUT': 'out-registrador-saida',
    'DISPLAY': 'display-decimal',
}
