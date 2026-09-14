# app.py — Simulador Score de Venda Urba (versão completa)


import streamlit as st
from datetime import date, datetime
import pdfplumber
import re

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
    """Extrai score e renda presumida do PDF do SPC."""
    score = None
    renda = None
    try:
        with pdfplumber.open(pdf_file) as pdf:
            texto = ""
            for page in pdf.pages:
                texto += page.extract_text() or ""
        texto_upper = texto.upper()

        # Score: busca padrão como "SCORE: A" ou "CLASSIFICAÇÃO: B"
        match_score = re.search(r'SCORE[:\s]+([A-F])', texto_upper)
        if match_score:
            letra = match_score.group(1)
            if letra in ['A', 'B']:
                score = 'A - B'
            elif letra in ['C', 'D']:
                score = 'C - D'
            else:
                score = 'E - F'

        # Renda presumida: busca padrão como "RENDA PRESUMIDA R$ 5.000,00"
        match_renda = re.search(r'RENDA\s+PRESUMIDA[:\s]+R?\$?\s*([\d.,]+)', texto_upper)
        if match_renda:
            valor_str = match_renda.group(1).replace('.', '').replace(',', '.')
            renda = float(valor_str)
    except Exception as e:
        st.warning(f"Erro ao ler PDF: {e}")
    return score, renda

def classificar_score(score_str):
    notas = {'A - B': 5, 'C - D': 3, 'E - F': 1}
    return notas.get(score_str, 1)

def classificar_idade(data_nasc):
    if data_nasc is None:
        return 0
    hoje = date.today()
    idade = (hoje - data_nasc).days // 365
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

def faixa_idade_str(data_nasc):
    if data_nasc is None:
        return "—"
    hoje = date.today()
    idade = (hoje - data_nasc).days // 365
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
    if renda is None or renda == 0:
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
    if pct_ato is None:
        return 0
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
    return (n_idade * 1) + (n_ato * 5) + (n_score * 5) + (n_renda * 4) + (n_plano * 4) + (n_ec * 1) + (n_tp * 3) + (n_comp * 4)

def classificar_venda(total):
    if total >= 90:
        return "🟢 BAIXO RISCO", "success"
    elif total >= 61:
        return "🟡 RISCO MODERADO", "warning"
    else:
        return "🔴 ALTO RISCO", "error"

def sugestoes_melhoria(n_ato, n_score, n_renda, n_plano, n_comp, total):
    sugs = []
    if total < 90:
        if n_ato < 5:
            sugs.append("💡 **Aumentar o Ato** para acima de 4% do valor do imóvel reduz significativamente o risco.")
        if n_plano < 5:
            sugs.append("💡 **Reduzir o prazo do plano** para Curto Prazo (até 48x) melhora muito o score.")
        if n_comp > 2:
            sugs.append("💡 **Reduzir o comprometimento de renda** abaixo de 20% melhora o score.")
        if n_score < 5:
            sugs.append("💡 **Score de crédito A-B** é o fator de maior peso — considere composição de renda com outro cliente.")
        if n_renda < 3:
            sugs.append("💡 **Composição de renda** com outro proponente pode elevar a faixa de renda e melhorar o score.")
    return sugs

# ─────────────────────────────────────────
# INTERFACE
# ─────────────────────────────────────────

st.header("🏘️ Dados do Empreendimento")
col1, col2, col3 = st.columns(3)
with col1:
    unidade = st.selectbox("Unidade", options=UNIDADES, help="Digite para filtrar")
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
    data_nasc = st.date_input("Data de Nascimento", value=None, min_value=date(1930,1,1), max_value=date.today(), format="DD/MM/YYYY")
with col2:
    estado_civil = st.selectbox("Estado Civil", ["SOLTEIRO(A)", "CASADO(A)", "DIVORCIADO(A)"])

st.subheader("📄 Upload do PDF do SPC — Proponente Principal")
pdf_principal = st.file_uploader("Selecione o PDF do SPC do proponente principal", type=["pdf"], key="pdf_p1")

score_p1 = None
renda_p1 = 0.0

if pdf_principal:
    score_extraido, renda_extraida = extrair_dados_spc(pdf_principal)
    if score_extraido:
        st.success(f"✅ Score extraído: **{score_extraido}**")
        score_p1 = score_extraido
    else:
        st.warning("⚠️ Não foi possível extrair o score automaticamente. Selecione manualmente.")
    if renda_extraida:
        st.success(f"✅ Renda Presumida extraída: **R$ {renda_extraida:,.2f}**")
        renda_p1 = renda_extraida
    else:
        st.warning("⚠️ Não foi possível extrair a renda automaticamente. Preencha manualmente.")

score_p1_sel = st.selectbox("Score de Crédito (SPC) — Proponente Principal", ["E - F", "C - D", "A - B"], index=["E - F","C - D","A - B"].index(score_p1) if score_p1 else 0)
renda_p1_input = st.number_input("Renda Presumida — Proponente Principal (R$)", min_value=0.0, value=float(renda_p1), step=100.0, format="%.2f")

st.markdown("---")

# ─────────────────────────────────────────
# CLIENTES ADICIONAIS (até 4)
# ─────────────────────────────────────────

st.header("👥 Composição de Renda — Clientes Adicionais")

scores_adicionais = []
rendas_adicionais = []

