from langchain_core.prompts import ChatPromptTemplate
from langchain_openai.chat_models import AzureChatOpenAI
import os

# Load the OpenAI API key from the environment.
os.environ.get("OPEN_API_TYPE")
os.environ.get("AZURE_OPENAI_API_KEY")
os.environ.get("AZURE_OPENAI_ENDPOINT")
os.environ.get("OPENAI_API_VERSION")

llm = AzureChatOpenAI(
    deployment_name="gpt-35-turbo",
    model_name="gpt-35-turbo",
    temperature=0,
    streaming=True,
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a AI Chatbot."),
        ("user", "{input}"),
    ]
)

chain = prompt | llm
