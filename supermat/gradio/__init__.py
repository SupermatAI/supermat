from __future__ import annotations

import random
import re
import traceback
from enum import StrEnum
from itertools import chain
from pathlib import Path
from typing import TYPE_CHECKING, Sequence, cast

import gradio as gr
from joblib import Parallel, delayed
from langchain_chroma import Chroma
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableSerializable
from langchain_huggingface import HuggingFaceEmbeddings

from supermat.core.models.parsed_document import ParsedDocument
from supermat.core.parser.adobe_parser.parser import (
    PDF_SERVICES_CLIENT_ID,
    PDF_SERVICES_CLIENT_SECRET,
)
from supermat.core.parser.file_processor import FileProcessor
from supermat.langchain.bindings import SupermatRetriever, get_default_chain

if TYPE_CHECKING:
    from pydantic import SecretStr

    from supermat.core.models.parsed_document import ParsedDocumentType
    from supermat.core.parser.file_processor import Handler


class LLMProvider(StrEnum):
    ollama = "Ollama"
    anthropic = "Anthropic"
    openai = "OpenAI"
    azure_openai = "Azure OpenAI"


BASE_URLS = {
    LLMProvider.ollama: "http://localhost:11434",
}


class LLMChat:
    def __init__(self):
        self.chat_model = None
        self.retriever = None
        self.handler_name = "PyMuPDFParser"

    @property
    def handler(self) -> Handler:
        return FileProcessor.get_handler(self.handler_name)

    def initialize_client(
        self,
        provider: str,
        model: str,
        credentials: str | None = None,
        base_url: str | None = None,
        temperature: float | None = 0.0,
    ) -> str:
        """Initialize the LangChain chat model based on selected provider."""
        gr.Info("Initializaing LLM")
        base_url = base_url if base_url else None
        self.provider = provider
        self.model = model

        if TYPE_CHECKING:
            assert isinstance(credentials, SecretStr)

        try:
            match (provider):
                case LLMProvider.ollama:
                    from langchain_ollama.llms import OllamaLLM  # noqa: I900

                    self.chat_model = OllamaLLM(model=model, temperature=temperature, base_url=base_url)
                case LLMProvider.anthropic:
                    from langchain_anthropic import ChatAnthropic  # noqa: I900

                    self.chat_model = ChatAnthropic(
                        model_name=model,
                        temperature=temperature,
                        timeout=None,
                        api_key=credentials,
                        stop=None,
                        base_url=base_url,
                    )
                case LLMProvider.openai:
                    from langchain_openai import ChatOpenAI  # noqa: I900

                    temperature = 0.7 if temperature is None else temperature
                    self.chat_model = ChatOpenAI(
                        model=model, temperature=temperature, api_key=credentials, base_url=base_url
                    )
                case LLMProvider.azure_openai:
                    from langchain_openai import AzureChatOpenAI

                    if not base_url:
                        raise gr.Error("Azure OpenAI requires API Enpoint")

                    api_version = None
                    api_version_match = re.search(r"[?&]api-version=([^&]+)", base_url)

                    if api_version_match:
                        api_version = api_version_match.group(1)
                    else:
                        raise gr.Error("Pass in `api_version` as query parameter in Azure API Endpoint")

                    self.chat_model = AzureChatOpenAI(
                        api_key=credentials,
                        azure_endpoint=base_url,
                        azure_deployment=model,
                        api_version=api_version,
                        temperature=0,
                    )
                case _:
                    raise gr.Error(f"Invalid LLM Provider {provider}")

            gr.Info(f"{self.chat_model.get_name()} initialized successfully!")
            return f"{self.chat_model.get_name()} initialized successfully!"

        except Exception as e:
            raise gr.Error(f"Error initializing client: {str(e)}")

    def update_handler(self, handler_name: str):
        self.handler_name = handler_name

    def parse_files(self, collection_name: str, pdf_files: Sequence[Path | str]) -> str:
        gr.Info(f"Parsing {len(pdf_files)} files.")
        pdf_files = list(map(Path, pdf_files))
        if TYPE_CHECKING:
            pdf_files = cast(list[Path], pdf_files)

        if not all(f.exists() for f in pdf_files):
            raise gr.Error("Few files do not exist.")
        non_pdf_files = [f.name for f in pdf_files if f.suffix.lower() != ".pdf"]
        if non_pdf_files:
            raise gr.Error(f"Following files are not pdf: \n{'\n'.join(non_pdf_files)}")

        parsed_files = Parallel(n_jobs=-1, backend="threading")(
            delayed(self.handler.parse_file)(path) for path in pdf_files
        )

        if TYPE_CHECKING:
            parsed_files = cast(list[ParsedDocumentType], parsed_files)

        documents = list(chain.from_iterable(parsed_docs for parsed_docs in parsed_files))

        if TYPE_CHECKING:
            documents = cast(ParsedDocumentType, documents)

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
        self.retriever = retriever
        gr.Info("Files parsed successfully.")
        return "Files parsed successfully."

    def convert_history_to_messages(self, history: list[dict]) -> list[HumanMessage | AIMessage]:
        """Convert Gradio chat history to LangChain message format."""

        return [
            HumanMessage(content=msg["content"]) if msg["role"] == "user" else AIMessage(content=msg["content"])
            for msg in history
        ]

    @property
    def chain(self) -> RunnableSerializable:
        assert self.chat_model and self.retriever
        chain = get_default_chain(self.retriever, self.chat_model, substitute_references=False, return_context=False)
        return chain

    def chat(self, message: str, _history):
        """Process chat message using LangChain chat model."""
        if not self.chat_model:
            raise gr.Error("Please initialize an LLM provider first!")

        if not self.retriever:
            raise gr.Error("Please parse relevant pdf documents!")

        try:
            # history_langchain_format = self.convert_history_to_messages(history)
            # history_langchain_format.append(HumanMessage(content=message))
            gpt_response = self.chain.invoke(message)
            return gpt_response if isinstance(gpt_response, str) else gpt_response.content

        except Exception as e:
            raise gr.Error(f"Error: {str(e)}\n{traceback.format_exc()}")

    def refresh(self) -> list[str]:
        if not self.retriever:
            raise gr.Error("Parse pdf documents first.")
        return list(self.retriever._document_index_map.keys())

    def get_document(self, document: str) -> list[dict]:
        if not self.retriever:
            raise gr.Error("Parse pdf documents first.")
        if document == "All":
            return ParsedDocument.dump_python(self.retriever.parsed_docs)
        elif document == "None":
            return []
        else:
            filtered_docs = [parsed_doc for parsed_doc in self.retriever.parsed_docs if parsed_doc.document == document]
            return ParsedDocument.dump_python(filtered_docs)


