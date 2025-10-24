"""
Test suite for FileOperationsService
Tests file and directory operations including deletion, creation, and YAML handling
"""
import pytest
import tempfile
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock

from services.file_operations.file_operations_service import FileOperationsService


class TestFileOperationsService:
    """Test cases for FileOperationsService"""
    
    def setup_method(self):
        """Setup before each test"""
        self.service = FileOperationsService()
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def teardown_method(self):
        """Cleanup after each test"""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_delete_directory_success(self):
        """Test successful directory deletion"""
        # Create a test directory
        test_dir = self.temp_dir / "test_dir"
        test_dir.mkdir()
        test_file = test_dir / "test_file.txt"
        test_file.write_text("test content")
        
        # Verify directory exists
        assert test_dir.exists()
        assert test_file.exists()
        
        # Delete directory
        result = self.service.delete_directory(test_dir)
        
        # Verify deletion
        assert result is True
        assert not test_dir.exists()
    
    def test_delete_directory_nonexistent(self):
        """Test deletion of non-existent directory"""
        nonexistent_dir = self.temp_dir / "nonexistent"
        
        result = self.service.delete_directory(nonexistent_dir)
        
        assert result is False
    
    def test_delete_directory_exception(self):
        """Test directory deletion with exception"""
        test_dir = self.temp_dir / "test_dir"
        test_dir.mkdir()
        
        # Mock shutil.rmtree to raise an exception
        with patch('shutil.rmtree', side_effect=Exception("Permission denied")):
            result = self.service.delete_directory(test_dir)
            assert result is False
    
    def test_delete_file_success(self):
        """Test successful file deletion"""
        test_file = self.temp_dir / "test_file.txt"
        test_file.write_text("test content")
        
        # Verify file exists
        assert test_file.exists()
        
        # Delete file
        result = self.service.delete_file(test_file)
        
        # Verify deletion
        assert result is True
        assert not test_file.exists()
    
    def test_delete_file_nonexistent(self):
        """Test deletion of non-existent file"""
        nonexistent_file = self.temp_dir / "nonexistent.txt"
        
        result = self.service.delete_file(nonexistent_file)
        
        assert result is False
    
    def test_delete_file_exception(self):
        """Test file deletion with exception"""
        test_file = self.temp_dir / "test_file.txt"
        test_file.write_text("test content")
        
        # Mock unlink to raise an exception
        with patch.object(Path, 'unlink', side_effect=Exception("Permission denied")):
            result = self.service.delete_file(test_file)
            assert result is False
    
    def test_create_directory_success(self):
        """Test successful directory creation"""
        test_dir = self.temp_dir / "new_dir" / "sub_dir"
        
        result = self.service.create_directory(test_dir)
        
        assert result is True
        assert test_dir.exists()
        assert test_dir.is_dir()
    
    def test_create_directory_exists_ok(self):
        """Test directory creation when directory already exists with exist_ok=True"""
        test_dir = self.temp_dir / "existing_dir"
        test_dir.mkdir()
        
        result = self.service.create_directory(test_dir, exist_ok=True)
        
        assert result is True
        assert test_dir.exists()
    
    def test_create_directory_exists_not_ok(self):
        """Test directory creation when directory already exists with exist_ok=False"""
        test_dir = self.temp_dir / "existing_dir"
        test_dir.mkdir()
        
        result = self.service.create_directory(test_dir, exist_ok=False)
        
        assert result is False
    
    def test_create_directory_exception(self):
        """Test directory creation with exception"""
        test_dir = self.temp_dir / "test_dir"
        
        # Mock mkdir to raise an exception
        with patch.object(Path, 'mkdir', side_effect=Exception("Permission denied")):
            result = self.service.create_directory(test_dir)
            assert result is False
    
    def test_save_yaml_file_success(self):
        """Test successful YAML file saving"""
        test_file = self.temp_dir / "test.yaml"
        test_data = {
            "name": "test",
            "version": "1.0",
            "config": {
                "enabled": True,
                "count": 42
            }
        }
        
        result = self.service.save_yaml_file(test_file, test_data)
        
        assert result is True
        assert test_file.exists()
        
        # Verify content
        with open(test_file, 'r') as f:
            loaded_data = yaml.safe_load(f)
        assert loaded_data == test_data
    
    def test_save_yaml_file_exclusive_success(self):
        """Test successful YAML file saving in exclusive mode"""
        test_file = self.temp_dir / "test.yaml"
        test_data = {"name": "test"}
        
        result = self.service.save_yaml_file(test_file, test_data, exclusive=True)
        
        assert result is True
        assert test_file.exists()
    
    def test_save_yaml_file_exclusive_exists(self):
        """Test YAML file saving in exclusive mode when file exists"""
        test_file = self.temp_dir / "test.yaml"
        test_file.write_text("existing content")
        test_data = {"name": "test"}
        
        with pytest.raises(FileExistsError):
            self.service.save_yaml_file(test_file, test_data, exclusive=True)
    
    def test_save_yaml_file_exception(self):
        """Test YAML file saving with exception"""
        test_file = self.temp_dir / "test.yaml"
        test_data = {"name": "test"}
        
        # Mock open to raise an exception
        with patch('builtins.open', side_effect=Exception("Permission denied")):
            result = self.service.save_yaml_file(test_file, test_data)
            assert result is False
    
    def test_load_yaml_file_success(self):
        """Test successful YAML file loading"""
        test_file = self.temp_dir / "test.yaml"
        test_data = {
            "name": "test",
            "version": "1.0",
            "config": {
                "enabled": True,
                "count": 42
            }
        }
        
        # Create test file
        with open(test_file, 'w') as f:
            yaml.safe_dump(test_data, f)
        
        result = self.service.load_yaml_file(test_file)
        
        assert result == test_data
    
    def test_load_yaml_file_nonexistent(self):
        """Test loading of non-existent YAML file"""
        nonexistent_file = self.temp_dir / "nonexistent.yaml"
        
        result = self.service.load_yaml_file(nonexistent_file)
        
        assert result is None
    
    def test_load_yaml_file_exception(self):
        """Test YAML file loading with exception"""
        test_file = self.temp_dir / "test.yaml"
        test_file.write_text("invalid: yaml: content: [")
        
        result = self.service.load_yaml_file(test_file)
        
        assert result is None
    
    def test_path_handling_string_input(self):
        """Test that string paths are properly converted to Path objects"""
        test_dir_str = str(self.temp_dir / "string_dir")
        
        result = self.service.create_directory(test_dir_str)
        
        assert result is True
        assert Path(test_dir_str).exists()
    
    def test_path_handling_path_input(self):
        """Test that Path objects are handled correctly"""
        test_dir_path = self.temp_dir / "path_dir"
        
        result = self.service.create_directory(test_dir_path)
        
        assert result is True
        assert test_dir_path.exists()
    
    def test_delete_directory_with_path_object(self):
        """Test directory deletion with Path object"""
        test_dir = self.temp_dir / "path_dir"
        test_dir.mkdir()
        
        result = self.service.delete_directory(test_dir)
        
        assert result is True
        assert not test_dir.exists()
    
    def test_delete_file_with_path_object(self):
        """Test file deletion with Path object"""
        test_file = self.temp_dir / "path_file.txt"
        test_file.write_text("test content")
        
        result = self.service.delete_file(test_file)
        
        assert result is True
        assert not test_file.exists()
    
    def test_save_yaml_with_path_object(self):
        """Test YAML saving with Path object"""
        test_file = self.temp_dir / "path_file.yaml"
        test_data = {"test": "data"}
        
        result = self.service.save_yaml_file(test_file, test_data)
        
        assert result is True
        assert test_file.exists()
    
    def test_load_yaml_with_path_object(self):
        """Test YAML loading with Path object"""
        test_file = self.temp_dir / "path_file.yaml"
        test_data = {"test": "data"}
        
        with open(test_file, 'w') as f:
            yaml.safe_dump(test_data, f)
        
        result = self.service.load_yaml_file(test_file)
        
        assert result == test_data