from fastapi.testclient import TestClient
from main import app

from api.v1.services.tools.summary import summary_service
import pytest
from langchain.chains.llm import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import Runnable
from unittest.mock import patch, MagicMock
from pypdf import PdfReader

client = TestClient(app)


class MockChatOpenAI(Runnable):
    def __call__(self, *args, **kwargs):
        return self

    def invoke(self, input, config=None, **kwargs):
        return "This is a mocked summary."


@pytest.fixture
def mock_pdf_reader():
    mock_pdf = MagicMock(spec=PdfReader)
    mock_pdf.pages = [MagicMock(), MagicMock(), MagicMock()]
    return mock_pdf


@pytest.fixture
def mock_upload_to_temp_dir(mocker):
    mocker.patch(
        "api.utils.files.upload_to_temp_dir", 
        return_value="test_files/sample.pdf", 
        max_file_size=10*1024*1024
    )


@pytest.fixture
def mock_upload_file_to_minio_tmp():
    with patch("api.utils.minio_service.minio_service.upload_to_tmp_bucket") as mock:
        mock.return_value = 'https://minio.example.com/tmp/test-video.mp4'
        yield mock


@pytest.fixture
def mock_summary_service(mocker):
    mocker.patch.object(
        summary_service,
        "summarize_pdf",
        return_value="This is a mock summary of the PDF.",
    )


# def test_summarize_pdf_invalid_file_type():
#     response = client.post(
#         "/api/v1/tools/summary/pdf-summarizer",
#         files={"file": ("sample.txt", b"Sample text file", "text/plain")},
#     )

#     assert response.status_code == 400 or response.status_code == 403
    # assert response.status_code == 202
