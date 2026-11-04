import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from utils.logger import logger
from utils.tools import save_technical_note, run_python_code

# Load the variables from the .env file
load_dotenv()

MAX_TOOL_ROUNDS = 3

class CodeAnalyzer:
    def __init__(self):
        # Create the model
        base_model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite",
                                            temperature=0,
                                            google_api_key=os.getenv("GOOGLE_API_KEY")
                                            )

        # Create the message memory
        self.chat_history = []

        # Connect the tools to the model
        tools = [save_technical_note, run_python_code]
        self.llm = base_model.bind_tools(tools)

        # Same model, but it has to answer without calling more tools
        self.final_llm = base_model.bind_tools(tools, tool_choice="none")

    def start_session(self, repo_data, max_characters=10000):
        """
        Takes all the files and injects them as a hidden system instruction.
        """
        try:
            # Build the context: turn the dictionary into a formatted string
            context = ""
            for path, content in repo_data.items():
                context += f"\n--- FILE: {path} ---\n {content}\n"

            # Limit the number of characters
            if len(context) > max_characters:
                logger.warning(f"Large context detected: {len(context)} characters. Truncating to avoid API errors...")
                context = context[:max_characters] + "\n\n... [CODE TRUNCATED FOR SAFETY] ..."

            # SystemMessage configures the model
            system_prompt = (
                "You are an Autonomous Agent for Code Analysis, Data and Software Engineering. "
                "Use strictly the code provided below as your knowledge base to answer the user's questions. "
                "If the answer is not in the code, say that you did not find it in the provided files. "
                "Always answer in the same language as the user's question.\n\n"
                "You have tools to save reports and to run Python code locally. "
                "If the user asks you to analyze spreadsheets (CSVs) or do complex calculations, WRITE AND RUN Python code using the 'run_python_code' tool. "
                "Always import the libraries you need in your code (e.g. import pandas as pd). "
                "Use a tool only when the answer is not in the files below. "
                "Python code runs from the project root and every repository file is inside data/raw/ "
                "(e.g. data/raw/src/main.py or data/raw/sales.csv). Ignore paths mentioned in the repository's documentation. "
                "Open text files with encoding='utf-8'. "
                f"\n\nCURRENT FILES READ AS TEXT:\n{context}"
            )

            # The first item in memory is the repository context
            self.chat_history = [SystemMessage(content=system_prompt)]
            logger.info("Session started with the repository context in memory.")
        except Exception as e:
            logger.error(f"Error starting session: {e}")
            raise

    def ask(self, question):
        """
        Receives the user's question, adds it to memory and generates the answer with the model.
        """
        try:
            # Add the user's question to memory
            self.chat_history.append(HumanMessage(content=question))

            # Send the full history to the model (repository + previous questions + new question)
            response = self.llm.invoke(self.chat_history)

            # Store the model's response in memory
            self.chat_history.append(response)

            # Let the model use tools for up to 3 rounds (e.g. read an error and try again)
            rounds = 0
            while response.tool_calls and rounds < MAX_TOOL_ROUNDS:
                rounds += 1
                for tool_call in response.tool_calls:
                    logger.info(f"Model decided to use the tool {tool_call['name']}")

                    if tool_call["name"] == "save_technical_note":
                        result = save_technical_note.invoke(tool_call["args"])
                    elif tool_call["name"] == "run_python_code":
                        result = run_python_code.invoke(tool_call["args"])
                    else:
                        result = f"Unknown tool: {tool_call['name']}"

                    logger.info(f"Tool args: {tool_call['args']}")
                    logger.info(f"Tool result: {str(result)[:300]}")

                    # Every tool sends its result back for the model to read
                    self.chat_history.append(ToolMessage(
                        content=result,
                        tool_call_id=tool_call["id"]
                    ))

                # In the last round, the model has to answer with what it already has
                model = self.final_llm if rounds == MAX_TOOL_ROUNDS else self.llm
                response = model.invoke(self.chat_history)
                self.chat_history.append(response)

            logger.info(f"rounds={rounds} pending_tools={len(response.tool_calls)} finish={response.response_metadata.get('finish_reason')} content={response.content!r}")
            return response.content
        except Exception as e:
            logger.error(f"Failed to communicate with the model: {e}")
            return "Sorry, an error occurred while getting the model's answer. Please try again later."
