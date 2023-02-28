import sys

lastreadchar = 0
filename=''
line = 1



quad_counter = 1                            #endiamesos kwdikas
quads = []
temp_var_counter = 0

func_proc_exists=0  

scope_level = 0                             #pinakas sumvolwn
scopes = []
offset = 12
framelength_of_main = 0

xml_code = []                                #telikos kwdikas  
pointer = 0 
labels_and_levels = [] 
callflag = 0


funcflag=0
procflag=0                                   #simasiologiki analusi
retflag=0
procedures=[]

scopefd = open("pinakas_symbolon.txt","w")

class Token:
    def __init__(self,tokenType,tokenString,lineNo):
       self.tokenType = tokenType
       self.tokenString = tokenString
       self.lineNo = lineNo
       
token = Token('', '', 0)

#gia ton pinaka sumvolon

class Variable:
    def __init__(var,name,offset):
       var.name = name
       var.offset = offset
       
class Tempvar:
    def __init__(tempvar,name,offset):
       tempvar.name = name
       tempvar.offset = offset
       
class Argument:
    def __init__(arg,name,mode,offset):
       arg.name = name
       arg.mode = mode
       arg.offset = offset
       
class Function:
    def __init__(func,name,startQuad,arguments,framelength):
       func.name = name
       func.startQuad = startQuad
       func.arguments = arguments
       func.framelength = framelength
       
class Scope:
    def __init__(scope,name,level,entities):
       scope.name = name
       scope.level = level
       scope.entities = entities
        
#----------------------------------------LEKTIKOS ANALUTIS------------------------------------------#

def lex():

    f = open(filename,"r")
    current = ""
    global line
    keywords = ["program","declare","if","else","while","switchcase","forcase","incase","case","default","not","and",
                "or","function","procedure","call","return","in","inout","input","print"]  
    reservedchars = [';',',','[',']','(',')','.','#',':','=','+','-','*','/','"','<','>','{','}']
    global lastreadchar
    f.seek(lastreadchar)
    charCount = 0
    stateIdent = 0

    
    
    while True:
        char = f.read(1)
        if char == '':
            print("Error @ Line "+ str(line) + ": EOF reached without the use of '.' to terminate the program")
            quit()
        elif char == '.':
            while True:
                temp=f.read(1)  
                if temp=='':
                    break
                elif temp.isspace():
                    continue
                else:
                    print("\nWarning:Possible code exists after program termination symbol '.'\n")
                    break
            token = Token("finish", '.', line)
            return token
        elif char == '\n':
            line = line + 1
            continue
        elif char.isspace():
           continue
        elif char == '#':
            while True:
                temp=f.read(1)  
                if temp=='':
                    print("Error @ Line " + str(line) + ": EOF while in comment state.")
                    quit()
                elif temp=='#':
                    break
                else:
                    continue
            

        elif(char>='a' and char<='z') or (char>='A' and char<='Z') or stateIdent==1:
            stateIdent=1
            current += char
            charCount += 1
            temp = f.read(1)
            f.seek(f.tell()-1)
            if (temp<'a' or temp>'z') and (temp<'A' or temp>'Z') and (temp<'0' or temp>'9') and not(temp.isspace()) and temp != '' and temp not in reservedchars: 
                print("Error @ Line " + str(line) + " Unknown character found in identifier")
                quit()
            elif (temp>='a' and temp<='z') or (temp>='A' and temp<='Z') or (temp>='0' and temp<='9'):
                continue
            elif (charCount>30):
                print("Error @ Line " + str(line) + ": Identifier is over 30 characters")
                quit()
            else:
                stateIdent=0
                current_type = "identifier"
                if current in keywords:
                    current_type = "keyword"
                token = Token(current_type, current, line)
                lastreadchar = f.tell()
                current = ""
                if temp=='':
                    lastreadchar = f.tell()+1
                return token

        elif (char>= '0' and char<= '9'):
            current += char
            temp = f.read(1)
            f.seek(f.tell()-1)
            if (int(current) < -(2**32-1)) or (int(current) > 2**32-1):
                print("Error @ Line " + str(line) + " Invalid number found")
                quit()
            if(temp>='0' and temp<='9'):
                continue
            elif (temp>='a' and temp<='z') or (temp>='A' and temp<='Z'):
                print("Error @ Line " + str(line) + ": a number cannot contain letters")
                quit()
            else:
                token = Token("number",current,line)
                lastreadchar = f.tell()
                current=""
                if temp=='':
                    lastreadchar = f.tell()+1
                return token
                
        elif char == ':':
            current += char
            temp = f.read(1)
            if temp == '' or temp != '=':
                print("Error @ Line " + str(line) + ": ':' must be followed by '=' " )
                quit()
            else:
                current = current + temp
                token = Token("assignment",current,line)
                lastreadchar = f.tell()
                current=""
                if temp == '':
                    lastreadchar = f.tell()+1
                return token
        
        elif(char == '+' or char == '-'):
            current += char
            token = Token("addOperator",current,line)                                                           
            lastreadchar = f.tell()
            current=""
            return token

        elif(char == '*' or char == '/'):
            current += char
            token = Token("mulOperator",current,line)
            lastreadchar = f.tell()
            current=""
            return token

        elif(char == ';' or  char == ','):
            current += char
            token = Token("delimeter",current,line)
            lastreadchar = f.tell()
            current=""
            return token

        elif(char == '='):
            current += char
            token = Token("relOperator",current,line)
            lastreadchar = f.tell()
            current=""
            return token

        elif(char == '<'):
            current += char
            temp = f.read(1)            
            if(temp == '=' or temp == '>'):
                current += temp
                token = Token("relOperator",current,line)
                lastreadchar = f.tell()
                current=""
                return token
            else:
                token = Token("relOperator",current,line)
                current=""
                f.seek(f.tell()-1)
                lastreadchar = f.tell()
                if temp == '':
                    lastreadchar = f.tell()+1
                return token

        elif(char == '>'):
            current += char
            temp = f.read(1)
            if(temp == '='):
                current += temp
                token = Token("relOperator",current,line)
                lastreadchar = f.tell()
                current=""
                return token
            else:
                token = Token("relOperator",current,line)
                current=""
                f.seek(f.tell()-1)
                lastreadchar = f.tell()
                if temp == '':
                    lastreadchar = f.tell()+1
                return token
                    
        elif char == '{' or char == '}' or char == '(' or char == ')' or char == '[' or char == ']':
            current += char
            token = Token("groupSymbol",current,line)
            lastreadchar = f.tell()
            current = ""
            return token

        else:
            print("Error @ Line " + str(line) + ": Unknown character found" )
            quit()

    f.close()
           
           
