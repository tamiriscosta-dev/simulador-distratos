import streamlit as st
import pandas as pd
from datetime import date, datetime
import os
import re

try:
    import pdfplumber
    PDF_OK = True
except ImportError:
    PDF_OK = False

# ─────────────────────────────────────────
# CONFIGURAÇÃO DA PÁGINA
# ─────────────────────────────────────────
st.set_page_config(
    page_title="Simulador de Score de Vendas",
    page_icon="🏠",
    layout="wide"
)

st.title("🏠 Simulador de Score de Vendas")
st.markdown("**Projeto Defensores do Contrato — Avaliação de Risco de Distrato**")
st.divider()

# ─────────────────────────────────────────
# LISTA DE EMPREENDIMENTOS
# ─────────────────────────────────────────
UNIDADES_SMART = [
    "SMART URBA RESERVA - QUADRA 01 - LOTE 0001","SMART URBA RESERVA - QUADRA 01 - LOTE 0002","SMART URBA RESERVA - QUADRA 01 - LOTE 0003","SMART URBA RESERVA - QUADRA 01 - LOTE 0004","SMART URBA RESERVA - QUADRA 01 - LOTE 0005",
    "SMART URBA RESERVA - QUADRA 01 - LOTE 0006","SMART URBA RESERVA - QUADRA 01 - LOTE 0007","SMART URBA RESERVA - QUADRA 01 - LOTE 0008","SMART URBA RESERVA - QUADRA 01 - LOTE 0009","SMART URBA RESERVA - QUADRA 01 - LOTE 0010",
    "SMART URBA RESERVA - QUADRA 01 - LOTE 0011","SMART URBA RESERVA - QUADRA 01 - LOTE 0012","SMART URBA RESERVA - QUADRA 01 - LOTE 0013","SMART URBA RESERVA - QUADRA 01 - LOTE 0014","SMART URBA RESERVA - QUADRA 01 - LOTE 0015",
    "SMART URBA RESERVA - QUADRA 01 - LOTE 0016","SMART URBA RESERVA - QUADRA 01 - LOTE 0017","SMART URBA RESERVA - QUADRA 01 - LOTE 0018","SMART URBA RESERVA - QUADRA 01 - LOTE 0019",
    "SMART URBA RESERVA - QUADRA 02 - LOTE 0001","SMART URBA RESERVA - QUADRA 02 - LOTE 0002","SMART URBA RESERVA - QUADRA 02 - LOTE 0003","SMART URBA RESERVA - QUADRA 02 - LOTE 0004","SMART URBA RESERVA - QUADRA 02 - LOTE 0005",
    "SMART URBA RESERVA - QUADRA 02 - LOTE 0006","SMART URBA RESERVA - QUADRA 02 - LOTE 0007","SMART URBA RESERVA - QUADRA 02 - LOTE 0008","SMART URBA RESERVA - QUADRA 02 - LOTE 0009","SMART URBA RESERVA - QUADRA 02 - LOTE 0010",
    "SMART URBA RESERVA - QUADRA 02 - LOTE 0011","SMART URBA RESERVA - QUADRA 02 - LOTE 0012","SMART URBA RESERVA - QUADRA 02 - LOTE 0013","SMART URBA RESERVA - QUADRA 02 - LOTE 0014","SMART URBA RESERVA - QUADRA 02 - LOTE 0015",
    "SMART URBA RESERVA - QUADRA 02 - LOTE 0016","SMART URBA RESERVA - QUADRA 02 - LOTE 0017","SMART URBA RESERVA - QUADRA 02 - LOTE 0018","SMART URBA RESERVA - QUADRA 02 - LOTE 0019","SMART URBA RESERVA - QUADRA 02 - LOTE 0020",
    "SMART URBA RESERVA - QUADRA 02 - LOTE 0021","SMART URBA RESERVA - QUADRA 02 - LOTE 0022","SMART URBA RESERVA - QUADRA 02 - LOTE 0023","SMART URBA RESERVA - QUADRA 02 - LOTE 0024","SMART URBA RESERVA - QUADRA 02 - LOTE 0025",
    "SMART URBA RESERVA - QUADRA 02 - LOTE 0026","SMART URBA RESERVA - QUADRA 02 - LOTE 0027","SMART URBA RESERVA - QUADRA 02 - LOTE 0028","SMART URBA RESERVA - QUADRA 02 - LOTE 0029","SMART URBA RESERVA - QUADRA 02 - LOTE 0030",
    "SMART URBA RESERVA - QUADRA 02 - LOTE 0031","SMART URBA RESERVA - QUADRA 02 - LOTE 0032","SMART URBA RESERVA - QUADRA 02 - LOTE 0033","SMART URBA RESERVA - QUADRA 02 - LOTE 0034","SMART URBA RESERVA - QUADRA 02 - LOTE 0035",
    "SMART URBA RESERVA - QUADRA 02 - LOTE 0036","SMART URBA RESERVA - QUADRA 02 - LOTE 0037","SMART URBA RESERVA - QUADRA 02 - LOTE 0038","SMART URBA RESERVA - QUADRA 02 - LOTE 0039",
    "SMART URBA RESERVA - QUADRA 03 - LOTE 0001","SMART URBA RESERVA - QUADRA 03 - LOTE 0002","SMART URBA RESERVA - QUADRA 03 - LOTE 0003","SMART URBA RESERVA - QUADRA 03 - LOTE 0004","SMART URBA RESERVA - QUADRA 03 - LOTE 0005",
    "SMART URBA RESERVA - QUADRA 03 - LOTE 0006","SMART URBA RESERVA - QUADRA 03 - LOTE 0007","SMART URBA RESERVA - QUADRA 03 - LOTE 0008","SMART URBA RESERVA - QUADRA 03 - LOTE 0009","SMART URBA RESERVA - QUADRA 03 - LOTE 0010",
    "SMART URBA RESERVA - QUADRA 03 - LOTE 0011","SMART URBA RESERVA - QUADRA 03 - LOTE 0012","SMART URBA RESERVA - QUADRA 03 - LOTE 0013","SMART URBA RESERVA - QUADRA 03 - LOTE 0014","SMART URBA RESERVA - QUADRA 03 - LOTE 0015",
    "SMART URBA RESERVA - QUADRA 03 - LOTE 0016","SMART URBA RESERVA - QUADRA 03 - LOTE 0017","SMART URBA RESERVA - QUADRA 03 - LOTE 0018","SMART URBA RESERVA - QUADRA 03 - LOTE 0019","SMART URBA RESERVA - QUADRA 03 - LOTE 0020",
    "SMART URBA RESERVA - QUADRA 03 - LOTE 0021","SMART URBA RESERVA - QUADRA 03 - LOTE 0022","SMART URBA RESERVA - QUADRA 03 - LOTE 0023","SMART URBA RESERVA - QUADRA 03 - LOTE 0024","SMART URBA RESERVA - QUADRA 03 - LOTE 0025",
    "SMART URBA RESERVA - QUADRA 03 - LOTE 0026","SMART URBA RESERVA - QUADRA 03 - LOTE 0027","SMART URBA RESERVA - QUADRA 03 - LOTE 0028",
    "SMART URBA RESERVA - QUADRA 04 - LOTE 0001","SMART URBA RESERVA - QUADRA 04 - LOTE 0002","SMART URBA RESERVA - QUADRA 04 - LOTE 0003","SMART URBA RESERVA - QUADRA 04 - LOTE 0004","SMART URBA RESERVA - QUADRA 04 - LOTE 0005",
    "SMART URBA RESERVA - QUADRA 04 - LOTE 0006","SMART URBA RESERVA - QUADRA 04 - LOTE 0007","SMART URBA RESERVA - QUADRA 04 - LOTE 0008","SMART URBA RESERVA - QUADRA 04 - LOTE 0009","SMART URBA RESERVA - QUADRA 04 - LOTE 0010",
    "SMART URBA RESERVA - QUADRA 04 - LOTE 0011","SMART URBA RESERVA - QUADRA 04 - LOTE 0012","SMART URBA RESERVA - QUADRA 04 - LOTE 0013","SMART URBA RESERVA - QUADRA 04 - LOTE 0014","SMART URBA RESERVA - QUADRA 04 - LOTE 0015",
    "SMART URBA RESERVA - QUADRA 04 - LOTE 0016","SMART URBA RESERVA - QUADRA 04 - LOTE 0017","SMART URBA RESERVA - QUADRA 04 - LOTE 0018","SMART URBA RESERVA - QUADRA 04 - LOTE 0019","SMART URBA RESERVA - QUADRA 04 - LOTE 0020",
    "SMART URBA RESERVA - QUADRA 04 - LOTE 0021","SMART URBA RESERVA - QUADRA 04 - LOTE 0022","SMART URBA RESERVA - QUADRA 04 - LOTE 0023","SMART URBA RESERVA - QUADRA 04 - LOTE 0024","SMART URBA RESERVA - QUADRA 04 - LOTE 0025",
    "SMART URBA RESERVA - QUADRA 04 - LOTE 0026","SMART URBA RESERVA - QUADRA 04 - LOTE 0027","SMART URBA RESERVA - QUADRA 04 - LOTE 0028","SMART URBA RESERVA - QUADRA 04 - LOTE 0029","SMART URBA RESERVA - QUADRA 04 - LOTE 0030",
    "SMART URBA RESERVA - QUADRA 04 - LOTE 0031","SMART URBA RESERVA - QUADRA 04 - LOTE 0032","SMART URBA RESERVA - QUADRA 04 - LOTE 0033","SMART URBA RESERVA - QUADRA 04 - LOTE 0034","SMART URBA RESERVA - QUADRA 04 - LOTE 0035",
    "SMART URBA RESERVA - QUADRA 04 - LOTE 0036","SMART URBA RESERVA - QUADRA 04 - LOTE 0037","SMART URBA RESERVA - QUADRA 04 - LOTE 0038","SMART URBA RESERVA - QUADRA 04 - LOTE 0039","SMART URBA RESERVA - QUADRA 04 - LOTE 0040",
    "SMART URBA RESERVA - QUADRA 04 - LOTE 0041","SMART URBA RESERVA - QUADRA 04 - LOTE 0042","SMART URBA RESERVA - QUADRA 04 - LOTE 0043","SMART URBA RESERVA - QUADRA 04 - LOTE 0044",
    "SMART URBA RESERVA - QUADRA 05 - LOTE 0001","SMART URBA RESERVA - QUADRA 05 - LOTE 0002","SMART URBA RESERVA - QUADRA 05 - LOTE 0003","SMART URBA RESERVA - QUADRA 05 - LOTE 0004","SMART URBA RESERVA - QUADRA 05 - LOTE 0005",
    "SMART URBA RESERVA - QUADRA 05 - LOTE 0006","SMART URBA RESERVA - QUADRA 05 - LOTE 0007","SMART URBA RESERVA - QUADRA 05 - LOTE 0008","SMART URBA RESERVA - QUADRA 05 - LOTE 0009","SMART URBA RESERVA - QUADRA 05 - LOTE 0010",
    "SMART URBA RESERVA - QUADRA 05 - LOTE 0011","SMART URBA RESERVA - QUADRA 05 - LOTE 0012","SMART URBA RESERVA - QUADRA 05 - LOTE 0013","SMART URBA RESERVA - QUADRA 05 - LOTE 0014","SMART URBA RESERVA - QUADRA 05 - LOTE 0015",
    "SMART URBA RESERVA - QUADRA 05 - LOTE 0016","SMART URBA RESERVA - QUADRA 05 - LOTE 0017","SMART URBA RESERVA - QUADRA 05 - LOTE 0018","SMART URBA RESERVA - QUADRA 05 - LOTE 0019","SMART URBA RESERVA - QUADRA 05 - LOTE 0020",
    "SMART URBA RESERVA - QUADRA 05 - LOTE 0021","SMART URBA RESERVA - QUADRA 05 - LOTE 0022","SMART URBA RESERVA - QUADRA 05 - LOTE 0023","SMART URBA RESERVA - QUADRA 05 - LOTE 0024","SMART URBA RESERVA - QUADRA 05 - LOTE 0025",
    "SMART URBA RESERVA - QUADRA 05 - LOTE 0026","SMART URBA RESERVA - QUADRA 05 - LOTE 0027","SMART URBA RESERVA - QUADRA 05 - LOTE 0028","SMART URBA RESERVA - QUADRA 05 - LOTE 0029","SMART URBA RESERVA - QUADRA 05 - LOTE 0030",
    "SMART URBA RESERVA - QUADRA 05 - LOTE 0031","SMART URBA RESERVA - QUADRA 05 - LOTE 0032","SMART URBA RESERVA - QUADRA 05 - LOTE 0033","SMART URBA RESERVA - QUADRA 05 - LOTE 0034","SMART URBA RESERVA - QUADRA 05 - LOTE 0035",
    "SMART URBA RESERVA - QUADRA 05 - LOTE 0036","SMART URBA RESERVA - QUADRA 05 - LOTE 0037","SMART URBA RESERVA - QUADRA 05 - LOTE 0038","SMART URBA RESERVA - QUADRA 05 - LOTE 0039","SMART URBA RESERVA - QUADRA 05 - LOTE 0040",
    "SMART URBA RESERVA - QUADRA 05 - LOTE 0041","SMART URBA RESERVA - QUADRA 05 - LOTE 0042","SMART URBA RESERVA - QUADRA 05 - LOTE 0043","SMART URBA RESERVA - QUADRA 05 - LOTE 0044","SMART URBA RESERVA - QUADRA 05 - LOTE 0045",
    "SMART URBA RESERVA - QUADRA 05 - LOTE 0046","SMART URBA RESERVA - QUADRA 05 - LOTE 0047","SMART URBA RESERVA - QUADRA 05 - LOTE 0048","SMART URBA RESERVA - QUADRA 05 - LOTE 0049","SMART URBA RESERVA - QUADRA 05 - LOTE 0050",
    "SMART URBA RESERVA - QUADRA 05 - LOTE 0051","SMART URBA RESERVA - QUADRA 05 - LOTE 0052","SMART URBA RESERVA - QUADRA 05 - LOTE 0053","SMART URBA RESERVA - QUADRA 05 - LOTE 0054","SMART URBA RESERVA - QUADRA 05 - LOTE 0055",
    "SMART URBA RESERVA - QUADRA 05 - LOTE 0056","SMART URBA RESERVA - QUADRA 05 - LOTE 0057","SMART URBA RESERVA - QUADRA 05 - LOTE 0058","SMART URBA RESERVA - QUADRA 05 - LOTE 0059","SMART URBA RESERVA - QUADRA 05 - LOTE 0060",
    "SMART URBA RESERVA - QUADRA 05 - LOTE 0061","SMART URBA RESERVA - QUADRA 05 - LOTE 0062","SMART URBA RESERVA - QUADRA 05 - LOTE 0063",
    "SMART URBA RESERVA - QUADRA 06 - LOTE 0001","SMART URBA RESERVA - QUADRA 06 - LOTE 0002","SMART URBA RESERVA - QUADRA 06 - LOTE 0003","SMART URBA RESERVA - QUADRA 06 - LOTE 0004","SMART URBA RESERVA - QUADRA 06 - LOTE 0005",
    "SMART URBA RESERVA - QUADRA 06 - LOTE 0006","SMART URBA RESERVA - QUADRA 06 - LOTE 0007","SMART URBA RESERVA - QUADRA 06 - LOTE 0008","SMART URBA RESERVA - QUADRA 06 - LOTE 0009","SMART URBA RESERVA - QUADRA 06 - LOTE 0010",
    "SMART URBA RESERVA - QUADRA 06 - LOTE 0011","SMART URBA RESERVA - QUADRA 06 - LOTE 0012","SMART URBA RESERVA - QUADRA 06 - LOTE 0013","SMART URBA RESERVA - QUADRA 06 - LOTE 0014","SMART URBA RESERVA - QUADRA 06 - LOTE 0015",
    "SMART URBA RESERVA - QUADRA 06 - LOTE 0016",
    "SMART URBA RESERVA - QUADRA 07 - LOTE 0001","SMART URBA RESERVA - QUADRA 07 - LOTE 0002","SMART URBA RESERVA - QUADRA 07 - LOTE 0003","SMART URBA RESERVA - QUADRA 07 - LOTE 0004","SMART URBA RESERVA - QUADRA 07 - LOTE 0005",
    "SMART URBA RESERVA - QUADRA 07 - LOTE 0006","SMART URBA RESERVA - QUADRA 07 - LOTE 0007","SMART URBA RESERVA - QUADRA 07 - LOTE 0008","SMART URBA RESERVA - QUADRA 07 - LOTE 0009","SMART URBA RESERVA - QUADRA 07 - LOTE 0010",
    "SMART URBA RESERVA - QUADRA 07 - LOTE 0011","SMART URBA RESERVA - QUADRA 07 - LOTE 0012","SMART URBA RESERVA - QUADRA 07 - LOTE 0013","SMART URBA RESERVA - QUADRA 07 - LOTE 0014","SMART URBA RESERVA - QUADRA 07 - LOTE 0015",
    "SMART URBA RESERVA - QUADRA 07 - LOTE 0016","SMART URBA RESERVA - QUADRA 07 - LOTE 0017","SMART URBA RESERVA - QUADRA 07 - LOTE 0018","SMART URBA RESERVA - QUADRA 07 - LOTE 0019","SMART URBA RESERVA - QUADRA 07 - LOTE 0020",
    "SMART URBA RESERVA - QUADRA 07 - LOTE 0021","SMART URBA RESERVA - QUADRA 07 - LOTE 0022",
    "SMART URBA RESERVA - QUADRA 08 - LOTE 0001","SMART URBA RESERVA - QUADRA 08 - LOTE 0002","SMART URBA RESERVA - QUADRA 08 - LOTE 0003","SMART URBA RESERVA - QUADRA 08 - LOTE 0004","SMART URBA RESERVA - QUADRA 08 - LOTE 0005",
    "SMART URBA RESERVA - QUADRA 08 - LOTE 0006","SMART URBA RESERVA - QUADRA 08 - LOTE 0007","SMART URBA RESERVA - QUADRA 08 - LOTE 0008","SMART URBA RESERVA - QUADRA 08 - LOTE 0009","SMART URBA RESERVA - QUADRA 08 - LOTE 0010",
    "SMART URBA RESERVA - QUADRA 08 - LOTE 0011","SMART URBA RESERVA - QUADRA 08 - LOTE 0012","SMART URBA RESERVA - QUADRA 08 - LOTE 0013","SMART URBA RESERVA - QUADRA 08 - LOTE 0014","SMART URBA RESERVA - QUADRA 08 - LOTE 0015",
    "SMART URBA RESERVA - QUADRA 08 - LOTE 0016","SMART URBA RESERVA - QUADRA 08 - LOTE 0017","SMART URBA RESERVA - QUADRA 08 - LOTE 0018","SMART URBA RESERVA - QUADRA 08 - LOTE 0019","SMART URBA RESERVA - QUADRA 08 - LOTE 0020",
    "SMART URBA RESERVA - QUADRA 08 - LOTE 0021","SMART URBA RESERVA - QUADRA 08 - LOTE 0022","SMART URBA RESERVA - QUADRA 08 - LOTE 0023","SMART URBA RESERVA - QUADRA 08 - LOTE 0024","SMART URBA RESERVA - QUADRA 08 - LOTE 0025",
    "SMART URBA RESERVA - QUADRA 08 - LOTE 0026","SMART URBA RESERVA - QUADRA 08 - LOTE 0027","SMART URBA RESERVA - QUADRA 08 - LOTE 0028","SMART URBA RESERVA - QUADRA 08 - LOTE 0029","SMART URBA RESERVA - QUADRA 08 - LOTE 0030",
    "SMART URBA RESERVA - QUADRA 08 - LOTE 0031","SMART URBA RESERVA - QUADRA 08 - LOTE 0032","SMART URBA RESERVA - QUADRA 08 - LOTE 0033","SMART URBA RESERVA - QUADRA 08 - LOTE 0034","SMART URBA RESERVA - QUADRA 08 - LOTE 0035",
    "SMART URBA RESERVA - QUADRA 08 - LOTE 0036","SMART URBA RESERVA - QUADRA 08 - LOTE 0037","SMART URBA RESERVA - QUADRA 08 - LOTE 0038","SMART URBA RESERVA - QUADRA 08 - LOTE 0039","SMART URBA RESERVA - QUADRA 08 - LOTE 0040",
    "SMART URBA RESERVA - QUADRA 08 - LOTE 0041","SMART URBA RESERVA - QUADRA 08 - LOTE 0042","SMART URBA RESERVA - QUADRA 08 - LOTE 0043","SMART URBA RESERVA - QUADRA 08 - LOTE 0044",
    "SMART URBA RESERVA - QUADRA 09 - LOTE 0001","SMART URBA RESERVA - QUADRA 09 - LOTE 0002","SMART URBA RESERVA - QUADRA 09 - LOTE 0003","SMART URBA RESERVA - QUADRA 09 - LOTE 0004","SMART URBA RESERVA - QUADRA 09 - LOTE 0005",
    "SMART URBA RESERVA - QUADRA 09 - LOTE 0006","SMART URBA RESERVA - QUADRA 09 - LOTE 0007","SMART URBA RESERVA - QUADRA 09 - LOTE 0008","SMART URBA RESERVA - QUADRA 09 - LOTE 0009","SMART URBA RESERVA - QUADRA 09 - LOTE 0010",
    "SMART URBA RESERVA - QUADRA 09 - LOTE 0011","SMART URBA RESERVA - QUADRA 09 - LOTE 0012","SMART URBA RESERVA - QUADRA 09 - LOTE 0013","SMART URBA RESERVA - QUADRA 09 - LOTE 0014","SMART URBA RESERVA - QUADRA 09 - LOTE 0015",
    "SMART URBA RESERVA - QUADRA 09 - LOTE 0016","SMART URBA RESERVA - QUADRA 09 - LOTE 0017","SMART URBA RESERVA - QUADRA 09 - LOTE 0018","SMART URBA RESERVA - QUADRA 09 - LOTE 0019","SMART URBA RESERVA - QUADRA 09 - LOTE 0020",
    "SMART URBA RESERVA - QUADRA 09 - LOTE 0021","SMART URBA RESERVA - QUADRA 09 - LOTE 0022","SMART URBA RESERVA - QUADRA 09 - LOTE 0023","SMART URBA RESERVA - QUADRA 09 - LOTE 0024","SMART URBA RESERVA - QUADRA 09 - LOTE 0025",
    "SMART URBA RESERVA - QUADRA 09 - LOTE 0026","SMART URBA RESERVA - QUADRA 09 - LOTE 0027","SMART URBA RESERVA - QUADRA 09 - LOTE 0028","SMART URBA RESERVA - QUADRA 09 - LOTE 0029","SMART URBA RESERVA - QUADRA 09 - LOTE 0030",
    "SMART URBA RESERVA - QUADRA 09 - LOTE 0031","SMART URBA RESERVA - QUADRA 09 - LOTE 0032","SMART URBA RESERVA - QUADRA 09 - LOTE 0033","SMART URBA RESERVA - QUADRA 09 - LOTE 0034",
    "SMART URBA RESERVA - QUADRA 10 - LOTE 0001","SMART URBA RESERVA - QUADRA 10 - LOTE 0002","SMART URBA RESERVA - QUADRA 10 - LOTE 0003","SMART URBA RESERVA - QUADRA 10 - LOTE 0004","SMART URBA RESERVA - QUADRA 10 - LOTE 0005",
    "SMART URBA RESERVA - QUADRA 10 - LOTE 0006","SMART URBA RESERVA - QUADRA 10 - LOTE 0007","SMART URBA RESERVA - QUADRA 10 - LOTE 0008","SMART URBA RESERVA - QUADRA 10 - LOTE 0009","SMART URBA RESERVA - QUADRA 10 - LOTE 0010",
    "SMART URBA RESERVA - QUADRA 10 - LOTE 0011","SMART URBA RESERVA - QUADRA 10 - LOTE 0012","SMART URBA RESERVA - QUADRA 10 - LOTE 0013","SMART URBA RESERVA - QUADRA 10 - LOTE 0014","SMART URBA RESERVA - QUADRA 10 - LOTE 0015",
    "SMART URBA RESERVA - QUADRA 10 - LOTE 0016","SMART URBA RESERVA - QUADRA 10 - LOTE 0017","SMART URBA RESERVA - QUADRA 10 - LOTE 0018","SMART URBA RESERVA - QUADRA 10 - LOTE 0019","SMART URBA RESERVA - QUADRA 10 - LOTE 0020",
    "SMART URBA RESERVA - QUADRA 10 - LOTE 0021","SMART URBA RESERVA - QUADRA 10 - LOTE 0022","SMART URBA RESERVA - QUADRA 10 - LOTE 0023","SMART URBA RESERVA - QUADRA 10 - LOTE 0024","SMART URBA RESERVA - QUADRA 10 - LOTE 0025",
    "SMART URBA RESERVA - QUADRA 10 - LOTE 0026",
]

