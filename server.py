from mcp.server.fastmcp import FastMCP 
from mcp.types import TextContent
from fastapi import UploadFile, Form
from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")

mcp = FastMCP("code_feedback")
model = ChatGoogleGenerativeAI(model = "gemini-2.0-flash", model_provider="google_genai")

@mcp.tool()
def evaluate_code(file_path: str, question:str)-> str:
    """
    You will be provided a python file. 
    
    This Tool Analyze the code for correctness, clarity and completeness.
    Give a score from 0 to 10,  and a short feedback (make 20 words)
    You have full access to the file system, you can read any file.
    Respond in format: "score":<int>, "feedback": <string>.

    """
    try:
        with open(file_path, "r") as f:
            code = f.read()
    except Exception as e:
        return f"Error reading file: {e}"
    # temp_path = f"{file_path}"
    # with open(temp_path, "r")as f:
    #     code = f.read()
    #     print(code)
    

    prompt = f"""
    you are a python code evaluator
    the question is : {question}:
    
    {code}

    you will be provided a python file as input.
    while using this tool, the user will provide a question related to the code file, Answer it accurately according to you intelligence or call this tool

    Analyze the code for correctness, clarity and completeness.
    Give a score from 0 to 10,  and a short feedback (make 20 words).
    Respond only in a string format.
    Respond strictly in this format: "score: <int>, feedback: <string>"

    You have full access to the file system, you can read any file.
    """
    response = model.invoke([HumanMessage(content = prompt)])
    cleaned_output = response.content.strip()
    # .replace("```python", "").replace("```", "")
    
    # return response.content
    return cleaned_output

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
    





   
