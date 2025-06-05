import unittest
from enum import Enum
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root)) 

from src.semantic_analyzer import (
    SymbolType, ArrayType, SymbolTable, 
    IntermediateCodeGenerator, SemanticAnalyzer
)

class TestSymbolTable(unittest.TestCase):
    def setUp(self):
        self.symbol_table = SymbolTable()
    
    def test_add_and_check_symbol(self):
        self.symbol_table.add_symbol("x", SymbolType.INT)
        symbol_info = self.symbol_table.check_symbol("x")
        self.assertEqual(symbol_info['type'], SymbolType.INT)
        
    def test_duplicate_declaration(self):
        self.symbol_table.add_symbol("x", SymbolType.INT)
        with self.assertRaises(ValueError):
            self.symbol_table.add_symbol("x", SymbolType.FLOAT)
    
    def test_undeclared_variable(self):
        with self.assertRaises(ValueError):
            self.symbol_table.check_symbol("undeclared")
    
    def test_nested_scope(self):
        parent = SymbolTable()
        parent.add_symbol("x", SymbolType.INT)
        child = SymbolTable(parent=parent)
        
        # Can access parent's symbols
        symbol_info = child.check_symbol("x")
        self.assertEqual(symbol_info['type'], SymbolType.INT)
        
        # Shadowing
        child.add_symbol("x", SymbolType.FLOAT)
        symbol_info = child.check_symbol("x")
        self.assertEqual(symbol_info['type'], SymbolType.FLOAT)

class TestIntermediateCodeGenerator(unittest.TestCase):
    def setUp(self):
        self.code_gen = IntermediateCodeGenerator()
    
    def test_emit(self):
        self.code_gen.emit("+", "t1", "t2", "t3")
        self.assertEqual(len(self.code_gen.code), 1)
        self.assertEqual(self.code_gen.code[0], ("+", "t1", "t2", "t3"))
    
    def test_new_temp(self):
        temp1 = self.code_gen.new_temp()
        temp2 = self.code_gen.new_temp()
        self.assertEqual(temp1, "t0")
        self.assertEqual(temp2, "t1")
    
    def test_new_label(self):
        label1 = self.code_gen.new_label()
        label2 = self.code_gen.new_label()
        self.assertEqual(label1, "L0")
        self.assertEqual(label2, "L1")

class TestSemanticAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = SemanticAnalyzer()
    
    def test_declaration(self):
        node = {'type': 'declaration', 'data_type': 'int', 'var_name': 'x'}
        self.analyzer.generate_code(node)
        self.assertIn('x', self.analyzer.current_scope.table)
    
    def test_array_declaration(self):
        node = {
            'type': 'declaration', 
            'data_type': 'float', 
            'var_name': 'arr',
            'array_size': 10
        }
        self.analyzer.generate_code(node)
        symbol_info = self.analyzer.current_scope.check_symbol("arr")
        self.assertIsInstance(symbol_info['type'], ArrayType)
        self.assertEqual(symbol_info['type'].base_type, SymbolType.FLOAT)
    
    def test_assignment(self):
        # Declare variable first
        decl_node = {'type': 'declaration', 'data_type': 'int', 'var_name': 'x'}
        self.analyzer.generate_code(decl_node)
        
        # Assign value
        assign_node = {
            'type': 'assignment',
            'var_name': 'x',
            'expr': {'type': 'literal', 'value': 42}
        }
        self.analyzer.generate_code(assign_node)
        
        # Check code generation
        code = self.analyzer.code_gen.get_code()
        self.assertEqual(code[-1], ('=', 42, None, 'x'))
    
    def test_array_assignment(self):
        # Declare array
        decl_node = {
            'type': 'declaration', 
            'data_type': 'int', 
            'var_name': 'arr',
            'array_size': 5
        }
        self.analyzer.generate_code(decl_node)
        
        # Assign to array element
        assign_node = {
            'type': 'assignment',
            'var_name': 'arr',
            'index': {'type': 'literal', 'value': 2},
            'expr': {'type': 'literal', 'value': 10}
        }
        self.analyzer.generate_code(assign_node)
        
        # Check code generation
        code = self.analyzer.code_gen.get_code()
        self.assertEqual(code[-1], ('arraystore', 'arr', 2, 10))
    
    def test_arithmetic_operations(self):
        # Test int operations
        node = {
            'type': 'binary_op',
            'op': '+',
            'left': {'type': 'literal', 'value': 5},
            'right': {'type': 'literal', 'value': 3}
        }
        result, typ = self.analyzer.generate_code(node)
        self.assertEqual(typ, SymbolType.INT)
        
        # Test float operations
        node = {
            'type': 'binary_op',
            'op': '*',
            'left': {'type': 'literal', 'value': 2.5},
            'right': {'type': 'literal', 'value': 1.5}
        }
        result, typ = self.analyzer.generate_code(node)
        self.assertEqual(typ, SymbolType.FLOAT)
    
    def test_type_promotion(self):
        # int + float should promote to float
        node = {
            'type': 'binary_op',
            'op': '+',
            'left': {'type': 'literal', 'value': 5},     # int
            'right': {'type': 'literal', 'value': 3.14}   # float
        }
        result, typ = self.analyzer.generate_code(node)
        self.assertEqual(typ, SymbolType.FLOAT)
    
    def test_invalid_operations(self):
        # bool + int should fail
        node = {
            'type': 'binary_op',
            'op': '+',
            'left': {'type': 'literal', 'value': True},
            'right': {'type': 'literal', 'value': 5}
        }
        with self.assertRaises(ValueError):
            self.analyzer.generate_code(node)
    
    def test_if_statement(self):
        # Declare variable
        decl_node = {'type': 'declaration', 'data_type': 'int', 'var_name': 'x'}
        self.analyzer.generate_code(decl_node)
        
        # If statement
        if_node = {
            'type': 'if',
            'condition': {
                'type': 'binary_op',
                'op': '>',
                'left': {'type': 'variable', 'name': 'x'},
                'right': {'type': 'literal', 'value': 0}
            },
            'then_block': {
                'type': 'block',
                'statements': [
                    {
                        'type': 'assignment',
                        'var_name': 'x',
                        'expr': {'type': 'literal', 'value': 1}
                    }
                ]
            }
        }
        self.analyzer.generate_code(if_node)
        
        # Check code generation
        code = self.analyzer.code_gen.get_code()
        self.assertTrue(any(op == 'ifnot' for op, _, _, _ in code))
        self.assertTrue(any(op == 'label' for op, _, _, _ in code))
    
    def test_while_loop(self):
        # While loop
        while_node = {
            'type': 'while',
            'condition': {
                'type': 'binary_op',
                'op': '<',
                'left': {'type': 'literal', 'value': 1},
                'right': {'type': 'literal', 'value': 2}
            },
            'body': {
                'type': 'block',
                'statements': []
            }
        }
        self.analyzer.generate_code(while_node)
        
        # Check code generation
        code = self.analyzer.code_gen.get_code()
        self.assertTrue(any(op == 'ifnot' for op, _, _, _ in code))
        self.assertTrue(any(op == 'goto' for op, _, _, _ in code))
        self.assertEqual(len([op for op, _, _, _ in code if op == 'label']), 2)
    
    def test_invalid_function_call(self):
        # Register a function
        self.analyzer.functions['pow'] = {
            'return_type': SymbolType.FLOAT,
            'params': [SymbolType.FLOAT, SymbolType.FLOAT]
        }
        
        # Wrong number of arguments
        call_node = {
            'type': 'function_call',
            'func_name': 'pow',
            'args': [{'type': 'literal', 'value': 2.0}]
        }
        with self.assertRaises(ValueError):
            self.analyzer.generate_code(call_node)
        
        # Wrong argument type
        call_node = {
            'type': 'function_call',
            'func_name': 'pow',
            'args': [
                {'type': 'literal', 'value': 2.0},
                {'type': 'literal', 'value': True}  # bool instead of float
            ]
        }
        with self.assertRaises(ValueError):
            self.analyzer.generate_code(call_node)
    
    def test_const_assignment(self):
        # Declare constant
        decl_node = {
            'type': 'declaration',
            'data_type': 'int',
            'var_name': 'MAX',
            'is_const': True
        }
        self.analyzer.generate_code(decl_node)
        
        # Try to assign to constant
        assign_node = {
            'type': 'assignment',
            'var_name': 'MAX',
            'expr': {'type': 'literal', 'value': 100}
        }
        with self.assertRaises(ValueError):
            self.analyzer.generate_code(assign_node)

class TestTypeSystem(unittest.TestCase):
    def test_array_type_equality(self):
        arr1 = ArrayType(SymbolType.INT, 10)
        arr2 = ArrayType(SymbolType.INT, 10)
        arr3 = ArrayType(SymbolType.FLOAT, 10)
        
        self.assertEqual(arr1, arr2)
        self.assertNotEqual(arr1, arr3)
    
    def test_symbol_type_values(self):
        self.assertEqual(SymbolType.INT.value, 'int')
        self.assertEqual(SymbolType.FLOAT.value, 'float')
        self.assertEqual(SymbolType.CHAR.value, 'char')
        self.assertEqual(SymbolType.BOOL.value, 'bool')

if __name__ == '__main__':
    unittest.main()