# Cole aqui as quadras 11 a 47 seguindo o mesmo padrão acima
# Por limitação de espaço no chat, as quadras 11-47 devem ser adicionadas manualmente
# seguindo exatamente o mesmo formato das quadras acima

EMPREENDIMENTOS = {
    "SMART URBA RESERVA": {
        "tipo": "SMART",
        "unidades": UNIDADES_SMART
    }
}

# ─────────────────────────────────────────
# TABELAS DE PARÂMETROS
# ─────────────────────────────────────────
PESOS = {
    "score_credito":         5,
    "ato":                   5,
    "comprometimento_renda": 4,
    "faixa_renda":           4,
    "plano":                 4,
    "tipo_produto":          3,
    "idade":                 1,
    "estado_civil":          1,
}

NOTAS_SCORE = {"A - B": 5, "C - D": 3, "E - F": 1}
NOTAS_ATO = {"ACIMA DE 4%": 5, "3% A 4%": 4, "2% A 3%": 3, "1% A 2%": 2, "ABAIXO DE 1%": 1}
NOTAS_COMPROMETIMENTO = {"ATÉ 10%": 5, "10% A 20%": 4, "20% A 30%": 3, "30% A 50%": 2, "50% A 100%": 1, "ACIMA DE 100%": 1}
NOTAS_RENDA = {"ACIMA DE R$ 15.000": 5, "R$ 10.001 A R$ 15.000": 4, "R$ 7.501 A R$ 10.000": 3, "R$ 5.001 A R$ 7.500": 2, "R$ 2.501 A R$ 5.000": 1, "ATÉ R$ 2.500": 1}
NOTAS_PLANO = {"CURTO PRAZO (1 A 48X)": 5, "MÉDIO PRAZO (49 A 70X)": 3, "MÉDIO LONGO (71 A 144X)": 2, "LONGO PRAZO (145 A 180X)": 1}
NOTAS_TIPO_PRODUTO = {"LOTEAMENTO FECHADO": 4, "SMART": 3, "CONDOMÍNIO SMART": 2, "LOTEAMENTO ABERTO": 1}
NOTAS_IDADE = {"60+ ANOS": 5, "45 A 60 ANOS": 4, "35 A 45 ANOS": 3, "ATÉ 25 ANOS": 2, "25 A 35 ANOS": 1}
NOTAS_ESTADO_CIVIL = {"CASADO(A)": 3, "DIVORCIADO(A)": 2, "SOLTEIRO(A)": 1}

