import sys
import os
sys.path.append(os.path.abspath(os.path.join("AFD/AFN")))
from BuilderEnum import BuilderEnum
import re

def find_all_positions(string, substring):
    res = [i for i in range(len(string)) if string.startswith(substring, i)]
    return res
"""
Identifies operands for + - and ..
"""

def get_literal(string):
    counter = 0
    toReturn = ''
    char = string[0]
    quoteCounter = 0
    while quoteCounter < 2:
        try:
            char = string[counter]
        except:
            print('Error, no ending of string literal')
            break
        if char == '"' or char == "'":
            quoteCounter += 1 
        toReturn += char
        counter += 1
    return toReturn, counter

def operands_identifier(value):
    count = 0
    
    operators = ["+", "-", '..']
    toBeIdentified = []
    word = ""
    string = ""
    skip = 0
    for i in range(len(value)-1):
        char = value[i]
        
        if skip != 0:
            count = 0
            skip -= 1
            continue


        if char == '"' or char == "'":
            count += 1
            if count % 2 != 0: 
                val, skip = get_literal(value[i:])
                string += val
                skip -= 1
    
        
            
        if char != "." and char not in operators and char != " " and string == "":
            word += char
            resta = len(value) - 1 - i
            if resta == 1:
                word += value[-1]
                toBeIdentified.append(word)
                word = ""

        if char in operators and count % 2 == 0:
            toBeIdentified.append(char)
            if string != "" and string != '"':
                toBeIdentified.append(string)
                string = ""
            
            if word != "" and word != '"':
                resta = len(value) - 1 - i
                if resta == 0:
                    word += value[-1]
                    toBeIdentified.append(word)
                    word = ""
                else:
                    toBeIdentified.append(word)
                    word = ""

        elif char == '.' and value[i+1] == '.':
            toBeIdentified.append('..')
            if string != "" and string != '"':
                
                toBeIdentified.append(string)
                string = ""
            if word != "" and word != '"':
                resta = len(value) - 1 - i
                if resta == 0:
                    word += value[-1]
                    toBeIdentified.append(word)
                    word = ""
                else:
                    toBeIdentified.append(word)
                    word = ""
            
            
            
            word = ""
            string = ""
        
    
    if word != "" and word != '"':
        toBeIdentified.append(word)
    if string != "" and word != '"':
        toBeIdentified.append(string)

    if len(toBeIdentified) == 0:
        toBeIdentified.append(value)

    
        
    return toBeIdentified


def operands_identifier_v2(value):
    inOp = False
    operand = ""
    operator = ""
    start_op = ["{", "[", "("]
    close_op = ["}", "]", ")"]
    count = 0
    toBeIdentified = []
    for char in value:
        #agregamos primer operador 
        if char == '"':
            count += 1
        if char in start_op and count % 2 == 0:
            inOp = True

            if operand != "":
                
                toBeIdentified.append(operand)
                operand = ""

            
            operator = char
            toBeIdentified.append(operator)
            operator = ""

            

        elif char in close_op and count % 2 == 0:
            inOp = False
            if operand != "":
                
                toBeIdentified.append(operand)
                operand = ""
            
            operator = char
            toBeIdentified.append(operator)
            operator = ""
        else:
            inOp = False
        if not inOp and char and char not in close_op and char !=" ":
            operand += char

        elif not inOp and char and char != " " and count % 2 != 0:
            operand += char

        if operand == "EXCEPT":
            toBeIdentified.append(operand)
            operand = ""
    if len(operand) > 0:
        toBeIdentified.append(operand)
    return toBeIdentified


"""
Given a string like abc -> (a|b|c)
"""
def to_regex(string, case):
    if case == 1:
        
        sentence = ""
        quotes = ["'", '"']
        notToAdd = [")", "(", BuilderEnum.OR.value, BuilderEnum.CONCAT.value, '"', "'"]
        counter = 0 
        for i in range(len(string) - 1):
            char = string[i]
            sentence += string[i]
            if char in quotes:
                counter += 1
            if counter % 2 == 0 and counter > 0 and char in quotes:
                sentence += BuilderEnum.OR.value
            if string[i+1] not in notToAdd and string[i] not in notToAdd:
                
                sentence += BuilderEnum.OR.value
                
        
        sentence += string[-1]

    elif case == 2:
        sentence = ""
        for i in range(len(string)):
            sentence += string[i]
            #no agrega ni al ultimo ni al primer valor
            if i != 0 and len(string) - i > 2:
                sentence += BuilderEnum.CONCAT.value

    elif case == 3:
        
        sentence = ""
        notToAdd = [BuilderEnum.OR.value, BuilderEnum.CONCAT.value, '"']
        for i in range(len(string) - 1):
            sentence += string[i]
            if string[i+1] not in notToAdd and string[i] not in notToAdd:
                
                sentence += BuilderEnum.CONCAT.value

        sentence += string[-1]
                
            

    return sentence

