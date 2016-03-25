import sys
import re
from pathlib import Path
 
class JackTokenizer(object):
    '''Removes all comments and white space from the input stream and
    breaks it into Jack-language tokens, as specified by the Jack
    grammar.'''
     
    def __init__(self,inputFile):
        '''Constructor - Opens inputFile and gets ready to tokenize it.'''
        self.file = open(inputFile, 'r')
        self.read = self.file.read()
        #The folowing RegEx removes comments of both types: // and /*
        self.read = re.sub('\//+(.*?)\n|\/\*[\s\S]+?\*\/','', self.read)
        #The following RegEx splits the jack input file into tokens
        regex = "\s*(\d+|\w+|.)"
        self.tokens = re.findall(regex, self.read)
        #Reversing as list.pop() is a FIFO operation
        self.tokens.reverse()
        #Pop the first token into the currentToken
        self.currentToken = self.tokens.pop()
 
    def hasMoreTokens(self):
        '''JT.hasMoreTokens() -> bool
 
        Returns True if there are more tokens left, False otherwise.'''
        #If list becomes empty, there are no more tokens left to parse
        if len(self.tokens) == 0:
            return False
        else:
            return True
         
    def nextToken(self):
        return self.tokens[-1]
     
    def advance(self):
        '''JT.advance() -> None
 
        Gets the next token from the input and makes it the current
        token. Should only be called if hasmoreTokens() is
        True. Initially there is no current token
        '''
        #pop() tokens into the currentToken variable
        if self.hasMoreTokens() == True:
            self.currentToken = self.tokens.pop()
         
     
    def tokenType(self):
        '''JT.tokenType() -> str
 
        Returns the type of the current token which is one of:
        KEYWORD
        SYMBOL
        IDENTIFIER
        INT_CONST
        STRING_CONST
        '''
        symbol = ['{','}','(',')','[',']','.',',',';','+','-','*','/','&','|','<','>','=','~']
        keyword=['class','constructor','function','method','field','static','var','int','char','boolean','void','true','false','null','this','let','do','if','else','while','return']
        if self.currentToken in keyword:
            return "KEYWORD"
        elif self.currentToken in symbol:
            return "SYMBOL"
        elif self.currentToken.isnumeric():
            return "INT_CONST"
        elif self.currentToken== '"':
            return "STRING_CONST"
        else:
            return "IDENTIFIER"
         
    def keyWord(self):
        '''JT.keyWord() -> str
 
        Returns the keyword which is the current token. Should be
        called only when tokentype() is KEYWORD. Return value is one of:
        CLASS, METHOD, FUNCTION, CONSTRUCTOR, INT,
        BOOLEAN, CHAR, VOID, VAR, STATIC, 'FIELD, LET,
        DO, IF, ELSE, WHILE, RETURN, TRUE, FALSE,
        NULL, THIS
        '''
        if self.tokenType() == "KEYWORD":
            return self.currentToken
     
    def symbol(self):
        '''JT.symbol() -> str
 
        Returns the character which is the current token. Should be
        called only when tokentype() is SYMBOL.
        '''
        if self.tokenType() == "SYMBOL":
            return self.currentToken
     
     
    def identifier(self):
        '''JT.identifier() -> str
 
        Returns the identifier which is the current token. Should be
        called only when tokenType() is IDENTIFIER.
        '''
        if self.tokenType() == "IDENTIFIER":
            return self.currentToken
     
    def intVal(self):
        '''JT.intVal() -> int
 
        Returns the integer value of the current token. Should be
        called only when tokenType() is INT_CONST.
        '''
        if self.tokenType() == "INT_CONST":
            numeric = int(self.currentToken)
            if numeric >= 0 and numeric <= 32767:
                return numeric
            else:
                print("CONSTANT OUT OF RANGE")
     
    def stringVal(self):
        '''JT.stringVal() -> str
 
        Returns the string value of the current token, without double
        quotes. Should be called only when TokenType() is
        STRING_CONST.
        '''
        if self.tokenType() == "STRING_CONST":
            #Combines all tokens between double quotes
            self.currentToken = self.currentToken + " " + self.tokens.pop()
            while self.currentToken[-1] != "\"":
                self.currentToken = self.currentToken + " " + self.tokens.pop()
            return self.currentToken
                 
         
     
