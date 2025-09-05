from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
import asyncio

async def main():
    transport = StreamableHttpTransport("http://localhost:8000/mcp")
    client = Client(transport)
    await client._connect()

    tools = await client.list_tools()
    print("Available tools:", [tool.name for tool in tools])

    file_path = "E:/LangChain/work/test.py"
    question = "Evaluate the provided code and give feedback and score from 0 to 10"
    # with open(file_path, "r") as f:
    #    file_path = f.read().encode('utf-8')
    result = await client.call_tool("evaluate_code", {"file_path": file_path, "question": question})

    print("Server response :" , result)

    await client.close()
if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())    
