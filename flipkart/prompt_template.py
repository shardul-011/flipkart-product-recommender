from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

def get_flipkart_product_prompt():
    return ChatPromptTemplate.from_messages([
        (
            "system",
            """You are a Flipkart product recommendation assistant.

Use ONLY the provided product reviews and titles as context.
Answer clearly and concisely.

If the context does not contain enough information, say:
"I do not have sufficient data to answer this question."

CONTEXT:
{context}
"""
        ),
        # 👇 THIS is what makes chat history influence answers
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}")
    ])