class CompilationEngine(object):
    '''Effects the actual compilation output. Gets its input from a
    JackTokenizer and emits its parsed structure into an output file.
    '''
 
    def __init__(self,inputFile,outputFile):
        '''Constructor - Creates a new compilation engine with inputFile and
        outputFile. The next method called must be compileClass().
        '''
        self.infile = JackTokenizer(inputFile)
        self.outFile = open(outputFile, 'w')
        self.compileClass()
         
     
    def compileClass(self):
        '''CE.compileClass() -> None
 
        Compiles a complete class.'''
        self.outFile.write("<class>\n")
        if self.infile.currentToken == "class":
            self.outFile.write("<keyword>class</keyword>\n")
            self.infile.advance()
            if self.infile.tokenType() == "IDENTIFIER":
                self.outFile.write("<identifier>" + self.infile.currentToken + "</identifier>\n")
                if self.infile.nextToken() == "{":
                    self.outFile.write("<symbol> { </symbol>\n")
                    self.infile.advance()
                    while self.infile.currentToken != "}":
                        if self.infile.nextToken() == "}":
                            self.outFile.write("<symbol> } </symbol>\n")
                            self.outFile.write("</class>\n")
                            break
                        self.compileClassVarDec()
                        self.infile.advance()
                        self.compileSubroutine()
                else:
                    print("Expected a { symbol after Identifier")
            else:
                print("Expected an IDENTIFIER")
        else:
            print("Expected Keyword class")
     
    def compileClassVarDec(self):
        '''CE.compileClassVarDec() -> None
         
        Compiles a static declaration or a field declaration.
        '''
        if self.infile.currentToken == "static" or self.infile.currentToken == "field":
            self.outFile.write("<classVarDec>\n")
            self.outFile.write("<keyword> " + self.infile.currentToken + " </keyword>\n")
            self.infile.advance()
            if self.infile.tokenType() == "IDENTIFIER" or self.infile.currentToken in ["int","char","boolean"]:
                if self.infile.tokenType() == "IDENTIFIER":
                    self.outFile.write("<identifier> " + self.infile.currentToken + " </identifier>\n")
                else:
                    self.outFile.write("<keyword> " + self.infile.currentToken + " </keyword>\n")
                 
                while self.infile.nextToken() != ";":
                    if self.infile.nextToken() == ",":
                        self.infile.advance()
                        self.outFile.write("<symbol> , </symbol>\n")
                    self.infile.advance()
                    if self.infile.tokenType() == "IDENTIFIER":
                        self.outFile.write("<identifier> " + self.infile.currentToken + "</identifier>\n")
                self.infile.advance()
                if self.infile.currentToken == ";":
                     
                    self.outFile.write("<symbol> ; </symbol>\n")
                     
                    self.outFile.write("</classVarDec>\n")
         
                     
 
    def compileSubroutine(self):
        '''CE.compileSubroutine() -> None
 
        Compiles a complete method, function, or constructor.
        '''
         
        if self.infile.currentToken in ["constructor","method","function"]:
            self.outFile.write("<subroutineDec>\n")
            self.outFile.write("<keyword> " + self.infile.currentToken + " </keyword>\n")
            self.infile.advance()
            if self.infile.tokenType() == "IDENTIFIER" or self.infile.currentToken in ["int","char","boolean", "void"]:
                if self.infile.tokenType() == "IDENTIFIER":
                    self.outFile.write("<identifier> " + self.infile.currentToken + " </identifier>\n")
                else:
                    self.outFile.write("<keyword> " + self.infile.currentToken + " </keyword>\n")
                self.infile.advance()
                if self.infile.tokenType() == "IDENTIFIER":
                    self.outFile.write("<identifier> " + self.infile.currentToken + "</identifier>\n")
                    self.outFile.write("<symbol> ( </symbol>\n")
                    self.infile.advance()
                self.compileParameterList()
                self.outFile.write("<subroutineBody>\n")
                if self.infile.nextToken() == "{":
                    self.outFile.write("<symbol> { </symbol>\n")
            self.compileVarDec()
            self.compileStatements()
            if self.infile.nextToken() == "}":
                self.outFile.write("<symbol> } </symbol>\n")
                self.infile.advance()
                if self.infile.nextToken() in ["method", "function", "constructor", "}"]:
                    self.outFile.write("</subroutineBody>\n")
                    self.outFile.write("</subroutineDec>\n")
                    self.infile.advance()
                          
 
    def compileParameterList(self):
        '''CE.compileParameterList() -> None
 
        Compiles a (possible empty) parameter list not including the
        enclosing "()".
        '''
         
         
        self.outFile.write("<parameterList>\n")
         
        while self.infile.nextToken() != ")":
            print(self.infile.currentToken)
            if self.infile.nextToken() == ",":
                self.infile.advance()
                self.outFile.write("<symbol> , </symbol>\n")
            self.infile.advance()
            if self.infile.tokenType() == "IDENTIFIER" or self.infile.currentToken in ["int","char","boolean"]:
                if self.infile.tokenType() == "IDENTIFIER":
                    self.outFile.write("<identifier> " + self.infile.currentToken + "</identifier>\n")
                else:
                    self.outFile.write("<keyword> " + self.infile.currentToken + " </keyword>\n")
                    #self.infile.advance()
                if self.infile.tokenType() == "IDENTIFER":
                    self.outFile.write("<identifier> " + self.infile.advance() + "</identifier>\n")
                else:
                    self.infile.advance()
                    if self.infile.tokenType() == "IDENTIFIER":
                        self.outFile.write("<identifier> " + self.infile.currentToken + "</identifier>\n")
        if self.infile.nextToken() == ")":
            self.outFile.write("</parameterList>\n")
            self.outFile.write("<symbol> ) </symbol>\n")
            self.infile.advance()                    
        self.outFile.write("</parameterList>\n")
         
    def compileVarDec(self):
        '''CE.compileVarDec() -> None
 
        Compiles a var declaration.
        '''
        self.infile.advance()
        if self.infile.currentToken == "var":
            self.outFile.write("<varDec>\n")
            sefl.outFile.write("<keyword>" + self.infile.currentToken + "</keyword>")
            self.infile.advance()
            if self.infile.tokenType() == "IDENTIFIER" or self.infile.currentToken in ["int","char","boolean"]:
                if self.infile.tokenType() == "IDENTIFIER":
                    self.outFile.write("<identifier> " + self.infile.currentToken + " </identifier>\n")
                else:
                    self.outFile.write("<keyword> " + self.infile.currentToken + "</keyword>\n")
                while self.infile.nextToken() != ";":
                    if self.infile.nextToken == ",":
                        self.outFile.write("<symbol> , </symbol>\n")
                        self.infile.advance()
                    else:
                        self.infile.advance()
                    if self.infile.tokenType() == "IDENTIFIER":
                        self.outFile.write("<identifier> " + self.infile.currentToken + " </identifier>\n")
                if self.infile.currentToken == ";":
                    self.outFile.write("<keyword> ; </keyword>\n")
                    self.outFile.write("</varDec>\n")
         
 
    def compileStatements(self):
        '''CE.compileStatements() -> None
 
        Compiles a sequence of statement not including the enclosing "{}".
        '''
         
        self.outFile.write("<statements>\n")
        while self.compileLet() or self.compileDo() or self.compileIf() or self.compileWhile():
            self.compileReturn()
        self.outFile.write("</statements>\n")
 
    def compileDo(self):
        '''CE.compileDo() -> None
 
        Compiles a do statement.
        '''
        self.infile.advance()
        if self.infile.currentToken == "do":
            self.outFile.write("<doStatement>\n")
            self.outFile.write("<keyword>" + self.infile.currentToken + "</keyword>\n")
            self.CompileSubroutine()
            if self.infile.nextToken() == ";":
                self.outFile.write("<symbol> ; </symbol>\n")
                self.outFile.write("</doStatment>\n")
 
    def compileLet(self):
        '''CE.compileLet() -> None
 
        Compiles a let statement.
        '''
        #NOT COMPLETE
        self.infile.advance()
        if self.infile.currentToken == "let":
            self.outFile.write("<letStatement>\n")
            self.outFile.write("<keyword> let </keyword>\n")
            self.infile.advance()
            if self.infile.tokenType() == "IDENTIFIER":
                self.outFile.write("<identifier>" + self.infile.currentToken +"</identifier>\n")
                if self.infile.nextToken == "[":
                    self.outFile.write("<symbol> [ </symbol>\n")
                    self.outFile.write("<identifier>" + self.infile.currentToken +"</identifier>\n")
                                         
                     
    def compileWhile(self):
        '''CE.compileWhile() -> None
 
        Compiles a while statement.
        '''
        self.infile.advance()
        if self.infile.currentToken == "while":
            self.outFile.write("<whileStatement>\n")
            self.outFile.write("</keyword>" + self.infile.currentToken+ "</keyword>\n")
            if self.infile.nextToken() == "(":
                self.outFile.write("<symbol> ( </symbol>\n")
                self.compileExpressionList()
                if self.infile.nextToken() == ")":
                    self.outFile.write("<symbol> ) </symbol>\n")
                    self.outFile.write("<symbol> { </symbol>\n")
                    self.compileStatements()
                    if self.infile.nextToken() == "}":
                        self.outFile.write("<symbol> } </symbol>\n")
            self.outFile.write("</whileStatements>\n")
             
    def compileReturn(self):
        '''CE.compileReturn() -> None
 
        Compiles a return statement.
        '''
        self.infile.advance()
        if self.infile.currentToken == "return":
            self.outfile.write("<returnStatement>\n")
            self.outfile.write("<keyword>" + self.infilecurrentToken + "</keyword>")
            if self.infile.nextToken() != ";":
                self.compileExpression()
            elif self.infile.nextToken() == ";":
                self.outFile.write("<symbol> ; </symbol>\n")
                self.outFile.write("</returnStatement>\n")
             
             
    def compileIf(self):
        '''CE.compileIf() -> None
 
        Compiles an if statement possibly with a trailing else clause.
        '''
        self.infile.advance()
        if self.infile.currentToken == "if":
            self.outFile.write("<ifStatement\n>")
            self.outFile.write("<keyword>\n")
            if self.infile.nextToken() == "(":
                self.outFile.write("<symbol> ( </symbol>\n")
                self.infile.advance()
                self.compileExpressionList()
                if self.infile.nextToken in [")", "{"]:
                    self.outFile.write("<symbol> ) </symbol>\n")
                    self.outFile.write("<symbol> { </symbol>\n")
                    self.compileStatements()
                    if self.infile.nextToken() == "}":
                        self.outFile.write("<symbol> } </symbol>")
            self.outFile.write("</ifStatement>")
             
     
    def compileExpression(self):
        '''CE.compileExpression() -> None
         
        Compiles an expression.
        '''
        self.outFile.write("<expression>\n")
        self.compileTerm()
        self.infile.advance()
        while self.infile.tokenType == "SYMBOL":
            symbol = ""
            if self.infile.currentToken() == "<":
                symbol = "&lt;"
            elif self.infile.currentToken() == ">":
                symbol = "&gt;"
            elif self.infile.currentToken() == "&":
                symbol = "&amp;"
            elif self.infile.currentToken() == "\"":
                symbol = "&quot;"
            self.outfile.write("<symbol>" + symbol + "</symbol>\n")
        self.compileTerm()
        self.outFile.write("</expression>\n")
 
    def compileTerm(self):
        '''CE.compileTerm() -> None
 
        Compiles a term. Uses lookahead to decide between alternative
        parsing rules. If the current token is an indentifier, a
        look=ahead token of "[", "(", or "." distinguish between a
        variable, array, and subroutine call. Any other token is not
        part of this term and should not be advanced over.
        '''
        #Not complete 
        self.outFile.write("<term>\n")
        self.infile.advance()
        if self.infile.currentToken in ["true","false","this","null"]:
            self.outFile.write("<keyword>" + self.infile.currentToken + "</keyword>\n")
        elif self.infile.currentToken == "(":
            self.outFile.write("<symbol>(</symbol>\n")
            self.compileExpression()
            if self.infile.nextToken() == ")":
                self.outFile.write("<symbol> ) </symbol>")
        elif self.infile.currentToken in ["-", "~"]:
            self.outFile.write("<symbol>" + self.infile.nextToken() + "</symbol>\n")
        elif self.infile.tokenType == "STRING_CONST":
            self.outFile.write("<stringConstant>" + self.infile.currentToken + "</stringConstant>")
        elif self.infile.tokenType() == "INT_CONST":
            self.outFile.write("<integerConstant>" + self.infile.currentToken + "</integerConstant>") 
        self.outFile.write("</term>")
    def compileExpressionList(self):
        '''CE.compileExpressionList() -> None
 
        Compiles a (possibly empty) comma separated list of expressions.
        '''
        while self.infile.nextToken() != "{":
            self.compileExpression()
 
