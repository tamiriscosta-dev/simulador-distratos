

import streamlit as st
from datetime import date, datetime
import pdfplumber
import re
import pandas as pd
import os

st.set_page_config(page_title="Simulador Score de Venda", page_icon="🏡", layout="wide")

st.title("🏡 Simulador de Score de Venda — URBA")
st.markdown("---")

# ─────────────────────────────────────────
# DADOS DO EMPREENDIMENTO
# ─────────────────────────────────────────

UNIDADES = [
    "SMART URBA RESERVA - QUADRA 01 - LOTE 0001","SMART URBA RESERVA - QUADRA 01 - LOTE 0002","SMART URBA RESERVA - QUADRA 01 - LOTE 0003","SMART URBA RESERVA - QUADRA 01 - LOTE 0004","SMART URBA RESERVA - QUADRA 01 - LOTE 0005","SMART URBA RESERVA - QUADRA 01 - LOTE 0006","SMART URBA RESERVA - QUADRA 01 - LOTE 0007","SMART URBA RESERVA - QUADRA 01 - LOTE 0008","SMART URBA RESERVA - QUADRA 01 - LOTE 0009","SMART URBA RESERVA - QUADRA 01 - LOTE 0010","SMART URBA RESERVA - QUADRA 01 - LOTE 0011","SMART URBA RESERVA - QUADRA 01 - LOTE 0012","SMART URBA RESERVA - QUADRA 01 - LOTE 0013","SMART URBA RESERVA - QUADRA 01 - LOTE 0014","SMART URBA RESERVA - QUADRA 01 - LOTE 0015","SMART URBA RESERVA - QUADRA 01 - LOTE 0016","SMART URBA RESERVA - QUADRA 01 - LOTE 0017","SMART URBA RESERVA - QUADRA 01 - LOTE 0018","SMART URBA RESERVA - QUADRA 01 - LOTE 0019",
    "SMART URBA RESERVA - QUADRA 02 - LOTE 0001","SMART URBA RESERVA - QUADRA 02 - LOTE 0002","SMART URBA RESERVA - QUADRA 02 - LOTE 0003","SMART URBA RESERVA - QUADRA 02 - LOTE 0004","SMART URBA RESERVA - QUADRA 02 - LOTE 0005","SMART URBA RESERVA - QUADRA 02 - LOTE 0006","SMART URBA RESERVA - QUADRA 02 - LOTE 0007","SMART URBA RESERVA - QUADRA 02 - LOTE 0008","SMART URBA RESERVA - QUADRA 02 - LOTE 0009","SMART URBA RESERVA - QUADRA 02 - LOTE 0010","SMART URBA RESERVA - QUADRA 02 - LOTE 0011","SMART URBA RESERVA - QUADRA 02 - LOTE 0012","SMART URBA RESERVA - QUADRA 02 - LOTE 0013","SMART URBA RESERVA - QUADRA 02 - LOTE 0014","SMART URBA RESERVA - QUADRA 02 - LOTE 0015","SMART URBA RESERVA - QUADRA 02 - LOTE 0016","SMART URBA RESERVA - QUADRA 02 - LOTE 0017","SMART URBA RESERVA - QUADRA 02 - LOTE 0018","SMART URBA RESERVA - QUADRA 02 - LOTE 0019","SMART URBA RESERVA - QUADRA 02 - LOTE 0020","SMART URBA RESERVA - QUADRA 02 - LOTE 0021","SMART URBA RESERVA - QUADRA 02 - LOTE 0022","SMART URBA RESERVA - QUADRA 02 - LOTE 0023","SMART URBA RESERVA - QUADRA 02 - LOTE 0024","SMART URBA RESERVA - QUADRA 02 - LOTE 0025","SMART URBA RESERVA - QUADRA 02 - LOTE 0026","SMART URBA RESERVA - QUADRA 02 - LOTE 0027","SMART URBA RESERVA - QUADRA 02 - LOTE 0028","SMART URBA RESERVA - QUADRA 02 - LOTE 0029","SMART URBA RESERVA - QUADRA 02 - LOTE 0030","SMART URBA RESERVA - QUADRA 02 - LOTE 0031","SMART URBA RESERVA - QUADRA 02 - LOTE 0032","SMART URBA RESERVA - QUADRA 02 - LOTE 0033","SMART URBA RESERVA - QUADRA 02 - LOTE 0034","SMART URBA RESERVA - QUADRA 02 - LOTE 0035","SMART URBA RESERVA - QUADRA 02 - LOTE 0036","SMART URBA RESERVA - QUADRA 02 - LOTE 0037","SMART URBA RESERVA - QUADRA 02 - LOTE 0038","SMART URBA RESERVA - QUADRA 02 - LOTE 0039",
    "SMART URBA RESERVA - QUADRA 03 - LOTE 0001","SMART URBA RESERVA - QUADRA 03 - LOTE 0002","SMART URBA RESERVA - QUADRA 03 - LOTE 0003","SMART URBA RESERVA - QUADRA 03 - LOTE 0004","SMART URBA RESERVA - QUADRA 03 - LOTE 0005","SMART URBA RESERVA - QUADRA 03 - LOTE 0006","SMART URBA RESERVA - QUADRA 03 - LOTE 0007","SMART URBA RESERVA - QUADRA 03 - LOTE 0008","SMART URBA RESERVA - QUADRA 03 - LOTE 0009","SMART URBA RESERVA - QUADRA 03 - LOTE 0010","SMART URBA RESERVA - QUADRA 03 - LOTE 0011","SMART URBA RESERVA - QUADRA 03 - LOTE 0012","SMART URBA RESERVA - QUADRA 03 - LOTE 0013","SMART URBA RESERVA - QUADRA 03 - LOTE 0014","SMART URBA RESERVA - QUADRA 03 - LOTE 0015","SMART URBA RESERVA - QUADRA 03 - LOTE 0016","SMART URBA RESERVA - QUADRA 03 - LOTE 0017","SMART URBA RESERVA - QUADRA 03 - LOTE 0018","SMART URBA RESERVA - QUADRA 03 - LOTE 0019","SMART URBA RESERVA - QUADRA 03 - LOTE 0020","SMART URBA RESERVA - QUADRA 03 - LOTE 0021","SMART URBA RESERVA - QUADRA 03 - LOTE 0022","SMART URBA RESERVA - QUADRA 03 - LOTE 0023","SMART URBA RESERVA - QUADRA 03 - LOTE 0024","SMART URBA RESERVA - QUADRA 03 - LOTE 0025","SMART URBA RESERVA - QUADRA 03 - LOTE 0026","SMART URBA RESERVA - QUADRA 03 - LOTE 0027","SMART URBA RESERVA - QUADRA 03 - LOTE 0028",
    "SMART URBA RESERVA - QUADRA 04 - LOTE 0001","SMART URBA RESERVA - QUADRA 04 - LOTE 0002","SMART URBA RESERVA - QUADRA 04 - LOTE 0003","SMART URBA RESERVA - QUADRA 04 - LOTE 0004","SMART URBA RESERVA - QUADRA 04 - LOTE 0005","SMART URBA RESERVA - QUADRA 04 - LOTE 0006","SMART URBA RESERVA - QUADRA 04 - LOTE 0007","SMART URBA RESERVA - QUADRA 04 - LOTE 0008","SMART URBA RESERVA - QUADRA 04 - LOTE 0009","SMART URBA RESERVA - QUADRA 04 - LOTE 0010","SMART URBA RESERVA - QUADRA 04 - LOTE 0011","SMART URBA RESERVA - QUADRA 04 - LOTE 0012","SMART URBA RESERVA - QUADRA 04 - LOTE 0013","SMART URBA RESERVA - QUADRA 04 - LOTE 0014","SMART URBA RESERVA - QUADRA 04 - LOTE 0015","SMART URBA RESERVA - QUADRA 04 - LOTE 0016","SMART URBA RESERVA - QUADRA 04 - LOTE 0017","SMART URBA RESERVA - QUADRA 04 - LOTE 0018","SMART URBA RESERVA - QUADRA 04 - LOTE 0019","SMART URBA RESERVA - QUADRA 04 - LOTE 0020","SMART URBA RESERVA - QUADRA 04 - LOTE 0021","SMART URBA RESERVA - QUADRA 04 - LOTE 0022","SMART URBA RESERVA - QUADRA 04 - LOTE 0023","SMART URBA RESERVA - QUADRA 04 - LOTE 0024","SMART URBA RESERVA - QUADRA 04 - LOTE 0025","SMART URBA RESERVA - QUADRA 04 - LOTE 0026","SMART URBA RESERVA - QUADRA 04 - LOTE 0027","SMART URBA RESERVA - QUADRA 04 - LOTE 0028","SMART URBA RESERVA - QUADRA 04 - LOTE 0029","SMART URBA RESERVA - QUADRA 04 - LOTE 0030","SMART URBA RESERVA - QUADRA 04 - LOTE 0031","SMART URBA RESERVA - QUADRA 04 - LOTE 0032","SMART URBA RESERVA - QUADRA 04 - LOTE 0033","SMART URBA RESERVA - QUADRA 04 - LOTE 0034","SMART URBA RESERVA - QUADRA 04 - LOTE 0035","SMART URBA RESERVA - QUADRA 04 - LOTE 0036","SMART URBA RESERVA - QUADRA 04 - LOTE 0037","SMART URBA RESERVA - QUADRA 04 - LOTE 0038","SMART URBA RESERVA - QUADRA 04 - LOTE 0039","SMART URBA RESERVA - QUADRA 04 - LOTE 0040","SMART URBA RESERVA - QUADRA 04 - LOTE 0041","SMART URBA RESERVA - QUADRA 04 - LOTE 0042","SMART URBA RESERVA - QUADRA 04 - LOTE 0043","SMART URBA RESERVA - QUADRA 04 - LOTE 0044",
    "SMART URBA RESERVA - QUADRA 05 - LOTE 0001","SMART URBA RESERVA - QUADRA 05 - LOTE 0002","SMART URBA RESERVA - QUADRA 05 - LOTE 0003","SMART URBA RESERVA - QUADRA 05 - LOTE 0004","SMART URBA RESERVA - QUADRA 05 - LOTE 0005","SMART URBA RESERVA - QUADRA 05 - LOTE 0006","SMART URBA RESERVA - QUADRA 05 - LOTE 0007","SMART URBA RESERVA - QUADRA 05 - LOTE 0008","SMART URBA RESERVA - QUADRA 05 - LOTE 0009","SMART URBA RESERVA - QUADRA 05 - LOTE 0010","SMART URBA RESERVA - QUADRA 05 - LOTE 0011","SMART URBA RESERVA - QUADRA 05 - LOTE 0012","SMART URBA RESERVA - QUADRA 05 - LOTE 0013","SMART URBA RESERVA - QUADRA 05 - LOTE 0014","SMART URBA RESERVA - QUADRA 05 - LOTE 0015","SMART URBA RESERVA - QUADRA 05 - LOTE 0016","SMART URBA RESERVA - QUADRA 05 - LOTE 0017","SMART URBA RESERVA - QUADRA 05 - LOTE 0018","SMART URBA RESERVA - QUADRA 05 - LOTE 0019","SMART URBA RESERVA - QUADRA 05 - LOTE 0020","SMART URBA RESERVA - QUADRA 05 - LOTE 0021","SMART URBA RESERVA - QUADRA 05 - LOTE 0022","SMART URBA RESERVA - QUADRA 05 - LOTE 0023","SMART URBA RESERVA - QUADRA 05 - LOTE 0024","SMART URBA RESERVA - QUADRA 05 - LOTE 0025","SMART URBA RESERVA - QUADRA 05 - LOTE 0026","SMART URBA RESERVA - QUADRA 05 - LOTE 0027","SMART URBA RESERVA - QUADRA 05 - LOTE 0028","SMART URBA RESERVA - QUADRA 05 - LOTE 0029","SMART URBA RESERVA - QUADRA 05 - LOTE 0030","SMART URBA RESERVA - QUADRA 05 - LOTE 0031","SMART URBA RESERVA - QUADRA 05 - LOTE 0032","SMART URBA RESERVA - QUADRA 05 - LOTE 0033","SMART URBA RESERVA - QUADRA 05 - LOTE 0034","SMART URBA RESERVA - QUADRA 05 - LOTE 0035","SMART URBA RESERVA - QUADRA 05 - LOTE 0036","SMART URBA RESERVA - QUADRA 05 - LOTE 0037","SMART URBA RESERVA - QUADRA 05 - LOTE 0038","SMART URBA RESERVA - QUADRA 05 - LOTE 0039","SMART URBA RESERVA - QUADRA 05 - LOTE 0040","SMART URBA RESERVA - QUADRA 05 - LOTE 0041","SMART URBA RESERVA - QUADRA 05 - LOTE 0042","SMART URBA RESERVA - QUADRA 05 - LOTE 0043","SMART URBA RESERVA - QUADRA 05 - LOTE 0044","SMART URBA RESERVA - QUADRA 05 - LOTE 0045","SMART URBA RESERVA - QUADRA 05 - LOTE 0046","SMART URBA RESERVA - QUADRA 05 - LOTE 0047","SMART URBA RESERVA - QUADRA 05 - LOTE 0048","SMART URBA RESERVA - QUADRA 05 - LOTE 0049","SMART URBA RESERVA - QUADRA 05 - LOTE 0050","SMART URBA RESERVA - QUADRA 05 - LOTE 0051","SMART URBA RESERVA - QUADRA 05 - LOTE 0052","SMART URBA RESERVA - QUADRA 05 - LOTE 0053","SMART URBA RESERVA - QUADRA 05 - LOTE 0054","SMART URBA RESERVA - QUADRA 05 - LOTE 0055","SMART URBA RESERVA - QUADRA 05 - LOTE 0056","SMART URBA RESERVA - QUADRA 05 - LOTE 0057","SMART URBA RESERVA - QUADRA 05 - LOTE 0058","SMART URBA RESERVA - QUADRA 05 - LOTE 0059","SMART URBA RESERVA - QUADRA 05 - LOTE 0060","SMART URBA RESERVA - QUADRA 05 - LOTE 0061","SMART URBA RESERVA - QUADRA 05 - LOTE 0062","SMART URBA RESERVA - QUADRA 05 - LOTE 0063",
    "SMART URBA RESERVA - QUADRA 06 - LOTE 0001","SMART URBA RESERVA - QUADRA 06 - LOTE 0002","SMART URBA RESERVA - QUADRA 06 - LOTE 0003","SMART URBA RESERVA - QUADRA 06 - LOTE 0004","SMART URBA RESERVA - QUADRA 06 - LOTE 0005","SMART URBA RESERVA - QUADRA 06 - LOTE 0006","SMART URBA RESERVA - QUADRA 06 - LOTE 0007","SMART URBA RESERVA - QUADRA 06 - LOTE 0008","SMART URBA RESERVA - QUADRA 06 - LOTE 0009","SMART URBA RESERVA - QUADRA 06 - LOTE 0010","SMART URBA RESERVA - QUADRA 06 - LOTE 0011","SMART URBA RESERVA - QUADRA 06 - LOTE 0012","SMART URBA RESERVA - QUADRA 06 - LOTE 0013","SMART URBA RESERVA - QUADRA 06 - LOTE 0014","SMART URBA RESERVA - QUADRA 06 - LOTE 0015","SMART URBA RESERVA - QUADRA 06 - LOTE 0016",
    "SMART URBA RESERVA - QUADRA 07 - LOTE 0001","SMART URBA RESERVA - QUADRA 07 - LOTE 0002","SMART URBA RESERVA - QUADRA 07 - LOTE 0003","SMART URBA RESERVA - QUADRA 07 - LOTE 0004","SMART URBA RESERVA - QUADRA 07 - LOTE 0005","SMART URBA RESERVA - QUADRA 07 - LOTE 0006","SMART URBA RESERVA - QUADRA 07 - LOTE 0007","SMART URBA RESERVA - QUADRA 07 - LOTE 0008","SMART URBA RESERVA - QUADRA 07 - LOTE 0009","SMART URBA RESERVA - QUADRA 07 - LOTE 0010","SMART URBA RESERVA - QUADRA 07 - LOTE 0011","SMART URBA RESERVA - QUADRA 07 - LOTE 0012","SMART URBA RESERVA - QUADRA 07 - LOTE 0013","SMART URBA RESERVA - QUADRA 07 - LOTE 0014","SMART URBA RESERVA - QUADRA 07 - LOTE 0015","SMART URBA RESERVA - QUADRA 07 - LOTE 0016","SMART URBA RESERVA - QUADRA 07 - LOTE 0017","SMART URBA RESERVA - QUADRA 07 - LOTE 0018","SMART URBA RESERVA - QUADRA 07 - LOTE 0019","SMART URBA RESERVA - QUADRA 07 - LOTE 0020","SMART URBA RESERVA - QUADRA 07 - LOTE 0021","SMART URBA RESERVA - QUADRA 07 - LOTE 0022",
    "SMART URBA RESERVA - QUADRA 08 - LOTE 0001","SMART URBA RESERVA - QUADRA 08 - LOTE 0002","SMART URBA RESERVA - QUADRA 08 - LOTE 0003","SMART URBA RESERVA - QUADRA 08 - LOTE 0004","SMART URBA RESERVA - QUADRA 08 - LOTE 0005","SMART URBA RESERVA - QUADRA 08 - LOTE 0006","SMART URBA RESERVA - QUADRA 08 - LOTE 0007","SMART URBA RESERVA - QUADRA 08 - LOTE 0008","SMART URBA RESERVA - QUADRA 08 - LOTE 0009","SMART URBA RESERVA - QUADRA 08 - LOTE 0010","SMART URBA RESERVA - QUADRA 08 - LOTE 0011","SMART URBA RESERVA - QUADRA 08 - LOTE 0012","SMART URBA RESERVA - QUADRA 08 - LOTE 0013","SMART URBA RESERVA - QUADRA 08 - LOTE 0014","SMART URBA RESERVA - QUADRA 08 - LOTE 0015","SMART URBA RESERVA - QUADRA 08 - LOTE 0016","SMART URBA RESERVA - QUADRA 08 - LOTE 0017","SMART URBA RESERVA - QUADRA 08 - LOTE 0018","SMART URBA RESERVA - QUADRA 08 - LOTE 0019","SMART URBA RESERVA - QUADRA 08 - LOTE 0020","SMART URBA RESERVA - QUADRA 08 - LOTE 0021","SMART URBA RESERVA - QUADRA 08 - LOTE 0022","SMART URBA RESERVA - QUADRA 08 - LOTE 0023","SMART URBA RESERVA - QUADRA 08 - LOTE 0024","SMART URBA RESERVA - QUADRA 08 - LOTE 0025","SMART URBA RESERVA - QUADRA 08 - LOTE 0026","SMART URBA RESERVA - QUADRA 08 - LOTE 0027","SMART URBA RESERVA - QUADRA 08 - LOTE 0028","SMART URBA RESERVA - QUADRA 08 - LOTE 0029","SMART URBA RESERVA - QUADRA 08 - LOTE 0030","SMART URBA RESERVA - QUADRA 08 - LOTE 0031","SMART URBA RESERVA - QUADRA 08 - LOTE 0032","SMART URBA RESERVA - QUADRA 08 - LOTE 0033","SMART URBA RESERVA - QUADRA 08 - LOTE 0034","SMART URBA RESERVA - QUADRA 08 - LOTE 0035","SMART URBA RESERVA - QUADRA 08 - LOTE 0036","SMART URBA RESERVA - QUADRA 08 - LOTE 0037","SMART URBA RESERVA - QUADRA 08 - LOTE 0038","SMART URBA RESERVA - QUADRA 08 - LOTE 0039","SMART URBA RESERVA - QUADRA 08 - LOTE 0040","SMART URBA RESERVA - QUADRA 08 - LOTE 0041","SMART URBA RESERVA - QUADRA 08 - LOTE 0042","SMART URBA RESERVA - QUADRA 08 - LOTE 0043","SMART URBA RESERVA - QUADRA 08 - LOTE 0044",
]

