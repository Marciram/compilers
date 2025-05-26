from enum import Enum

"""
GRAMMAR

program        → statement*
statement      → declaration | assignment
declaration    → "let" IDENTIFIER "=" expression ";"
assignment     → IDENTIFIER "=" expression ";"
expression     → term ((PLUS | MINUS) term)*
term           → factor ((MUL | DIV) factor)*
factor         → INTEGER
               | IDENTIFIER
               | "(" expression ")"

"""

# Token types with explicit values
class TokenType(Enum):
    INTEGER = 1
    FLOAT = 2
    IDENTIFIER = 3
    PLUS = 4
    MINUS = 5
    MUL = 6
    DIV = 7
    ASSIGN = 8
    LPAREN = 9
    RPAREN = 10
    LBRACE = 11
    RBRACE = 12
    SEMICOLON = 13
    LET = 14
    EOF = 15

# Token structure with position information
class Token:
    def __init__(self, type, value=None, line=None, column=None):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type.name}, {self.value}, line={self.line}, col={self.column})"

# AST Node Classes
class ASTNode:
    pass

class Program(ASTNode):
    def __init__(self, statements):
        self.statements = statements

    def __repr__(self):
        return f"Program({self.statements})"

class VarDecl(ASTNode):
    def __init__(self, identifier, initializer):
        self.identifier = identifier
        self.initializer = initializer

    def __repr__(self):
        return f"VarDecl({self.identifier}, {self.initializer})"

class Assignment(ASTNode):
    def __init__(self, identifier, value):
        self.identifier = identifier
        self.value = value

    def __repr__(self):
        return f"Assignment({self.identifier}, {self.value})"

class BinOp(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def __repr__(self):
        return f"BinOp({self.left}, {self.op.type.name}, {self.right})"

class Num(ASTNode):
    def __init__(self, token):
        self.token = token
        self.value = token.value

    def __repr__(self):
        return f"Num({self.value})"

class Var(ASTNode):
    def __init__(self, token):
        self.token = token
        self.value = token.value

    def __repr__(self):
        return f"Var({self.value})"

# Parser with enhanced error handling
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token = self.tokens[0]
        self.pos = 0

    def error(self, expected=None):
        if expected:
            msg = f"Syntax error at line {self.current_token.line}, column {self.current_token.column}: " \
                  f"Expected {expected}, got {self.current_token.type.name}"
        else:
            msg = f"Syntax error at line {self.current_token.line}, column {self.current_token.column}: " \
                  f"Unexpected token {self.current_token.type.name}"
        raise Exception(msg)

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.pos += 1
            if self.pos < len(self.tokens):
                self.current_token = self.tokens[self.pos]
            else:
                self.current_token = Token(TokenType.EOF)
        else:
            self.error(expected=token_type.name)

    def factor(self):
        token = self.current_token
        if token.type == TokenType.INTEGER or token.type == TokenType.FLOAT:
            self.eat(token.type)
            return Num(token)
        elif token.type == TokenType.IDENTIFIER:
            self.eat(TokenType.IDENTIFIER)
            return Var(token)
        elif token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            node = self.expr()
            self.eat(TokenType.RPAREN)
            return node
        else:
            self.error(expected="number, identifier, or '('")

    def term(self):
        node = self.factor()

        while self.current_token.type in (TokenType.MUL, TokenType.DIV):
            token = self.current_token
            self.eat(token.type)
            node = BinOp(left=node, op=token, right=self.factor())

        return node

    def expr(self):
        node = self.term()

        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            token = self.current_token
            self.eat(token.type)
            node = BinOp(left=node, op=token, right=self.term())

        return node

    def assignment(self):
        identifier = self.current_token.value
        self.eat(TokenType.IDENTIFIER)
        self.eat(TokenType.ASSIGN)
        value = self.expr()
        return Assignment(identifier, value)

    def var_decl(self):
        self.eat(TokenType.LET)
        identifier = self.current_token.value
        self.eat(TokenType.IDENTIFIER)
        self.eat(TokenType.ASSIGN)
        initializer = self.expr()
        return VarDecl(identifier, initializer)

    def statement(self):
        if self.current_token.type == TokenType.LET:
            return self.var_decl()
        elif self.current_token.type == TokenType.IDENTIFIER and \
             len(self.tokens) > self.pos + 1 and \
             self.tokens[self.pos + 1].type == TokenType.ASSIGN:
            return self.assignment()
        else:
            return self.expr()

    def parse(self):
        statements = []
        while self.current_token.type != TokenType.EOF:
            statements.append(self.statement())
            if self.current_token.type == TokenType.SEMICOLON:
                self.eat(TokenType.SEMICOLON)
        return Program(statements)

if __name__ == "__main__":
    # Sample token stream for: let x = 2 + 3; x = x * 4
    tokens = [
        Token(TokenType.LET, line=1, column=1),
        Token(TokenType.IDENTIFIER, "x", line=1, column=5),
        Token(TokenType.ASSIGN, line=1, column=7),
        Token(TokenType.INTEGER, 2, line=1, column=9),
        Token(TokenType.PLUS, line=1, column=11),
        Token(TokenType.INTEGER, 3, line=1, column=13),
        Token(TokenType.SEMICOLON, line=1, column=14),
        Token(TokenType.IDENTIFIER, "x", line=1, column=16),
        Token(TokenType.ASSIGN, line=1, column=18),
        Token(TokenType.IDENTIFIER, "x", line=1, column=20),
        Token(TokenType.MUL, line=1, column=22),
        Token(TokenType.INTEGER, 4, line=1, column=24),
        Token(TokenType.EOF, line=1, column=25)
    ]

    try:
        parser = Parser(tokens)
        ast = parser.parse()
        print(ast)
    except Exception as e:
        print(f"Error: {e}")