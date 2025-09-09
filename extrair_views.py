import os
import re

import pandas as pd

# Caminho base do seu projeto Django
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Pasta onde salvar o Excel
PASTA_DESTINO = os.path.join(BASE_DIR, "Arquivos")
os.makedirs(PASTA_DESTINO, exist_ok=True)

# Lista para armazenar os nomes encontrados
nomes_views = []

# Expressão regular para encontrar 'view_name = "..."' ou 'view_name = \'...\''
regex_view_name = re.compile(r'view_name\s*=\s*[\'"]([\w\d_]+)[\'"]')

# Percorrer os arquivos .py do projeto
for root, _, files in os.walk(BASE_DIR):
    for file in files:
        if file.endswith(".py"):
            caminho_arquivo = os.path.join(root, file)
            with open(caminho_arquivo, "r", encoding="utf-8") as f:
                conteudo = f.read()
                encontrados = regex_view_name.findall(conteudo)
                for nome in encontrados:
                    nomes_views.append(
                        {
                            "view_name": nome,
                            "arquivo": os.path.relpath(caminho_arquivo, BASE_DIR),
                        }
                    )

# Remover duplicatas
df = pd.DataFrame(nomes_views).drop_duplicates().sort_values(by="view_name")

# Salvar em Excel
caminho_excel = os.path.join(PASTA_DESTINO, "Nomes_views.xlsx")
df.to_excel(caminho_excel, index=False)

print(f"Arquivo gerado em: {caminho_excel}")
