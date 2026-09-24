import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.environ.get("OPENROUTER_API_KEY")
if api_key == None:
    raise RuntimeError("OR API key not found!")



client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

def main():
    print("Hello from magent!")


if __name__ == "__main__":
    main()
