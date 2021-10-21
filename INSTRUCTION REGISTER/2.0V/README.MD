**Instruction Register**
===============================

Description 
-------

A register is a series of physical switches on a microprocessor or circuit board that can be turned on or off, making each switch equivalent to a bit. When several of the switches, also called latches, are linked, they are able to store binary data such as numbers, which can be turned into memory addresses or instruction codes. Within the CPU, the instruction register can hold either the address in computer memory of the instruction that is being executed or, for efficiency, it can hold the instruction itself. This information is passed to the register through another register known as the program counter, which in most cases jumps forward to the next instruction to be executed after passing on the current instruction.

Electronic Scheme
-------

![image](https://github.com/aragonxpd154/8-bit-computer/blob/main/INSTRUCTION%20REGISTER/2.0V/Schematic_Instruction%20Register_2021-10-21.png?raw=true)


3D Visualization and Progress
-------

![image](https://i.imgur.com/ORPsYBU.png)


UPDATE 2.0V
-------

2.0.1 - Placing coupling capacitors close to logic gate ICs to avoid parallel noise coming from the clock circuit

2.0.2 - Optimized electronic component locations
