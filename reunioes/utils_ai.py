import io
import os

import fitz  # PyMuPDF
import openai
import requests
from django.conf import settings
from openai import OpenAI

from SGC.settings import OPENROUTER_API_KEY

from .utils_google_drive import download_file_from_drive

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMP_DIR = os.path.join(BASE_DIR, "temp")
openai.api_key = settings.OPENAI_API_KEY
client = OpenAI(api_key=settings.OPENAI_API_KEY)


# Cria a pasta temp se ela não existir
os.makedirs(TEMP_DIR, exist_ok=True)


def extrair_texto_pdfs_da_ata(ata):
    """
    Busca os arquivos PDF anexados a uma AtaReuniao (model ArquivoAta) no Google Drive,
    baixa para um arquivo temporário, extrai o texto e retorna tudo concatenado.
    """
    texto_total = ""

    arquivos = ata.arquivos.all()

    if not arquivos:
        return ""

    for arquivo in arquivos:
        file_id = arquivo.id_arquivo_drive
        if not file_id:
            continue

        temp_path = os.path.join(TEMP_DIR, f"{file_id}.pdf")
        try:
            download_file_from_drive(file_id, temp_path)
        except Exception as e:
            print(f"Erro ao baixar PDF {file_id}: {e}")
            continue

        try:
            with fitz.open(temp_path) as pdf:
                for pagina in pdf:
                    texto_total += pagina.get_text() + "\n"
        except Exception as e:
            print(f"Erro ao extrair texto do PDF {file_id}: {e}")

        try:
            os.remove(temp_path)
        except:
            pass

    return texto_total.strip()


def extrair_texto_itens_da_ata(ata):
    """
    Monta um texto concatenado com os itens da ata (ItemAta).
    """
    itens = ata.itens.all()
    if not itens:
        return ""

    texto = "Itens da Ata:\n"
    for item in itens:
        texto += f"- {item.categoria}: {item.descricao}\n"

    return texto.strip()


def gerar_resumo_openai(texto):
    """
    Envia o texto para a OpenAI (SDK novo) e retorna o resumo gerado.
    """
    prompt = f"Leia o conteúdo abaixo (texto de atas de reunião) e gere um resumo claro e objetivo com no máximo 10 linhas:\n\n{texto}"

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Troca aqui
            messages=[
                {
                    "role": "system",
                    "content": "Você é um assistente especialista em gerar resumos claros e objetivos de atas de reunião.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=400,
            temperature=0.5,
        )

        resumo = response.choices[0].message.content.strip()
        return resumo
    except Exception as e:
        print(f"Erro ao chamar OpenAI: {e}")
        return "Erro ao gerar resumo."


def gerar_resumo_openrouter(texto):
    prompt = f"Leia o conteúdo abaixo (texto de atas de reunião) e gere um resumo claro e objetivo com no máximo 10 linhas:\n\n{texto}"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://sgccro.dbsistemas.com.br/",  # Substitui pelo domínio do teu sistema ou deixa genérico
        "X-Title": "SGC Resumo",
    }

    data = {
        "model": "mistralai/mistral-small-3.2-24b-instruct",
        "messages": [
            {
                "role": "system",
                "content": "Você é um assistente especialista em gerar resumos claros e objetivos de atas de reunião.",
            },
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 400,
        "temperature": 0.5,
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions", json=data, headers=headers
        )
        response.raise_for_status()
        resumo = response.json()["choices"][0]["message"]["content"]
        return resumo.strip()
    except Exception as e:
        print(f"Erro ao chamar OpenRouter: {e}")
        return "Erro ao gerar resumo."


def gerar_resumo_ata(ata_id):
    from reunioes.models import AtaReuniao

    ata = AtaReuniao.objects.get(id=ata_id)

    # Extrai o texto dos PDFs
    texto = extrair_texto_pdfs_da_ata(ata)

    # Se não tiver PDF, usa os itens da ata
    if not texto.strip():
        texto = extrair_texto_itens_da_ata(ata)

    if not texto.strip():
        return "Nenhum conteúdo encontrado para resumir."

    # Troca aqui:
    resumo = gerar_resumo_openrouter(texto)

    ata.resumo = resumo

    return resumo
