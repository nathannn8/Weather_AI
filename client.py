import asyncio
import os
from groq import Groq
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv

load_dotenv()

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

            groq_tools = [{
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.inputSchema
                }
            } for t in tools.tools]

            messages = [
                {"role": "system", "content": "You are a helpful and hyperintelligent assistant with access to live weather data and web search. Use get_weather for weather questions and tavily_search for everything else."},
            ]

            print("Chat started! Type 'quit' or 'exit' to stop.\n")

            while True:
                loop = asyncio.get_event_loop()
                user_input = await loop.run_in_executor(None, lambda: input("You: "))

                if user_input.lower() in ["quit", "exit"]:
                    print("AI: Bye!")
                    break

                messages.append({"role": "user", "content": user_input})

                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages,
                    tools=groq_tools
                )

                if response.choices[0].message.tool_calls:
                    for tool_call in response.choices[0].message.tool_calls:
                        tool_name = tool_call.function.name
                        tool_args = eval(tool_call.function.arguments)
                        result = await session.call_tool(tool_name, tool_args)
                        tool_data = result.content[0].text

                        messages.append({"role": "assistant", "content": str(response.choices[0].message)})
                        messages.append({"role": "tool", "content": tool_data, "tool_call_id": tool_call.id})

                    final = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=messages
                    )
                    reply = final.choices[0].message.content
                else:
                    reply = response.choices[0].message.content

                print(f"AI: {reply}\n")
                messages.append({"role": "assistant", "content": reply})

asyncio.run(main())