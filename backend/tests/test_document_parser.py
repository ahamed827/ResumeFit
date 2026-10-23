import pytest
from app.integrations.document_parser import document_parser
from app.core.errors import BadRequestError


def test_txt_extraction_valid():
    content = b"Candidate Name\nSoftware Engineer with experience in Python, FastAPI, and PostgreSQL.\n\nEducation: B.S. in Computer Science"
    text = document_parser.extract_text(content, "sample_resume.txt")
    assert "Candidate Name" in text
    assert "Software Engineer" in text
    assert "PostgreSQL" in text


def test_txt_extraction_too_short():
    content = b"Too short"
    with pytest.raises(BadRequestError):
        document_parser.extract_text(content, "short.txt")


def test_unsupported_file_extension():
    content = b"Random binary data"
    with pytest.raises(BadRequestError):
        document_parser.extract_text(content, "resume.exe")
