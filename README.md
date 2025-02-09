# ![supermat](docs/assets/supermat-logo-black-sub.png "supermat")

[![Open in Spaces](https://huggingface.co/datasets/huggingface/badges/resolve/main/open-in-hf-spaces-sm.svg)](https://huggingface.co/spaces/legendof-selda/supermat-demo)

## Quick Start

> Take a look at the Installation section in our [docs](https://supermatai.github.io/supermat/Installation/).

1. Clone this repository
2. Setup [python-poetry](https://python-poetry.org/docs/#installation) in your system.
3. Run `poetry install --with=frontend --all-extras` in your virtual environment to install all required dependencies.
4. In terminal run `python -m supermat.gradio` to the run the gradio interface to see it in action.
5. You can also take a look at our demo notebook `notebooks/pdf_demo.ipynb`

### HuggingFace spaces

Interact with out live demo over at HuggingFace spaces [here](https://huggingface.co/spaces/legendof-selda/supermat-demo).

### Brief Code Overview

#### `FileProcessor`

The FileProcessor class is used to register different `Handler`s for various types of documents.
All that needs to be done is,

```python
from supermat import FileProcessor, ParsedDocument

document: ParsedDocument = FileProcessor.parse_file(Path(<your pdf file>))
```

The above picks the main handler for the given file and parses it to a `ParsedDocument` pydantic model.
Take a closer look at `supermat.core.models.parsed_document`.

> Currently, Adobe is set to be the main handler.

If you want to get a list of handlers for a file to choose from,

```python
from supermat import FileProcessor
from supermat.core.file_processor import Handler


handlers: dict[str, Handler] = FileProcessor.get_handlers(Path(<your pdf file>))
```

This provides a dictionary of handlers to choose from to parse a document.

```python
from supermat import FileProcessor

document = FileProcessor.get_handler('<handler_name>').parse(Path(<your pdf file>))
```

#### `SupermatRetriever`

The `SupermatRetriever` is a drop in replacement for Langchain's [VectorStore](https://python.langchain.com/docs/concepts/vectorstores/).

```python
from supermat.langchain.bindings import SupermatRetriever
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


embedding_model=HuggingFaceEmbeddings(
    model_name="thenlper/gte-base"
)

retriever = SupermatRetriever(
    parsed_docs=documents,
    vector_store=Chroma(
        embedding_function=embedding_model,
        collection_name="PDFS_SUPERMAT_DEMO",
    ),
)
```

Now `retriever` can be used as a regular langchain component in any RAG based project.

## Introduction

Supermat introduces a novel data representation framework for the AI era, making relationships explicit and retrievable by design.


### Structured Citations

Our Structure ID is a unique referencing system that leverages hierarchies (document, section, paragraph, and sentence) to precisely locate text. This intuitive system makes precise attribution straightforward.

The Structure ID, goes like this **`2.1.4.8`**. This points specifically to **Document Index number `2`**, the **`1`st section** in that document, then the **`4`th paragraph** in that section, and finally the **`8`th sentence** in that paragraph.
This simple yet powerful structure serves two purposes: it maintains connections between different text chunks while remaining token-efficient for LLM processing.

Furthermore, through post-processing of LLM outputs, this structure enables direct verbatim retrieval of original content from source documents, reducing the need for token repetition and minimizing the risk of hallucinations.

## Evaluation

We chose to work with the [CUAD](https://www.atticusprojectai.org/cuad) dataset to showcase our approach. The legal domain provides an excellent testing ground due to its complexity and ambiguous language. If Supermat works here, it can be generalized to other domains. We evaluated our approach against two benchmarks:

1. A baseline standard chunking strategy
2. LangChain's current state-of-the-art [SemanticChunker](https://python.langchain.com/api_reference/experimental/text_splitter/langchain_experimental.text_splitter.SemanticChunker.html) with `breakpoint_threshold_type="percentile"`

Key Metrics:

> **Accuracy: +15.56% | Faithfulness: +12.53% | ROUGE-1 Recall: +33.33%**

In our internal evaluation, we see double-digit lifts in factual correctness and broader coverage with more complete outputs. This translates to fewer hallucinations and more trust in automated answers.

For more details, take a look [here](https://supermatai.github.io/supermat/Evaluation/).

## Conclusion

This is only the beginning of our journey as we build products on this foundation. 

Our findings suggest significant untapped potential in this area. Preserving and representing both explicit and implicit connections within data before any chunking or processing yields better results than immediately jumping into chunking.

Far beyond just efficiency gains, we believe this crucial intersection enables simplified yet powerful human + AI interfaces and novel operating models of tomorrow. We're building for those.

## Contributing

We welcome contributors and collaborators to join us on this journey.