SCORE_MAX = 130
LIMITE_BAIXO = 90
LIMITE_MODERADO = 61

ABREV_RENDA = {
    "ACIMA DE R$ 15.000": "> R$ 15k",
    "R$ 10.001 A R$ 15.000": "R$ 10k-15k",
    "R$ 7.501 A R$ 10.000": "R$ 7,5k-10k",
    "R$ 5.001 A R$ 7.500": "R$ 5k-7,5k",
    "R$ 2.501 A R$ 5.000": "R$ 2,5k-5k",
    "ATÉ R$ 2.500": "< R$ 2,5k",
}

# ─────────────────────────────────────────
# FUNÇÕES AUXILIARES
# ─────────────────────────────────────────
def calcular_idade(nascimento):
    hoje = date.today()
    return hoje.year - nascimento.year - ((hoje.month, hoje.day) < (nascimento.month, nascimento.day))

def faixa_etaria(idade):
    if idade <= 25: return "ATÉ 25 ANOS"
    elif idade <= 35: return "25 A 35 ANOS"
    elif idade <= 45: return "35 A 45 ANOS"
    elif idade <= 60: return "45 A 60 ANOS"
    else: return "60+ ANOS"

def faixa_comprometimento(perc):
    if perc <= 10: return "ATÉ 10%"
    elif perc <= 20: return "10% A 20%"
    elif perc <= 30: return "20% A 30%"
    elif perc <= 50: return "30% A 50%"
    elif perc <= 100: return "50% A 100%"
    else: return "ACIMA DE 100%"

