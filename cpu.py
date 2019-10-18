"""CPU functionality."""

import sys

SP = 7
class CPU:
    def __init__(self):
        self.reg = [0] * 8
        self.ram = [0] * 256
        self.pc = 0
        #R7 is reserved as the SP
        self.reg[7] = 0xF4

    def ram_read(self, MAR): # MAR = Memory Address Register
        return self.ram[MAR]
    
    def ram_write(self, MAR, MDR): #MDR = Memory Data Register
        self.ram[MAR] = MDR

    def load(self, argv):
        """Load a program into memory."""

        try:
            address = 0
            with open(sys.argv[1]) as file:
                #ignore everything after # and space
                lines = [line for line in file if not (line[0]=='#' or line[0]=='\n')]
                program = [int(line.split('#')[0].strip(), 2) for line in lines]

            for instruction in program:
                self.ram[address] = instruction
                address += 1


        except FileNotFoundError:
            print(f"{sys.argv[0]}: {sys.argv[1]} not found")
            sys.exit(2)


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
       
        """Run the CPU."""
        LDI = 0b10000010
        PRN = 0b01000111
        HLT = 0b00000001
        MUL = 0b10100010
        PUSH = 0b01000101
        POP = 0b01000110
        CALL = 0b01010000
        RET = 0b00010001
        ADD = 0b10100000

        running = True

        while running:
            
            IR = self.ram[self.pc]
            #register
            operand_a = self.ram_read(self.pc + 1)
            #value
            operand_b = self.ram_read(self.pc + 2)

            if IR == HLT:
                running = False
                self.pc += 1

            elif IR == LDI:
                #set specificed register to a specified value
                # increment program counter
                self.reg[operand_a] = operand_b
                self.pc += 3
                
            elif IR == PRN:
                #print numberic value stored in the given register
                print(self.reg[operand_a])
                self.pc += 2

            elif IR == ADD:
                self.alu("ADD", operand_a, operand_b)
                self.pc += 3

            elif IR == MUL:
                self.alu("MUL", operand_a, operand_b)
                self.pc += 3

            elif IR == PUSH:
                #Decrement the SP
                self.reg[SP] -= 1
                #Copy the value in the given register to the address pointed to by SP
                self.ram[self.reg[SP]] = self.reg[operand_a]
                self.pc += 2

            elif IR == POP:
                #copy the value from the address pointed to by SP to the given register
                self.reg[operand_a] = self.ram[self.reg[SP]]
                #Increment SP
                self.reg[SP] += 1
                self.pc += 2

            elif IR == CALL:
                # Push the return address on the stack
                self.reg[SP] -= 1
                self.ram[self.reg[SP]] = self.pc + 2
                # The PC is set to the address stored in the given register.
                # We jump to that location in RAM and execute the first instruction in the subroutine
                reg_num = self.ram[self.pc + 1]
                self.pc = self.reg[reg_num]
            
            elif IR == RET:
                #Return from subroutine
                self.pc = self.ram[self.reg[SP]]
                #Pop the value from the top of the stack and store it in the PC
                self.reg[SP] += 1

            else:
                print(f"Unknown instruction: {IR}")
                sys.exit(1)




