from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv


load_dotenv()
def get_student_tutor_response(student_question: str, lesson_title: str, lesson_content: str):
    api_key = os.getenv("GOOGLE_API_KEY")
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash", 
        temperature=0.3, # Lower temperature for more factual, less "creative" answers
        google_api_key=api_key
    )

    system_message = (
        "You are a supportive Academic Tutor. Your task is to answer student questions "
        "based strictly on the provided lesson content. \n\n"
        "INSTRUCTIONS:\n"
        "1. Use the 'LESSON CONTENT' below to form your answer.\n"
        "2. If the answer is not in the text, say 'That isn't covered in this lesson, but based on general knowledge...' and then explain.\n"
        "3. Use Markdown for clarity (bullet points, bold text).\n"
        "4. Keep the tone encouraging and professional."
    )

    # This template combines the database content with the student's actual query
    user_template = (
        "COURSE TITLE: {title}\n"
        "LESSON CONTENT:\n{content}\n\n"
        "STUDENT QUESTION: {question}"
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        ("human", user_template)
    ])

    chain = prompt | llm | StrOutputParser()
    
    return chain.invoke({
        "title": lesson_title,
        "content": lesson_content,
        "question": student_question
    })

def get_tutor_response(prompt_text: str, user_role: str):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found. Ensure it is set in your .env file.")
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", 
    temperature=0.7,
    google_api_key=api_key,
    model_kwargs={"api_version": "v1"}
    )
    # The prompt changes based on who is asking!
    if user_role == "instructor":
        system_message = (
            "You are an expert curriculum designer. Create a comprehensive lesson plan "
            "for a student. Use Markdown formatting. Include: \n"
            "1. A catchy Title\n"
            "2. Learning Objectives\n"
            "3. Detailed Content divided into sections\n"
            "4. A 'Key Takeaways' summary at the end."
        )
    else:
        system_message = "You are a helpful peer tutor. Explain this topic clearly and simply."
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        ("human", "The topic is: {user_input}")
    ])
    
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"user_input": prompt_text})