def faixa_renda(valor):
    if valor > 15000: return "ACIMA DE R$ 15.000"
    elif valor > 10000: return "R$ 10.001 A R$ 15.000"
    elif valor > 7500: return "R$ 7.501 A R$ 10.000"
    elif valor > 5000: return "R$ 5.001 A R$ 7.500"
    elif valor > 2500: return "R$ 2.501 A R$ 5.000"
    else: return "ATÉ R$ 2.500"

def faixa_ato(perc):
    if perc >= 4: return "ACIMA DE 4%"
    elif perc >= 3: return "3% A 4%"
    elif perc >= 2: return "2% A 3%"
    elif perc >= 1: return "1% A 2%"
    else: return "ABAIXO DE 1%"

def calcular_score_total(notas):
    return sum(notas[k] * PESOS[k] for k in PESOS)

def classificar(score):
    if score >= LIMITE_BAIXO: return "🟢 BAIXO RISCO", "green"
    elif score >= LIMITE_MODERADO: return "🟡 RISCO MODERADO", "orange"
    else: return "🔴 ALTO RISCO", "red"

def normalizar(s):
    return (s.upper()
            .replace("É","E").replace("Ê","E").replace("Ã","A")
            .replace("Ç","C").replace("Á","A").replace("Â","A")
            .replace("Í","I").replace("Ó","O").replace("Ô","O")
            .replace("Ú","U").replace("Õ","O"))

