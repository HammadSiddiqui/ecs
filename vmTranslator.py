import sys
from pathlib import Path
#HAMMAD SIDDIQUI
class Parser(object):
    '''Parses a single vm file to provide convenient access to the
    contained commands and their components.
    '''
     
    def __init__(self, fname):
        '''Opens the input file at fname and get ready to parse it.
        '''
        self.vmFile = open(fname, 'r')
        self.data = self.vmFile.readline()
     
    def __str__(self):
        '''Leave as is.'''
        return 'Parser object'
 
    def hasMoreCommands(self):
        '''P.hasMoreCommands() -> bool
 
        Returns True if there are commands in the input, False
        otherwise.
        '''
        if self.data == '' or self.data == None:
            self.vmFile.close()
            return False
        else:
            return True
 
    def advance(self):
        '''P.advance() -> None
 
        Makes the next command the current command. Should be called
        only if hasMoreCommands() is True.
        '''
        if self.hasMoreCommands() == True:
            self.data = self.vmFile.readline()
 
    def commandType(self):
        '''P.commandType() -> str
 
        Returns the type of the current VM command: one of
        C_ARITHMETIC
        C_PUSH, C_POP
        C_LABEL
        C_GOTO
        C_IF
        C_FUNCTION
        C_RETURN
        C_CALL
        '''
        if self.data.find('push') == 0:
            return 'C_PUSH'
        elif self.data.find('pop') == 0:
            return 'C_POP'
        elif self.data.find('label') == 0:
            return 'C_LABEL'
        elif self.data.find('goto') == 0:
            return 'C_GOTO'
        elif self.data.find('if-goto') == 0:
            return 'C_IF'
        elif self.data.find('function') == 0:
            return 'C_Function'
        elif self.data.find('call') == 0:
            return "C_CALL"
        elif self.data.find('return') == 0:
            return 'C_RETURN'
        else:
            return 'C_ARITHMETIC'
 
     
    def arg1(self):
        '''P.arg1() -> string
 
        Returns the first argument of the current command. In the case
        of C_ARTIHMETIC, the command itself (e.g. sub, add) is
        returned. Should not be called if the current command is
        C_RETURN.
        '''
        commandTypes = ['C_PUSH', 'C_POP',
        'C_LABEL',
        'C_GOTO',
        'C_IF',
        'C_FUNCTION',
        'C_CALL']
         
        if self.commandType() == 'C_ARITHMETIC':
            return self.data
        elif self.commandType() in commandTypes:
            return self.data.split()[1]
 
    def arg2(self):
        '''P.arg2() -> int
 
        Returns the second argument of the current command. Should be
        called only if the current command is any of
        C_PUSH
        C_POP
        C_FUNCTION
        C_CALL
        '''
        commandTypes = ['C_PUSH',
        'C_POP',
        'C_FUNCTION',
        'C_CALL']
        if self.commandType() in commandTypes:
            return int(self.data.split()[2])
     
