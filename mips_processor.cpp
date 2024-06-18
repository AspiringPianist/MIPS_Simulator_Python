#include <iostream>
#include <vector>
#include <bitset>

using namespace std;

// Helper functions for binary conversion and flipping bits
string num_to_8bit_binary(int num) {
    return bitset<8>(num).to_string();
}

string num_to_16bit_binary(int num) {
    return bitset<16>(num).to_string();
}

int flipBits(string binary_str) {
    string ans = "";
    for (int i = 0; i < binary_str.length(); ++i) {
        if (binary_str[i] == '1') {
            ans += '0';
        } else if (binary_str[i] == '0') {
            ans += '1';
        }
    }
    return stoi(ans, nullptr, 2);
}

int imm_convert(int imm) {
    if (imm >> 15) {
        imm = 0 - (flipBits(num_to_16bit_binary(imm)) + 1);
        return imm;
    } else if (imm >> 15 == 0) {
        return imm;
    }
}

// Class definitions
class PC {
private:
    int value;
    int pcSrc;
    int jump;
    int jal;
    int jr;
    int branch;

public:
    PC(int value) : value(value), pcSrc(0), jump(0), jal(0), jr(0), branch(0) {}

    void update(int address, int branchAddress) {
        if (jump) {
            value = address << 2;
        } else if (pcSrc) {
            value = value + 4 + branchAddress;
        } else if (jal) {
            value = address << 2;
        } else if (jr) {
            // Do nothing for jr
        } else {
            value = value + 4;
        }

        pcSrc = 0;
        jump = 0;
        jal = 0;
        jr = 0;
        branch = 0;
    }
};

class IM {
private:
    vector<int> mem;
    int RD;

public:
    IM() : mem(0xffc), RD(0) {
        cout << "Initialized Instruction Memory" << endl;
    }

    void RDPort(int A) {
        RD = stoi(num_to_8bit_binary(mem[A + 3]) + num_to_8bit_binary(mem[A + 2]) +
                   num_to_8bit_binary(mem[A + 1]) + num_to_8bit_binary(mem[A]), nullptr, 2);
        cout << "Instruction fetched from memory: " << RD << endl;
    }
};

class RF {
private:
    int WE3;
    int RD1;
    int RD2;
    vector<int> file;
    int RegDst;
    int MemtoReg;

public:
    RF() : WE3(0), RD1(0), RD2(0), file(32), RegDst(0), MemtoReg(0) {
        file[29] = 16380;  // stack pointer location in DM
    }

    void RD1Port(int A1) {
        RD1 = file[A1];
    }

    void RD2Port(int A2) {
        RD2 = file[A2];
    }

    void WD3Port(int rt, int rd, int ALUResult, int RD) {
        int value = 0;
        if (MemtoReg == 0) {
            value = ALUResult;
            cout << "Chose ALuResult" << endl;
        } else if (MemtoReg == 1) {
            value = RD;
            cout << "Chose RD" << endl;
        }
        if (WE3) {
            if (RegDst == 0) {
                file[rt] = value;
                cout << "Wrote to rt " << rt << " : " << value << endl;
            } else if (RegDst == 1) {
                file[rd] = value;
                cout << "Wrote to rd " << rd << " : " << value << endl;
            }
        }
    }
};

class DM {
private:
    int WE;
    int RD;
    vector<int> mem;

public:
    DM() : WE(0), RD(0), mem(0x3fff) {}

    void RDPort(int A) {
        RD = mem[A];
    }

    void WDPort(int A, int value) {
        if (WE) {
            mem[A] = value;
        }
    }
};

class ALU {
private:
    int ALUResult;
    int Zero;
    int Control;
    int ALUSrc;
    int srcA;
    int srcB;

public:
    ALU() : ALUResult(0), Zero(0), Control(0), ALUSrc(0), srcA(0), srcB(0) {}