def create_llm_interface():
    llm_chat = LLMChat()

    with gr.Blocks() as app:
        with gr.Tab("Setup"):
            with gr.Row():
                provider_option = gr.Dropdown(
                    choices=["--SELECT--"] + list(map(str, LLMProvider)), label="Select LLM Provider"
                )

            @gr.render(inputs=provider_option, triggers=[provider_option.change])
            def provider_update(provider: LLMProvider):
                if provider == "--SELECT--":
                    raise gr.Error("Select a provider from dropdown.", print_exception=False)
                with gr.Row():
                    llm_init_inputs = []
                    initialize_client = llm_chat.initialize_client
                    with gr.Column():
                        if provider == LLMProvider.ollama:
                            base_url = gr.Textbox(
                                value=BASE_URLS[provider],
                                label="API Host",
                                placeholder="e.g., http://localhost:11434 for Ollama",
                            )
                            model = gr.Textbox(
                                value="deepseek-r1:8b",
                                label="Model Name",
                                placeholder="Required. Model setup in Ollama",
                            )
                            llm_init_inputs = [provider_option, model, base_url]
                            initialize_client = lambda p, m, b: llm_chat.initialize_client(  # noqa: E731
                                provider=p,
                                model=m,
                                base_url=b,
                            )
                        else:
                            credentials = gr.Textbox(
                                label="API Key/Credentials",
                                type="password",
                                placeholder="Required. Enter your API key here",
                            )
                            model = gr.Textbox(
                                label=f"{provider} model", placeholder="Required. Name of the model to run."
                            )
                            base_url = gr.Textbox(
                                value=BASE_URLS.get(provider),
                                label="Azure Endpoint" if provider == LLMProvider.azure_openai else "API Host",
                                placeholder="Optional. Only provide if required.",
                            )
                            llm_init_inputs = [provider_option, model, credentials, base_url]
                            initialize_client = lambda p, m, c, b: llm_chat.initialize_client(  # noqa: E731
                                provider=p, model=m, credentials=c, base_url=b
                            )

                    with gr.Column():
                        initialize_btn = gr.Button("Initialize LLM")
                        init_status = gr.Textbox(label="Initialization Status")

                        initialize_btn.click(fn=initialize_client, inputs=llm_init_inputs, outputs=init_status)

            with gr.Row():
                handler_option = gr.Dropdown(
                    choices=list(FileProcessor.get_handlers("test.pdf").keys()),
                    value=llm_chat.handler_name,
                    label="Select File Handler",
                )

            @gr.render(inputs=[handler_option], triggers=[handler_option.change])
            def handler_update(handler_name: str):
                llm_chat.update_handler(handler_name)
                if not (PDF_SERVICES_CLIENT_ID and PDF_SERVICES_CLIENT_SECRET):
                    with gr.Row():
                        with gr.Column():
                            gr.Markdown(
                                "Follow [this](https://developer.adobe.com/document-services/docs/overview/pdf-services-api/gettingstarted/)."
                            )
                            adobe_client_id = gr.Textbox(
                                label="PDF_SERVICES_CLIENT_ID", type="password", placeholder="Required. Adobe Client ID"
                            )
                            adobe_client_secret = gr.Textbox(
                                label="PDF_SERVICES_CLIENT_SECRET",
                                type="password",
                                placeholder="Required. Adobe Client Secret",
                            )
                            adobe_btn = gr.Button("Initialize Adobe")

                    def setup_env(adobe_client_id: str, adobe_client_secret: str):
                        if not (adobe_client_id or adobe_client_secret):
                            raise gr.Error("Adobe credentials required")
                        global PDF_SERVICES_CLIENT_ID, PDF_SERVICES_CLIENT_SECRET
                        PDF_SERVICES_CLIENT_ID = adobe_client_id
                        PDF_SERVICES_CLIENT_SECRET = adobe_client_secret
                        gr.Info("Adobe credentials set.")

                    adobe_btn.click(fn=setup_env, inputs=[adobe_client_id, adobe_client_secret])

            with gr.Row():
                with gr.Column():
                    pdf_files = gr.Files(
                        label="PDF Files to parse",
                    )
                with gr.Column():
                    collection_id = gr.State(random.randint(1, 100))
                    collection_name = gr.Textbox(
                        f"TEST{collection_id.value}", label="Collection Name", placeholder="Required."
                    )
                    upload_btn = gr.Button("Parse PDF files.", variant="primary")
                with gr.Column():
                    upload_status = gr.Textbox(label="Upload Status")

                upload_btn.click(fn=llm_chat.parse_files, inputs=[collection_name, pdf_files], outputs=upload_status)

        with gr.Tab("Documents"):
            with gr.Row():
                refresh_btn = gr.Button("Refresh")
                doc_drop_down = gr.Dropdown(
                    choices=["None"], label="Document", value="None", interactive=True, key="documents_dropdown"
                )

                def update_documents():
                    documents_list = llm_chat.refresh()
                    return gr.update(choices=["None", "All"] + documents_list, label="Document", value="None")

                refresh_btn.click(fn=update_documents, outputs=doc_drop_down)
            with gr.Row():
                parsed_document = gr.JSON()

            doc_drop_down.change(llm_chat.get_document, inputs=[doc_drop_down], outputs=parsed_document)

        with gr.Tab("Chat"):

            def respond(message, chat_history):
                if isinstance(message, dict):
                    message = message["text"]
                bot_message = llm_chat.chat(message, chat_history)
                think_match = re.search(r"<think>[\s\S]*?</think>", bot_message)
                if think_match:
                    think_block = think_match.group(0)
                    bot_message = bot_message.replace(think_block, "")
                    return [
                        gr.ChatMessage(
                            content=f"```\n{think_block}\n```", role="assistant", metadata={"title": "🧠 Thinking"}
                        ),
                        gr.ChatMessage(content=bot_message, role="assistant"),
                    ]
                return gr.ChatMessage(content=bot_message, role="assistant")

            gr.ChatInterface(respond, type="messages")

    return app
