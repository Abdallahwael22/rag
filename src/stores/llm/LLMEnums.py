from enum import Enum

class LLMEnums(Enum):
    """
    Enum class for provider (Language Model Models).
    """
    OPENAI = "OPENAI"
    ANTHROPIC = "ANTHROPIC"
    COHERE = "COHERE"
    GROQ = "GROQ"

class OpenAIEnums(Enum):
    SystemRole = "system"
    UserRole = "user"
    assistantRole = "assistant"
class CohereEnums(Enum):
    SystemRole = "SYSTEM"
    UserRole = "USER"
    assistantRole = "CHATBOT"
    DOCUMENT = "search_document"
    QUERY = "search_query"

class DocumentType(Enum):
    """
    Enum class for document types.
    """
    DOCUMENT = "search_document"
    QUERY = "search_query"