def extrair_dados_spc(pdf_file):
    score_extraido = None
    renda_extraida = None
    if not PDF_OK:
        st.warning("⚠️ pdfplumber não instalado.")
        return score_extraido, renda_extraida
    try:
        with pdfplumber.open(pdf_file) as pdf:
            linhas = []
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    linhas.extend(t.splitlines())

        linhas_norm = [normalizar(l) for l in linhas]
        texto_norm = "\n".join(linhas_norm)

        # ── Extração do Score ──
        # Busca linha com RISCO DE CREDITO e pega a letra logo após
        padroes_score = [
            r"RISCO\s+DE\s+CREDITO\s*[:\-]?\s*([A-F])\b",
            r"SCORE\s*[:\-]?\s*([A-F])\b",
            r"CLASSIFICACAO\s*[:\-]?\s*([A-F])\b",
        ]
        for padrao in padroes_score:
            match = re.search(padrao, texto_norm)
            if match:
                letra = match.group(1).upper()
                if letra in ("A","B"): score_extraido = "A - B"
                elif letra in ("C","D"): score_extraido = "C - D"
                elif letra in ("E","F"): score_extraido = "E - F"
                break

        # ── Extração da Renda Presumida ──
        # Busca linha "Renda Presumida - SPC Brasil" e pega o valor da coluna VALOR
        padroes_renda = [
            r"RENDA\s+PRESUMIDA\s*[-–]?\s*SPC\s+BRASIL[^\d]*([\d\.]+,\d{2})",
            r"RENDA\s+PRESUMIDA\s*R?\$?\s*([\d\.]+,\d{2})",
            r"RENDA\s+ESTIMADA\s*R?\$?\s*([\d\.]+,\d{2})",
            r"RENDA\s+MENSAL\s*R?\$?\s*([\d\.]+,\d{2})",
        ]
        for padrao in padroes_renda:
            match = re.search(padrao, texto_norm)
            if match:
                valor_str = match.group(1).replace(".","").replace(",",".")
                try:
                    renda_extraida = float(valor_str)
                    if renda_extraida > 0:
                        break
                except:
                    pass

    except Exception as e:
        st.warning(f"Erro ao processar PDF: {e}")

    return score_extraido, renda_extraida

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
# SESSION STATE
# ─────────────────────────────────────────
if "resultado_calculado" not in st.session_state:
    st.session_state.resultado_calculado = False