#-----------------------------VOITHITIKES SUNARTHSEIS ENDIAMESOU KWDIKA-----------------------------#



def nextquad():
    global quad_counter

    return quad_counter

def genquad(op,x,y,z):
    global quads
    global quad_counter
    lab = nextquad()
    newquad = [lab,op,x,y,z]
    
    quad_counter = quad_counter + 1
    quads.append(newquad)
    
def nextemp():
    global temp_var_counter
    temp_var_counter = temp_var_counter + 1
    temp = "T_" + str(temp_var_counter)
    return temp
    
def emptylist():
    empty_list = []
    return empty_list
    
def makelist(x):
    new_list = [x]
    return new_list
    
def merge(list1, list2):
    merged_list = []
    merged_list += list1
    merged_list += list2
    return merged_list
    
def backpatch(my_list, z):
    global quads
    for x in my_list:
        for y in quads:
            if y[0] == x and y[4] == '_':
                y[4] = z
    

#-----------------------------VOITHITIKES SUNARTHSEIS PINAKA SUMBOLWN------------------------------#   

def addScope(name):
    global scope_level, scopes
    new_scope = Scope(name,scope_level,[])
    scopes.append(new_scope)
    scope_level += 1
    
def deleteScope():
    global scope_level, scopes
    scope = scopes.pop(len(scopes)-1)
    scope_level -= 1
    
def addVarEntity(name, offset):
    global scopes
    variable = Variable(name, offset)
    curr_scope = scopes[len(scopes)-1]
    curr_scope.entities.append(variable)
    
def addTempVarEntity(name, offset):
    global scopes
    tempvar = Tempvar(name, offset)
    curr_scope = scopes[len(scopes)-1]
    curr_scope.entities.append(tempvar)
    
def addFuncEntity(name, start_quad, arguments, framelength):
    global scopes
    function = Function(name, start_quad, arguments, framelength)
    curr_scope = scopes[len(scopes)-1]
    curr_scope.entities.append(function)
    
def addArgEntity(name, mode, offset):
    global scopes
    argument = Argument(name, mode, offset)
    curr_scope = scopes[len(scopes)-1]
    curr_scope.entities.append(argument)
    
def searchEntity(name):
    for scope in reversed(scopes):
        for entity in scope.entities:
            if entity.name == name:
                return entity,scope
    
def addArgument(mode):
    global scopes
    curr_scope = scopes[len(scopes)-1]
    for scope in reversed(scopes):
        for entity in scope.entities:
            if entity.name == curr_scope.name and isinstance(entity, Function):          
                entity.arguments.append(mode)

    
#----------------------------VOITHITIKES SUNARTHSEIS TELIKOU KWDIKA------------------------------#   

def type_of_entity(entity):
    if isinstance(entity, Variable):
        return "var"
    elif isinstance(entity, Tempvar):
        return "tempvar"
    elif isinstance(entity, Argument):
        return "arg"
    elif isinstance(entity, Function):
        return "func"

def gnlvcode(x):
    global xml_code, scopes
    xml_code.append("lw $t0,-4($sp) \n\t\t")
    search_x = searchEntity(x)
    entity = search_x[0]
    scope_of_entity = search_x[1]
    i = (scope_level-1) - scope_of_entity.level
    for rep in range(1,i):
        xml_code.append("lw $t0,-4($t0) \n\t\t")
    xml_code.append("addi $t0,$t0,-" +str(entity.offset)+ " \n\t\t")
    
    
def loadvr(v,r):
    global xml_code
    if  v>= "0" and v<="9":
        xml_code.append("li " +r+ "," +v+ "\n\t\t")
    else:
        search_v = searchEntity(v)
        entity = search_v[0]
        scope_of_entity = search_v[1]
        type_ent = type_of_entity(entity)

        if scope_of_entity.level == 0 and scope_of_entity.level != scope_level-1:
            xml_code.append("lw " +r+ ",-" +str(entity.offset)+ "($s0) \n\t\t")
        elif scope_of_entity.level == scope_level-1:
            if type_ent=="var" or type_ent=="tempvar" or (type_ent=="arg" and entity.mode == "cv"): 
                xml_code.append("lw " +r+ ",-" +str(entity.offset)+ "($sp) \n\t\t")
            elif type_ent=="arg" and entity.mode == "ref":
                xml_code.append("lw $t0,-" +str(entity.offset)+ "($sp) \n\t\t")
                xml_code.append("lw " +r+ ",($t0) \n\t\t")
        else:
            if type_ent=="var" or (type_ent=="arg" and entity.mode == "cv"):
                gnlvcode(v)
                xml_code.append("lw " +r+ ",($t0) \n\t\t")
            elif type_ent=="arg" and entity.mode == "ref":
                gnlvcode(v)
                xml_code.append("lw $t0,($t0) \n\t\t")
                xml_code.append("lw " +r+ ",($t0) \n\t\t")
            
def storerv(r,v):
    global xml_code
    search_v = searchEntity(v)
    entity = search_v[0]
    scope_of_entity = search_v[1]
    type_ent = type_of_entity(entity)
    if scope_of_entity.level == 0 and scope_of_entity.level != scope_level-1:
        xml_code.append("sw " +r+ ",-" +str(entity.offset)+ "($s0) \n\t\t")
    elif scope_of_entity.level == scope_level-1:
        if type_ent=="var" or type_ent=="tempvar" or (type_ent=="arg" and entity.mode == "cv"): 
            xml_code.append("sw " +r+ ",-" +str(entity.offset)+ "($sp) \n\t\t")
        elif type_ent=="arg" and entity.mode == "ref":
            xml_code.append("lw $t0,-" +str(entity.offset)+ "($sp) \n\t\t")
            xml_code.append("sw " +r+ ",($t0) \n\t\t")
    else:
        if type_ent=="var" or (type_ent=="arg" and entity.mode == "cv"):
            gnlvcode(v)
            xml_code.append("sw " +r+ ",($t0) \n\t\t")
        elif type_ent=="arg" and entity.mode == "ref":
            gnlvcode(v)
            xml_code.append("lw $t0,($t0) \n\t\t")
            xml_code.append("sw " +r+ ",($t0) \n\t\t")
                
       

