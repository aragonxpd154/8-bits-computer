**Control Decoder**
===============================

Description 
-------

Binary encoders usually have a number of inputs that must be mutually exclusive, meaning only one of the inputs can be active at a time. The encoder then produces a binary code on the output pins, which changes in response to the input that has been activated. Because it is always possible when using input switches that more than one input can be active at the same time, most encoders of this type feature 'priority encoding' where, if more than one input is activated at the same time, the output will be selected only the most significant active input. For example, if 6 and 7 are pressed together, the BCD output will indicate 7. 

Some other encoder ICs also feature extra inputs and outputs that allow multiple ICs to be connected together for more flexibility in the number of input and output lines available. This includes ENABLE inputs, (usually labeled E ), which can consist of one or more input pins that need to have a certain logic level applied (usually logic 0) to activate the encoding action. In the absence of a correct ENABLE signal, the IC output pins will remain inactive.

One problem with combinatorial logic circuits is that unintended changes to the output data can occur during times when the IC outputs are changing. This can be due to problems such as switch contacts 'bouncing' as they close, creating rapid and unpredictable changes in logic levels for a very short period. However, the logic IC operates at high speed and will respond to these changes very quickly.

The 74HC148 also uses priority encoding and has eight active low inputs and a three-bit active low binary output (Octal). The internal logic of the 74HC148 is shown in Fig. 4.4.2

The IC is enabled by an active low activation ( EI ) input and an active low activation ( EO ) output is provided so that multiple ICs can be cascaded together, allowing encoding more inputs, eg 16 to 6 line encoder using two 8 to 3 encoders. The CMOS 74HC148 also uses active low inputs and outputs.


![image](https://www.learnabout-electronics.org/Digital/images/encoder-8-to-3.gif)

![image](https://www.learnabout-electronics.org/Digital/images/table-4-4-1.gif)

These IC-shaped circuits are often called Decoders / Demultiplexers and perform the opposite function of an encoder (or multiplexer).

Binary data is used in digital circuits in the form of either binary code, which is an arrangement of binary bits in a particular order to represent 'real' quantities, as a set of decimal numbers (BCD code) or text ( ASCII ) In a complete digital system, therefore, it is often necessary to convert one code to another or to convert a binary code to drive some user interface, such as an LED display.

A decoder is a combinational logic circuit that takes a binary input, usually in coded form, and produces a one-bit output on each of several output lines. The logical state (1 or 0) on any of the output lines depends on a specific code that appears on the input lines.

![image](https://www.learnabout-electronics.org/Digital/images/decoder-BCD-to-decimal-74HC42.gif)

![image](https://www.learnabout-electronics.org/Digital/images/table-4-4-3.gif)

THe 2 to 4 line decoders (also called 1 of 4 decoders) are commercially available in types HC and HCT in various versions from different manufacturers. These are typically dual packets, like NXP's 74HC139 with two decoders per chip. A (commonly used) difference from the basic example shown in Fig. 4.4.5 is that the outputs, and sometimes also the inputs, on such ICs can be 'active low', meaning that the active or logic 1 state is in lower voltage level of the two possible logic states, so the output is drawing current when it is 'logic 1'. This provides greater drive capacity than would be available if logic 1 were at high voltage and current source.

In addition, decoder ICs are often used to activate the Enable or Chip Select ( CS ) inputs of other ICs, which are normally low active, so having a decoder with an active low output saves by using extra inverter ports.

Another feature found on the 74 series ICs is the common presence of buffer ports (which can be inverted or non-inverted) on IC inputs and outputs to provide enhanced input and output capabilities. Clamping diodes and current limiting resistors are also often included on inputs and outputs to provide enhanced protection against high external electrostatic voltages.

Depending on the decoder IC and the type of display used, although it may sometimes be necessary to use a transient amplifier to drive each display segment, there are Decoder / Driver ICs available such as the 74LS46, 47, 48 and 49 that have enough current outputs and a choice of output designs such as open collector, internal pullup resistors and high or low active output levels that allow direct connection to LED and filament lamp displays.


Prototype working article basis [website (https://www.learnabout-electronics.org/Digital/dig44.php)][website] 

Electronic Scheme
-------

![image](https://www.learnabout-electronics.org/Digital/images/encoder-8-to-3.gif)


3D Visualization and Progress
-------

![image](https://i.imgur.com/ujPggqG.png)


UPDATE 2.0V
-------

2.0.1 - Placing coupling capacitors close to logic gate ICs to avoid parallel noise coming from the clock circuit

2.0.2 - Optimized electronic component locations


