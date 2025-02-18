# ![Supermat](docs/assets/supermat-logo-black-sub.png "Supermat")

**A novel data representation framework for the AI era—offering structured annotations, granular traceability, and enhanced evaluation metrics to tackle hallucinations and compliance challenges.**

[![Open in Spaces](https://huggingface.co/datasets/huggingface/badges/resolve/main/open-in-hf-spaces-sm.svg)](https://huggingface.co/spaces/legendof-selda/supermat-demo)

---

## Table of Contents

1. [Overview](#overview)  
2. [Features](#features)  
3. [Installation](#installation)  
4. [Quick Start](#quick-start)  
5. [Hugging Face Spaces Demo](#hugging-face-spaces-demo)  
6. [Code Overview](#code-overview)  
   - [FileProcessor](#fileprocessor)  
   - [SupermatRetriever](#supermatretriever)  
7. [Evaluation & Metrics](#evaluation--metrics)  
8. [Conclusion](#conclusion)  
9. [Contributing](#contributing)

---

## Overview

**Supermat** introduces a structured approach to data processing and retrieval for Large Language Models (LLMs). It preserves annotations even after an LLM is trained, enabling clear traceability from any LLM output back to the original source text. This is critical for:

- **Hallucination Prevention**: Identify and mitigate fabricated answers  
- **Compliance & Auditing**: Ensure regulatory standards are met by tracing outputs  
- **Legal & Security**: Quickly verify authenticity and control sensitive content  

By leveraging **Structure IDs** (e.g., `2.1.4.8` for document/section/paragraph/sentence), Supermat maintains a transparent map between raw data and tokenized text, thereby reducing hallucinations and offering granular document-level context.

---

## Features

1. **Persistent Annotations**  
   - Supermat encodes unique identifiers at the sentence or paragraph level, so the lineage of any output text is never lost—even when building or fine-tuning LLMs.

2. **Structure-Aware Data**  
   - Parsed documents maintain hierarchical relationships: sections, paragraphs, and sentences. This allows for more informed chunking and retrieval strategies.

3. **Traceability & Compliance**  
   - Instantly link LLM outputs to their original references. Ideal for auditing, legal e-discovery, and policy enforcement.

4. **Drop-In Retriever**  
   - The `SupermatRetriever` class seamlessly integrates with [LangChain’s VectorStore](https://python.langchain.com/docs/concepts/vectorstores/), enabling structured queries with minimal refactoring.

5. **Enhanced Evaluation Pipeline**  
   - Built-in metrics (Faithfulness, Accuracy, ROUGE, Cosine Similarity, etc.) let you rigorously test and iterate on your retrieval-augmented generation (RAG) workflows.

---

## Installation

Supermat uses [Poetry](https://python-poetry.org/docs/#installation) for dependency management:

```bash
# 1. Clone the repository
git clone https://github.com/supermatai/supermat.git
cd supermat

# 2. Install Poetry (if not already installed)
#    Follow the official Poetry docs for your environment

# 3. Install dependencies
poetry install --with=frontend --all-extras

# 4. Activate your virtual environment
poetry shell
```

For additional instructions or troubleshooting, check our [Documentation](https://supermatai.github.io/supermat/Installation/).

---

## Quick Start

### 1. Parse Documents

```python
from supermat import FileProcessor
from pathlib import Path

pdf_path = Path("sample_document.pdf")
parsed_document = FileProcessor.parse_file(pdf_path)
```

### 2. Create a Retriever

```python
from supermat.langchain.bindings import SupermatRetriever
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings

# Suppose you have multiple parsed documents
documents = [parsed_document]  # or a list of them

embedding_model = HuggingFaceEmbeddings(model_name="thenlper/gte-base")
vector_store = Chroma(
    embedding_function=embedding_model,
    collection_name="PDFS_SUPERMAT_DEMO",
    persist_directory="./chromadb"
)

retriever = SupermatRetriever(parsed_docs=documents, vector_store=vector_store)
```

### 3. Run the Gradio Interface (Optional)

```bash
python -m supermat.gradio
```

Open the provided local URL to see a live demo of how Supermat processes and retrieves text.

### 4. Explore the Notebook Demo

```bash
cd notebooks
poetry run jupyter notebook pdf_demo.ipynb
```

This end-to-end walkthrough demonstrates:
- Parsing and annotating PDF content  
- Structuring data into the `ParsedDocument` model  
- Using the retriever for queries and tracing outputs  

---

## Hugging Face Spaces Demo

Try **Supermat** directly in your browser—no setup required:

[![Open in Spaces](https://huggingface.co/datasets/huggingface/badges/resolve/main/open-in-hf-spaces-sm.svg)](https://huggingface.co/spaces/legendof-selda/supermat-demo)

---

## Code Overview

### `FileProcessor`

- **Purpose**: Converts files (PDF, DOCX, HTML, etc.) into a `ParsedDocument` model, preserving hierarchical structure.
- **Usage**:
  ```python
  from supermat import FileProcessor, ParsedDocument
  from pathlib import Path

  doc: ParsedDocument = FileProcessor.parse_file(Path("your_file.pdf"))
  ```
- **Handler Management**:  
  ```python
  handlers = FileProcessor.get_handlers(Path("your_file.pdf"))
  doc_custom = FileProcessor.get_handler("some_handler").parse(Path("your_file.pdf"))
  ```

### `SupermatRetriever`

- **Goal**: Serve as a drop-in replacement for LangChain’s standard retrievers, adding structure-aware indexing and traceability.
- **Usage**:
  ```python
  from supermat.langchain.bindings import SupermatRetriever
  from langchain.vectorstores import Chroma

  retriever = SupermatRetriever(parsed_docs=[doc1, doc2], vector_store=Chroma(...))
  ```
- **Advantages**:
  - Retains hierarchical references (Structure IDs)
  - Easily integrates into RAG workflows
  - Minimizes hallucination risk by enabling direct text tracebacks

---

## Evaluation & Metrics

Supermat includes an **evaluation module** aligned with LangChain’s frameworks to measure the quality of LLM outputs. Key metrics include:

- **Faithfulness**: Checks if the generated response accurately reflects the source documents (i.e., no made-up facts).  
- **Accuracy**: Measures correctness against reference answers or ground truth.  
- **Cosine Similarity**: Quantifies semantic closeness between the generated response and reference text.  
- **ROUGE (1, 2, L)**: Assesses textual overlap at unigram, bigram, and longest common subsequence levels.

**Highlights** (vs. standard chunking & semantic chunking strategies):

- **+12.5%** improvement in faithfulness  
- **+15.6%** improvement in accuracy  
- **+33%** ROUGE-1 recall lift  
- Slightly faster or comparable runtime performance  

Such gains emphasize Supermat’s focus on preserving structural context and annotated references, which reduces hallucinations and improves overall LLM response quality.

---

## Conclusion

Supermat is more than just another chunking library. By **embedding structured annotations** into the document processing pipeline, it ensures every piece of information remains traceable—an essential component for building trustworthy AI systems. Whether you need robust compliance checks, advanced RAG pipelines, or improved user confidence, Supermat delivers a **scalable** and **adaptable** solution for AI-driven data workflows.

---

## Contributing

We welcome your contributions! You can help by:

1. **Forking** the repository  
2. Creating a **feature branch**  
3. Submitting a **pull request**  

For guidelines, please see [CONTRIBUTING.md](./CONTRIBUTING.md) (coming soon).

---

**Thanks for trying Supermat!**  
Find more details and advanced guides at our [Documentation](https://supermatai.github.io/supermat/). Feel free to open an issue or a pull request if you have any suggestions or improvements!
