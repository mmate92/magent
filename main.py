import os
import sys
from dotenv import load_dotenv
from openai import OpenAI
from prompts import system_prompt
import argparse
from call_function import available_functions, call_function

def main():
    # Get API Key
    load_dotenv()
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if api_key is None:
        raise RuntimeError("OR API key not found!")

    # Load client and parser
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )
    parser = argparse.ArgumentParser(description="Chatbot argument")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    # The -- prefix signals that it is optional, and action="store_true" signals that 
    # it operates as a toggle switch without needing an accompanying value.
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")


    args = parser.parse_args()


    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": args.user_prompt},
    ]

    for _ in range(20):
        # call the model, handle responses, etc.
        response = generate_content(client, messages)

        # Print usage info and response
        if not response.usage or not response.choices:
            raise RuntimeError("Failed response from OpenRouter!")
        
        if args.verbose:
            print(f"User prompt: {args.user_prompt}")
            print(f"Prompt tokens: {response.usage.prompt_tokens}")
            print(f"Response tokens: {response.usage.completion_tokens}")

        # Handle tool calls
        if response.choices[0].message.tool_calls:
            message = response.choices[0].message
            messages.append(message)
            for tool_call in response.choices[0].message.tool_calls:
                res = call_function(tool_call, args.verbose)
                if not res["content"]:
                    raise Exception(f"Error while calling function tool {tool_call.function.name}")
                if args.verbose:
                    print(f"-> {res['content']}")   
                messages.append(res)
        else: 
            print(response.choices[0].message.content)
            break

    else: 
        print(f"Maximum iterations ({20}) reached")
        sys.exit(1)

def generate_content(client, messages): 
    response = client.chat.completions.create(
        model="openrouter/free",
        messages=messages,
        temperature=0,
        tools=available_functions
    )

    return response

if __name__ == "__main__":
    main()