    void calculate(int srcA, int rtVal, int imm) {
        // Source Decision
        // imm = imm_convert(imm);
        this->srcA = srcA;
        cout << "rtVal is " << rtVal << " and imm is " << imm << endl;
        if (ALUSrc == 0) {
            srcB = rtVal;
        } else if (ALUSrc == 1) {
            srcB = imm;
        } else {
            srcB = 0;
        }
        Zero = srcA - srcB;

        // ALU operation
        if (Control == -2) {  // mul instruction
            cout << "Mul Called" << endl;
            ALUResult = srcA * srcB;
        } else if (Control == 0b010) {
            ALUResult = srcA + srcB;
            cout << "Added " << srcA << " and " << srcB << " together" << endl;
        } else if (Control == 0b110) {
            cout << "Called sub" << endl;
            ALUResult = srcA - srcB;
        } else if (Control == 0b101) {
            ALUResult = srcA * srcB;
        } else if (Control == 0b111) {
            ALUResult = srcA / srcB;
        } else if (Control == 0b001) {
            ALUResult = srcA << srcB;
        } else if (Control == 0b100) {
            ALUResult = srcA >> srcB;
        } else {
            ALUResult = 0;
        }

        // Z flag
        if (ALUResult == 0) {
            Zero = 1;
        }
    }

    int getALUResult() {
        return ALUResult;
    }

    int getZero() {
        return Zero;
    }
};

class CU {
private:
    int RegDst;
    int Jump;
    int Branch;
    int MemRead;
    int MemtoReg;
    int ALUOp;
    int MemWrite;
    int ALUSrc;
    int RegWrite;
    int jal;
    int jr;

public:
    CU() : RegDst(0), Jump(0), Branch(0), MemRead(0), MemtoReg(0), ALUOp(0), MemWrite(0), ALUSrc(0), RegWrite(0), jal(0), jr(0) {}

    void setControlSignals(int opcode) {
        switch (opcode) {
            case 0b000000:  // R-type
                RegDst = 1;
                Jump = 0;
                Branch = 0;
                MemRead = 0;
                MemtoReg = 0;
                ALUOp = 0b010;
                MemWrite = 0;
                ALUSrc = 0;
                RegWrite = 1;
                break;
            case 0b100011:  // lw
                RegDst = 0;
                Jump = 0;
                Branch = 0;
                MemRead = 1;
                MemtoReg = 1;
                ALUOp = 0b010;
                MemWrite = 0;
                ALUSrc = 1;
                RegWrite = 1;
                break;
            case 0b101011:  // sw
                RegDst = 0;
                Jump = 0;
                Branch = 0;
                MemRead = 0;
                MemtoReg = 0;
                ALUOp = 0b010;
                MemWrite = 1;
                ALUSrc = 1;
                RegWrite = 0;
                break;
            case 0b000100:  // beq
                RegDst = 0;
                Jump = 0;
                Branch = 1;
                MemRead = 0;
                MemtoReg = 0;
                ALUOp = 0b110;
                MemWrite = 0;
                ALUSrc = 0;
                RegWrite = 0;
                break;
            case 0b000010:  // jump
                RegDst = 0;
                Jump = 1;
                Branch = 0;
                MemRead = 0;
                MemtoReg = 0;
                ALUOp = 0;
                MemWrite = 0;
                ALUSrc = 0;
                RegWrite = 0;
                break;
            case 0b000011:  // jal
                RegDst = 0;
                Jump = 0;
                Branch = 0;
                MemRead = 0;
                MemtoReg = 0;
                ALUOp = 0;
                MemWrite = 0;
                ALUSrc = 0;
                RegWrite = 1;
                jal = 1;
                break;
            case 0b000111:  // jr
                RegDst = 0;
                Jump = 0;
                Branch = 0;
                MemRead = 0;
                MemtoReg = 0;
                ALUOp = 0;
                MemWrite = 0;
                ALUSrc = 0;
                RegWrite = 0;
                jr = 1;
                break;
            default:
                break;
        }
    }

    int getRegDst() {
        return RegDst;
    }

    int getJump() {
        return Jump;
    }

    int getBranch() {
        return Branch;
    }

    int getMemRead() {
        return MemRead;
    }

    int getMemtoReg() {
        return MemtoReg;
    }

    int getALUOp() {
        return ALUOp;
    }

    int getMemWrite() {
        return MemWrite;
    }

    int getALUSrc() {
        return ALUSrc;
    }

    int getRegWrite() {
        return RegWrite;
    }

    int getJal() {
        return jal;
    }

    int getJr() {
        return jr;
    }
};

// Processor class implementation...
int main() {
    // Instantiate and use classes here for testing...
    return 0;
}