#---------------------------------------SYNTAKTIKOS ANALUTIS----------------------------------------#

def Syntax():
    global token
    token = lex()

    def program():
        global token
        if token.tokenString == "program": 
            token=lex()
            if token.tokenType == "identifier": 
                name = token.tokenString             #endiamesos kwdikas
                
                token=lex()
                
                addScope(name)                          #pinakas sumvolwn
                
                block(name, 1)               
                if token.tokenString == '.':
                    print("\n Compilation finished without any errors")
                else:
                    print("Error @ Line "+ str(line) + ": Possibility of main block ending but code still under it.")
                    quit()
            else: 
                print("Error @ Line " + str(token.lineNo) + " Program name expected, instead I found " +"'"+ str(token.tokenString) +"'")
                quit()
        else: 
            print("Error @ Line " + str(token.lineNo) + " The keyword 'program' was expected, instead I found " +"'"+ str(token.tokenString) +"'")
            quit()
    
    def block(name, main_flag):
        global offset, framelength_of_main,retflag,scopefd
        
        declarations()
        subprograms()
        
        genquad("begin_block",name,'_','_')                 #endiamesos kwdikas
        
        if main_flag == 0:
            func_entity = searchEntity(name)          #pinakas sumvolwn
            func_entity[0].startQuad = nextquad()
        
        statements()
        
        if main_flag == 1:
            genquad("halt",'_','_','_')
            
            if(retflag==1):
                print("Error:Main cannot contain a return value")   #simasiologiki analusi
                quit()
            
       
        else:
            func_entity = searchEntity(name)          #pinakas sumvolwn
            func_entity[0].framelength = offset
            
            
        genquad("end_block",name,'_','_')
        
        if len(scopes) == 1:
            framelength_of_main = offset

            
        #---------print--------#
        for scope in scopes:
            scopefd.write(scope.name + " " + str(scope.level)+"-> ")  
            s = scope.entities
            for i in s:
                is_func = isinstance(i, Function)
                is_arg = isinstance(i, Argument)
                if is_func:
                    scopefd.write(i.name + " " + str(i.startQuad) + " " + str(i.framelength)+" ")
                    scopefd.write(str(i.arguments)+" ")
                    scopefd.write(",")
                elif is_arg:
                    scopefd.write(i.name + " " + i.mode + " " + str(i.offset)+" ")
                    scopefd.write(",")
                else:
                    scopefd.write(i.name + " " + str(i.offset)+" ")
                    scopefd.write(",")
            scopefd.write("\n")
        scopefd.write("\n\n")                       
        #---------print--------#
        
        counter=0
        for x in scopes[len(scopes)-1].entities:                                                                                                     #simasiologiki analusi
            for i in scopes[len(scopes)-1].entities:
                if(x.name == i.name):
                    counter+=1
            if(counter>1):
                print("Error : Two entities(Variable,Argument,Procedure,Function) have the same name '"+x.name+"' while in the same scope")
                quit()
            else:
                counter=0
        
        int_to_xml()
        deleteScope()

                       
        
    def declarations():
        global token , scopes                                                                                                                               #simasiologiki analusi
        while token.tokenString == "declare":
            token=lex()
            varlist()
            if token.tokenString == ';':
                token=lex()
            else:
                print("Error @ Line " + str(token.lineNo) + " The delimeter ',' or ';' was expected")
                quit()
        
        
    def varlist():
        global token, offset
        if token.tokenType == "identifier": 
        
            name = token.tokenString
            addVarEntity(name, offset)             #pinakas sumvolwn
            offset += 4
            
            token=lex()
            while token.tokenString == ',':
                token=lex()
                if token.tokenType == "identifier":
                
                    name = token.tokenString
                    addVarEntity(name, offset)             #pinakas sumvolwn
                    offset += 4
                
                    token=lex()
                else:
                    print("Error @ Line " + str(token.lineNo) + " variable name was expected")
                    quit()
        else: 
            print("Error @ Line " + str(token.lineNo) + " variable name was expected after keyword delimeter")
            quit()
                
    def subprograms():
        global token
        global func_proc_exists
        while token.tokenString == "function" or token.tokenString == "procedure":
            func_proc_exists=1
            subprogram()
        
        counter=0
        for x in scopes[len(scopes)-1].entities:                                                                                                     #simasiologiki analusi
            for i in scopes[len(scopes)-1].entities:
                if(x.name == i.name and isinstance(i,Function) and isinstance(x,Function)):
                    counter+=1
            if(counter>1):
                print("Error @ Line " + str(token.lineNo) +": "+x.name+" was declared more than once as a function or procedure")
                quit()
            else:
                counter=0
        
        
    def subprogram():
        global token, offset, retflag,procedures
        if token.tokenString == "function":
            token=lex()
            
            if token.tokenType == "identifier":
            
                name = token.tokenString                                #endiamesos kwdikas
                
                addFuncEntity(name, 0, [], 0)
                addScope(name)                                          #pinakas sumvolwn
                last_offset = offset
                offset = 12
                
                token=lex()
                if token.tokenString == '(':
                    token=lex()
                    formalparlist()
                    if token.tokenString == ')':
                        token=lex()
                        
                        block(name, 0)
                        
                        offset = last_offset                             #pinakas sumvolwn
                        
                        if(retflag==1):
                            retflag=0
                        else:
                            print("Error:A function must contain at least one 'return' value @ function "+name)
                            quit()
                        
                    else:
                        print("Error @ Line " + str(token.lineNo) + " Group symbol ')' was expected")
                        quit()
                else:
                    print("Error @ Line " + str(token.lineNo) + " Group symbol '(' was expected")
                    quit()
            else:
                print("Error @ Line " + str(token.lineNo) + " function name was expected, instead I found " +"'"+ str(token.tokenString) +"'")
                quit()
        elif token.tokenString == "procedure":
            token=lex()
            if token.tokenType == "identifier": 
            
                name = token.tokenString                #endiamesos kwdikas
                
                procedures.append(name)                 #simasiologiki analusi
                
                addFuncEntity(name, 0, [], 0)
                addScope(name)                          #pinakas sumvolwn
                last_offset = offset
                offset=12
                
                token=lex()
                if token.tokenString == '(':
                    token=lex()
                    formalparlist()
                    if token.tokenString == ')':
                        token=lex()
                        
                        block(name, 0)
                        
                        offset = last_offset                             #pinakas sumvolwn
                        
                        if(retflag==1):
                            print("Error:A Procedure cannot contain a return value @ Procedure "+name)
                            quit()
                        
                    else:
                        print("Error @ Line " + str(token.lineNo) + " Group symbol ')' was expected")
                        quit()
                else:
                    print("Error @ Line " + str(token.lineNo) + " Group symbol '(' was expected")
                    quit()
            else:
                print("Error @ Line " + str(token.lineNo) + " procedure name was expected, instead I found " +"'"+ str(token.tokenString) +"'")
                quit()

        
        
    def formalparlist():
        global token
        if token.tokenString == ')':
            return
        else:
            formalparitem()
            while token.tokenString == ',':
                token=lex()
                formalparitem()
            
    def formalparitem():
        global token, offset
        if token.tokenString == "in":
            token=lex()
            if token.tokenType == "identifier":
            
                name = token.tokenString
                addArgEntity(name, "cv", offset)                #pinakas sumvolwn
                offset += 4
                addArgument("cv")
                            
                token=lex()
            else:
                print("Error @ Line " + str(token.lineNo) + " parameter name was expected")
                quit()
        elif token.tokenString=="inout":
            token=lex()
            if token.tokenType == "identifier":
            
                name = token.tokenString
                addArgEntity(name, "ref", offset)              #pinakas sumvolwn
                offset += 4
                addArgument("ref")
            
                token=lex()
            else:
                print("Error @ Line " + str(token.lineNo) + " parameter name was expected")
                quit()
        else:
            print("Error @ Line " + str(token.lineNo) + ": 'inout' or 'in' was expected" )
            quit()
            

    def statements():
        global token
        if token.tokenString == '{':
            token=lex()
            statement()
            while token.tokenString == ';':
                token=lex()
                statement()
            if token.tokenString !=';' and token.tokenString !='}':
                print("Error @ Line " + str(token.lineNo) + ": delimeter ';' was expected") 
                quit()
            elif token.tokenString == '}':
                token=lex()
            else:
                print("Error @ Line " + str(token.lineNo) + ": Group symbol '}' was expected")
                quit()
        else:
            statement()
            if token.tokenString == ';':
                token=lex()
            else:
                print("Error @ Line " + str(token.lineNo) + ": delimeter ';' was expected")
                quit()
        
    def statement():
        global token, retflag,scopes
        if token.tokenType == "identifier":
            ID = token.tokenString
            token=lex()
            
            existsflag=0
            for scope in reversed(scopes):
                for entity in scope.entities:
                    if entity.name == ID:
                        existsflag=1
                    
                if existsflag==1:
                    break
            if existsflag==0:
                    print("Error @ Line " + str(token.lineNo) + ": Variable,Procedure or Function '"+idplace+"' is undeclared")
                    quit()
                    
            assignStat(ID)
        elif token.tokenString == "if":
            token=lex()
            ifStat()                                           
        elif token.tokenString == "while":
            token=lex()
            whileStat()
        elif token.tokenString == "switchcase":
            token=lex()
            switchcaseStat()
        elif token.tokenString == "forcase":
            token=lex()
            forcaseStat()
        elif token.tokenString == "incase":
            token=lex()
            incaseStat()
        elif token.tokenString == "call":
            token=lex()
            callStat()
        elif token.tokenString == "return":
            token=lex()
            
            retflag=1                                                                   #simasiologiki analusi
            
            returnStat()
        elif token.tokenString == "input":
            token=lex()
            inputStat()
        elif token.tokenString == "print":
            token=lex()
            printStat()
        else:                                                                                              
            return
    
    def assignStat(ID):
        global token
        if token.tokenType=="assignment":
            token=lex()
            
            Eplace = expression()
            genquad(":=",Eplace,'_',ID)
            
        else:
            print("Error @ Line " + str(token.lineNo) + " Assignment symbol ':=' was expected")
            quit()
    
   
    def ifStat():
        global token
        if token.tokenString=='(':
            token=lex()
            
            B = condition()
            Btrue = B[0]
            Bfalse = B[1]
            
            if token.tokenString ==')':
                backpatch(Btrue,nextquad())
                
                token=lex()
                statements()
                
                ifList=makelist(nextquad())
                genquad("jump",'_','_','_')
                backpatch(Bfalse,nextquad())
                
                elsepart()

                backpatch(ifList,nextquad())
            else:
                print("Error @ Line " + str(token.lineNo) + " Group symbol ')' was expected")
                quit()
        else:
            print("Error @ Line " + str(token.lineNo) + " Group symbol '(' was expected")
            quit()
            
        tf = [Btrue,Bfalse]
        return tf

        
    def elsepart():
        global token
        if token.tokenString=="else":
            token=lex()
            statements()
    
    def whileStat():
        global token
        if token.tokenString=='(':
            token=lex()
            
            Bquad = nextquad()
            B = condition()
            Btrue = B[0] 
            Bfalse = B[1]
            
            if token.tokenString ==')':
            
                backpatch(Btrue, nextquad())
                
                token=lex()
                statements()
                
                genquad("jump",'_','_',Bquad)
                backpatch(Bfalse, nextquad())
                
            else:
                print("Error @ Line " + str(token.lineNo) + " Group symbol ')' was expected")
                quit()
        else:
            print("Error @ Line " + str(token.lineNo) + " Group symbol '(' was expected")
            quit()
            
        tf = [Btrue, Bfalse]
        return tf
    
    def switchcaseStat():
        global token
        
        exitlist = emptylist()
        
        while token.tokenString=="case":
            token=lex()
            
            if token.tokenString=='(':
                token=lex()
                
                cond = condition() 
                condTrue = cond[0]
                condFalse = cond[1]
                backpatch(condTrue, nextquad())
                
                if token.tokenString == ')':
                    token=lex()
                    statements()
                    
                    e = makelist(nextquad())
                    genquad("jump",'_','_','_')
                    exitlist = merge(exitlist,e)
                    backpatch(condFalse,nextquad())
                    
                else:
                    print("Error @ Line " + str(token.lineNo) + " Group symbol ')' was expected")
                    quit()
            else:
                print("Error @ Line " + str(token.lineNo) + " Group symbol '(' was expected")
                quit()
        
        if token.tokenString=="default":
            token=lex()
            statements()
            
            backpatch(exitlist,nextquad())
            
        else:
            print("Error @ Line " + str(token.lineNo) + " Keyword 'default' was expected")
            quit()
    
    def forcaseStat():
        global token
                
        p1Quad=nextquad()
        
        while token.tokenString=="case":
            token=lex()
            if token.tokenString=='(':
                token=lex()
                
                
                cond = condition()
                
                condTrue = cond[0]
                condFalse = cond[1]
                
                backpatch(condTrue, nextquad())
                        
                if token.tokenString == ')':
                    token=lex()
                    statements()
                    
                    genquad("jump",'_','_',p1Quad)
                    backpatch(condFalse,nextquad())
                    
                else:
                    print("Error @ Line " + str(token.lineNo) + " Group symbol ')' was expected")
                    quit()
            else:
                print("Error @ Line " + str(token.lineNo) + " Group symbol '(' was expected")
                quit()
        
        if token.tokenString=="default":
            token=lex()
            statements()
             
        else:
            print("Error @ Line " + str(token.lineNo) + " Keyword 'default' was expected")
            quit()
            
    def incaseStat():
        global token, offset
        
        w = nextemp()
        p1Quad = nextquad()
        genquad(":=",1,"_",w)
        
        addTempVarEntity(w,offset)                  #pinakas sumvolwn
        offset += 4
                         
        while token.tokenString=="case":
            token=lex()
            if token.tokenString=='(':
                token=lex()
                
                cond = condition() 
                condTrue = cond[0]
                condFalse = cond[1]
     
                
                backpatch(condTrue, nextquad())
                genquad(":=",0,"_",w)
                        
                if token.tokenString == ')':
                    token=lex()
                    statements()
                                       
                    backpatch(condFalse,nextquad())
                    
                else:
                    print("Error @ Line " + str(token.lineNo) + " Group symbol ')' was expected")
                    quit()
            else:
                print("Error @ Line " + str(token.lineNo) + " Group symbol '(' was expected")
                quit()
        
        genquad("=",w,0,p1Quad)
        
    def returnStat():
        global token
        if token.tokenString=='(':
            token=lex()
            
            Eplace = expression()
            
            if token.tokenString == ')':
                token=lex()
                
                genquad("retv",Eplace,'_','_')
                
            else:
                 print("Error @ Line " + str(token.lineNo) + " Group symbol ')' was expected")
                 quit()
        else:
            print("Error @ Line " + str(token.lineNo) + " Group symbol '(' was expected")
            quit()
            
    def callStat():
        global token
        if token.tokenType == "identifier":
        
            name = token.tokenString
            
            token=lex()
            if token.tokenString=='(':
                token=lex()
                actualparlist()
                if token.tokenString == ')':
                    token=lex()
                    
                    genquad("call",name,'_','_')
                    
                else:
                    print("Error @ Line " + str(token.lineNo) + " Group symbol ')' was expected")
                    quit()
            else:
                print("Error @ Line " + str(token.lineNo) + " Group symbol '(' was expected")
                quit()
        else:
            print("Error @ Line " + str(token.lineNo) + " Procedure name was expected")
            quit()
    
    def printStat():
        global token
        if token.tokenString=='(':
            token=lex()
            
            Eplace = expression()
            
            if token.tokenString==')':
                token=lex()
                
                genquad("out",Eplace,'_','_')
                
            else:
                print("Error @ Line " + str(token.lineNo) + ": Group symbol ')' was expected")
                quit()
            
        else:
            print("Error @ Line " + str(token.lineNo) + " Group symbol '(' was expected")
            quit()
    
    
    def inputStat():
        global token
        if token.tokenString=='(':
            token=lex()
            if token.tokenType=="identifier":
            
                ID = token.tokenString
            
                token=lex()
                if token.tokenString==')':
                    token=lex()
                    
                    genquad("inp",ID,'_','_')
                    
                else:
                    print("Error @ Line " + str(token.lineNo) + ": Group symbol ')' was expected")
                    quit()
            else:
                print("Error @ Line " + str(token.lineNo) + ": Identifier was expected")
                quit()
        else:
            print("Error @ Line " + str(token.lineNo) + " Group symbol '(' was expected")
            quit()
    
    def actualparlist():
        global token
                                                                                             
        recursion_temps=[]
        listofparams=[]                                                                                                                 #simasiologiki analusi

        if token.tokenString == ')':
            return 
        else:
            w = actualparitem()
            if(w[1]=="cv"):
                recursion_temps.append(["par",w[0],"CV",'_'])
                listofparams.append("cv")
            else:
                recursion_temps.append(["par",w[0],"REF",'_'])
                listofparams.append("ref")
                
            while token.tokenString==',':
                token=lex()
                w = actualparitem()
                if(w[1]=="cv"):
                    recursion_temps.append(["par",w[0],"CV",'_'])
                    listofparams.append("cv")
                else:
                    recursion_temps.append(["par",w[0],"REF",'_'])
                    listofparams.append("ref")
                    
            for x in recursion_temps:
                genquad("par",x[1],x[2],'_')
                
            return listofparams
    
    def actualparitem():
        global token
   
        if token.tokenString=="in":
            token=lex()
            
            Eplace = expression()
            return Eplace,"cv"

        elif token.tokenString=="inout":
            token=lex()
            if token.tokenType == "identifier":
            
                ID = token.tokenString
                token=lex()
                return ID,"ref"
            else:
                print("Error @ Line " + str(token.lineNo) + " Identifier was expected")
                quit()
        else:
            token=lex()
            print("Error @ Line " + str(token.lineNo) + ": 'inout' or 'in' was expected")
            quit()
        
    def condition():
        global token
        
        Q1 = boolterm()
        Btrue = Q1[0]
        Bfalse = Q1[1]
        
        while token.tokenString=="or":
        
            backpatch(Bfalse, nextquad())
            
            token=lex()
            
            Q2 = boolterm()
            Btrue = merge(Btrue, Q2[0])
            Bfalse = Q2[1]
            
        tf = [Btrue,Bfalse]
        return tf
    
    def boolterm():
        global token
        
        R1 = boolfactor()
        Qtrue = R1[0]
        Qfalse = R1[1]
        
        while token.tokenString == "and":
        
            backpatch(Qtrue, nextquad())
            
            token=lex()
            
            R2 = boolfactor()
            Qfalse = merge(Qfalse, R2[1])
            Qtrue = R2[0]
           
        tf = [Qtrue,Qfalse]
        return tf
             
    def boolfactor():
        global token
        if token.tokenString == "not":
            token=lex()
            if token.tokenString == '[':
                token=lex() 
                
                B = condition()
                
                if token.tokenString == ']':
                    token=lex()
                    
                    Rtrue = B[1]
                    Rfalse = B[0]
                    
                else:
                    print("Error @ Line " + str(token.lineNo) + " Group symbol ']' was expected")
                    quit()
                    
            else:
                print("Error @ Line " + str(token.lineNo) + " Group symbol '[' was expected")
                quit()
        elif token.tokenString == '[':
            token=lex()
            
            B = condition()
            
            if token.tokenString == ']':
                token=lex()
                
                Rtrue = B[0]
                Rfalse = B[1]
                
            else:
                print("Error @ Line " + str(token.lineNo) + " Group symbol ']' was expected")
                quit()
                    
        else:

            E1place=expression();
            
            if token.tokenType== "relOperator":
            
                relop = token.tokenString
                
                token=lex()
                
                E2place=expression()
                Rtrue = makelist(nextquad())
                genquad(relop,E1place,E2place,'_')
                Rfalse = makelist(nextquad())
                genquad("jump","_","_","_")
                
            else:
                print("Error @ Line " + str(token.lineNo) + " Relational operator was expected")
                quit()
                
        tf = [Rtrue,Rfalse]
        return tf
    
    def expression():
        global token, offset
        optional = optionalSign()
        
        T1place=term()
        
        if(optional==1):
            w = nextemp()
            genquad('-',0,T1place,w)
            T1place = w
            
            addTempVarEntity(w,offset)                  #pinakas sumvolwn
            offset += 4
        
        while token.tokenType=="addOperator":
        
            operator = token.tokenString
            
            token=lex()
            
            T2place =term()
            w = nextemp()
            genquad(operator,T1place,T2place,w)
            T1place = w
            
            addTempVarEntity(w,offset)                    #pinakas sumvolwn
            offset += 4
    
        Eplace = T1place
        return Eplace
    
    def term():
        global token, offset
        
        F1place = factor()
        
        while token.tokenType=="mulOperator":
        
            operator = token.tokenString
            
            token=lex()
            
            F2place = factor()
            w = nextemp()
            genquad(operator,F1place,F2place,w)
            F1place = w 
            
            addTempVarEntity(w,offset)                  #pinakas sumvolwn
            offset += 4
            
        Tplace = F1place 
        return Tplace
            
    
    def factor():
        global token,scopes
        if token.tokenType=="number":
        
            Fplace = token.tokenString
            
            token=lex()
        elif token.tokenString=='(':
            token=lex()
            
            Eplace=expression()
            
            if token.tokenString==')':
            
                Fplace = Eplace
                
                token=lex()
            else:
                print("Error @ Line " + str(token.lineNo) + ": Group symbol ')' was expected")
                quit()
        elif token.tokenType=="identifier":
        
            idplace = token.tokenString
            
            token=lex()
            
            Fplace = idtail(idplace)
            
            existsflag=0
            for scope in reversed(scopes):
                for entity in scope.entities:
                    if entity.name == idplace:
                        existsflag=1
                    
                if existsflag==1:
                    break
            if existsflag==0:
                    print("Error @ Line " + str(token.lineNo) + ": Variable,Procedure or Function '"+idplace+"' is undeclared")
                    quit()
        else:
            print("Error @ Line " + str(token.lineNo) + ": Identifier,'(' or number was expected but not found")
            quit()
            
        return Fplace
            
    def idtail(idplace):
        global token, offset,scopes
        
        global flag
        
        if token.tokenString == '(':
            token=lex()
            

                
            listofparams = actualparlist()                                                                                                              #simasiologiki analusi
            if token.tokenString == ')':
                token=lex()
                
                for x in scopes[len(scopes)-1].entities:                                                                                                     #simasiologiki analusi
                    if(x.name == idplace and isinstance(x,Function)):
                        if(len(listofparams)!=len(x.arguments)):
                            print("Error @ Line " + str(token.lineNo) + ": Function or Procedure "+x.name+" is called with more or less parameters than it actually has")
                            quit()
                            
                        for i in range(len(listofparams)-1):
                            if listofparams[i] == x.arguments[i]:
                                continue
                            else:
                                print("Error @ Line " + str(token.lineNo) + ": Function or Procedure "+x.name+" must be called with the right series of parameters")
                                quit()
 
                
                w = nextemp()
                
                addTempVarEntity(w,offset)                    #pinakas sumvolwn
                offset += 4
                
                genquad("par",w,"RET",'_')
                genquad("call",idplace,'_','_')
                return w
                
            else:
                print("Error @ Line " + str(token.lineNo) + " Group symbol ')' was expected")
                quit()
        
        return idplace
        
    def optionalSign():
        global token
        if token.tokenType == "addOperator":
            operator=token.tokenString
            token=lex()
            if(operator=='-'):
                return 1
        return 0
    
    
    
    program()
            
