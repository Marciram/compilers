import unittest
import os
import tempfile
import sys
import re

from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.main import read_text_file

class TestReadTextFile(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_file_path = os.path.join(self.temp_dir.name, 'test.txt')
    
    def tearDown(self):
        # Clean up the temporary directory
        self.temp_dir.cleanup()
    
    def test_read_normal_file(self):
        """Test reading a normal file without comments"""
        content = "line1 word1\nline2 word2\nline3 word3"
        with open(self.test_file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        expected = [['line1', 'word1'], ['line2', 'word2'], ['line3', 'word3']]
        result = read_text_file(self.test_file_path)
        self.assertEqual(result, expected)
    
    def test_filter_single_line_comments(self):
        """Test filtering of // single-line comments"""
        content = "valid1 valid2\n//comment\nvalid3 valid4\n//comment"
        with open(self.test_file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        expected = [['valid1', 'valid2'], ['valid3', 'valid4']]
        result = read_text_file(self.test_file_path)
        self.assertEqual(result, expected)
    
    def test_filter_multi_line_comments(self):
        """Test filtering of /* */ multi-line comments"""
        content = "before\n/* comment\nspanning\nmultiple\nlines */\nafter"
        with open(self.test_file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        expected = [['before'], ['after']]
        result = read_text_file(self.test_file_path)
        self.assertEqual(result, expected)
    
    def test_unclosed_multi_line_comment(self):
        """Test behavior with unclosed multi-line comment"""
        content = "valid\n/* unclosed comment\nshould skip this"
        with open(self.test_file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        expected = [['valid']]
        result = read_text_file(self.test_file_path)
        self.assertEqual(result, expected)
    
    def test_empty_lines(self):
        """Test handling of empty lines"""
        content = "\n\nvalid\n\n\n"
        with open(self.test_file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        expected = [['valid']]
        result = read_text_file(self.test_file_path)
        self.assertEqual(result, expected)
    
    def test_file_not_found(self):
        """Test FileNotFoundError is raised for non-existent files"""
        with self.assertRaises(FileNotFoundError):
            read_text_file("nonexistent_file.txt")
    
    def test_mixed_comments(self):
        """Test files with mixed comments"""
        content = "valid1\n// line comment\nvalid2\n/* block\ncomment */\nvalid3"
        with open(self.test_file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        expected = [['valid1'], ['valid2'], ['valid3']]
        result = read_text_file(self.test_file_path)
        self.assertEqual(result, expected)
    """
    @patch('builtins.open', side_effect=UnicodeDecodeError('utf-8', b'', 0, 1, 'invalid byte'))
    def test_encoding_error(self, mock_open):
        \"""Test handling of encoding errors\"""
        with self.assertRaises(UnicodeDecodeError):
            read_text_file(self.test_file_path)
    """
            
            
if __name__ == '__main__':
    unittest.main()