EMPREENDIMENTO = "SMART URBA RESERVA"
TIPO_PRODUTO = "SMART"

# ─────────────────────────────────────────
# FUNÇÕES AUXILIARES
# ─────────────────────────────────────────

def extrair_dados_spc(pdf_file):
    """
    Extrai Score de Crédito (Risco) e Renda Presumida do PDF do SPC.
    Baseado no layout padrão SPC Brasil:
      - Score/Risco: linha com 'RISCO DE CREDITO' seguida de letra A-F
      - Renda Presumida: linha com 'RENDA' e valor monetário
    """
    score = None
    renda = None
    try:
        with pdfplumber.open(pdf_file) as pdf:
            texto = ""
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    texto += t + "\n"

        texto_upper = texto.upper()

        # ── EXTRAÇÃO DO SCORE / RISCO DE CRÉDITO ──────────────────────────
        # Padrão 1: "RISCO DE CREDITO C" ou "RISCO DE CRÉDITO: C"
        match_risco = re.search(
            r'RISCO\s+DE\s+CR[EÉ]DITO[\s:]+([A-F])',
            texto_upper
        )
        # Padrão 2: "SCORE C" ou "SCORE: C" ou "SCORE CREDITO C"
        match_score_direto = re.search(
            r'SCORE[\s\w]*?[\s:]+([A-F])\b',
            texto_upper
        )
        # Padrão 3: letra isolada após "CLASSIFICAÇÃO"
        match_classif = re.search(
            r'CLASSIFICA[CÇ][AÃ]O[\s:]+([A-F])\b',
            texto_upper
        )

        letra_encontrada = None
        if match_risco:
            letra_encontrada = match_risco.group(1)
        elif match_score_direto:
            letra_encontrada = match_score_direto.group(1)
        elif match_classif:
            letra_encontrada = match_classif.group(1)

        if letra_encontrada:
            if letra_encontrada in ['A', 'B']:
                score = 'A - B'
            elif letra_encontrada in ['C', 'D']:
                score = 'C - D'
            else:
                score = 'E - F'

        # ── EXTRAÇÃO DA RENDA PRESUMIDA ────────────────────────────────────
        # Padrão 1: "RENDA PRESUMIDA R$ 8.870,00" ou "RENDA PRESUMIDA: 8.870,00"
        match_renda = re.search(
            r'RENDA\s+PRESUMIDA[\s:R$]*([0-9]{1,3}(?:\.[0-9]{3})*(?:,[0-9]{2})?)',
            texto_upper
        )
        # Padrão 2: "RENDA ESTIMADA" como fallback
        if not match_renda:
            match_renda = re.search(
                r'RENDA\s+ESTIMADA[\s:R$]*([0-9]{1,3}(?:\.[0-9]{3})*(?:,[0-9]{2})?)',
                texto_upper
            )
        # Padrão 3: "RENDA R$" genérico como último recurso
        if not match_renda:
            match_renda = re.search(
                r'RENDA[\s:]+R?\$?\s*([0-9]{1,3}(?:\.[0-9]{3})*(?:,[0-9]{2})?)',
                texto_upper
            )

        if match_renda:
            valor_str = match_renda.group(1)
            # Converte formato brasileiro: 8.870,00 -> 8870.00
            valor_str = valor_str.replace('.', '').replace(',', '.')
            try:
                renda = float(valor_str)
            except ValueError:
                renda = None

    except Exception as e:
        st.warning(f"Erro ao processar PDF: {e}")

    return score, renda


