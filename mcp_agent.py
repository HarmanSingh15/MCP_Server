from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_tool_calling_agent , AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from langchain.chat_models import init_chat_model 
from dotenv import load_dotenv
import asyncio 
from pydantic import BaseModel, Field, ValidationError
import re
import os
from typing import Optional

load_dotenv(override = True)

# class CodeEvaluationInput(BaseModel): trying pydantic 
#     file_path: str = Field(..., description="Path to the Python file to evaluate")
#     question: str = Field(default="Evaluate the provided code and give feedback and score from 0 to 10", description="The question related to the code file")




async def main(user_input):
    client = MultiServerMCPClient(
        {
            "feedback_API_server":{
                "url":"http://localhost:8000/mcp",
                "transport":"streamable_http",
            }
        }    
    )
    tool_list = await client.get_tools()
    
    model = init_chat_model("gemini-2.5-flash", model_provider="google_genai")

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful assistant with access to tools. 
        Use your general knowledge to answer questions when tools are not needed.
        Use the available tools when they can provide more accurate or specific information.
        Always provide helpful responses whether using tools or your general knowledge.
         
        you have full access to the file system, you can read any file.
        Always answer in a structured string format.
          
        you will be provided a question related to a python code file, you have to answer the question
        by using the tools available to you or use you general knowledge.
        if you use a tool, make sure to use the tool that is most relevant to the question.
        
        If the user asks to evaluate a python file:
         -Extract the file path from the input
         -Extract the question from the input
        then call the 'evaluate_code' tool with:
         -file_path: <the extracted file path>  
         -question: <the extracted question>  
        Always provide a structured responses 
         """),
        ("human", "Input: {input}"),
        ("placeholder", "{agent_scratchpad}")
    ])

    agent  = create_tool_calling_agent(model, tool_list, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tool_list, verbose=True)

    # user_message = {
    #     "message":[
    #         {
    #             "role": "user",
    #             "content": "Evaluate the file E:/LangChain/work/test.py and give feedback and score from 0 to 10"
    #         }
    #     ]
    # }


    response = await agent_executor.ainvoke({"input": user_input})
    print("feedback response: ", response['output'])

if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    user_input = ""
    while user_input.lower() != "exit":
        user_input = input("Enter your question or type (exit) to quit: ")
        if user_input.lower() != "exit":
            asyncio.run(main(user_input))