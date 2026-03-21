"""Tests for the parser module."""
import pytest
from pathlib import Path
from archie.engine.parser import CodeParser


@pytest.fixture
def parser():
    return CodeParser()


@pytest.fixture
def sample_repo_path():
    return Path(__file__).parent / "fixtures" / "sample_repo"


def test_parse_python_file(parser, sample_repo_path):
    """Test parsing a Python file."""
    result = parser.parse_file(str(sample_repo_path / "validators.py"))
    
    assert result is not None
    assert result["language"] == "python"
    assert result["file_path"] == str(sample_repo_path / "validators.py")
    
    # Check functions
    func_names = [f["name"] for f in result["functions"]]
    assert "validate_card" in func_names
    assert "validate_amount" in func_names
    assert "validate_email" in func_names
    
    # Check parameters
    validate_card = next(f for f in result["functions"] if f["name"] == "validate_card")
    assert "card" in validate_card["params"]


def test_parse_python_class(parser, sample_repo_path):
    """Test parsing Python classes."""
    result = parser.parse_file(str(sample_repo_path / "payment.py"))
    
    assert len(result["classes"]) > 0
    payment_class = next(c for c in result["classes"] if c["name"] == "PaymentService")
    assert "process_payment" in payment_class["methods"]
    assert "refund" in payment_class["methods"]


def test_parse_python_imports(parser, sample_repo_path):
    """Test extracting imports."""
    result = parser.parse_file(str(sample_repo_path / "user_service.py"))
    
    assert len(result["imports"]) > 0


def test_parse_javascript_file(parser, sample_repo_path):
    """Test parsing a JavaScript file."""
    result = parser.parse_file(str(sample_repo_path / "utils.js"))
    
    assert result is not None
    assert result["language"] == "javascript"
    
    func_names = [f["name"] for f in result["functions"]]
    assert "validateRequest" in func_names
    assert "formatResponse" in func_names


def test_parse_javascript_class(parser, sample_repo_path):
    """Test parsing JavaScript classes."""
    result = parser.parse_file(str(sample_repo_path / "api.js"))
    
    assert len(result["classes"]) > 0
    api_class = next(c for c in result["classes"] if c["name"] == "ApiClient")
    assert "fetchUser" in api_class["methods"]
    assert "createPayment" in api_class["methods"]


def test_parse_nonexistent_file(parser):
    """Test parsing a file that doesn't exist."""
    result = parser.parse_file("nonexistent.py")
    assert result is None


def test_parse_unsupported_extension(parser, tmp_path):
    """Test parsing an unsupported file type."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("some text")
    result = parser.parse_file(str(test_file))
    assert result is None
