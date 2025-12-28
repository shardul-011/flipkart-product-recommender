from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from flipkart.config import config
from operator import itemgetter
from flipkart.prompt_template import get_flipkart_product_prompt


class RAGchainBuilder:
    def __init__(self, vector_store):
        self.vector_store = vector_store
        self.llm = ChatGroq(
            model=config.RAG_Model,
            temperature=0.5
        )
        self.history_store = {}
        self.prompt=get_flipkart_product_prompt()

    def _get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        if session_id not in self.history_store:
            self.history_store[session_id] = InMemoryChatMessageHistory()
        return self.history_store[session_id]

    def build_chain(self):
        retriever = self.vector_store.as_retriever(search_kwargs={"k": 5})

       

        rag_chain =( RunnablePassthrough.assign(
            
                context=itemgetter("question") | retriever
                
        ) ##we have use assign as it wills tore questions too along with the documnets and pass it to llm 
            | self.prompt
            | self.llm
            | StrOutputParser()
        )

        return RunnableWithMessageHistory(
            rag_chain,
            self._get_session_history,
            input_messages_key="question",
            history_messages_key="chat_history"
        )