if "dados_resultado" not in st.session_state:
    st.session_state.dados_resultado = {}

# ─────────────────────────────────────────
# SEÇÃO 1 — EMPREENDIMENTO
# ─────────────────────────────────────────
st.subheader("🏗️ Dados do Empreendimento")
col_e1, col_e2, col_e3 = st.columns(3)

with col_e1:
    empreendimento = st.selectbox("Empreendimento *", options=[""] + list(EMPREENDIMENTOS.keys()), index=0)

with col_e2:
    if empreendimento and empreendimento in EMPREENDIMENTOS:
        unidades_lista = EMPREENDIMENTOS[empreendimento]["unidades"]
        unidade = st.selectbox("Unidade *", options=[""] + unidades_lista, index=0)
    else:
        unidade = st.selectbox("Unidade *", options=[""], disabled=True)

with col_e3:
    tipo_produto = EMPREENDIMENTOS[empreendimento]["tipo"] if empreendimento and empreendimento in EMPREENDIMENTOS else ""
    st.text_input("Tipo de Produto", value=tipo_produto, disabled=True)

st.divider()

# ─────────────────────────────────────────
# SEÇÃO 2 — DADOS DO PROPONENTE
# ─────────────────────────────────────────
st.subheader("👤 Dados do Cliente Proponente")
col1, col2 = st.columns(2)

with col1:
    nascimento = st.date_input("Data de Nascimento *", min_value=date(1930,1,1), max_value=date.today(), value=None, format="DD/MM/YYYY")
    if nascimento:
        idade = calcular_idade(nascimento)
        faixa = faixa_etaria(idade)
        st.info(f"🎂 Idade: **{idade} anos** — Faixa: **{faixa}**")
    else:
        idade = None
        faixa = None

    estado_civil = st.selectbox("Estado Civil *", options=["", "SOLTEIRO(A)", "CASADO(A)", "DIVORCIADO(A)"], index=0)

with col2:
    st.markdown("**📄 Upload do SPC — Proponente**")
    pdf_proponente = st.file_uploader("Anexar PDF do SPC (Proponente)", type=["pdf"], key="pdf_prop")

    score_prop_auto = None
    renda_prop_auto = 0.0

    if pdf_proponente:
        with st.spinner("Lendo PDF do SPC..."):
            score_prop_auto, renda_prop_auto = extrair_dados_spc(pdf_proponente)
        if score_prop_auto:
            st.success(f"✅ Score extraído: **{score_prop_auto}**")
        else:
            st.warning("⚠️ Score não identificado. Selecione manualmente.")
        if renda_prop_auto and renda_prop_auto > 0:
            st.success(f"✅ Renda Presumida: **R$ {renda_prop_auto:,.2f}**")
        else:
            st.warning("⚠️ Renda não identificada. Informe manualmente.")

    opcoes_score = ["", "A - B", "C - D", "E - F"]
    idx_score = opcoes_score.index(score_prop_auto) if score_prop_auto in opcoes_score else 0
    score_proponente = st.selectbox("Score de Crédito (SPC) — Proponente *", options=opcoes_score, index=idx_score)
    renda_proponente = st.number_input("Renda Presumida — Proponente (R$) *", min_value=0.0, value=float(renda_prop_auto) if renda_prop_auto and renda_prop_auto > 0 else 0.0, step=100.0, format="%.2f")

st.divider()

# ─────────────────────────────────────────
# SEÇÃO 3 — CLIENTES ADICIONAIS
# ─────────────────────────────────────────
st.subheader("👥 Composição de Renda — Clientes Adicionais")
scores_adicionais = []
rendas_adicionais = []