"""
Identifies if we are given a variable, it will replace that value
x = 'ola' -> 'ola'
"""
def identify_char(chars, diction, isTokens):
    keys = diction.keys()
    for key in keys:
        if chars == key:
            return diction[key]

    #si posiciones esta vacia, es un operador. Si no, es un string que hay que a|b|c.. 


    if chars.find("CHR(") > -1:
        chars = chr_interpreter(chars)
    else:

        positions = find_all_positions(chars, '"')
        if len(positions) > 0 and isTokens:
            chars = to_regex(chars, 3)

        elif len(positions) > 0 and not isTokens:
            chars = to_regex(chars, 1)
        
    return chars
    

def chr_interpreter(word):
    substring = "\d+"
    startPos = []
    endPos = []
    numbArr = []
    for m in re.finditer(substring, word):
        startPos.append(m.start())
        endPos.append(m.end())
    
    for i in range(len(startPos)):
        try:
            numbArr.append(int(word[startPos[i]:endPos[i]]))
        except ValueError:
            print("Incorrect grammar for CHR() expr")

    if len(numbArr) <= 1:
        try:
            numb = int(numbArr[0])
            if numb == 148:
                numb = 32
        except ValueError:
            print("Incorrect grammar for CHR() expr") 

        return chr(numb)

    else:
        resta = numbArr[-1] - numbArr[0]
        answer = []
        for i in range(1,resta):
            if numbArr[0] + i == 32:
                continue
            else:
                answer.append(numbArr[0] + i)
        stringAns = ""
        for number in answer:
            a = chr(number)
            stringAns += a

        return stringAns

"""
Here we evaluate strings that contain  op + op2. We evaluate and return a string 'abc'
INPUT: array of operands
OUTPUT: sentence already processed
"""
def evaluate_characters(array, mode, isTokens):
    operations = ["+", "-", "{", "[", ".."]

    stack = []
    toBeDone = []
    sentence = ""
    result = ""
    for operator in array:
        if operator not in operations:
            res = identify_char(operator, mode, isTokens)
            res.replace('"', "")
            stack.append(res)
                
        else:   
            toBeDone.append(operator)
        
    #si es unitario, solo expulsamos lo que procesamos
    if len(toBeDone) == 0:
        return stack.pop()

    while len(toBeDone) > 0:
        sentence = ""
        op = toBeDone.pop(0).strip()
        
        
        if op == "-":
            first = stack.pop(0).strip().replace('"', "")
            second = stack.pop(0).strip().replace('"', "")

            sentence += first
            firstSet = set(first)
            secondSet = set(second)

            sentence = firstSet - secondSet
            sentence = ''.join(sentence)
            stack.insert(0, sentence)
            
        elif op == "+": 
            first = stack.pop(0).strip().replace('"', "")
            second = stack.pop(0).strip().replace('"', "")
            sentence += "("
            sentence += first
            sentence += ")"
            sentence += BuilderEnum.CONCAT.value
            sentence += "("
            sentence += second
            sentence += ")"
            stack.insert(0,sentence)

        elif op == "..":
            first = stack.pop(0).replace('"', "")
            second = stack.pop(0).replace('"', "")
            sentence += "(" + get_alphabet_set(first, second) + ")"
            stack.insert(0, sentence)
            

        elif op == "{":
            next_op = stack.pop(0)
            #jala todo lo que este dentro
            while next_op != "}":
                sentence += "(" + next_op +")"
                next_op = stack.pop(0)

            sentence += BuilderEnum.KLEENE.value

            stack.insert(0, sentence)
        elif op == "[":
            next_op = stack.pop(0)
            while next_op != "]":
                sentence += "(" + next_op +")"
                next_op = stack.pop(0)
            try:
                next_op = stack.pop(0)    
            except IndexError:
                next_op = "&"

            sentence += BuilderEnum.OR.value
            sentence += next_op

            stack.insert(0, sentence)

    
    

        

    
    #si queda algo son concat

    while len(stack) > 1:
        sentence = ""
        sentence += stack.pop(0)
        sentence += BuilderEnum.CONCAT.value
        sentence += "("
        sentence += stack.pop(0)
        sentence += ")"

        stack.insert(0, sentence)


    return stack.pop(0)


def get_alphabet_set(initial, final):
    if initial.islower():
        alpha = "abcdefghijklmnopqrstuvwxyz"
    else:
        alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    alpha = list(alpha)
    toReturn = ""
    counter = 0
    for i in range(len(alpha)):
        if initial == alpha[i]:
            x = alpha[i]
            counter = i
            
            for j in range(counter, len(alpha)):
                if x != final:
                    x = alpha[j]
                    toReturn += alpha[j]
                else:
                    break

            break
        
    return toReturn
                