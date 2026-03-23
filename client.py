import asyncio
import os
from groq import Groq
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv

load_dotenv() 
print(os.getenv("GROQ_API_KEY"))

async def main():
    server_params = StdioServerParameters(
        command="python",
        args=["weather_server.py"]
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()

            client = Groq(api_key=os.getenv("GROQ_API_KEY"))

            user_input = input("Ask a weather question: ")

            groq_tools = [{
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.inputSchema
                }
            } for t in tools.tools]

            messages = [
                {"role": "system", "content": "You are a helpful weather assistant. Always use the get_weather tool for weather questions."},
                {"role": "user", "content": user_input}
            ]

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                tools=groq_tools
            )

            if response.choices[0].message.tool_calls:
                tool_call = response.choices[0].message.tool_calls[0]
                city = eval(tool_call.function.arguments)["city"]

                result = await session.call_tool("get_weather", {"city": city})
                weather_data = result.content[0].text

                messages.append({"role": "assistant", "content": str(response.choices[0].message)})
                messages.append({"role": "tool", "content": weather_data, "tool_call_id": tool_call.id})

                final = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages
                )
                print(final.choices[0].message.content)
            else:
                print(response.choices[0].message.content)

asyncio.run(main())