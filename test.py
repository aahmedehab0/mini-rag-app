from langchain_text_splitters import RecursiveCharacterTextSplitter

# Example text
text = """LangChain makes it easy to build LLM applications.
It provides tools for prompt engineering, memory, and more."""

# Initialize splitter
splitter = RecursiveCharacterTextSplitter(
    chunk_size=100,        # حجم كل قطعة
    chunk_overlap=20,      # مقدار التداخل بين القطع
    length_function=len
)

# Split the text
chunks = splitter.split_text(text)

print(chunks)