def classificar_score(score_str):
    notas = {'A - B': 5, 'C - D': 3, 'E - F': 1}
    return notas.get(score_str, 1)


def calcular_idade(data_nasc):
    if data_nasc is None:
        return None
    hoje = date.today()
    return hoje.year - data_nasc.year - (
        (hoje.month, hoje.day) < (data_nasc.month, data_nasc.day)
    )


def faixa_idade_str(data_nasc):
    idade = calcular_idade(data_nasc)
    if idade is None:
        return "—"
    if idade < 25:
        return "ATÉ 25 ANOS"
    elif idade <= 35:
        return "25 A 35 ANOS"
    elif idade <= 45:
        return "35 A 45 ANOS"
    elif idade <= 60:
        return "45 A 60 ANOS"
    else:
        return "60+ ANOS"


def classificar_idade(data_nasc):
    idade = calcular_idade(data_nasc)
    if idade is None:
        return 0
    if idade < 25:
        return 2
    elif idade <= 35:
        return 1
    elif idade <= 45:
        return 3
    elif idade <= 60:
        return 4
    else:
        return 5


def classificar_estado_civil(ec):
    notas = {'CASADO(A)': 3, 'DIVORCIADO(A)': 2, 'SOLTEIRO(A)': 1}
    return notas.get(ec, 1)


