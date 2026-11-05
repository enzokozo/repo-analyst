# Repo Analyst

A small terminal agent that answers questions about a code repository. It reads the repository's text files and can write and run Python to analyze data files such as CSVs.

I built it as a personal project to learn about LLMs and agents. It has no real users, so I measure it with my own test questions.

## How it works

1. `src/reader.py` loads the `.py`, `.txt`, `.md` and `.js` files from `data/raw`.
2. `src/agent.py` puts those files in the system prompt and keeps the chat history.
3. The model answers directly or calls a tool: `run_python_code` or `save_technical_note`.
4. Tool results go back to the model for up to 3 rounds. In the last round, the model has to answer without tools.

## How to run

Requires Python and a Gemini API key.

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
GOOGLE_API_KEY=your_key_here
```

Put the repository you want to analyze in `data/raw`, then run:

```bash
python src/main.py
```

## Evaluation

I graded the answers by hand against expected answers. The model is `gemini-3.5-flash-lite`.

| Version | Test | Context limit | Correct |
|---|---|---|---|
| Baseline | 20 questions on `projeto-internacoes-itajuba` | 10,000 characters | 12/20 |
| Baseline | Same questions | 100,000 characters | 16/20 |
| After fixes | Same questions | 10,000 characters | 15/20 |
| After fixes | Same questions | 100,000 characters | 20/20 |
| Final | 10 new questions on a repository the agent had not seen (`ito`) | 100,000 characters | 8/10 |

Run them with `python src/evaluate.py internacoes` and `python src/evaluate.py ito`. Each one needs its test repository in `data/raw`. The graded answers are in `results/`.

These are small samples. I adjusted the agent while looking at the 20 questions, so the 8/10 is the fairer number.

## Known limitations

- **Files it can't see:** the reader skips `.html` files and files that aren't UTF-8. The agent may then say the information doesn't exist instead of checking.
- **Unsafe code execution:** the agent runs model-generated code with `exec()`, with no isolation. That code can reach other files in the project, including `.env`. Only use it on repositories you trust.
- **Large repositories:** content beyond the context limit is cut, and the agent can answer with confidence without having seen it.
- **Token use:** every call resends the whole context, which can hit the API's rate limits.

## Next steps

- Let the agent list and read files on demand instead of loading everything up front.
- Run generated code in a container.
- Add more repositories and questions to the evaluation.
