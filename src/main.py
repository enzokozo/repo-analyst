import sys

from agent import RepoAgent
from logger import logger
from reader import read_text_files

def main():
    # Default to the sample repository, or use the folder passed in the command
    path_to_analyze = sys.argv[1] if len(sys.argv) > 1 else "data/raw_internacoes"
    logger.info(f"Reading repository files: {path_to_analyze}")

    files = read_text_files(path_to_analyze)

    if not files:
        # Warning: doesn't break the app, but needs attention
        logger.warning(f"No files found to analyze in {path_to_analyze}. Check the path and try again.")
        return

    logger.info(f"Analyzing {len(files)} files with the LLM...")

    # Create the agent and load the initial memory
    agent = RepoAgent()
    agent.start_session(files, path_to_analyze)

    # Terminal interface
    print("\n" + "="*55)
    print("🤖 REPO ANALYST STARTED")
    print("Ask about the files or type 'exit' to quit.")
    print("="*55)

    while True:
        question = input("\n 👤 You: ")

        # Exit condition
        if question.strip().lower() in ['exit', 'quit', 'sair']:
            print("🤖 Closing the assistant. See you next time!")
            logger.info("Session closed by the user.")
            break

        # Avoid sending an empty message to the API
        if not question.strip():
            continue

        # Call the model
        logger.info("Sending question to the model...")
        answer = agent.ask(question)

        print(f"🤖 Assistant: {answer}")

if __name__ == "__main__":
    main()