def classificar_plano(plano):
    notas = {
        'CURTO PRAZO (1 A 48X)': 5,
        'MÉDIO PRAZO (49 A 70X)': 3,
        'MÉDIO LONGO (71 A 144X)': 2,
        'LONGO PRAZO (145 A 180X)': 1,
    }
    return notas.get(plano, 1)


def classificar_tipo_produto(tp):
    notas = {
        'LOTEAMENTO FECHADO': 4,
        'SMART': 3,
        'CONDOMÍNIO': 2,
        'LOTEAMENTO ABERTO': 1,
    }
    return notas.get(tp, 1)


def classificar_faixa_renda(renda):
    if not renda or renda == 0:
        return 0, "—"
    if renda <= 2500:
        return 1, "ATÉ R$ 2.500"
    elif renda <= 5000:
        return 1, "R$ 2.501 A R$ 5.000"
    elif renda <= 7500:
        return 2, "R$ 5.001 A R$ 7.500"
    elif renda <= 10000:
        return 3, "R$ 7.501 A R$ 10.000"
    elif renda <= 15000:
        return 4, "R$ 10.001 A R$ 15.000"
    else:
        return 5, "ACIMA DE R$ 15.000"


def classificar_comprometimento(comp_pct):
    if comp_pct is None:
        return 0, "—"
    if comp_pct <= 10:
        return 5, "ATÉ 10%"
    elif comp_pct <= 20:
        return 4, "10% A 20%"
    elif comp_pct <= 30:
        return 3, "20% A 30%"
    elif comp_pct <= 50:
        return 2, "30% A 50%"
    elif comp_pct <= 100:
        return 1, "50% A 100%"
    else:
        return 1, "ACIMA DE 100%"