def printUsage():
    '''printUsage() -> None
     
    Prints infomration on how to invoke this program.
    '''
    print("Usage: {} dir".format(sys.argv[0]))
    print("dir is the program directory - it contains the .jack file(s) to be compiled.")
 
def getFileNames():
    '''getFileNames() -> list
 
    Returns a list containing the names of the Jack files in the given
    directory name. Prints help and exits this program gracefully if
    the program is invoked incorrectly.
    '''
    if len(sys.argv) != 2:
        printUsage()
        print('Invalid call:', str(sys.argv).translate(str.maketrans('','',"',[]")))
        sys.exit()
    p = Path(sys.argv[1])
    if not p.is_dir():
        printUsage()
        print('{} is not a directory'.format(p))
        sys.exit()
    jackFiles = list(p.glob('*.jack'))
    jackFiles = [str(f) for f in jackFiles]
    return jackFiles
 
def main():
    '''Compiles the Jack program in the directory whose name is supplied
    through the command line when invoking this program.
    '''
    jackFiles = getFileNames()
    vmFiles = [s.replace('.jack','.vm') for s in jackFiles]
    # jackFiles contains the names of the Jack files to be compiled.
    # vmFiles contains the names of the corresponding vm files to be written to.
    for jackFile in jackFiles:
        index = jackFile.index('.jack')
        xmlFile = jackFile[:index] + '.xml'
        compiler = CompilationEngine(jackFile,xmlFile)
 
if __name__ == '__main__':
    '''Leave as is.'''
    main()