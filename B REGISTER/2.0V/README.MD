**B REGISTER**
===============================

Description 
-------

It is the record in a computer's processor, which stores the data being transferred to and from storage for immediate access. It contains a copy of designated memory locations created by the memory address register. It acts as a buffer, allows the processor and memory units to act independently, unaffected by small differences in operation. The data item will be copied to the MBR ready for use in the next clock cycle, when it can be used by the processor for reading or writing or stored in main memory after being written.

This register contains the memory contents that are to be transferred from memory to other components or vice versa. A word to be stored must be transferred to the MBR, from where it goes to the specific memory location, and the arithmetic data to be processed in the ALU goes first to the MBR and then to the accumulated record, and then is processed in the ALU.

This register contains the memory contents that are to be transferred from memory to other components or vice versa. A word to be stored must be transferred to the MBR, from where it goes to the specific memory location, and the arithmetic data to be processed in the ALU goes first to the MBR and then to the accumulated record, and then is processed in the ALU.


Electronic Scheme
-------

![image](https://raw.githubusercontent.com/aragonxpd154/8-bit-computer/main/B%20REGISTER/1.0V/Schematic_B%20Register_2021-10-06.png)


3D Visualization and Progress
-------

![image](https://i.imgur.com/SKj16Ml.png)


UPDATE 2.0V
-------

2.0.1 - placing coupling capacitors close to logic gate ICs to avoid parallel noise coming from the clock circuit

2.0.2 - Optimized electronic component locations



