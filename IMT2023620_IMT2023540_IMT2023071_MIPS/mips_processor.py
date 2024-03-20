def num_to_8bit_binary(num):
  binary_str = bin(num)[2:]
  zero_padding = '0' * (8 - len(binary_str))
  return zero_padding + binary_str


def num_to_16bit_binary(num):
  binary_str = bin(num)[2:]
  zero_padding = '0' * (16 - len(binary_str))
  return zero_padding + binary_str


def flipBits(binary_str):
  ans = ''
  for i in range(len(binary_str)):
    if (binary_str[i] == '1'):
      ans += '0'
    elif (binary_str[i] == '0'):
      ans += '1'
  return int(ans, 2)


def imm_convert(imm):
  if (imm >> 15):
    imm = 0 - (flipBits(num_to_16bit_binary(imm)) + 1)
    return imm
  elif (imm >> 15 == 0):
    return (imm)


class PC:

  def __init__(self, value):
    self.value = value
    self.pcSrc = 0
    self.jump = 0
    self.jal = 0
    self.jr = 0
    self.branch = 0

  def update(self, address, branchAddress):
    if (self.jump):
      self.value = address << 2
    elif (self.pcSrc):  #branch on equal to condition
      self.value = self.value + 4 + branchAddress
    elif (self.jal):
      self.value = address << 2
    elif (self.jr):
      pass
    else:
      self.value = self.value + 4

    self.pcSrc = 0
    self.jump = 0
    self.jal = 0
    self.jr = 0
    self.branch = 0


class IM:

  def __init__(self):
    self.mem = [0] * 0xffc
    print('Initialized Instruction Memory')
    self.RD = 0

  def RDPort(self, A):
    self.RD = int(
        num_to_8bit_binary(self.mem[A + 3]) +
        num_to_8bit_binary(self.mem[A + 2]) +
        num_to_8bit_binary(self.mem[A + 1]) + num_to_8bit_binary(self.mem[A]),
        2)
    print('Instruction fetched from memory: ', self.RD)
    return


class RF:

  def __init__(self):
    self.WE3 = 0
    self.RD1 = 0
    self.RD2 = 0
    self.file = [0] * 32
    self.file[29] = 16380  # stack pointer location in DM
    self.RegDst = 0
    self.MemtoReg = 0

  def RD1Port(self, A1):
    self.RD1 = self.file[A1]

  def RD2Port(self, A2):
    self.RD2 = self.file[A2]

  def WD3Port(self, rt, rd, ALUResult, RD):
    value = 0
    if (self.MemtoReg == 0):
      value = ALUResult
      print('Chose ALuResult')
    elif (self.MemtoReg == 1):
      value = RD
      print('Chose RD')
    if (self.WE3):
      if (self.RegDst == 0):
        self.file[rt] = value
        print('Wrote to rt', rt, ' :', value)
      elif (self.RegDst == 1):
        self.file[rd] = value
        print('Wrote to rd ', rd, ' :', value)


class DM:

  def __init__(self):
    self.WE = 0
    self.RD = 0
    self.mem = [0] * 0x3fff

  def RDPort(self, A):
    self.RD = self.mem[A]

  def WDPort(self, A, value):
    if (self.WE):
      self.mem[A] = value


class ALU:

  def __init__(self):
    self.ALUResult = 0
    self.Zero = 0
    self.Control = 0
    self.ALUSrc = 0
    self.srcA = 0
    self.srcB = 0

  def calculate(self, srcA, rtVal, imm):
    #...#Source Decision
    #imm = imm_convert(imm)
    self.srcA = srcA
    print('rtVal is', rtVal, 'and imm is', imm)
    if (self.ALUSrc == 0):
      self.srcB = rtVal
    elif (self.ALUSrc == 1):
      self.srcB = imm
    else:
      self.srcB = 0
    self.Zero = self.srcA - self.srcB
    #Alu operation
    if self.Control == -2:  #mul instruction
      print('Mul Called')
      self.ALUResult = self.srcA * self.srcB
    if self.Control == 0b010:  # 0x2 in binary is 0010
      self.ALUResult = self.srcA + self.srcB
      print('Added', self.srcA, 'and', self.srcB, 'together')
    elif self.Control == 0b110:  # 0x6 in binary is 0110
      print('Called sub')
      self.ALUResult = self.srcA - self.srcB
    elif self.Control == 0b101:
      self.ALUResult = self.srcA * self.srcB
    elif self.Control == 0b000:  # 0x0 in binary is 0000
      self.ALUResult = self.srcA & self.srcB
    elif self.Control == 0b001:  # 0x1 in binary is 0001
      self.ALUResult = self.srcA | self.srcB
    elif self.Control == 0b111:  # 0x7 in binary is 0111
      if self.srcA < self.srcB:
        self.ALUResult = 0b1
      else:
        self.ALUResult = 0b0
    else:
      pass


# class pcSrc:
#   def __init__(self, PC):
#     self.PC = PC

#   def update(self):
#     pass


