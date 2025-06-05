import unittest
from enum import Enum
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root)) 

from src.sintax_analyzer import TokenType, Token, Program, VarDecl, Assignment, BinOp, Num, Var, Parser

class TestTokenType(unittest.TestCase):
    def test_token_type_values(self):
        self.assertEqual(TokenType.INTEGER.value, 1)
        self.assertEqual(TokenType.FLOAT.value, 2)
        self.assertEqual(TokenType.IDENTIFIER.value, 3)
        self.assertEqual(TokenType.PLUS.value, 4)
        self.assertEqual(TokenType.MINUS.value, 5)
        self.assertEqual(TokenType.MUL.value, 6)
        self.assertEqual(TokenType.DIV.value, 7)
        self.assertEqual(TokenType.ASSIGN.value, 8)
        self.assertEqual(TokenType.LPAREN.value, 9)
        self.assertEqual(TokenType.RPAREN.value, 10)
        self.assertEqual(TokenType.LBRACE.value, 11)
        self.assertEqual(TokenType.RBRACE.value, 12)
        self.assertEqual(TokenType.SEMICOLON.value, 13)
        self.assertEqual(TokenType.LET.value, 14)
        self.assertEqual(TokenType.EOF.value, 15)

class TestToken(unittest.TestCase):
    def test_token_creation(self):
        token = Token(TokenType.INTEGER, 42, line=1, column=5)
        self.assertEqual(token.type, TokenType.INTEGER)
        self.assertEqual(token.value, 42)
        self.assertEqual(token.line, 1)
        self.assertEqual(token.column, 5)
    
    def test_token_repr(self):
        token = Token(TokenType.PLUS, '+', line=2, column=3)
        self.assertEqual(repr(token), "Token(PLUS, +, line=2, col=3)")

class TestASTNodes(unittest.TestCase):
    def test_num_node(self):
        token = Token(TokenType.INTEGER, 42)
        num = Num(token)
        self.assertEqual(num.value, 42)
        self.assertEqual(repr(num), "Num(42)")
    
    def test_var_node(self):
        token = Token(TokenType.IDENTIFIER, "x")
        var = Var(token)
        self.assertEqual(var.value, "x")
        self.assertEqual(repr(var), "Var(x)")
    
    def test_binop_node(self):
        left = Num(Token(TokenType.INTEGER, 2))
        right = Num(Token(TokenType.INTEGER, 3))
        op = Token(TokenType.PLUS)
        binop = BinOp(left, op, right)
        self.assertEqual(binop.left, left)
        self.assertEqual(binop.op, op)
        self.assertEqual(binop.right, right)
        self.assertEqual(repr(binop), "BinOp(Num(2), PLUS, Num(3))")
    
    def test_var_decl_node(self):
        initializer = Num(Token(TokenType.INTEGER, 5))
        var_decl = VarDecl("x", initializer)
        self.assertEqual(var_decl.identifier, "x")
        self.assertEqual(var_decl.initializer, initializer)
        self.assertEqual(repr(var_decl), "VarDecl(x, Num(5))")
    
    def test_assignment_node(self):
        value = Num(Token(TokenType.INTEGER, 10))
        assignment = Assignment("y", value)
        self.assertEqual(assignment.identifier, "y")
        self.assertEqual(assignment.value, value)
        self.assertEqual(repr(assignment), "Assignment(y, Num(10))")
    
    def test_program_node(self):
        stmt1 = VarDecl("a", Num(Token(TokenType.INTEGER, 1)))
        stmt2 = Assignment("a", Num(Token(TokenType.INTEGER, 2)))
        program = Program([stmt1, stmt2])
        self.assertEqual(len(program.statements), 2)
        self.assertEqual(repr(program), "Program([VarDecl(a, Num(1)), Assignment(a, Num(2))])")

