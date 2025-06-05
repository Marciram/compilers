from enum import Enum
from dataclasses import dataclass
from typing import Union, List, Dict, Optional

class SymbolType(Enum):
    INT = 'int'
    FLOAT = 'float'
    CHAR = 'char'
    BOOL = 'bool'
    ARRAY = 'array'
    FUNCTION = 'function'

@dataclass
class ArrayType:
    base_type: SymbolType
    size: int

@dataclass
class FunctionType:
    return_type: SymbolType
    params: List[SymbolType]

SymbolInfo = Union[SymbolType, ArrayType, FunctionType]

class SymbolTable:
    def __init__(self, parent=None):
        self.table: Dict[str, Dict] = {}
        self.parent = parent
    
    def add_symbol(self, name: str, symbol_type: SymbolInfo, is_const: bool = False):
        if name in self.table:
            raise ValueError(f"Variable '{name}' already declared")
        self.table[name] = {'type': symbol_type, 'is_const': is_const}
    
    def check_symbol(self, name: str) -> Dict:
        if name in self.table:
            return self.table[name]
        if self.parent:
            return self.parent.check_symbol(name)
        raise ValueError(f"Variable '{name}' not declared")

class IntermediateCodeGenerator:
    def __init__(self):
        self.code: List = []
        self.temp_count = 0
        self.label_count = 0
    
    def new_temp(self) -> str:
        temp = f"t{self.temp_count}"
        self.temp_count += 1
        return temp
    
    def new_label(self) -> str:
        label = f"L{self.label_count}"
        self.label_count += 1
        return label
    
    def emit(self, op: str, arg1=None, arg2=None, result=None):
        self.code.append((op, arg1, arg2, result))
    
    def get_code(self) -> List:
        return self.code