class CU:

  def __init__(self, RF, DM, ALU, PC):
    self.ALUControl = 0
    self.RF = RF
    self.DM = DM
    self.ALU = ALU
    self.PC = PC

  def set_signals(self, opcode, funct):
    ALUOp = -1
    # R TYPE
    self.PC.jr = 0
    self.PC.jump = 0
    self.PC.branch = 0
    self.PC.jal = 0

    if opcode == 0b0:  # 0x0 in binary is 0000
      if funct == 0b1000:
        #jr
        self.PC.jr = 1
        print('We in jump R, and jump to:', self.RF.RD1)
        self.PC.value = self.RF.RD1
        self.RF.WE3 = 0  # RegWrite
        # self.RF.RegDst = 0      # RegDst
        # self.ALU.ALUSrc = 0     # ALUSrc
        # self.PC.branch = 1      # Branch
        self.DM.WE = 0  # MemWrite
        # self.RF.MemtoReg = 1    # MemtoReg
        ALUOp = -1  # ALUOp
        self.PC.jump = 0
        self.PC.branch = 0
        self.PC.jal = 0

      else:
        self.RF.WE3 = 1  # RegWrite
        self.RF.RegDst = 1  # RegDst
        self.ALU.ALUSrc = 0  # ALUSrc
        self.DM.WE = 0  # MemWrite
        self.RF.MemtoReg = 0  # MemtoReg
        ALUOp = 0b10  # ALUOp (0x2 in binary is 0010)
        self.PC.jump = 0
        self.PC.branch = 0
        self.PC.jal = 0
        self.PC.jr = 0

  # lw
    elif opcode == 0b100011:  # 0x23 in binary is 10011
      print('YEAA I AM LOADING')
      self.RF.WE3 = 1  # RegWrite
      self.RF.RegDst = 0  # RegDst
      self.ALU.ALUSrc = 1  # ALUSrc
      self.DM.WE = 0  # MemWrite
      self.RF.MemtoReg = 1  # MemtoReg
      ALUOp = 0b00  # ALUOp (0x0 in binary is 0000)
      self.PC.jump = 0
      self.PC.branch = 0
      self.PC.jal = 0
      self.PC.jr = 0

  # sw
    elif opcode == 0b101011:  # 0x2b in binary is 101011
      print('Storing')
      self.RF.WE3 = 0  # RegWrite
      # self.RF.RegDst = 0      # RegDst
      self.ALU.ALUSrc = 1  # ALUSrc
      self.DM.WE = 1  # MemWrite
      # self.RF.MemtoReg = 1    # MemtoReg
      ALUOp = 0b00  # ALUOp
      self.PC.jump = 0
      self.PC.branch = 0
      self.PC.jal = 0
      self.PC.jr = 0

  # Beq

    elif opcode == 0b000100:  # 0x2b in binary 000100
      print('branchinggg yeaa')
      self.RF.WE3 = 0  # RegWrite
      # self.RF.RegDst = 0      # RegDst
      self.ALU.ALUSrc = 0  # ALUSrc
      self.PC.branch = 1  # Branch
      self.DM.WE = 0  # MemWrite
      # self.RF.MemtoReg = 1    # MemtoReg
      ALUOp = 0b01  # ALUOp
      self.PC.jump = 0  # Jump
      self.PC.jal = 0
      self.PC.jr = 0

  # addi

    elif opcode == 0b001000:
      self.RF.WE3 = 1  # RegWrite
      self.RF.RegDst = 0  # RegDst
      self.ALU.ALUSrc = 1  # ALUSrc
      self.DM.WE = 0  # MemWrite
      self.RF.MemtoReg = 0  # MemtoReg
      ALUOp = 0b00  # ALUOp (0x0 in binary is 0000)
      self.PC.jump = 0
      self.PC.branch = 0
      self.PC.jal = 0
      self.PC.jr = 0

  # jump

    elif opcode == 0b000010:
      self.RF.WE3 = 0  # RegWrite
      # self.RF.RegDst = 0      # RegDst
      # self.ALU.ALUSrc = 0     # ALUSrc
      # self.PC.branch = 1      # Branch
      self.DM.WE = 0  # MemWrite
      # self.RF.MemtoReg = 1    # MemtoReg
      # ALUOp = 0b01               # ALUOp
      self.PC.jump = 1
      self.PC.branch = 0
      self.PC.jal = 0
      self.PC.jr = 0

  # jal

    elif opcode == 0b000011:
      self.RF.WE3 = 0  # RegWrite
      # self.RF.RegDst = 0      # RegDst
      self.RF.file[31] = self.PC.value + 4
      # self.ALU.ALUSrc = 0     # ALUSrc
      # self.PC.branch = 1      # Branch
      self.DM.WE = 0  # MemWrite
      # self.RF.MemtoReg = 1    # MemtoReg
      # ALUOp = 0b01               # ALUOp
      self.PC.jump = 0
      self.PC.jump = 0
      self.PC.branch = 0
      self.PC.jal = 1

    # mul
    elif opcode == 0b011100:
      self.RF.WE3 = 1  # RegWrite
      self.RF.RegDst = 1  # RegDst
      self.ALU.ALUSrc = 0  # ALUSrc
      self.DM.WE = 0  # MemWrite
      self.RF.MemtoReg = 0  # MemtoReg
      ALUOp = -2  # ALUOp (0x2 in binary is 0010)
      self.ALU.Control = 0b101
      self.PC.jump = 0
      self.PC.branch = 0
      self.PC.jal = 0
      self.PC.jr = 0

  # Alu decoder

    if ALUOp == 0b00:
      self.ALU.Control = 0b010
    elif ALUOp == -2:
      self.ALU.Control = -2
    elif ALUOp % 2 != 0:
      self.ALU.Control = 0b110
    elif ALUOp % 2 == 0 and funct == 0b100000:
      self.ALU.Control = 0b010
    elif ALUOp % 2 == 0 and funct == 0b100010:
      self.ALU.Control = 0b110
    elif ALUOp % 2 == 0 and funct == 0b100100:
      self.ALU.Control = 0b000
    elif ALUOp % 2 == 0 and funct == 0b100101:
      self.ALU.Control = 0b001
    elif ALUOp % 2 == 0 and funct == 0b101010:
      self.ALU.Control = 0b111