for i in range(1, 5):
    adicionar = st.checkbox(f"Adicionar Cliente {i+1} para composição de renda", key=f"check_{i}")
    if adicionar:
        col_a, col_b = st.columns(2)
        with col_a:
            pdf_adicional = st.file_uploader(f"PDF do SPC — Cliente {i+1}", type=["pdf"], key=f"pdf_add_{i}")
            score_add_auto = None
            renda_add_auto = 0.0
            if pdf_adicional:
                with st.spinner(f"Lendo PDF do Cliente {i+1}..."):
                    score_add_auto, renda_add_auto = extrair_dados_spc(pdf_adicional)
                if score_add_auto:
                    st.success(f"✅ Score: **{score_add_auto}**")
                else:
                    st.warning("⚠️ Score não identificado. Selecione manualmente.")
                if renda_add_auto and renda_add_auto > 0:
                    st.success(f"✅ Renda: **R$ {renda_add_auto:,.2f}**")
                else:
                    st.warning("⚠️ Renda não identificada. Informe manualmente.")
            opcoes_s = ["", "A - B", "C - D", "E - F"]
            idx_s = opcoes_s.index(score_add_auto) if score_add_auto in opcoes_s else 0
            sc = st.selectbox(f"Score — Cliente {i+1}", options=opcoes_s, index=idx_s, key=f"score_add_{i}")
            scores_adicionais.append(sc)
        with col_b:
            rd = st.number_input(f"Renda — Cliente {i+1} (R$)", min_value=0.0, value=float(renda_add_auto) if renda_add_auto and renda_add_auto > 0 else 0.0, step=100.0, format="%.2f", key=f"renda_add_{i}")
            rendas_adicionais.append(rd)
    else:
        break

# ─────────────────────────────────────────
# SCORE CONSOLIDADO E RENDA TOTAL
# ─────────────────────────────────────────
todos_scores_validos = [s for s in ([score_proponente] + scores_adicionais) if s]
ORDEM_SCORE = {"A - B": 1, "C - D": 2, "E - F": 3}
score_consolidado = min(todos_scores_validos, key=lambda x: ORDEM_SCORE.get(x, 99)) if todos_scores_validos else None
renda_total = renda_proponente + sum(rendas_adicionais)

st.divider()

# ─────────────────────────────────────────
# SEÇÃO 4 — DADOS FINANCEIROS
# ─────────────────────────────────────────
st.subheader("💰 Dados Financeiros")
col3, col4 = st.columns(2)

with col3:
    ato_urba = st.number_input("Ato Urba (R$) *", min_value=0.0, value=0.0, step=100.0, format="%.2f")
    valor_proposta = st.number_input("Valor da Proposta / Líquido CV (R$) *", min_value=0.0, value=0.0, step=100.0, format="%.2f")

with col4:
    plano = st.selectbox("Plano *", options=["", "CURTO PRAZO (1 A 48X)", "MÉDIO PRAZO (49 A 70X)", "MÉDIO LONGO (71 A 144X)", "LONGO PRAZO (145 A 180X)"], index=0)
    primeira_mensal = st.number_input("Valor da 1ª Mensal (R$) *", min_value=0.0, value=0.0, step=10.0, format="%.2f")

# ─────────────────────────────────────────
# CÁLCULOS AUTOMÁTICOS
# ─────────────────────────────────────────
perc_ato = (ato_urba / valor_proposta * 100) if valor_proposta > 0 else 0
perc_comprometimento = (primeira_mensal / renda_total * 100) if renda_total > 0 else 0
faixa_comp = faixa_comprometimento(perc_comprometimento)
faixa_at = faixa_ato(perc_ato)
faixa_rd = faixa_renda(renda_total)

st.divider()
col5, col6, col7, col8 = st.columns(4)
col5.metric("📊 % do Ato", f"{perc_ato:.1f}%", faixa_at)
col6.metric("📉 Comprometimento", f"{perc_comprometimento:.1f}%", faixa_comp)
col7.metric("💵 Renda Total", f"R$ {renda_total:,.2f}", ABREV_RENDA.get(faixa_rd, faixa_rd))
col8.metric("🎂 Faixa Etária", faixa if faixa else "—")

# ─────────────────────────────────────────
# VALIDAÇÃO
# ─────────────────────────────────────────
campos_faltando = []
if not empreendimento: campos_faltando.append("Empreendimento")
if not unidade: campos_faltando.append("Unidade")
if not nascimento: campos_faltando.append("Data de Nascimento")
if not estado_civil: campos_faltando.append("Estado Civil")
if not score_consolidado: campos_faltando.append("Score de Crédito")
if renda_total <= 0: campos_faltando.append("Renda")
if valor_proposta <= 0: campos_faltando.append("Valor da Proposta")
if not plano: campos_faltando.append("Plano")
if primeira_mensal <= 0: campos_faltando.append("Valor da 1ª Mensal")

st.divider()
if campos_faltando:
    st.warning(f"⚠️ Preencha: **{', '.join(campos_faltando)}**")

# ─────────────────────────────────────────
# BOTÃO CALCULAR
# ─────────────────────────────────────────
btn_calcular = st.button("🎯 CALCULAR SCORE DA VENDA", use_container_width=True, type="primary", disabled=bool(campos_faltando))

if btn_calcular:
    notas = {
        "score_credito": NOTAS_SCORE.get(score_consolidado, 0),
        "ato": NOTAS_ATO.get(faixa_at, 0),
        "comprometimento_renda": NOTAS_COMPROMETIMENTO.get(faixa_comp, 0),
        "faixa_renda": NOTAS_RENDA.get(faixa_rd, 0),
        "plano": NOTAS_PLANO.get(plano, 0),
        "tipo_produto": NOTAS_TIPO_PRODUTO.get(tipo_produto, 0),
        "idade": NOTAS_IDADE.get(faixa, 0),
        "estado_civil": NOTAS_ESTADO_CIVIL.get(estado_civil, 0),
    }
    score_final = calcular_score_total(notas)
    classificacao, cor = classificar(score_final)
    st.session_state.resultado_calculado = True
    st.session_state.dados_resultado = {
        "notas": notas, "score_final": score_final, "classificacao": classificacao, "cor": cor,
        "faixa_comp": faixa_comp, "faixa_at": faixa_at, "faixa_rd": faixa_rd, "faixa": faixa,
        "perc_ato": perc_ato, "perc_comprometimento": perc_comprometimento, "renda_total": renda_total,
        "plano": plano, "score_consolidado": score_consolidado, "empreendimento": empreendimento,
        "unidade": unidade, "tipo_produto": tipo_produto, "idade": idade, "estado_civil": estado_civil,
        "primeira_mensal": primeira_mensal, "valor_proposta": valor_proposta, "ato_urba": ato_urba,
    }