class TestParser(unittest.TestCase):
    def create_parser(self, token_list):
        tokens = token_list + [Token(TokenType.EOF)]
        return Parser(tokens)
    
    def test_parse_integer(self):
        tokens = [Token(TokenType.INTEGER, 42)]
        parser = self.create_parser(tokens)
        ast = parser.parse()
        self.assertIsInstance(ast, Program)
        self.assertEqual(len(ast.statements), 1)
        self.assertIsInstance(ast.statements[0], Num)
        self.assertEqual(ast.statements[0].value, 42)
    
    def test_parse_float(self):
        tokens = [Token(TokenType.FLOAT, 3.14)]
        parser = self.create_parser(tokens)
        ast = parser.parse()
        self.assertIsInstance(ast.statements[0], Num)
        self.assertEqual(ast.statements[0].value, 3.14)
    
    def test_parse_identifier(self):
        tokens = [Token(TokenType.IDENTIFIER, "x")]
        parser = self.create_parser(tokens)
        ast = parser.parse()
        self.assertIsInstance(ast.statements[0], Var)
        self.assertEqual(ast.statements[0].value, "x")
    
    def test_parse_simple_addition(self):
        tokens = [
            Token(TokenType.INTEGER, 2),
            Token(TokenType.PLUS),
            Token(TokenType.INTEGER, 3)
        ]
        parser = self.create_parser(tokens)
        ast = parser.parse()
        binop = ast.statements[0]
        self.assertIsInstance(binop, BinOp)
        self.assertEqual(binop.op.type, TokenType.PLUS)
        self.assertIsInstance(binop.left, Num)
        self.assertIsInstance(binop.right, Num)
    
    def test_parse_expression_with_precedence(self):
        tokens = [
            Token(TokenType.INTEGER, 2),
            Token(TokenType.PLUS),
            Token(TokenType.INTEGER, 3),
            Token(TokenType.MUL),
            Token(TokenType.INTEGER, 4)
        ]
        parser = self.create_parser(tokens)
        ast = parser.parse()
        # Should be 2 + (3 * 4)
        top_binop = ast.statements[0]
        self.assertEqual(top_binop.op.type, TokenType.PLUS)
        self.assertIsInstance(top_binop.right, BinOp)
        self.assertEqual(top_binop.right.op.type, TokenType.MUL)
    
    def test_parse_parentheses(self):
        tokens = [
            Token(TokenType.LPAREN),
            Token(TokenType.INTEGER, 2),
            Token(TokenType.PLUS),
            Token(TokenType.INTEGER, 3),
            Token(TokenType.RPAREN),
            Token(TokenType.MUL),
            Token(TokenType.INTEGER, 4)
        ]
        parser = self.create_parser(tokens)
        ast = parser.parse()
        # Should be (2 + 3) * 4
        top_binop = ast.statements[0]
        self.assertEqual(top_binop.op.type, TokenType.MUL)
        self.assertIsInstance(top_binop.left, BinOp)
        self.assertEqual(top_binop.left.op.type, TokenType.PLUS)
    
    def test_parse_var_declaration(self):
        tokens = [
            Token(TokenType.LET),
            Token(TokenType.IDENTIFIER, "x"),
            Token(TokenType.ASSIGN),
            Token(TokenType.INTEGER, 5)
        ]
        parser = self.create_parser(tokens)
        ast = parser.parse()
        self.assertIsInstance(ast.statements[0], VarDecl)
        self.assertEqual(ast.statements[0].identifier, "x")
        self.assertEqual(ast.statements[0].initializer.value, 5)
    
    def test_parse_assignment(self):
        tokens = [
            Token(TokenType.IDENTIFIER, "x"),
            Token(TokenType.ASSIGN),
            Token(TokenType.INTEGER, 10)
        ]
        parser = self.create_parser(tokens)
        ast = parser.parse()
        self.assertIsInstance(ast.statements[0], Assignment)
        self.assertEqual(ast.statements[0].identifier, "x")
        self.assertEqual(ast.statements[0].value.value, 10)
    
    def test_parse_multiple_statements(self):
        tokens = [
            Token(TokenType.LET),
            Token(TokenType.IDENTIFIER, "x"),
            Token(TokenType.ASSIGN),
            Token(TokenType.INTEGER, 1),
            Token(TokenType.SEMICOLON),
            Token(TokenType.IDENTIFIER, "x"),
            Token(TokenType.ASSIGN),
            Token(TokenType.INTEGER, 2)
        ]
        parser = self.create_parser(tokens)
        ast = parser.parse()
        self.assertEqual(len(ast.statements), 2)
        self.assertIsInstance(ast.statements[0], VarDecl)
        self.assertIsInstance(ast.statements[1], Assignment)
    

    def test_syntax_error_missing_operand(self):
        tokens = [
            Token(TokenType.INTEGER, 1),
            Token(TokenType.PLUS)  # Missing right operand
        ]
        parser = self.create_parser(tokens)
        with self.assertRaises(Exception) as context:
            parser.parse()
        self.assertIn("Syntax error", str(context.exception))
    

if __name__ == '__main__':
    unittest.main()