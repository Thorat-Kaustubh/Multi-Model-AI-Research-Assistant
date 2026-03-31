"""Define the configurable parameters for the agent."""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import Annotated, Any, Literal, Optional, Type, TypeVar

from langchain_core.runnables import RunnableConfig, ensure_config


@dataclass(kw_only=True)
class BaseConfiguration:
    """Configuration class for indexing and retrieval operations.

    This class defines the parameters needed for configuring the indexing and
    retrieval processes, including embedding model selection, retriever provider choice, and search parameters.
    """

    embedding_model: Annotated[
        str,
        {"__template_metadata__": {"kind": "embeddings"}},
    ] = field(
        default="huggingface/all-MiniLM-L6-v2",
        metadata={
            "description": "Name of the embedding model to use. Must be a valid embedding model name."
        },
    )

    retriever_provider: Annotated[
        Literal["elastic-local", "elastic", "pinecone", "mongodb", "chroma"],
        {"__template_metadata__": {"kind": "retriever"}},
    ] = field(
        default="chroma",
        metadata={
            "description": "The vector store provider to use for retrieval. Options are 'elastic', 'pinecone', 'mongodb', or 'chroma'."
        },
    )

    core_model: str = field(
        default="groq/llama-3.3-70b-versatile",
        metadata={"description": "The core intelligence model (Groq Llama 3.3)."},
    )

    fast_model: str = field(
        default="groq/llama-3.1-8b-instant",
        metadata={"description": "The fast synthesis model (Groq Llama 3.1)."},
    )

    grounding_model: str = field(
        default="google/gemini-2.5-flash-lite",
        metadata={"description": "The grounding and fact-checking model (Google Gemini)."},
    )

    research_model: str = field(
        default="google/gemini-3.1-flash-lite-preview",
        metadata={"description": "The deep research model (Google Gemini)."},
    )

    search_kwargs: dict[str, Any] = field(
        default_factory=dict,
        metadata={
            "description": "Additional keyword arguments to pass to the search function of the retriever."
        },
    )

    @classmethod
    def from_runnable_config(
        cls: Type[T], config: Optional[RunnableConfig] = None
    ) -> T:
        """Create an IndexConfiguration instance from a RunnableConfig object.

        Args:
            cls (Type[T]): The class itself.
            config (Optional[RunnableConfig]): The configuration object to use.

        Returns:
            T: An instance of IndexConfiguration with the specified configuration.
        """
        config = ensure_config(config)
        configurable = config.get("configurable") or {}
        _fields = {f.name for f in fields(cls) if f.init}
        return cls(**{k: v for k, v in configurable.items() if k in _fields})


T = TypeVar("T", bound=BaseConfiguration)