def classificar_ato(pct_ato):
    if pct_ato > 4.0:
        return 5
    elif pct_ato >= 3.0:
        return 3
    elif pct_ato >= 2.0:
        return 4
    elif pct_ato >= 1.0:
        return 2
    else:
        return 1


def calcular_score_total(n_idade, n_ato, n_score, n_renda, n_plano, n_ec, n_tp, n_comp):
    return (
        (n_idade * 1) +
        (n_ato   * 5) +
        (n_score * 5) +
        (n_renda * 4) +
        (n_plano * 4) +
        (n_ec    * 1) +
        (n_tp    * 3) +
        (n_comp  * 4)
    )


def classificar_venda(total):
    if total >= 90:
        return "🟢 BAIXO RISCO", "success"
    elif total >= 61:
        return "🟡 RISCO MODERADO", "warning"
    else:
        return "🔴 ALTO RISCO", "error"


def gerar_sugestoes(n_ato, n_score, n_renda, n_plano, n_comp, total):
    """
    Gera sugestões inteligentes e quantificadas para reduzir o risco.
    Calcula quanto cada variável contribuiria se melhorada ao máximo.
    """
    sugs = []
    if total >= 90:
        return sugs  # Já é baixo risco

    # Ganho potencial por variável se melhorada ao máximo
    ganho_ato   = (5 - n_ato)   * 5
    ganho_score = (5 - n_score) * 5
    ganho_renda = (5 - n_renda) * 4
    ganho_plano = (5 - n_plano) * 4
    ganho_comp  = (5 - n_comp)  * 4

    falta_moderado = max(0, 61 - total)
    falta_baixo    = max(0, 90 - total)

    if total < 61:
        sugs.append(f"⚠️ **Score atual: {total}/130** — Faltam **{falta_moderado} pontos** para RISCO MODERADO e **{falta_baixo} pontos** para BAIXO RISCO.")
    else:
        sugs.append(f"⚠️ **Score atual: {total}/130** — Faltam **{falta_baixo} pontos** para BAIXO RISCO.")

    sugs.append("---")
    sugs.append("**Ajustes que podem melhorar o score (do maior para o menor impacto):**")

    melhorias = []
    if ganho_score > 0:
        melhorias.append((ganho_score, f"📋 **Score de Crédito (SPC)** — Melhorar para A-B pode adicionar até **+{ganho_score} pontos**. Sugestão: incluir um segundo titular com score A-B na composição."))
    if ganho_ato > 0:
        melhorias.append((ganho_ato, f"💰 **Ato (Entrada)** — Aumentar o Ato para acima de 4% do valor da proposta pode adicionar até **+{ganho_ato} pontos**. Sugestão: negociar reforço de entrada com o cliente."))
    if ganho_comp > 0:
        melhorias.append((ganho_comp, f"📉 **Comprometimento de Renda** — Reduzir para até 10% pode adicionar até **+{ganho_comp} pontos**. Sugestão: composição de renda com familiar ou redução da mensal via plano mais curto."))
    if ganho_renda > 0:
        melhorias.append((ganho_renda, f"💵 **Faixa de Renda** — Elevar a renda total para acima de R$ 15.000 pode adicionar até **+{ganho_renda} pontos**. Sugestão: adicionar mais um proponente à composição de renda."))
    if ganho_plano > 0:
        melhorias.append((ganho_plano, f"📅 **Plano** — Migrar para Curto Prazo (até 48x) pode adicionar até **+{ganho_plano} pontos**. Sugestão: verificar capacidade financeira do cliente para plano mais curto."))

    # Ordena do maior ganho para o menor
    melhorias.sort(key=lambda x: x[0], reverse=True)
    for _, texto in melhorias:
        sugs.append(texto)

    return sugs


