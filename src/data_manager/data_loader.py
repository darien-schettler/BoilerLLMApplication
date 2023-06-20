import re
import docx2txt
import streamlit as st
from io import BytesIO
from pypdf import PdfReader
from typing import List, Union, Tuple

# OPENAI
from openai.error import AuthenticationError

# LANGCHAIN
from langchain.vectorstores import VectorStore
from langchain.vectorstores.faiss import FAISS
from langchain.docstore.document import Document
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter


@st.cache_data()
def parse_docx(file: BytesIO) -> str:
    """ Parses a docx file and returns the contents as a string.

    The st.cache_data decorator caches the result of this function
    so that it is only run once per file. This is useful for large files
    that take a long time to process. The decorator is only available in
    Streamlit 0.84 and above.

    Args:
        file (BytesIO): A file-like object containing a docx file.

    Returns:
        str: The contents of the docx file.
    """
    text = docx2txt.process(file)

    # Remove multiple newlines
    text = re.sub(r"\n\s*\n", "\n\n", text)

    return text


def pdf_repair(text: str) -> str:
    """ Fixes common issues with pdf text extraction.

    The following operations are conducted:
        1. Merge hyphenated words
        2. Fix newlines in the middle of sentences
        3. Remove multiple newlines

    Args:
        text (str): The text extracted from a pdf file.

    Returns:
        str: The repaired text.
    """
    # Merge hyphenated words
    text = re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)

    # Fix newlines in the middle of sentences
    text = re.sub(r"(?<!\n\s)\n(?!\s\n)", " ", text.strip())

    # Remove multiple newlines
    text = re.sub(r"\n\s*\n", "\n\n", text)

    return text


@st.cache_data()
def parse_pdf(file: BytesIO) -> List[str]:
    """ Parses a pdf file and returns the contents as a string.

    The st.cache_data decorator caches the result of this function
    so that it is only run once per file. This is useful for large files
    that take a long time to process. The decorator is only available in
    Streamlit 0.84 and above.

    Args:
        file (BytesIO): A file-like object containing a txt file.

    Returns:
        str: The contents of the txt file.
    """
    # Extract text from pdf
    pdf = PdfReader(file)

    # Fix common issues with pdf text extraction
    output = [pdf_repair(page.extract_text()) for page in pdf.pages]

    return output


@st.cache_data()
def parse_txt(file: BytesIO) -> str:
    """ Parses a txt file and returns the contents as a string.

    The st.cache_data decorator caches the result of this function
    so that it is only run once per file. This is useful for large files
    that take a long time to process. The decorator is only available in
    Streamlit 0.84 and above.

    Args:
        file (BytesIO): A file-like object containing a txt file.

    Returns:
        str: The contents of the txt file.
    """
    text = file.read().decode("utf-8")

    # Remove multiple newlines
    text = re.sub(r"\n\s*\n", "\n\n", text)
    return text


@st.cache_data()
def text_to_docs(
        text: Union[str, List[str]],
        chunk_size: int = 1000,
        chunk_overlap: int = 0,
        separators: Tuple[str] = ("\n\n", "\n", ".", "!", "?", ",", " ", ""),
) -> List[Document]:
    """Converts a string or list of strings to a list of Documents with metadata.

    The st.cache_data decorator caches the result of this function so that it is
    only run once per file. This is useful for large files that take a long
    time to process. `` is required because the
    Document objects need to be mutable so that we can add metadata to them.

    Args:
        text (Union[str, List[str]]): A string or list of strings.
        chunk_size (int, optional): The size of each chunk.
        chunk_overlap (int, optional): The number of characters to overlap between chunks.
        separators (Tuple[str], optional): A tuple of strings to split on.

    Returns:
        List[Document]: A list of Documents.
    """
    # Take a single string as one page (coercion)
    if isinstance(text, str): text = [text]

    # Convert pages to Documents
    page_docs = [Document(page_content=page) for page in text]

    # Add page numbers as metadata
    for i, doc in enumerate(page_docs):
        doc.metadata["page"] = i + 1

    # - Define the text splitter to use for chunking -
    #     - RecursiveCharacterTextSplitter is a splitter that splits text into chunks of a specified size, but tries to
    #       split on a list of separators first.
    #     - This is useful for splitting text into contiguous sentences or paragraphs that have consistent semantics
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, separators=list(separators), chunk_overlap=chunk_overlap,
    )

    # Split each page into chunks and add page numbers and chunk numbers as metadata.
    doc_chunks = []
    for doc in page_docs:
        chunks = text_splitter.split_text(doc.page_content)
        # Add chunk numbers and `sources` as metadata
        for i, chunk in enumerate(chunks):
            doc = Document(page_content=chunk, metadata={"page": doc.metadata["page"], "chunk": i})
            doc.metadata["source"] = f"{doc.metadata['page']}-{doc.metadata['chunk']}"
            doc_chunks.append(doc)
    return doc_chunks


@st.cache_data(show_spinner=False)
def embed_text(doc_txt: str) -> VectorStore:
    """Embeds a list of Documents and returns a FAISS index

    The st.cache_data decorator caches the result of this function so that it is
    only run once per file. This is useful for large files that take a long
    time to process. `` is required because the
    Document objects need to be mutable. `show_spinner=False` hides the
    spinner that Streamlit displays while the function is running.

    FAISS is a library for efficient similarity search and clustering of dense vectors.

    Args:
        doc_txt (str): The full document text to embed. This is kept as a string to allow for hashing

    Raises:
        AuthenticationError: If the user has not previously entered a valid OpenAI API key that is stored in state.
                             The user can enter this information in the Streamlit sidebar.
    Returns:
        VectorStore: A FAISS index of the embedded Documents.
    """

    # Convert the text to Langchain Documents
    docs = text_to_docs(doc_txt)

    # If the user has not entered an API key that is stored in state, raise an error
    if not st.session_state.get("OPENAI_API_KEY"):
        raise AuthenticationError("👈 Enter your API key in the sidebar (https://platform.openai.com/account/api-keys)")

    # Embed the chunks
    embeddings = OpenAIEmbeddings(openai_api_key=st.session_state.get("OPENAI_API_KEY"))  # type: ignore
    index = FAISS.from_documents(docs, embeddings)
    return index


@st.cache_data()
def search_docs(_index: VectorStore, query: str, top_k: int = 5) -> List[Document]:
    """Searches a FAISS index for similar chunks to the query and returns a list of Documents.

    The `query` is embedded and then compared to the embedded Documents in the vectorstore`index`.
    The `top_k` most similar Documents are then returned.

    The st.cache_data decorator caches the result of this function so that it is
    only run once per file. This is useful for large files that take a long
    time to process. `` is required because the
    input arguments need to be mutable.

    FAISS is a library for efficient similarity search and clustering of dense vectors.

    Args:
        index (VectorStore): A FAISS index (vectorstore) of the embedded Documents.
        query (str): A query string.
        top_k (int): The number of similar chunks to return.

    Returns:
        List[Document]: A list of Documents that are similar to the query based on the embedded vector similarity.
    """

    # Search for similar chunks
    docs = _index.similarity_search(query, k=top_k)
    return docs
