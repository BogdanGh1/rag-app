import pytest
from langchain_core.documents import Document


@pytest.fixture
def make_chunks():
    def _make(*texts: str) -> list[Document]:
        return [Document(page_content=t) for t in texts]

    return _make
