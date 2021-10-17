**Fetch Execution Counter**
===============================

Description 
-------

In plain CPUs the fetch execute cycle is carried out progressively, each instruction is being handled before the succeeding one is initiated.  In modern CPUs the fetch execute cycle is executed simultaneously, in parallel via an instruction pipeline, which means the next command starts being executed before the previous command has completed.  This is made possible since the cycle has been broken up into separate steps.

Abstract
-------

* The processor reviews the program counter to see which command to execute next.
* The program counter gives an address value in the memory of where the next command is.
* The processor fetches the command value from the memory location.
* Once the command has been fetched, it needs to be decoded and executed. For example, this could include taking one value, putting it into the Arithmetic Logic Unit (ALU), then taking a different value from a register and adding the two together.
* Once this has been completed, the processor returns to the program counter to find the next command.
* This cycle is replicated until the program stops.
* The Execute Cycle is the only step useful to the end user, everything else is required to make the execute cycle happen, as it performs the function of the command.  The ALU is utilised if the command involves arithmetic or logical operations.


Electronic Scheme
-------

![image](https://raw.githubusercontent.com/aragonxpd154/8-bit-computer/main/FETCH%20EXECUTION%20COUNTER/1.0V/Schematic_Fetch%20Execution%20Counter_2021-10-10.png)


3D Visualization and Progress
-------

![image](https://i.imgur.com/RgGtgZl.png)