def salvar_historico(dados):
    arquivo = "historico.csv"
    df_novo = pd.DataFrame([dados])
    if os.path.exists(arquivo):
        df_existente = pd.read_csv(arquivo)
        df_final = pd.concat([df_existente, df_novo], ignore_index=True)
    else:
        df_final = df_novo
    df_final.to_csv(arquivo, index=False)


# ─────────────────────────────────────────
# INTERFACE — EMPREENDIMENTO
# ─────────────────────────────────────────

st.header("🏘️ Dados do Empreendimento")
col1, col2, col3 = st.columns(3)
with col1:
    unidade = st.selectbox("Unidade", options=UNIDADES, help="Digite para filtrar a unidade")
with col2:
    st.text_input("Empreendimento", value=EMPREENDIMENTO, disabled=True)
with col3:
    st.text_input("Tipo de Produto", value=TIPO_PRODUTO, disabled=True)

st.markdown("---")

# ─────────────────────────────────────────
# PROPONENTE PRINCIPAL
# ─────────────────────────────────────────

st.header("👤 Dados do Proponente Principal")

col1, col2 = st.columns(2)
with col1:
    data_nasc = st.date_input(
        "Data de Nascimento",
        value=None,
        min_value=date(1930, 1, 1),
        max_value=date.today(),
        format="DD/MM/YYYY"
    )
    if data_nasc:
        idade_calc = calcular_idade(data_nasc)
        st.info(f"🎂 Idade: **{idade_calc} anos** — Faixa: **{faixa_idade_str(data_nasc)}**")
with col2:
    estado_civil = st.selectbox("Estado Civil", ["SOLTEIRO(A)", "CASADO(A)", "DIVORCIADO(A)"])

st.subheader("📄 Upload do PDF do SPC — Proponente Principal")
st.caption("O sistema irá extrair automaticamente o Score de Crédito e a Renda Presumida.")
pdf_principal = st.file_uploader(
    "Selecione o PDF do SPC do proponente principal",
    type=["pdf"],
    key="pdf_p1"
)

