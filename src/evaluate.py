"""Evaluates the agent: the same 20 questions with two context limits.

Run from the project root: python src/evaluate.py
Output: data/output/test_results.csv. Fill the "correct" column with 1 or 0.
Each question uses a new session, so one answer can't influence the next.
The questions are in Portuguese because the test repository (data/raw) is too.
"""
import csv
import time

from core.analyzer import CodeAnalyzer
from utils.reader import read_repository_file

LIMITS = [10000, 100000]
PAUSE_SECONDS = 5  # Increase this if the API complains about rate limits

QUESTIONS = [
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
    ("C", "Usando data/raw/sih_sus_raw.csv, qual foi o total de internações em 2013?", "1918"),
    ("C", "Usando data/raw/sih_sus_raw.csv, qual mês teve mais internações e quantas foram?", "Maio de 2014, 232"),
    ("C", "Usando data/raw/sih_sus_raw.csv, qual faixa etária teve mais internações no total e quantas foram?", "80 anos e mais, 2782"),
    ("C", "Usando data/raw/nasa_raw.csv, qual foi a amplitude térmica média diária (T2M_MAX - T2M_MIN) em 2015?", "12,69 °C"),
    ("C", "Usando data/raw/nasa_raw.csv, em que dia a amplitude térmica (T2M_MAX - T2M_MIN) foi maior e qual foi o valor?", "23/09/2014 (ano 2014, DOY 266), 22,89 °C"),
    # D: no answer in the repository; the agent has to say so
    ("D", "Qual modelo de machine learning foi treinado neste projeto?", "Nenhum / não encontrou"),
    ("D", "Em qual banco de dados relacional os dados são salvos?", "Nenhum, usa arquivos / não encontrou"),
    ("D", "Em qual serviço de nuvem o projeto foi implantado?", "Não encontrou"),
    ("D", "Quem é o orientador deste projeto?", "Não encontrou"),
    ("D", "Qual foi a conclusão final do projeto sobre a amplitude térmica?", "Ainda não há conclusão; a camada Ouro não foi implementada"),
]


def main():
    files = read_repository_file("data/raw")
    if not files:
        raise SystemExit("No files found in data/raw.")

    with open("data/output/test_results.csv", "w", newline="", encoding="utf-8-sig") as output:
        writer = csv.writer(output, delimiter=";")
        writer.writerow(["limit", "group", "question", "expected", "answer", "correct"])

        for limit in LIMITS:
            for group, question, expected in QUESTIONS:
                print(f"[limit {limit}] group {group}: {question}")
                agent = CodeAnalyzer()
                agent.start_session(files, max_characters=limit)
                answer = agent.ask(question)
                writer.writerow([limit, group, question, expected, answer, ""])
                output.flush()
                time.sleep(PAUSE_SECONDS)

    print("Done: data/output/test_results.csv")


if __name__ == "__main__":
    main()
