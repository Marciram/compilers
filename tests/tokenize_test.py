import unittest
import re
from unittest.mock import patch, MagicMock
from io import StringIO

class TestCategorizeTokens(unittest.TestCase):
    
    @patch('__main__.read_text_file')
    def test_categorize_keywords(self, mock_read_file):
        """Test categorizing keywords"""
        # Mock the read_text_file function to return specific tokens
        mock_read_file.return_value = ['if', 'else', 'while', 'for', 'nonkeyword']
        
        # Import the function to test
        from __main__ import categorize_tokens
        
        # Redirect stdout to capture print statements
        with patch('sys.stdout', new_callable=StringIO):
            tokens = categorize_tokens()
        
        # Check if keywords were categorized correctly
        self.assertEqual(tokens['keyword'], {'if', 'else', 'while', 'for'})
        # Nonkeyword should be an identifier
        self.assertEqual(tokens['identifier'], {'nonkeyword'})
    
    @patch('__main__.read_text_file')
    def test_categorize_operators(self, mock_read_file):
        """Test categorizing operators"""
        mock_read_file.return_value = ['+', '-', '*', '/', 'nonoperator']
        
        from __main__ import categorize_tokens
        
        with patch('sys.stdout', new_callable=StringIO):
            tokens = categorize_tokens()
        
        self.assertEqual(tokens['operator'], {'+', '-', '*', '/'})
        self.assertEqual(tokens['identifier'], {'nonoperator'})
    
    @patch('__main__.read_text_file')
    def test_categorize_delimiters(self, mock_read_file):
        """Test categorizing delimiters"""
        mock_read_file.return_value = ['(', ')', '{', '}', '[', ']', ',', ';', 'nondelimiter']
        
        from __main__ import categorize_tokens
        
        with patch('sys.stdout', new_callable=StringIO):
            tokens = categorize_tokens()
        
        # Note: Function uses 'delimeters' (misspelled) not 'delimiters'
        self.assertEqual(tokens['delimeters'], {'(', ')', '{', '}', '[', ']', ',', ';'})
        self.assertEqual(tokens['identifier'], {'nondelimiter'})
    
    @patch('__main__.read_text_file')
    def test_categorize_numbers(self, mock_read_file):
        """Test categorizing numbers"""
        mock_read_file.return_value = ['123', '456', '789', 'abc']
        
        from __main__ import categorize_tokens
        
        with patch('sys.stdout', new_callable=StringIO):
            tokens = categorize_tokens()
        
        self.assertEqual(tokens['number'], {'123', '456', '789'})
        self.assertEqual(tokens['identifier'], {'abc'})
    
    @patch('__main__.read_text_file')
    def test_categorize_identifiers(self, mock_read_file):
        """Test categorizing identifiers"""
        mock_read_file.return_value = ['abc', 'var1', 'test_var', '123']
        
        from __main__ import categorize_tokens
        
        with patch('sys.stdout', new_callable=StringIO):
            tokens = categorize_tokens()
        
        self.assertEqual(tokens['identifier'], {'abc', 'var1', 'test_var'})
        self.assertEqual(tokens['number'], {'123'})
    
    @patch('__main__.read_text_file')
    def test_categorize_mixed_tokens(self, mock_read_file):
        """Test categorizing mixed tokens"""
        mock_read_file.return_value = ['if', '123', 'variable', '+', '(', ')']
        
        from __main__ import categorize_tokens
        
        with patch('sys.stdout', new_callable=StringIO):
            tokens = categorize_tokens()
        
        self.assertEqual(tokens['keyword'], {'if'})
        self.assertEqual(tokens['number'], {'123'})
        self.assertEqual(tokens['identifier'], {'variable'})
        self.assertEqual(tokens['operator'], {'+'})
        self.assertEqual(tokens['delimeters'], {'(', ')'})
    
    @patch('__main__.read_text_file')
    def test_categorize_empty_array(self, mock_read_file):
        """Test categorizing with empty input"""
        mock_read_file.return_value = []
        
        from __main__ import categorize_tokens
        
        with patch('sys.stdout', new_callable=StringIO):
            tokens = categorize_tokens()
        
        # All categories should be empty
        for category in tokens:
            self.assertEqual(tokens[category], set())
    
    @patch('__main__.read_text_file')
    def test_categorize_special_identifiers(self, mock_read_file):
        """Test categorizing identifiers with underscores and numbers"""
        mock_read_file.return_value = ['var_1', 'test123', '_var', '1var']
        
        from __main__ import categorize_tokens
        
        with patch('sys.stdout', new_callable=StringIO):
            tokens = categorize_tokens()
        
        # Regular identifiers should be categorized correctly
        self.assertIn('var_1', tokens['identifier'])
        self.assertIn('test123', tokens['identifier'])
        
        # '_var' should be an identifier if your regex allows leading underscores
        # But your current regex doesn't support this
        self.assertNotIn('_var', tokens['identifier'])
        
        # '1var' should not be an identifier since it starts with a number
        self.assertNotIn('1var', tokens['identifier'])
    
    @patch('__main__.read_text_file')
    def test_categorize_unidentified_tokens(self, mock_read_file):
        """Test handling of tokens that don't match any category"""
        mock_read_file.return_value = ['@', '$', '_start', '1var']
        
        from __main__ import categorize_tokens
        
        # Capture print output to verify "not identified" messages
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            tokens = categorize_tokens()
            
            output = mock_stdout.getvalue()
            # Check if "not identified" appears in the output
            self.assertIn("not identified", output)
        
        # All token categories should be empty
        for category, token_set in tokens.items():
            self.assertEqual(token_set, set())

if __name__ == '__main__':
    unittest.main()