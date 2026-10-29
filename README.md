# PyLangchain

This project contains simple examples for learning LangChain and LangGraph with Google Gemini.

## Files

- `basic.py`: Shows how to use a Gemini model with LangChain prompts and output parsers. It currently runs a chain that asks the model for five comma-separated words about a topic.
- `langgraphbasic.py`: Contains small LangGraph examples, including:
  - A greeting graph
  - Adding and multiplying numbers
  - A sequence of graph nodes
  - Conditional graph paths
  - A looping number-guessing graph
  - A simple chatbot
  - A chatbot that remembers the conversation
- `logging.txt`: Stores the conversation log when the memory chatbot is enabled.

## Setup

Install the required packages:

```bash
pip install langchain langchain-core langgraph langchain-google-genai python-dotenv pydantic pandas
```

Create a `.env` file in the project folder and add your Google API key:

```env
GOOGLE_API_KEY=your_api_key_here
```

You can also choose a different Gemini model:

```env
GEMINI_MODEL=gemini-3.8-flash
```

## Run

Run the LangChain example:

```bash
python basic.py
```

The examples in `langgraphbasic.py` are disabled by default. Uncomment one function call at the bottom of the file, then run:

```bash
python langgraphbasic.py
```

For example, uncomment `#First_graph()` to run the first graph example.

## Note

These files are practice examples. Some imported packages are included for future LangChain and LangGraph experiments and may not be used by every example.