# ─────────────────────────────────────────
# RESULTADO
# ─────────────────────────────────────────
if st.session_state.resultado_calculado and st.session_state.dados_resultado:
    d = st.session_state.dados_resultado
    notas = d["notas"]; score_final = d["score_final"]; classificacao = d["classificacao"]; cor = d["cor"]
    faixa_comp = d["faixa_comp"]; faixa_at = d["faixa_at"]; faixa_rd = d["faixa_rd"]; faixa = d["faixa"]
    plano_res = d["plano"]; score_cons = d["score_consolidado"]

    st.divider()
    st.subheader("📊 Resultado do Score")
    col9, col10 = st.columns([1, 2])

    with col9:
        st.metric("Score Final", f"{score_final} / {SCORE_MAX}")
        if cor == "green": st.success(f"### {classificacao}")
        elif cor == "orange": st.warning(f"### {classificacao}")
        else: st.error(f"### {classificacao}")

    with col10:
        st.markdown("**Detalhamento por variável:**")
        LABELS = {
            "score_credito": "Score de Crédito", "ato": "% do Ato",
            "comprometimento_renda": "Comprometimento de Renda", "faixa_renda": "Faixa de Renda",
            "plano": "Plano", "tipo_produto": "Tipo de Produto", "idade": "Faixa Etária", "estado_civil": "Estado Civil",
        }
        detalhes = []
        for k, peso in PESOS.items():
            nota = notas[k]
            nota_max = 5 if k != "tipo_produto" else 4
            detalhes.append({"Variável": LABELS[k], "Nota": f"{nota}/{nota_max}", "Peso": peso, "Contribuição": nota*peso, "Máximo": nota_max*peso})
        st.dataframe(pd.DataFrame(detalhes), use_container_width=True, hide_index=True)

    # ── SUGESTÕES INTELIGENTES ──
    if cor in ("red", "orange"):
        st.divider()
        falta_moderado = max(0, LIMITE_MODERADO - score_final)
        falta_baixo = max(0, LIMITE_BAIXO - score_final)

        if cor == "red":
            st.subheader("💡 Sugestões para Reduzir o Risco")
            st.markdown(f"| Meta | Pontos necessários |\n|---|---|\n| 🟡 Risco Moderado | **+{falta_moderado} pontos** |\n| 🟢 Baixo Risco | **+{falta_baixo} pontos** |")
        else:
            st.subheader("⚠️ Pontos de Melhoria")
            st.markdown(f"Faltam **+{falta_baixo} pontos** para 🟢 BAIXO RISCO")

        sugestoes = []
        if notas["score_credito"] < 5:
            ganho = (5 - notas["score_credito"]) * PESOS["score_credito"]
            sugestoes.append((ganho, f"📋 **Score de Crédito ({score_cons})** → Incluir titular com score **A-B** pode agregar até **+{ganho} pontos**. {'✅ Suficiente para sair do Alto Risco!' if ganho >= falta_moderado else ''}"))
        if notas["comprometimento_renda"] < 5:
            ganho = (5 - notas["comprometimento_renda"]) * PESOS["comprometimento_renda"]
            sugestoes.append((ganho, f"📉 **Comprometimento de Renda ({faixa_comp})** → Composição de renda ou redução da mensal pode agregar até **+{ganho} pontos**. {'✅ Suficiente para sair do Alto Risco!' if ganho >= falta_moderado else ''}"))
        if notas["ato"] < 5:
            ganho = (5 - notas["ato"]) * PESOS["ato"]
            sugestoes.append((ganho, f"💰 **% do Ato ({faixa_at})** → Aumentar o Ato para acima de 4% pode agregar até **+{ganho} pontos**. {'✅ Suficiente para sair do Alto Risco!' if ganho >= falta_moderado else ''}"))
        if notas["faixa_renda"] < 5:
            ganho = (5 - notas["faixa_renda"]) * PESOS["faixa_renda"]
            sugestoes.append((ganho, f"💵 **Faixa de Renda ({ABREV_RENDA.get(faixa_rd, faixa_rd)})** → Adicionar titulares pode agregar até **+{ganho} pontos**."))
        if notas["plano"] < 5:
            ganho = (5 - notas["plano"]) * PESOS["plano"]
            sugestoes.append((ganho, f"📅 **Plano ({plano_res})** → Migrar para prazo menor pode agregar até **+{ganho} pontos**."))

        sugestoes.sort(key=lambda x: x[0], reverse=True)
        for _, texto in sugestoes:
            st.markdown(f"- {texto}")

    # ── SALVAR NO HISTÓRICO ──
    st.divider()
    st.markdown("### 💾 Salvar no Histórico")
    st.caption("Salve apenas simulações de propostas reais.")
    col_s1, col_s2 = st.columns([1, 3])
    with col_s1:
        if st.button("✅ Confirmar e Salvar", type="primary"):
            dados_registro = {
                "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "Empreendimento": d["empreendimento"], "Unidade": d["unidade"], "Tipo Produto": d["tipo_produto"],
                "Idade": d["idade"], "Faixa Etária": d["faixa"], "Estado Civil": d["estado_civil"],
                "Score Crédito": d["score_consolidado"], "Ato Urba (R$)": d["ato_urba"],
                "Valor Proposta (R$)": d["valor_proposta"], "% Ato": round(d["perc_ato"],1),
                "Faixa Ato": d["faixa_at"], "Plano": d["plano"], "Renda Total (R$)": d["renda_total"],
                "1ª Mensal (R$)": d["primeira_mensal"], "% Comprometimento": round(d["perc_comprometimento"],1),
                "Faixa Comprometimento": d["faixa_comp"], "Faixa Renda": d["faixa_rd"],
                "Score Final": d["score_final"], "Classificação": d["classificacao"],
            }
            salvar_historico(dados_registro)
            st.success("✅ Simulação salva!")
            st.session_state.resultado_calculado = False
    with col_s2:
        if st.button("🗑️ Descartar", type="secondary"):
            st.info("Simulação descartada.")
            st.session_state.resultado_calculado = False

# ─────────────────────────────────────────
# HISTÓRICO
# ─────────────────────────────────────────
st.divider()
with st.expander("📂 Ver Histórico de Simulações Salvas"):
    if os.path.exists("historico.csv"):
        df_hist = pd.read_csv("historico.csv")
        st.dataframe(df_hist, use_container_width=True, hide_index=True)
        csv = df_hist.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Baixar Histórico em CSV", csv, "historico_simulacoes.csv", "text/csv")
    else:
        st.info("Nenhuma simulação salva ainda.")
