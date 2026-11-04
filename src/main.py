from utils.reader import read_repository_file
from core.analyzer import CodeAnalyzer
from utils.logger import logger

def main():
    path_to_analyze = "data/raw"
    logger.info(f"Reading repository files: {path_to_analyze}")

    files = read_repository_file(path_to_analyze)

    if not files:
        # Warning: doesn't break the app, but needs attention
        logger.warning(f"No files found to analyze in {path_to_analyze}. Check the path and try again.")
        return

    logger.info(f"Analyzing {len(files)} files with the LLM...")

    # Create the analyzer and load the initial memory
    analyzer = CodeAnalyzer()
    analyzer.start_session(files)

    # Terminal interface
    print("\n" + "="*55)
    print("🤖 CODE ANALYSIS ASSISTANT STARTED")
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
        answer = analyzer.ask(question)

        print(f"🤖 Assistant: {answer}")

if __name__ == "__main__":
    main()