score_p1_auto = None
renda_p1_auto = 0.0

if pdf_principal:
    with st.spinner("Lendo PDF..."):
        score_extraido, renda_extraida = extrair_dados_spc(pdf_principal)

    col_a, col_b = st.columns(2)
    with col_a:
        if score_extraido:
            st.success(f"✅ Score extraído automaticamente: **{score_extraido}**")
            score_p1_auto = score_extraido
        else:
            st.warning("⚠️ Score não encontrado no PDF. Selecione manualmente abaixo.")
    with col_b:
        if renda_extraida:
            st.success(f"✅ Renda Presumida extraída: **R$ {renda_extraida:,.2f}**")
            renda_p1_auto = renda_extraida
        else:
            st.warning("⚠️ Renda não encontrada no PDF. Preencha manualmente abaixo.")

score_opcoes = ["E - F", "C - D", "A - B"]
score_p1_idx = score_opcoes.index(score_p1_auto) if score_p1_auto in score_opcoes else 0
score_p1_sel = st.selectbox(
    "Score de Crédito (SPC) — Proponente Principal",
    score_opcoes,
    index=score_p1_idx
)
renda_p1_input = st.number_input(
    "Renda Presumida — Proponente Principal (R$)",
    min_value=0.0,
    value=float(renda_p1_auto),
    step=100.0,
    format="%.2f"
)

st.markdown("---")

# ─────────────────────────────────────────
# CLIENTES ADICIONAIS (até 4)
# ─────────────────────────────────────────

st.header("👥 Composição de Renda — Clientes Adicionais")
st.caption("Adicione até 4 clientes adicionais. O score consolidado será o melhor entre todos.")

scores_adicionais = []
rendas_adicionais = []

for i in range(1, 5):
    adicionar = st.checkbox(f"Adicionar Cliente {i + 1} à composição de renda?", key=f"add_{i}")
    if adicionar:
        with st.container():
            st.subheader(f"👤 Cliente {i + 1}")
            pdf_add = st.file_uploader(
                f"PDF do SPC — Cliente {i + 1}",
                type=["pdf"],
                key=f"pdf_add_{i}"
            )
            score_add_auto = None
            renda_add_auto = 0.0

            if pdf_add:
                with st.spinner(f"Lendo PDF do Cliente {i + 1}..."):
                    sc, rd = extrair_dados_spc(pdf_add)
                if sc:
                    st.success(f"✅ Score extraído: **{sc}**")
                    score_add_auto = sc
                else:
                    st.warning("⚠️ Score não encontrado. Selecione manualmente.")
                if rd:
                    st.success(f"✅ Renda extraída: **R$ {rd:,.2f}**")
                    renda_add_auto = rd
                else:
                    st.warning("⚠️ Renda não encontrada. Preencha manualmente.")

            idx_add = score_opcoes.index(score_add_auto) if score_add_auto in score_opcoes else 0
            score_add_sel = st.selectbox(
                f"Score SPC — Cliente {i + 1}",
                score_opcoes,
                index=idx_add,
                key=f"score_add_{i}"
            )
            renda_add_input = st.number_input(
                f"Renda Presumida — Cliente {i + 1} (R$)",
                min_value=0.0,
                value=float(renda_add_auto),
                step=100.0,
                format="%.2f",
                key=f"renda_add_{i}"
            )
            scores_adicionais.append(score_add_sel)
            rendas_adicionais.append(renda_add_input)
    else:
        break

# Renda total e score consolidado
renda_total = renda_p1_input + sum(rendas_adicionais)
todos_scores = [score_p1_sel] + scores_adicionais
ordem_score = {'A - B': 3, 'C - D': 2, 'E - F': 1}
melhor_score = max(todos_scores, key=lambda s: ordem_score.get(s, 0))

col_rt, col_sc = st.columns(2)
col_rt.metric("💵 Renda Total Consolidada", f"R$ {renda_total:,.2f}")
col_sc.metric("🏆 Score SPC Consolidado", melhor_score)

st.markdown("---")

# ─────────────────────────────────────────
# DADOS FINANCEIROS
# ─────────────────────────────────────────

st.header("💰 Dados Financeiros")

col1, col2 = st.columns(2)
with col1:
    ato_valor = st.number_input(
        "Ato Urba (R$)",
        min_value=0.0,
        step=100.0,
        format="%.2f",
        help="Valor do ato sem comissão fora do contrato"
    )
with col2:
    valor_proposta = st.number_input(
        "Valor da Proposta / Líquido CV (R$)",
        min_value=0.01,
        step=100.0,
        format="%.2f",
        value=1.0
    )

plano = st.selectbox("Plano", [
    "LONGO PRAZO (145 A 180X)",
    "MÉDIO LONGO (71 A 144X)",
    "MÉDIO PRAZO (49 A 70X)",
    "CURTO PRAZO (1 A 48X)",
])

primeira_mensal = st.number_input(
    "Valor da 1ª Mensal (R$)",
    min_value=0.0,
    step=10.0,
    format="%.2f"
)

st.markdown("---")

# ─────────────────────────────────────────
# CÁLCULOS AUTOMÁTICOS
# ─────────────────────────────────────────

pct_ato  = (ato_valor / valor_proposta * 100) if valor_proposta > 0 else 0
comp_pct = (primeira_mensal / renda_total * 100) if renda_total > 0 else 0