num_adicionais = 0
for i in range(1, 5):
    adicionar = st.checkbox(f"Adicionar Cliente {i+1} à composição de renda?", key=f"add_{i}")
    if adicionar:
        num_adicionais += 1
        st.subheader(f"👤 Cliente {i+1}")
        pdf_add = st.file_uploader(f"PDF do SPC — Cliente {i+1}", type=["pdf"], key=f"pdf_add_{i}")
        score_add = None
        renda_add = 0.0
        if pdf_add:
            sc, rd = extrair_dados_spc(pdf_add)
            if sc:
                st.success(f"✅ Score extraído: **{sc}**")
                score_add = sc
            if rd:
                st.success(f"✅ Renda extraída: **R$ {rd:,.2f}**")
                renda_add = rd
        score_add_sel = st.selectbox(f"Score SPC — Cliente {i+1}", ["E - F","C - D","A - B"], index=["E - F","C - D","A - B"].index(score_add) if score_add else 0, key=f"score_add_{i}")
        renda_add_input = st.number_input(f"Renda Presumida — Cliente {i+1} (R$)", min_value=0.0, value=float(renda_add), step=100.0, format="%.2f", key=f"renda_add_{i}")
        scores_adicionais.append(score_add_sel)
        rendas_adicionais.append(renda_add_input)
    else:
        break

# Renda total
renda_total = renda_p1_input + sum(rendas_adicionais)

# Score consolidado (melhor score entre todos)
todos_scores = [score_p1_sel] + scores_adicionais
ordem_score = {'A - B': 3, 'C - D': 2, 'E - F': 1}
melhor_score = max(todos_scores, key=lambda s: ordem_score.get(s, 0))

st.markdown("---")

# ─────────────────────────────────────────
# DADOS FINANCEIROS
# ─────────────────────────────────────────

st.header("💰 Dados Financeiros")

col1, col2 = st.columns(2)
with col1:
    ato_valor = st.number_input("Ato Urba (R$)", min_value=0.0, step=100.0, format="%.2f")
with col2:
    valor_proposta = st.number_input("Valor da Proposta / Líquido CV (R$)", min_value=0.01, step=100.0, format="%.2f", value=1.0)

plano = st.selectbox("Plano", [
    "LONGO PRAZO (145 A 180X)",
    "MÉDIO LONGO (71 A 144X)",
    "MÉDIO PRAZO (49 A 70X)",
    "CURTO PRAZO (1 A 48X)",
])

primeira_mensal = st.number_input("Valor da 1ª Mensal (R$)", min_value=0.0, step=10.0, format="%.2f")

st.markdown("---")

# ─────────────────────────────────────────
# CÁLCULOS
# ─────────────────────────────────────────

pct_ato = (ato_valor / valor_proposta * 100) if valor_proposta > 0 else 0
comp_pct = (primeira_mensal / renda_total * 100) if renda_total > 0 else 0

nota_idade = classificar_idade(data_nasc)
nota_ato = classificar_ato(pct_ato)
nota_score = classificar_score(melhor_score)
nota_renda, faixa_renda_str = classificar_faixa_renda(renda_total)
nota_plano = classificar_plano(plano)
nota_ec = classificar_estado_civil(estado_civil)
nota_tp = classificar_tipo_produto(TIPO_PRODUTO)
nota_comp, faixa_comp_str = classificar_comprometimento(comp_pct)

score_total = calcular_score_total(nota_idade, nota_ato, nota_score, nota_renda, nota_plano, nota_ec, nota_tp, nota_comp)
classificacao, tipo_alerta = classificar_venda(score_total)

# ─────────────────────────────────────────
# PAINEL DE RESULTADOS
# ─────────────────────────────────────────

st.header("📊 Resultado do Score de Venda")

col1, col2, col3 = st.columns(3)
col1.metric("% do Ato", f"{pct_ato:.1f}%")
col2.metric("Comprometimento de Renda", f"{comp_pct:.1f}%")
col3.metric("Faixa Etária", faixa_idade_str(data_nasc))

col4, col5, col6 = st.columns(3)
col4.metric("Renda Total", f"R$ {renda_total:,.2f}")
col5.metric("Faixa de Renda", faixa_renda_str)
col6.metric("Score SPC Consolidado", melhor_score)

st.markdown("---")

col_score, col_class = st.columns(2)
col_score.metric("🏆 Score Total", f"{score_total} / 130")
col_class.metric("🎯 Classificação", classificacao)

if tipo_alerta == "success":
    st.success(f"✅ {classificacao} — Score: {score_total}/130")
elif tipo_alerta == "warning":
    st.warning(f"⚠️ {classificacao} — Score: {score_total}/130")
else:
    st.error(f"🚨 {classificacao} — Score: {score_total}/130")

# ─────────────────────────────────────────
# SUGESTÕES DE MELHORIA
# ─────────────────────────────────────────

sugs = sugestoes_melhoria(nota_ato, nota_score, nota_renda, nota_plano, nota_comp, score_total)
if sugs:
    st.markdown("---")
    st.subheader("💡 O que pode ser ajustado para melhorar o score?")
    for s in sugs:
        st.markdown(s)

# ─────────────────────────────────────────
# DETALHAMENTO DAS NOTAS
# ─────────────────────────────────────────

with st.expander("🔍 Ver detalhamento das notas por variável"):
    import pandas as pd
    df = pd.DataFrame({
        "Variável": ["Idade","Ato","Score SPC","Faixa de Renda","Plano","Estado Civil","Tipo de Produto","Comprometimento de Renda"],
        "Peso": [1, 5, 5, 4, 4, 1, 3, 4],
        "Nota": [nota_idade, nota_ato, nota_score, nota_renda, nota_plano, nota_ec, nota_tp, nota_comp],
        "Pontuação": [nota_idade*1, nota_ato*5, nota_score*5, nota_renda*4, nota_plano*4, nota_ec*1, nota_tp*3, nota_comp*4],
    })
    df.loc[len(df)] = ["TOTAL", 27, "—", score_total]
    st.dataframe(df, use_container_width=True)

