from mips_processor import PC, IM, RF, DM, ALU, CU, Processor

PC = PC(0)  # Program Counter
IM = IM()  # Instruction Memory
RF = RF()  # Register File
DM = DM()  # Data Memory
ALU = ALU()  # Arithmetic Logic Unit
CU = CU(RF, DM, ALU, PC)  # Control Unit
Processor = Processor(PC, IM, RF, DM, ALU, CU)  # Processor
# Open the file in read mode
with open('dump.txt', 'r') as file:
  # Reading each line from the file
  cnt = 0  # cnt keeps track of the instruction_memory index
  lncnt = 0  # lncnt is the instruction number
  for line in file:  # memory is byte-addressible
    print('WROTE INSTR', lncnt, ':', int(line[0:32], 2))
    lncnt += 1
    pc_0 = int(line[24:32], 2)
    pc_1 = int(line[16:24], 2)
    pc_2 = int(line[8:16], 2)
    pc_3 = int(line[0:8], 2)
    Processor.IM.mem[cnt] = pc_0  # First 8 lsb's, so we follow big-endian
    cnt += 1
    Processor.IM.mem[cnt] = pc_1
    cnt += 1
    Processor.IM.mem[cnt] = pc_2
    cnt += 1
    Processor.IM.mem[cnt] = pc_3
    cnt += 1
# Run the processor for the loaded instructions
print(Processor.DM.mem[8192:8232:4])
Processor.run()

# Enumerate the processor RF file and print it
for index, value in enumerate(Processor.RF.file):
  print(f"RF[{index}]: {value}")

# Feel free to inspect whatever DataMemory Location you want by changing the indices
print(Processor.DM.mem[8192:8232:4])