nota_idade = classificar_idade(data_nasc)
nota_ato   = classificar_ato(pct_ato)
nota_score = classificar_score(melhor_score)
nota_renda, faixa_renda_str = classificar_faixa_renda(renda_total)
nota_plano = classificar_plano(plano)
nota_ec    = classificar_estado_civil(estado_civil)
nota_tp    = classificar_tipo_produto(TIPO_PRODUTO)
nota_comp, faixa_comp_str = classificar_comprometimento(comp_pct)

score_total = calcular_score_total(
    nota_idade, nota_ato, nota_score,
    nota_renda, nota_plano, nota_ec,
    nota_tp, nota_comp
)
classificacao, tipo_alerta = classificar_venda(score_total)

# ─────────────────────────────────────────
# PAINEL DE RESULTADOS
# ─────────────────────────────────────────

st.header("📊 Resultado do Score de Venda")

col1, col2, col3 = st.columns(3)
col1.metric("% do Ato", f"{pct_ato:.1f}%")
col2.metric("Comprometimento de Renda", f"{comp_pct:.1f}%", faixa_comp_str)
col3.metric("Faixa Etária", faixa_idade_str(data_nasc))

col4, col5, col6 = st.columns(3)
col4.metric("Renda Total", f"R$ {renda_total:,.2f}")
col5.metric("Faixa de Renda", faixa_renda_str)
col6.metric("Score SPC", melhor_score)

st.markdown("---")

col_score_res, col_class_res = st.columns(2)
col_score_res.metric("🏆 Score Total", f"{score_total} / 130")
col_class_res.metric("🎯 Classificação da Venda", classificacao)

if tipo_alerta == "success":
    st.success(f"✅ {classificacao} — Score: {score_total}/130")
elif tipo_alerta == "warning":
    st.warning(f"⚠️ {classificacao} — Score: {score_total}/130")
else:
    st.error(f"🚨 {classificacao} — Score: {score_total}/130")

# ─────────────────────────────────────────
# SUGESTÕES INTELIGENTES DE MELHORIA
# ─────────────────────────────────────────

sugs = gerar_sugestoes(nota_ato, nota_score, nota_renda, nota_plano, nota_comp, score_total)
if sugs:
    st.markdown("---")
    st.subheader("💡 Estratégias para Reduzir o Risco")
    for s in sugs:
        st.markdown(s)

# ─────────────────────────────────────────
# DETALHAMENTO DAS NOTAS
# ─────────────────────────────────────────

with st.expander("🔍 Ver detalhamento das notas por variável"):
    df_notas = pd.DataFrame({
        "Variável": [
            "Idade", "Ato (%)", "Score SPC",
            "Faixa de Renda", "Plano",
            "Estado Civil", "Tipo de Produto",
            "Comprometimento de Renda"
        ],
        "Peso": [1, 5, 5, 4, 4, 1, 3, 4],
        "Nota (1-5)": [
            nota_idade, nota_ato, nota_score,
            nota_renda, nota_plano,
            nota_ec, nota_tp, nota_comp
        ],
        "Pontuação": [
            nota_idade * 1, nota_ato * 5, nota_score * 5,
            nota_renda * 4, nota_plano * 4,
            nota_ec * 1, nota_tp * 3, nota_comp * 4
        ],
    })
    total_row = pd.DataFrame([{
        "Variável": "TOTAL",
        "Peso": 27,
        "Nota (1-5)": "—",
        "Pontuação": score_total
    }])
    df_notas = pd.concat([df_notas, total_row], ignore_index=True)
    st.dataframe(df_notas, use_container_width=True, hide_index=True)

# ─────────────────────────────────────────
# SALVAR HISTÓRICO
# ─────────────────────────────────────────

st.markdown("---")
if st.button("💾 Salvar Simulação no Histórico", use_container_width=True, type="primary"):
    dados_registro = {
        "Data/Hora": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "Empreendimento": EMPREENDIMENTO,
        "Unidade": unidade,
        "Tipo Produto": TIPO_PRODUTO,
        "Faixa Etária": faixa_idade_str(data_nasc),
        "Estado Civil": estado_civil,
        "Score SPC Consolidado": melhor_score,
        "Qtd Clientes": 1 + len(scores_adicionais),
        "Renda Total (R$)": round(renda_total, 2),
        "Faixa de Renda": faixa_renda_str,
        "Ato (R$)": round(ato_valor, 2),
        "% Ato": round(pct_ato, 1),
        "Valor Proposta (R$)": round(valor_proposta, 2),
        "Plano": plano,
        "1ª Mensal (R$)": round(primeira_mensal, 2),
        "% Comprometimento": round(comp_pct, 1),
        "Faixa Comprometimento": faixa_comp_str,
        "Score Total": score_total,
        "Classificação": classificacao,
    }
    salvar_historico(dados_registro)
    st.success("✅ Simulação salva com sucesso no histórico!")

# ─────────────────────────────────────────
# HISTÓRICO DE SIMULAÇÕES
# ─────────────────────────────────────────

st.markdown("---")
with st.expander("📂 Ver Histórico de Simulações"):
    if os.path.exists("historico.csv"):
        df_hist = pd.read_csv("historico.csv")
        st.dataframe(df_hist, use_container_width=True, hide_index=True)
        csv_bytes = df_hist.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Baixar Histórico em CSV",
            csv_bytes,
            "historico_simulacoes.csv",
            "text/csv"
        )
    else:
        st.info("Nenhuma simulação registrada ainda. Preencha o formulário e clique em 'Salvar Simulação'.")