class Processor:

  def __init__(self, PC, IM, RF, DM, ALU, CU):
    self.PC = PC
    self.IM = IM
    self.RF = RF
    self.DM = DM
    self.ALU = ALU
    self.CU = CU
    self.flag = 1

  def fetch(self):
    self.IM.RDPort(self.PC.value)

  def sign_extend(self, value):
    return (value & 0xFFFFFFFF)

  def decode_execute(self):
    instr = self.IM.RD
    if (instr & 0xffffffff == 0x0000000c):
      print('Syscall Interrupt')
      self.flag = 0
    opcode = (instr & 0b11111100000000000000000000000000) >> 26  #31:26
    rs = (instr & 0b00000011111000000000000000000000) >> 21  #25:21
    rt = (instr & 0b00000000000111110000000000000000) >> 16  #20:16
    rd = (instr & 0b00000000000000001111100000000000) >> 11  #15:11
    shamt = instr & 0b00000000000000000000011111000000  #10:6
    funct = instr & 0b00000000000000000000000000111111  #5:0
    imm = imm_convert(instr & 0xFFFF)  #15:0

    branch_address = imm << 2  # Multiply by 4
    self.RF.RD1Port(rs)
    self.RF.RD2Port(rt)
    self.CU.set_signals(opcode, funct)
    print("Decoding instruction:")
    print("Opcode:", opcode)
    print("rs:", rs, 'and rs value ', self.RF.RD1)
    print("rt:", rt, 'and rt value ', self.RF.RD2)
    print("rd:", rd, 'and rd value ', self.RF.file[rd])
    print("shamt:", shamt)
    print("funct:", funct)

    self.ALU.calculate(self.RF.RD1, self.RF.RD2, imm)
    print('ALU result: ', self.ALU.ALUResult)
    self.PC.pcSrc = self.PC.branch and (not self.ALU.Zero)
    print(
        f'pc source is {self.PC.pcSrc}, alu zero signal: {self.ALU.Zero}, self.CU.branch is  {self.PC.branch}'
    )

  def memAccess(self):
    if self.DM.WE == 0:
      print('We in mem access and ALUResult is', self.ALU.ALUResult)
      self.DM.RDPort(self.ALU.ALUResult)
    elif self.DM.WE == 1:
      self.DM.WDPort(self.ALU.ALUResult, self.RF.RD2)

  def writeBack(self):
    instr = self.IM.RD
    opcode = (instr & 0b11111100000000000000000000000000) >> 26
    rs = (instr & 0b00000011111000000000000000000000) >> 21
    rt = (instr & 0b00000000000111110000000000000000) >> 16
    rd = (instr & 0b00000000000000001111100000000000) >> 11
    shamt = instr & 0b00000000000000000000011111000000
    funct = instr & 0b00000000000000000000000000111111
    imm = imm_convert(instr & 0xFFFF)
    print(f'{self.DM.RD} ok, cheq')
    self.RF.WD3Port(rt, rd, self.ALU.ALUResult, self.DM.RD)

  def pc_update(self):
    instr = self.IM.RD
    imm = imm_convert(instr & 0xFFFF)
    branch_address = imm << 2
    funct = instr & 0b00000000000000000000000000111111
    opcode = (instr & 0b11111100000000000000000000000000) >> 26
    address = instr & 0x1FFFFFF  # Mask for extracting bits 25 to 0
    self.PC.update(address, branch_address)

  def run(self):
    while self.flag:
      print("Starting iteration...")
      print(f'pc value is {self.PC.value}')
      self.fetch()
      self.decode_execute()
      if (self.flag == 0):
        break
      self.memAccess()
      self.writeBack()
      self.pc_update()
      print("End of iteration.")
      for index, value in enumerate(self.RF.file):
        print(f"RF[{index}]: {value}")
        # Feel free to inspect whatever DataMemory Location you want by changing the indices
      print(self.DM.mem[8192:8232:4])
    print("Done")