class CodeWriter(object):
    '''Translates VM commands into Hack assembly code.'''
     
    def __init__(self, fname):
        '''Opens the output file at fname and gets ready to write to it.'''
        self.output = open(fname, 'w')
        self.output.write("@256\nD=A\n@SP\nM=D\n")
        self._count = 0
     
    def __str__(self):
        '''Leave as is.'''
        return 'CodeWriter object.'
 
    def setFileName(self, fname):
        '''CW.setFileName(str) -> None
 
        Informs the code writer that the translation of the VM file at
        fname is to be started.
        '''
        self.name = fname
     
    def writeArithmetic(self, command):
        '''CW.writeArithmetic(str) -> None
 
        Writes to the output file the assmebly code that is the
        translation of the given arithmetic command.
        '''
        #self.data of Class Parser = command
        self.output.write("\n@SP\nA=M-1\n")
        if command == 'neg':
            self.output.write('M=-M\n')
        elif command == 'not':
            self.output.write('M=!M\n')
        else:
            self.output.write("\nD=M\n@SP\nAM=M-1\nM=0\nA=A-1\n")
            #if command == 'add' Doesn't works, Strange
            if 'add' in command:
                self.output.write("M=M+D\n")
            elif 'sub' in command:
                self.output.write("M=M-D\n")
            elif 'or' in command:
                self.output.write("M=M|D\n")
            elif 'and' in command:
                self.output.write("M=M&D\n")
            else:
                self.output.write("D=M-D\n@TRUE" + str(self._count) + "\nD;J")
                if command == 'eq':
                    self.output.write("EQ")
                elif command == 'lt':
                    self.output.write("LT")
                elif command == 'gt':
                    self.output.write("GT")
                self.output.write("\n@SP\nA=M-1\nM=0\n@FALSE" + str(self._count) + "\n0;JEQ\n(TRUE" + str(self._count) + ")\n@SP\nA=M-1\nM=-1\n" + "(FALSE" + str(self._count) + ")\n")
                self._count = self._count + 1
 
    def writePushPop(self, command, segment, index):
        '''CW.writePushPop(str) -> None
 
        Writes to the output file the assmebly code that is the
        translation of the given command, where command is either
        C_PUSH or C_POP.
        '''
        if segment == 'local':
            self.output.write("@LCL\nD=M")
        elif segment == 'argument':
            self.output.write("@ARG\nD=M")
        elif segment == 'that':
            self.output.write("@THAT\nD=M")
        elif segment == 'this':
            self.output.write("@THIS\nD=M")
        elif segment == 'temp':
            self.output.write("@5\nD=A")
        elif segment == 'pointer':
            self.output.write("@3\nD=A")
        elif segment == 'static':
            self.output.write("@" + self.name + "." + str(index) + "\nD=A")
        elif segment == 'constant':
            if index == 0 or index == 1:
                self.output.write("\nD=" + str(index))
            else:
                self.output.write("@" + str(index) + "\nD=A")
        if segment != 'static' and segment != 'constant' and index != 0:
            self.output.write("\n@" + str(index) + "\nD=D+A")
        if command == 'C_PUSH':
            if segment == "constant":
                self.output.write("\n@SP\nAM=M+1\nA=A-1\nM=D\n")
            else:
                self.output.write("\nA=D\nD=M\n@SP\nAM=M+1\nA=A-1\nM=D\n")
        else:
            self.output.write("\n@R13\nM=D\n@SP\nAM=M-1\nD=M\nM=0\n@R13\nA=M\nM=D\n")
 
 
    def close(self):
        '''CW.close() -> None
 
        Close the output file.
        '''
        self.output.write("(INFINITE_LOOP)\n@INFINITE_LOOP\n0;JEQ\n")
        self.output.close()
 
def printUsage():
    '''printUsage() -> None
     
    Prints infomration on how to call this file.
    '''
    print("Usage: VMtranslator source")
    print("source is one of")
    print("\ta .vm file\n\ta directory containing .vm files")
 
def getFileNames():
    '''getFileNames() -> tuple
 
    Returns a tuple contianing the name of the output ASM file and a
    list of names of the VM files to operate on, as per the call to
    the program from command line.
    '''
    if len(sys.argv) != 2:
        printUsage()
        print('Invalid call:', end=' ')
        for x in sys.argv:
            print(x, end=' ')
        print()
        sys.exit()  # End program.
    p = Path(sys.argv[1])
    fname = str(p)
    if p.is_dir():
        while fname[-1] == '/':
            fname = fname[:-1]
        asmFname = fname + '.asm'
        vmFiles = list(p.glob('*.vm'))
    elif fname[-3:] == '.vm' and p.exists():
        asmFname = fname[:-3]+'.asm'
        vmFiles = [p]
    else:
        printUsage()
        print('Invalid file:', fname,'\nAborting!')
        sys.exit() # End program.
    vmFiles = [str(f) for f in vmFiles]
    return (asmFname, vmFiles)
 
def main():
    asmFname, vmFiles = getFileNames()
    # asmFname now contains the name of the file to output to.
    # vmFiles is a list contianing the names of VM files to be translated.
    #asmFname returns complete Path to the output file not just the name.
    asmFname = asmFname.split("\\")[-1]
    asmObject = CodeWriter(asmFname)
    for vmfile in vmFiles:
        #Handles Multiple Files and writes all in one asm File
        vmObject = Parser(vmfile)
        asmObject.setFileName(vmfile)
         
        while vmObject.hasMoreCommands() == True:
            while '//' in vmObject.data: #using while loop for more than 1 comments
                index = vmObject.data.index('//') #Finds the start of comments
                if index == 0:
                    vmObject.advance()
                    #After moving to next line have to perform the remove space operation again
                else:
                    #this takes care of comments writen on same line as instructions
                    vmObject.data = vmObject.data[:index]
                while vmObject.data == '\n': #using while loop for more than 1 emptyline
                     vmObject.advance()
            index = 0
            if vmObject.commandType() != "C_RETURN":
                index = vmObject.arg2()
            if vmObject.commandType() == 'C_ARITHMETIC':
                asmObject.writeArithmetic(vmObject.data)
            elif vmObject.commandType() == "C_PUSH" or vmObject.commandType() == "C_POP":
                command = vmObject.commandType()
                segment = vmObject.arg1()
                asmObject.writePushPop(command,segment,index)
             
            vmObject.advance()
    asmObject.close()
if __name__ == "__main__":
    # Leave as is.
    main()