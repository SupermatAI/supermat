from itertools import chain
from pathlib import Path
from typing import TYPE_CHECKING, cast

import pandas as pd
from joblib import Parallel, delayed
from langchain.smith import RunEvalConfig
from langchain.smith.evaluation.runner_utils import TestResult
from langchain_benchmarks.extraction.evaluators import get_eval_config
from langchain_benchmarks.utils import run_without_langsmith
from langchain_chroma import Chroma
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import (
    RunnableLambda,
    RunnableParallel,
    RunnablePassthrough,
)
from langchain_core.runnables.base import Runnable
from langchain_huggingface import HuggingFaceEmbeddings

from supermat.core.models.parsed_document import ParsedDocumentType
from supermat.core.parser import FileProcessor
from supermat.langchain.bindings import SupermatRetriever


def get_docs(pdf_files: list[Path]) -> ParsedDocumentType:
    parsed_files = Parallel(n_jobs=-1)(delayed(FileProcessor.parse_file)(path) for path in pdf_files)
    if TYPE_CHECKING:
        from supermat.core.models.parsed_document import ParsedDocumentType

        parsed_files = cast(list[ParsedDocumentType], parsed_files)

    documents = list(chain.from_iterable(parsed_docs for parsed_docs in parsed_files))

    if TYPE_CHECKING:
        from supermat.core.models.parsed_document import ParsedDocumentType

        documents = cast(ParsedDocumentType, documents)
    return documents


def get_retriever(documents: ParsedDocumentType, collection_name: str) -> SupermatRetriever:
    retriever = SupermatRetriever(
        parsed_docs=documents,
        vector_store=Chroma(
            embedding_function=HuggingFaceEmbeddings(
                model_name="thenlper/gte-base",
            ),
            persist_directory="./chromadb",
            collection_name=collection_name,
        ),
    )
    return retriever


def get_qa_chain(retriever: SupermatRetriever, template: str, llm_model: BaseChatModel) -> Runnable:
    qa_chain = (
        RunnableLambda(lambda x: x["Question"])  # pyright: ignore[reportIndexIssue]
        | RunnableParallel({"context": retriever, "Question": RunnablePassthrough()})
        | ChatPromptTemplate.from_template(template)
        | llm_model
        | StrOutputParser()
    )
    return qa_chain


def calculate_metrics(llm_model: BaseChatModel, evaluators: list, datset_path: Path, qa_chain: Runnable) -> TestResult:
    rag_evaluation = get_eval_config(llm_model)
    eval_config = RunEvalConfig.model_validate(
        rag_evaluation.model_dump()
        | RunEvalConfig(
            custom_evaluators=evaluators,
            input_key="Question",
        ).model_dump()
    )
    test_run = run_without_langsmith(
        path_or_token_id=datset_path.as_posix(),
        llm_or_chain_factory=qa_chain,  # pyright: ignore[reportArgumentType]
        evaluation=eval_config,
        verbose=True,
        concurrency_level=10,
    )
    assert isinstance(test_run, TestResult)
    return test_run


def compare_baseline(baseline_pkl_path: Path, run_agg: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    baseline_agg_results = pd.read_pickle(baseline_pkl_path)
    baseline_agg_results = baseline_agg_results = baseline_agg_results.droplevel(
        ["llm_model", "vectorstore_name", "dataset"], axis=1
    )
    diff_to_baseline = (
        run_agg.select_dtypes("float64") - baseline_agg_results.select_dtypes("float64")
    ) / baseline_agg_results.select_dtypes("float64")
    return baseline_agg_results, diff_to_baseline


def results_to_excel(file_name: str, test_run: TestResult, run_agg: pd.DataFrame, diff_to_baseline: pd.DataFrame):
    with pd.ExcelWriter(f"{file_name}.xlsx") as writer:
        test_run.to_dataframe().to_excel(writer, sheet_name="LLM Results", index=True)
        run_agg.to_excel(writer, sheet_name="Agg Results", index=True)
        diff_to_baseline.to_excel(writer, sheet_name="Baseline Diff Agg Results", index=True)