class SemanticAnalyzer:
    def __init__(self):
        self.current_scope = SymbolTable()
        self.code_gen = IntermediateCodeGenerator()
        self.functions = {}
    
    def enter_scope(self):
        self.current_scope = SymbolTable(parent=self.current_scope)
    
    def exit_scope(self):
        if self.current_scope.parent:
            self.current_scope = self.current_scope.parent
    
    def analyze_declaration(self, type_spec: str, var_name: str, is_const: bool = False, array_size: int = None):
        try:
            if array_size is not None:
                if array_size <= 0:
                    raise ValueError("Array size must be positive")
                base_type = SymbolType(type_spec)
                symbol_type = ArrayType(base_type, array_size)
            else:
                symbol_type = SymbolType(type_spec)
            
            self.current_scope.add_symbol(var_name, symbol_type, is_const)
        except ValueError as e:
            raise ValueError(f"Declaration error: {str(e)}")
    
    def analyze_assignment(self, var_name: str, expr_type: SymbolInfo):
        try:
            var_info = self.current_scope.check_symbol(var_name)
            
            if var_info['is_const']:
                raise ValueError(f"Cannot assign to constant '{var_name}'")
            
            # Handle array assignment
            if isinstance(var_info['type'], ArrayType):
                raise ValueError(f"Cannot directly assign to array '{var_name}'")
            
            # Type checking
            if var_info['type'] != expr_type:
                # Allow implicit int to float conversion
                if var_info['type'] == SymbolType.FLOAT and expr_type == SymbolType.INT:
                    return SymbolType.FLOAT
                raise ValueError(f"Type mismatch in assignment to '{var_name}'")
            
            return var_info['type']
        except ValueError as e:
            raise ValueError(f"Assignment error: {str(e)}")
    
    def analyze_binary_op(self, left_type: SymbolInfo, right_type: SymbolInfo, op: str):
        # Arithmetic operations
        if op in ['+', '-', '*', '/']:
            if left_type not in [SymbolType.INT, SymbolType.FLOAT] or right_type not in [SymbolType.INT, SymbolType.FLOAT]:
                raise ValueError(f"Invalid operands for '{op}' operation")
            
            # Type promotion: if either operand is float, result is float
            if left_type == SymbolType.FLOAT or right_type == SymbolType.FLOAT:
                return SymbolType.FLOAT
            return SymbolType.INT
        
        # Relational operations
        elif op in ['<', '>', '<=', '>=', '==', '!=']:
            if left_type != right_type:
                # Allow comparing int with float
                if {left_type, right_type} == {SymbolType.INT, SymbolType.FLOAT}:
                    return SymbolType.BOOL
                raise ValueError(f"Type mismatch in relational operation '{op}'")
            return SymbolType.BOOL
        
        # Logical operations
        elif op in ['&&', '||']:
            if left_type != SymbolType.BOOL or right_type != SymbolType.BOOL:
                raise ValueError(f"Invalid operands for logical '{op}' operation")
            return SymbolType.BOOL
        
        else:
            raise ValueError(f"Unknown operator '{op}'")
    
    def analyze_unary_op(self, operand_type: SymbolInfo, op: str):
        if op == '!':
            if operand_type != SymbolType.BOOL:
                raise ValueError(f"Invalid operand for logical NOT '!' operation")
            return SymbolType.BOOL
        elif op == '-':
            if operand_type not in [SymbolType.INT, SymbolType.FLOAT]:
                raise ValueError(f"Invalid operand for unary '-' operation")
            return operand_type
        else:
            raise ValueError(f"Unknown unary operator '{op}'")
    
    def analyze_array_access(self, array_name: str, index_type: SymbolInfo):
        try:
            array_info = self.current_scope.check_symbol(array_name)
            
            if not isinstance(array_info['type'], ArrayType):
                raise ValueError(f"'{array_name}' is not an array")
            
            if index_type != SymbolType.INT:
                raise ValueError(f"Array index must be integer")
            
            return array_info['type'].base_type
        except ValueError as e:
            raise ValueError(f"Array access error: {str(e)}")
    
    def analyze_function_call(self, func_name: str, arg_types: List[SymbolInfo]):
        if func_name not in self.functions:
            raise ValueError(f"Function '{func_name}' not declared")
        
        func_info = self.functions[func_name]
        
        if len(arg_types) != len(func_info['params']):
            raise ValueError(f"Function '{func_name}' expects {len(func_info['params'])} arguments")
        
        for i, (arg_type, param_type) in enumerate(zip(arg_types, func_info['params'])):
            if arg_type != param_type:
                raise ValueError(f"Argument {i+1} type mismatch in call to '{func_name}'")
        
        return func_info['return_type']
    
    def generate_code(self, node):
        if node['type'] == 'declaration':
            array_size = node.get('array_size')
            self.analyze_declaration(node['data_type'], node['var_name'], 
                                   node.get('is_const', False), array_size)
            
            # Initialize array if needed
            if array_size is not None:
                self.code_gen.emit('alloc', node['var_name'], array_size)
        
        elif node['type'] == 'assignment':
            # Handle array element assignment
            if 'index' in node:
                # Evaluate array index
                index_result, index_type = self.generate_code(node['index'])
                
                # Check array access
                array_type = self.analyze_array_access(node['var_name'], index_type)
                
                # Evaluate expression
                expr_result, expr_type = self.generate_code(node['expr'])
                
                # Check assignment compatibility
                if array_type != expr_type:
                    raise ValueError(f"Array element type mismatch in assignment to '{node['var_name']}'")
                
                # Generate code for array store
                temp = self.code_gen.new_temp()
                self.code_gen.emit('arraystore', node['var_name'], index_result, expr_result)
            else:
                # Regular variable assignment
                expr_result, expr_type = self.generate_code(node['expr'])
                result_type = self.analyze_assignment(node['var_name'], expr_type)
                
                # Handle implicit type conversion
                if result_type == SymbolType.FLOAT and expr_type == SymbolType.INT:
                    temp = self.code_gen.new_temp()
                    self.code_gen.emit('inttofloat', expr_result, None, temp)
                    self.code_gen.emit('=', temp, None, node['var_name'])
                else:
                    self.code_gen.emit('=', expr_result, None, node['var_name'])
        
        elif node['type'] == 'binary_op':
            left_result, left_type = self.generate_code(node['left'])
            right_result, right_type = self.generate_code(node['right'])
            
            result_type = self.analyze_binary_op(left_type, right_type, node['op'])
            
            temp = self.code_gen.new_temp()
            self.code_gen.emit(node['op'], left_result, right_result, temp)
            return temp, result_type
        
        elif node['type'] == 'unary_op':
            operand_result, operand_type = self.generate_code(node['operand'])
            result_type = self.analyze_unary_op(operand_type, node['op'])
            
            temp = self.code_gen.new_temp()
            self.code_gen.emit(node['op'], operand_result, None, temp)
            return temp, result_type
        
        elif node['type'] == 'array_access':
            array_info = self.current_scope.check_symbol(node['array_name'])
            index_result, index_type = self.generate_code(node['index'])
            
            element_type = self.analyze_array_access(node['array_name'], index_type)
            
            temp = self.code_gen.new_temp()
            self.code_gen.emit('arrayload', node['array_name'], index_result, temp)
            return temp, element_type
        
        elif node['type'] == 'if':
            # Evaluate condition
            cond_result, cond_type = self.generate_code(node['condition'])
            
            if cond_type != SymbolType.BOOL:
                raise ValueError("If condition must be boolean")
            
            # Create labels
            else_label = self.code_gen.new_label()
            end_label = self.code_gen.new_label()
            
            # Emit conditional jump
            self.code_gen.emit('ifnot', cond_result, None, else_label)
            
            # Generate then block
            self.generate_code(node['then_block'])
            
            # Jump to end if there's an else
            if 'else_block' in node:
                self.code_gen.emit('goto', None, None, end_label)
            
            # Emit else label
            self.code_gen.emit('label', else_label, None, None)
            
            # Generate else block if exists
            if 'else_block' in node:
                self.generate_code(node['else_block'])
                self.code_gen.emit('label', end_label, None, None)
        
        elif node['type'] == 'while':
            # Create labels
            start_label = self.code_gen.new_label()
            end_label = self.code_gen.new_label()
            
            # Emit start label
            self.code_gen.emit('label', start_label, None, None)
            
            # Evaluate condition
            cond_result, cond_type = self.generate_code(node['condition'])
            
            if cond_type != SymbolType.BOOL:
                raise ValueError("While condition must be boolean")
            
            # Emit conditional jump
            self.code_gen.emit('ifnot', cond_result, None, end_label)
            
            # Generate body
            self.generate_code(node['body'])
            
            # Jump back to start
            self.code_gen.emit('goto', None, None, start_label)
            
            # Emit end label
            self.code_gen.emit('label', end_label, None, None)
        
        elif node['type'] == 'function_call':
            # Evaluate arguments
            arg_results = []
            arg_types = []
            for arg in node['args']:
                res, typ = self.generate_code(arg)
                arg_results.append(res)
                arg_types.append(typ)
            
            # Check function call semantics
            return_type = self.analyze_function_call(node['func_name'], arg_types)
            
            # Generate call code
            if return_type != SymbolType.INT:  # Void function
                self.code_gen.emit('call', node['func_name'], arg_results)
            else:
                temp = self.code_gen.new_temp()
                self.code_gen.emit('call', node['func_name'], arg_results, temp)
                return temp, return_type
        
        elif node['type'] == 'variable':
            var_info = self.current_scope.check_symbol(node['name'])
            return node['name'], var_info['type']
        
        elif node['type'] == 'literal':
            value = node['value']
            
            # Determine type from literal value
            if isinstance(value, bool):
                return value, SymbolType.BOOL
            elif isinstance(value, int):
                return value, SymbolType.INT
            elif isinstance(value, float):
                return value, SymbolType.FLOAT
            elif isinstance(value, str) and len(value) == 1:
                return value, SymbolType.CHAR
            else:
                raise ValueError(f"Invalid literal value: {value}")
        
        return None, None

