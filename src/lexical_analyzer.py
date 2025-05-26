"""
MARIA RAMIREZ ZAVALA A01562798
5/72025
Lexical Analyzer Script 

This script reads a source code file, processes it to identify and categorize lexical tokens,
and outputs the results in JSON format. It handles:
- Skipping comments (both single-line and multi-line)
- Identifying keywords, identifiers, numbers, operators, and delimiters
- Generating structured token output with type information
"""

import re
from typing import List
import os
import json


def read_text_file(file_path: str, mode: str = 'r', encoding: str = 'utf-8') -> List[List[str]]:
    """
    Reads and tokenizes a text file, skipping comments and empty lines.
    
    Args:
        file_path: Path to the input file
        mode: File opening mode (default 'r')
        encoding: File encoding (default 'utf-8')
    
    Returns:
        A list of lines, each containing a list of tokens
        
    Raises:
        FileNotFoundError: If the specified file doesn't exist
    """
    textLines = []  # Stores the final tokenized lines
    isOnAComment = False  # Flag for multi-line comment tracking
    
    try:
        with open(file_path, mode, encoding=encoding) as file:
            # Process each line in the file
            for line in file:
                # Skip if we're inside a multi-line comment block
                if isOnAComment:
                    # Check if this line contains the end of the comment
                    if re.search(r"\*/", line):
                        isOnAComment = False
                    continue
                
                # Skip empty lines (whitespace only)
                if line.strip() == "":
                    continue
                
                # Skip single-line comments (// style)
                if re.match(r"^\s*\/\/.*", line): 
                    continue
                
                # Handle start of multi-line comments (/* style)
                if re.match(r"^\s*\/\*", line):
                    # Check if comment ends on same line
                    if not re.search(r"\*/", line):
                        isOnAComment = True
                    continue
                
                # Process the line to separate tokens
                tokens = []
                line_text = line.strip()  # Remove leading/trailing whitespace
                
                # Regex pattern to match:
                # - Floating point numbers (e.g., 3.14)
                # - Integers (e.g., 42)
                # - Identifiers (e.g., variable_name)
                # - Special characters (operators and delimiters)
                pattern = r'([0-9]+\.[0-9]+|[0-9]+|[a-zA-Z_][a-zA-Z0-9_]*|[;:,\(\)\{\}\[\]<>=\+\-\*/])'
                
                # Find all tokens in the line
                matches = list(re.finditer(pattern, line_text))
                
                # Process each matched token
                for match in matches:
                    token = match.group(0)
                    
                    # Handle cases where tokens might be incorrectly concatenated:
                    # Case 1: When a special character follows another token (e.g., '42;')
                    if len(token) > 1 and token[-1] in ';:,(){}[]<>=+-*/':
                        tokens.append(token[:-1])  # Add the main token
                        tokens.append(token[-1])  # Add the special character
                    
                    # Case 2: When a special character precedes another token (e.g., '(x')
                    elif len(token) > 1 and token[0] in ';:,(){}[]<>=+-*/':
                        tokens.append(token[0])    # Add the special character
                        tokens.append(token[1:])   # Add the remaining token
                    
                    # Normal case: add the token as-is
                    else:
                        tokens.append(token)
                
                # Add non-empty token lists to our results
                if tokens:
                    textLines.append(tokens)
                
    except FileNotFoundError:
        raise FileNotFoundError(f"The file '{file_path}' was not found")
    
    return textLines


def categorize_tokens(array: List[List[str]]) -> List[dict]:
    """
    Categorizes tokens into lexical categories and generates JSON output.
    
    Args:
        array: List of tokenized lines from read_text_file()
    
    Returns:
        List of dictionaries containing token information with:
        - id: Unique identifier
        - content: The token text
        - type: Token category
    """
    # Define token patterns and categories
    tokenDefinitions = {
        'identifier': re.compile(r"^[a-zA-Z][a-zA-Z0-9_]*$"),  # Variable/function names
        'number': re.compile(r"^\d+$"),                        # Integer numbers
        'float': re.compile(r"^\d+\.\d+$"),                     # Floating point numbers
        'keyword': {"if", "else", "while", "for", "return", "int", "float", "char"},  
        'operator': {"+", "-", "*", "/", "%", "**", "//", "="},
        'delimiters': {"(", ")", "{", "}", "[", "]", ",", ";"}
    }

    # Initialize storage for each token category
    listOfTokens = ['identifier', 'number', 'keyword', 'operator', 'delimiters']
    tokens = {category: set() for category in listOfTokens}

    print("Input array:", array)  # Debug output
    
    # Prepare JSON output structure
    type = ''       # Token category
    id = 0          # Unique token identifier
    json_token = {} # Individual token data
    json_tokens = [] # Complete token list
    
    # Process each token in the input
    for line in array:
        for lexeme in line:
            print("\nProcessing lexeme:", lexeme)  # Debug output
            
            # Determine token category
            if lexeme in tokenDefinitions['keyword']:
                tokens['keyword'].add(lexeme)
                type = 'keyword'                
            elif lexeme in tokenDefinitions['operator']:
                tokens['operator'].add(lexeme)
                type = 'operator'   
            elif lexeme in tokenDefinitions['delimiters']:
                tokens['delimiters'].add(lexeme)
                type = 'delimiters'
            elif tokenDefinitions['number'].fullmatch(lexeme):
                tokens['number'].add(lexeme)
                type = 'number'
            elif tokenDefinitions['identifier'].fullmatch(lexeme):
                tokens['identifier'].add(lexeme)
                type = 'identifier'
            else:
                print("not identified")  # Debug output
                type = 'not identified'
            
            # Create token entry for JSON output
            json_token = {
                "id": id,
                "content": lexeme,
                "type": type               
            }
            json_tokens.append(json_token)
            id += 1  # Increment unique ID
    
    print(tokens)  # Debug output: show categorized tokens

    return json_tokens


def convert_json(json_file_name: str, data: List[dict]) -> None:
    """
    Saves token data to a JSON file.
    
    Args:
        json_file_name: Path to output JSON file
        data: Token data to serialize
    """
    with open(json_file_name, "w") as json_file:
        json.dump(data, json_file, indent=4)  # Write with pretty-printing


if __name__ == "__main__":
    """
    Main execution block when run as a script.
    Processes code.txt in the script's directory and outputs to tokens.json.
    """
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define input and output file paths
    file_path = os.path.join(script_dir, 'code_simple.txt')    
    file_path_json = os.path.join(script_dir, 'tokens_simple.json')    
    
    try:
        # Execute the tokenization pipeline
        tokens = read_text_file(file_path)
        result = categorize_tokens(tokens)
        convert_json(file_path_json, result)

    except FileNotFoundError as e:
        # Handle missing input file
        print(f"Error: {e}")
        print(f"Please make sure 'code.txt' exists in: {script_dir}")