#-------------------------------------METATROPI INT KWDIKA SE C-------------------------------------#            

def int_to_c(filename):
    
    
    f = open(filename+".c","w")
    
    with open(filename+".int","r") as file:
        f.write("void main(){"+"\n")
        declare_list=[]
        final_list = []
        
        for line in file:
            list=[]
            for word in line.split():
                list.append(word)                                       #used to find which variables to declare
                
            if list[1]=="+":
                if list[4] not in declare_list:
                    declare_list.append(list[4])
            elif list[1]=="-":
                if list[4] not in declare_list:
                    declare_list.append(list[4])
            elif list[1]==":=":
                if list[4] not in declare_list:
                    declare_list.append(list[4])
            elif list[1]=="/":
                if list[4] not in declare_list:
                    declare_list.append(list[4])
            elif list[1]=="*":
                if list[4] not in declare_list:
                    declare_list.append(list[4])
                    
        final_list.append("\tint ")
        for i in range(len(declare_list)-1):
            final_list.append(declare_list[i] +",")
        final_list.append(declare_list[len(declare_list)-1])
        final_list.append("; \n\n")
        
        with open(filename+".int","r") as file:
            for line in file:
                list=[]
                for word in line.split():                                   #used to find the commands to write
                    list.append(word)

                if list[1]=="jump":
                    final_list.append("\t"+"L_"+list[0]+":""goto L_"+list[4]+";"+"/*["+list[1]+','+list[2]+','+list[3]+','+list[4]+"]*/"+"\n")
                    
                elif list[1]=="begin_block":
                    continue
                
                elif list[1]=="+":
                    final_list.append("\t"+"L_"+list[0]+":"+list[4]+"="+list[2]+"+"+list[3]+";"+"/*["+list[1]+','+list[2]+','+list[3]+','+list[4]+"]*/"+"\n")
                
                elif list[1]=="-":   
                    final_list.append("\t"+"L_"+list[0]+":"+list[4]+"="+list[2]+"-"+list[3]+";"+"/*["+list[1]+','+list[2]+','+list[3]+','+list[4]+"]*/"+"\n")
                    
                elif list[1]=="/":   
                    final_list.append("\t"+"L_"+list[0]+":"+list[4]+"="+list[2]+"/"+list[3]+";"+"/*["+list[1]+','+list[2]+','+list[3]+','+list[4]+"]*/"+"\n")
                
                elif list[1]=="*":   
                    final_list.append("\t"+"L_"+list[0]+":"+list[4]+"="+list[2]+"*"+list[3]+";"+"/*["+list[1]+','+list[2]+','+list[3]+','+list[4]+"]*/"+"\n")
                    
                elif list[1]=="<" or list[1]==">" or list[1]=="<=" or list[1]==">=":
                    final_list.append("\t"+"L_"+list[0]+":"+"if ("+list[2]+list[1]+list[3]+") "+"goto L_"+list[4]+";"+"/*["+list[1]+','+list[2]+','+list[3]+','+list[4]+"]*/"+"\n")
                
                elif list[1]=="=":
                    final_list.append("\t"+"L_"+list[0]+":"+"if ("+list[2]+"=="+list[3]+") "+"goto L_"+list[4]+";"+"/*["+list[1]+','+list[2]+','+list[3]+','+list[4]+"]*/"+"\n")
                
                elif list[1]==":=":   
                    final_list.append("\t"+"L_"+list[0]+":"+list[4]+"="+list[2]+";"+"/*["+list[1]+','+list[2]+','+list[3]+','+list[4]+"]*/"+"\n")
                    
                elif list[1]=="inp":   
                    final_list.append("\t"+"L_"+list[0]+":"+'scanf("%d",&'+list[2]+")"+";"+"/*["+list[1]+','+list[2]+','+list[3]+','+list[4]+"]*/"+"\n")
                  
                elif list[1]=="out":   
                    final_list.append("\t"+"L_"+list[0]+":"+'printf("%d",'+list[2]+")"+";"+"/*["+list[1]+','+list[2]+','+list[3]+','+list[4]+"]*/"+"\n")
        final_list.append("}")
        
        for i in final_list:
            f.write(i)

