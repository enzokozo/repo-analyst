"""Evaluates the agent with a fixed set of questions.

Run from the project root:
    python src/evaluate.py internacoes
    python src/evaluate.py ito

Output: results/<name>.csv. Fill the "correct" column with 1 or 0.
Each question uses a new session, so one answer can't influence the next.
The questions are in Portuguese because the test repositories are too.
"""
import csv
import os
import sys
import time

from agent import RepoAgent
from reader import read_text_files

PAUSE_SECONDS = 15

INTERNACOES_QUESTIONS = [
    # A: content that fits in the 10,000-character limit
    ("A", "Qual é a pergunta norteadora do projeto?", "Se a amplitude térmica extrema impacta mais as internações do que a queda da temperatura média"),
    ("A", "Qual é o total de internações validado no projeto?", "13.644"),
    ("A", "O que o caractere '-' significa nos dados do SIH/SUS?", "Zero ocorrências, não é dado faltante"),
    ("A", "Qual código o NASA POWER usa para valores ausentes?", "-999"),
    ("A", "Qual classe gera o relatório de qualidade em explorar.py?", "ProfileReport"),
    # B: content located after the 10,000-character cut
    ("B", "O que a função chave_texto faz em limpeza.py?", "Minúsculas, remove espaços das extremidades e elimina acentos"),
    ("B", "Quais codificações transformar_sih.py tenta ao ler o CSV, e em que ordem?", "utf-8 e depois latin1"),
    ("B", "Qual função de transformar_sih.py converte '..Janeiro/2010' em data?", "converter_periodo"),
    ("B", "Qual exceção transformar_nasa.py lança se a amplitude térmica for negativa?", "ValueError"),
    ("B", "Como obter_arquivo_mais_recente em limpeza.py escolhe o arquivo?", "Ordena pelo nome e pega o último"),
    # C: calculations on the CSVs, using the Python tool
    ("C", "Usando data/raw_internacoes/sih_sus_raw.csv, qual foi o total de internações em 2013?", "1918"),
    ("C", "Usando data/raw_internacoes/sih_sus_raw.csv, qual mês teve mais internações e quantas foram?", "Maio de 2014, 232"),
    ("C", "Usando data/raw_internacoes/sih_sus_raw.csv, qual faixa etária teve mais internações no total e quantas foram?", "80 anos e mais, 2782"),
    ("C", "Usando data/raw_internacoes/nasa_raw.csv, qual foi a amplitude térmica média diária (T2M_MAX - T2M_MIN) em 2015?", "12,69 °C"),
    ("C", "Usando data/raw_internacoes/nasa_raw.csv, em que dia a amplitude térmica (T2M_MAX - T2M_MIN) foi maior e qual foi o valor?", "23/09/2014 (ano 2014, DOY 266), 22,89 °C"),
    # D: no answer in the repository; the agent has to say so
    ("D", "Qual modelo de machine learning foi treinado neste projeto?", "Nenhum / não encontrou"),
    ("D", "Em qual banco de dados relacional os dados são salvos?", "Nenhum, usa arquivos / não encontrou"),
    ("D", "Em qual serviço de nuvem o projeto foi implantado?", "Não encontrou"),
    ("D", "Quem é o orientador deste projeto?", "Não encontrou"),
    ("D", "Qual foi a conclusão final do projeto sobre a amplitude térmica?", "Ainda não há conclusão; a camada Ouro não foi implementada"),
]

ITO_QUESTIONS = [
    # Answer in the code
    ("code", "Qual é o número mínimo de jogadores para iniciar uma rodada?", "2"),
    ("code", "Quantas cartas tem o baralho e quais são os valores?", "100 cartas, de 1 a 100"),
    ("code", "Quantas cores estão disponíveis para os jogadores?", "8"),
    ("code", "O que acontece com a cor de um jogador quando ele sai do jogo?", "Volta para a lista de cores disponíveis"),
    ("code", "Qual é a rota do WebSocket?", "/ws/{player_name}"),
    ("code", "get_game_state revela as cartas dos jogadores?", "Não"),
    # Files the reader does not load: .html and a UTF-16 requirements.txt
    ("skipped", "Em qual endereço o frontend se conecta ao WebSocket?", "ws://127.0.0.1:8000/ws/{name}"),
    ("skipped", "Qual versão do FastAPI o projeto usa?", "0.135.3"),
    # No answer in the repository
    ("none", "Em qual banco de dados o estado do jogo é salvo?", "Nenhum, fica em memória"),
    ("none", "Qual provedor de login o projeto usa?", "Nenhum / não encontrou"),
]

# Each test: questions, the context limits to compare and the repository folder
TESTS = {
    "internacoes": (INTERNACOES_QUESTIONS, [10000, 100000], "data/raw_internacoes"),
    "ito": (ITO_QUESTIONS, [100000], "data/raw_ito"),
}


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in TESTS:
        raise SystemExit(f"Usage: python src/evaluate.py [{' | '.join(TESTS)}]")

    name = sys.argv[1]
    questions, limits, repo_path = TESTS[name]

    files = read_text_files(repo_path)
    if not files:
        raise SystemExit(f"No files found in {repo_path}.")

    os.makedirs("results", exist_ok=True)
    with open(f"results/{name}.csv", "w", newline="", encoding="utf-8-sig") as output:
        writer = csv.writer(output, delimiter=";")
        writer.writerow(["limit", "group", "question", "expected", "answer", "correct"])

        for limit in limits:
            for group, question, expected in questions:
                print(f"[limit {limit}] group {group}: {question}")
                agent = RepoAgent()
                agent.start_session(files, repo_path, max_characters=limit)
                answer = agent.ask(question)
                writer.writerow([limit, group, question, expected, answer, ""])
                output.flush()
                time.sleep(PAUSE_SECONDS)

    print(f"Done: results/{name}.csv")


if __name__ == "__main__":
    main()
