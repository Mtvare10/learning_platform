from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

def get_tutor_response(topic: str, user_role: str):
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7)
    # The prompt changes based on who is asking!
    role_instruction = "a helpful peer tutor" if user_role == "student" else "a teaching assistant"
    prompt = ChatPromptTemplate.from_template(f"You are {role_instruction}. Explain: {{topic}}")
    
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"topic": topic})