#-------------------------------------METATROPI INT KWDIKA SE XML-------------------------------------#
def int_to_xml():
    global xml_code,quads,pointer, labels_and_levels
    par_counter = 1
    flag_main = 0
    par_flag = 0
    
    if pointer == 0:
        xml_code.append("L0:     b Lmain \n")
       
    for i in range(pointer,len(quads)):

        if quads[i][0] < 10:
            if scope_level-1 == 0 and flag_main==0:
                xml_code.append("Lmain: \n")
                flag_main = 1
            xml_code.append("L" +str(quads[i][0])+ ":\t\t")
        else:
            if scope_level-1 == 0 and flag_main==0:
                xml_code.append("Lmain: \n")
                flag_main = 1
            xml_code.append("L" +str(quads[i][0])+ ":\t")
            
        if quads[i][1] == "begin_block":
            if scope_level-1> 0:
                xml_code.append("sw $ra,-0($sp) \n\t\t")
                labels_and_levels.append([quads[i][0],scope_level-1,quads[i][2]])
            else:
                xml_code.append("addi $sp,$sp," +str(framelength_of_main)+ " \n\t\t")
                xml_code.append("move $s0,$sp \n\t\t")
        elif quads[i][1] == "end_block":
            if scope_level-1> 0:
                xml_code.append("lw $ra,-0($sp) \n\t\t")
                xml_code.append("jr $ra \n\t\t")
        elif quads[i][1] == "jump":
            xml_code.append("b " + str(quads[i][4]))
        elif quads[i][1] == "<=" or quads[i][1] == ">=" or quads[i][1] == "<" or quads[i][1] == ">" or quads[i][1] == "><" or quads[i][1] == "=":
            loadvr(quads[i][2],"$t1")
            loadvr(quads[i][3],"$t2")
            if quads[i][1] == "<=":
                xml_code.append("ble $t1,$t2,"+ str(quads[i][4]) + " \n\t\t")
            elif quads[i][1] == ">=":
                xml_code.append("bge $t1,$t2,"+ str(quads[i][4]) + " \n\t\t")
            elif quads[i][1] == "<":
                xml_code.append("blt $t1,$t2,"+ str(quads[i][4]) + " \n\t\t")
            elif quads[i][1] == ">":
                xml_code.append("bgt $t1,$t2,"+ str(quads[i][4]) + " \n\t\t")
            elif quads[i][1] == "<>":                                                                                       
                xml_code.append("bne $t1,$t2,"+ str(quads[i][4]) + " \n\t\t")
            else:
                xml_code.append("beq $t1,$t2,"+ str(quads[i][4]) + " \n\t\t")
        elif quads[i][1] == ":=":
            loadvr(quads[i][2],"$t1")
            storerv("$t1",quads[i][4])
        elif quads[i][1] == "+" or quads[i][1] == "-" or quads[i][1] == "/" or quads[i][1] == "*":
            loadvr(quads[i][2],"$t1")
            loadvr(quads[i][3],"$t2")
            if quads[i][1] == "+":
                xml_code.append("add $t1,$t1,$t2 \n\t\t")
            elif quads[i][1] == "-":
                xml_code.append("sub $t1,$t1,$t2 \n\t\t")
            elif quads[i][1] == "*":
                xml_code.append("mul $t1,$t1,$t2 \n\t\t")
            else:
                xml_code.append("div $t1,$t1,$t2 \n\t\t")
                xml_code.append("div $t1,$t1,$t2 \n\t\t")
            storerv("$t1",quads[i][4])
        elif quads[i][1] == "out":
            xml_code.append("li $v0,10 \n\t\t")
            loadvr(quads[i][2],"$a0")
            xml_code.append("syscall \n\t\t")
        elif quads[i][1] == "in":
            xml_code.append("li $v0,5 \n\t\t")
            xml_code.append("syscall \n\t\t")
            loadvr("$v0",quads[i][2])
        elif quads[i][1] == "retv":
            loadvr(quads[i][2],"$t1")
            xml_code.append("lw $t0,-8($sp) \n\t\t")
            xml_code.append("sw $t1,($t0) \n\t\t")
        elif quads[i][1] == "par":
            if par_flag == 0:
                called_function = ''
                for c in range(i,len(quads)):
                    if quads[c][1] == "call":
                        called_function = quads[c][2]
                        break
                search_f = searchEntity(called_function)
                entity_f = search_f[0]
                xml_code.append("addi $fp,$sp," +str(entity_f.framelength)+ " \n\t\t")
                par_flag = 1
            
            x = quads[i][2]
            search_x = searchEntity(x)
            entity = search_x[0]
            
            if quads[i][3] == "CV":
                loadvr(x, "$t1")
                xml_code.append("sw $t1,-" +str(entity.offset)+ "($fp) \n\t\t")
            elif quads[i][3] == "REF":
                scope_of_entity_x = search_x[1]
                type_ent = type_of_entity(entity)
                if scope_of_entity_x.level == scope_level-1:
                    if type_ent=="var" or (type_ent=="arg" and entity.mode == "cv"): 
                        xml_code.append("addi $t0,$sp,-" +str(entity.offset)+ " \n\t\t")
                        xml_code.append("sw $t0,-" +str(entity.offset)+ "($fp) \n\t\t")
                    elif type_ent=="arg" and entity.mode == "ref": 
                        xml_code.append("lw $t0,-" +str(entity.offset)+ " \n\t\t")
                        xml_code.append("sw $t0,-" +str(entity.offset)+ "($fp) \n\t\t")
                else:
                    if type_ent=="var" or (type_ent=="arg" and entity.mode == "cv"):
                        gnlvcode(x)
                        xml_code.append("sw $t0,-" +str(entity.offset)+ "($fp) \n\t\t")
                    elif type_ent=="arg" and entity.mode == "ref":
                            gnlvcode(x)
                            xml_code.append("lw $t0,($t0) \n\t\t")
                            xml_code.append("sw $t0,-" +str(entity.offset)+ "($fp) \n\t\t")
            elif quads[i][3] == "RET":
                xml_code.append("addi $t0,$sp,-" +str(entity.offset)+ " \n\t\t")
                xml_code.append("sw $t0,-8($fp) \n\t\t")   
        elif quads[i][1] == "call":
            if par_flag == 0:
                called_function = ''
                for c in range(i,len(quads)):
                    if quads[c][1] == "call":
                        called_function = quads[c][2]
                        break
                search_f = searchEntity(called_function)
                entity_f = search_f[0]
                xml_code.append("addi $fp,$sp," +str(entity_f.framelength)+ " \n\t\t")
            else:
                par_flag = 0
            
            level_of_function = 0
            label = ''
            for l in labels_and_levels:
                if l[2] == quads[i][2]:
                    label = l[0]
                    level_of_function = l[1]
                    break
        
            c = quads[i][2]
            called = searchEntity(c)
            entity = called[0]
            scope_of_entity = called[1]
            
            if level_of_function == scope_level-1: 
                xml_code.append("lw $t0,-4($sp) \n\t\t")
                xml_code.append("sw $t0,-4($fp) \n\t\t")
            else:
                xml_code.append("sw $sp,-4($fp) \n\t\t")
          
            xml_code.append("addi $sp,$sp," +str(entity.framelength)+ "\n\t\t")
            xml_code.append("jal L" +str(label)+ "\n\t\t")
            xml_code.append("addi $sp,$sp,-" +str(entity.framelength)+ "\n\t\t")
                
        xml_code.append("\n")
        
    pointer = len(quads)
    
    
def xml_file(filename):

    f = open(filename+".xml", "w")
    for i in xml_code:
        f.write(i)
            
#-----------------------------------------------MAIN------------------------------------------------#
        
        
def main(argv):
    global filename
    global quads,scopefd
    filename = str(sys.argv[1])
    Syntax()
    
    filename = filename.replace('.ci', '')
    
    f = open(filename+".int", "w")
    
    xml_file(filename)
    
    for x in quads:
        for i in x:
            f.write(str(i)+" ")
        f.write("\n")
    f.close()
    if func_proc_exists==0:
        int_to_c(filename)
    
    scopefd.close()
    
if __name__ == "__main__":
    main(sys.argv[1:])
    