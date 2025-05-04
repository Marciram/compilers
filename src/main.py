import re
from typing import List

class Token:
    def __init__(self, type_: str, value: any):
        self.type = type_
        self.value = value
        
    def __repr__(self):
        return f"Token(type='{self.type}', value={repr(self.value)})"

class Lexer:
    def __init__(self, source_code: str):
        self.tokens: List[Token] = []    

def read_text_file(file_path, mode='r', encoding='utf-8'):
    """
    Reads a text file and returns its content.
    
    Parameters:
        file_path (str): Path to the text file
        mode (str): File opening mode 'r' for read
        encoding (str): Text encoding (default is 'utf-8')
    
    Returns:
        matrix: Content of the file
    """
    textLines = []
    isOnAComment = False
    
    try:
        with open(file_path, 'r', encoding=encoding) as file:
            for line in file:
                if isOnAComment:
                    if re.fullmatch(r"[\s\S]*?\*/", line):
                        isOnAComment = False
                        continue                            
                    else: 
                        continue
                    
                if line == "":
                    continue
                    
                if re.fullmatch(r"\/\/.*", line): 
                    continue
                
                if re.fullmatch(r"\/\*[\s\S]*", line):
                    isOnAComment = True
                    continue
                textLines.append(line.strip().split())
                
    except FileNotFoundError:
        raise FileNotFoundError(f"The file '{file_path}' was not found")
    
    return textLines


string = "123 hola if / hola 8"
array = string.split()

tokenDefinitions = {
    'identifier': re.compile(r"^[a-zA-Z]+$"),  
    'number': re.compile(r"^\d+$"),       
    'keyword': {"if", "else", "while", "for", "return", "int", "float", "char"},  
    'operator': {"+", "-", "*", "/", "%", "**", "//"} ,
    'comment': re.compile
}
listOfTokens = ['identifier','number', 'keyword', 'operator']
tokens = {category: set() for category in listOfTokens}

print("Input array:", array)

for lexeme in array:
    print("\nProcessing lexeme:", lexeme)
    
    if lexeme in tokenDefinitions['keyword']:
        tokens['keyword'].add(lexeme)
    elif lexeme in tokenDefinitions['operator']:
        tokens['operator'].add(lexeme)
    elif tokenDefinitions['number'].fullmatch(lexeme):
        tokens['number'].add(lexeme)
    elif tokenDefinitions['identifier'].fullmatch(lexeme):
        tokens['identifier'].add(lexeme)
    else:
        print("not identified")

print(tokens)