if __name__ == "__main__":
    ast = [
        {
            'type': 'declaration',
            'data_type': 'int',
            'var_name': 'x'
        },
        {
            'type': 'declaration',
            'data_type': 'float',
            'var_name': 'y',
            'is_const': True
        },
        {
            'type': 'declaration',
            'data_type': 'int',
            'var_name': 'arr',
            'array_size': 10
        },
        {
            'type': 'function_decl',
            'func_name': 'factorial',
            'return_type': 'int',
            'params': [('int', 'n')],
            'body': {
                'type': 'block',
                'statements': [
                    {
                        'type': 'if',
                        'condition': {
                            'type': 'binary_op',
                            'op': '<=',
                            'left': {
                                'type': 'variable',
                                'name': 'n'
                            },
                            'right': {
                                'type': 'literal',
                                'value': 1
                            }
                        },
                        'then_block': {
                            'type': 'block',
                            'statements': [
                                {
                                    'type': 'return',
                                    'value': {
                                        'type': 'literal',
                                        'value': 1
                                    }
                                }
                            ]
                        }
                    },
                    {
                        'type': 'return',
                        'value': {
                            'type': 'binary_op',
                            'op': '*',
                            'left': {
                                'type': 'variable',
                                'name': 'n'
                            },
                            'right': {
                                'type': 'function_call',
                                'func_name': 'factorial',
                                'args': [
                                    {
                                        'type': 'binary_op',
                                        'op': '-',
                                        'left': {
                                            'type': 'variable',
                                            'name': 'n'
                                        },
                                        'right': {
                                            'type': 'literal',
                                            'value': 1
                                        }
                                    }
                                ]
                            }
                        }
                    }
                ]
            }
        },
        
        {
            'type': 'assignment',
            'var_name': 'x',
            'expr': {
                'type': 'literal',
                'value': 5
            }
        },
        {
            'type': 'assignment',
            'var_name': 'arr',
            'index': {
                'type': 'literal',
                'value': 2
            },
            'expr': {
                'type': 'binary_op',
                'op': '+',
                'left': {
                    'type': 'variable',
                    'name': 'x'
                },
                'right': {
                    'type': 'literal',
                    'value': 3
                }
            }
        },
        {
            'type': 'while',
            'condition': {
                'type': 'binary_op',
                'op': '>',
                'left': {
                    'type': 'variable',
                    'name': 'x'
                },
                'right': {
                    'type': 'literal',
                    'value': 0
                }
            },
            'body': {
                'type': 'block',
                'statements': [
                    {
                        'type': 'assignment',
                        'var_name': 'x',
                        'expr': {
                            'type': 'binary_op',
                            'op': '-',
                            'left': {
                                'type': 'variable',
                                'name': 'x'
                            },
                            'right': {
                                'type': 'literal',
                                'value': 1
                            }
                        }
                    }
                ]
            }
        },
        {
            'type': 'function_call',
            'func_name': 'factorial',
            'args': [
                {
                    'type': 'literal',
                    'value': 5
                }
            ]
        }
    ]

    analyzer = SemanticAnalyzer()
    
    analyzer.functions['factorial'] = {
        'return_type': SymbolType.INT,
        'params': [SymbolType.INT]
    }
    
    # Process AST
    for node in ast:
        if node['type'] == 'function_decl':
            continue
        analyzer.generate_code(node)
    
    # Print generated intermediate code
    print("Generated Intermediate Code:")
    for op, arg1, arg2, result in analyzer.code_gen.get_code():
        if op == 'label':
            print(f"{result}:")
        elif op == 'ifnot':
            print(f"ifnot {arg1} goto {result}")
        elif op == 'goto':
            print(f"goto {result}")
        elif op in ['alloc', 'arraystore', 'arrayload']:
            print(f"{op} {arg1}, {arg2}, {result}")
        elif op == 'call':
            args = ', '.join(map(str, arg2)) if arg2 else ''
            if result:
                print(f"{result} = call {arg1}({args})")
            else:
                print(f"call {arg1}({args})")
        elif arg2 is not None:
            print(f"{result} = {arg1} {op} {arg2}")
        else:
            print(f"{result} = {arg1}")