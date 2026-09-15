

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
EMPREENDIMENTOS = {
    "SMART URBA RESERVA": {
        "tipo": "SMART",
        "unidades": [
            "QUADRA 01 LOTE 01", "QUADRA 01 LOTE 02", "QUADRA 01 LOTE 03",
            "QUADRA 01 LOTE 04", "QUADRA 01 LOTE 05", "QUADRA 02 LOTE 01",
            "QUADRA 02 LOTE 02", "QUADRA 02 LOTE 03", "QUADRA 02 LOTE 04",
            "QUADRA 02 LOTE 05", "QUADRA 03 LOTE 01", "QUADRA 03 LOTE 02",
        ]
    }
}

TIPOS_PRODUTO = ["LOTEAMENTO ABERTO", "CONDOMÍNIO SMART", "LOTEAMENTO FECHADO", "SMART"]

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

NOTAS_SCORE = {
    "A - B": 5,
    "C - D": 3,
    "E - F": 1,
}

NOTAS_ATO = {
    "ACIMA DE 4%":  5,
    "3% A 4%":      3,
    "2% A 3%":      4,
    "1% A 2%":      2,
    "ABAIXO DE 1%": 1,
}

NOTAS_COMPROMETIMENTO = {
    "ATÉ 10%":       5,
    "10% A 20%":     4,
    "20% A 30%":     3,
    "30% A 50%":     2,
    "50% A 100%":    1,
    "ACIMA DE 100%": 1,
}

NOTAS_RENDA = {
    "ACIMA DE R$ 15.000":      5,
    "R$ 10.001 A R$ 15.000":   4,
    "R$ 7.501 A R$ 10.000":    3,
    "R$ 5.001 A R$ 7.500":     2,
    "R$ 2.501 A R$ 5.000":     1,
    "ATÉ R$ 2.500":            1,
}

NOTAS_PLANO = {
    "CURTO PRAZO (1 A 48X)":          5,
    "MÉDIO PRAZO (49 A 70X)":         3,
    "MÉDIO LONGO (71 A 144X)":        2,
    "LONGO PRAZO (145 A 180X)":       1,
}

NOTAS_TIPO_PRODUTO = {
    "LOTEAMENTO FECHADO": 4,
    "SMART":              3,
    "CONDOMÍNIO SMART":   2,
    "LOTEAMENTO ABERTO":  1,
}

NOTAS_IDADE = {
    "35 A 45 ANOS": 3,
    "45 A 60 ANOS": 4,
    "60+ ANOS":     5,
    "25 A 35 ANOS": 1,
    "ATÉ 25 ANOS":  2,
}

NOTAS_ESTADO_CIVIL = {
    "CASADO(A)":     3,
    "DIVORCIADO(A)": 2,
    "SOLTEIRO(A)":   1,
}

SCORE_MAX = 130
LIMITE_BAIXO = 90
LIMITE_MODERADO = 61

# ─────────────────────────────────────────
# FUNÇÕES AUXILIARES
# ─────────────────────────────────────────
def calcular_idade(nascimento):
    hoje = date.today()
    return hoje.year - nascimento.year - ((hoje.month, hoje.day) < (nascimento.month, nascimento.day))

def faixa_etaria(idade):
    if idade <= 25:  return "ATÉ 25 ANOS"
    elif idade <= 35: return "25 A 35 ANOS"
    elif idade <= 45: return "35 A 45 ANOS"
    elif idade <= 60: return "45 A 60 ANOS"
    else:             return "60+ ANOS"

def faixa_comprometimento(perc):
    if perc <= 10:   return "ATÉ 10%"
    elif perc <= 20: return "10% A 20%"
    elif perc <= 30: return "20% A 30%"
    elif perc <= 50: return "30% A 50%"
    elif perc <= 100:return "50% A 100%"
    else:            return "ACIMA DE 100%"

def faixa_renda(valor):
    if valor > 15000:   return "ACIMA DE R$ 15.000"
    elif valor > 10000: return "R$ 10.001 A R$ 15.000"
    elif valor > 7500:  return "R$ 7.501 A R$ 10.000"
    elif valor > 5000:  return "R$ 5.001 A R$ 7.500"
    elif valor > 2500:  return "R$ 2.501 A R$ 5.000"
    else:               return "ATÉ R$ 2.500"

def faixa_ato(perc):
    if perc >= 4:   return "ACIMA DE 4%"
    elif perc >= 3: return "3% A 4%"
    elif perc >= 2: return "2% A 3%"
    elif perc >= 1: return "1% A 2%"
    else:           return "ABAIXO DE 1%"

def calcular_score_total(notas):
    return sum(notas[k] * PESOS[k] for k in PESOS)

def classificar(score):
    if score >= LIMITE_BAIXO:    return "🟢 BAIXO RISCO",    "green"
    elif score >= LIMITE_MODERADO: return "🟡 RISCO MODERADO", "orange"
    else:                          return "🔴 ALTO RISCO",     "red"

def extrair_dados_spc(pdf_file):
    """Extrai Score (Risco de Crédito) e Renda Presumida do PDF do SPC."""
    score_extraido = None
    renda_extraida = None

    if not PDF_OK:
        return score_extraido, renda_extraida

    try:
        with pdfplumber.open(pdf_file) as pdf:
            texto_completo = ""
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    texto_completo += t + "\n"

        texto_upper = texto_completo.upper()

        # ── Extração do Score / Risco de Crédito ──────────────────
        # Padrão: "RISCO DE CREDITO C" ou "RISCO DE CRÉDITO: C"
        padroes_score = [
            r"RISCO\s+DE\s+CR[EÉ]DITO[:\s]+([A-F])",
            r"SCORE[:\s]+([A-F])\b",
            r"CLASSIFICA[CÇ][AÃ]O[:\s]+([A-F])\b",
        ]
        for padrao in padroes_score:
            match = re.search(padrao, texto_upper)
            if match:
                letra = match.group(1).upper()
                if letra in ["A", "B"]:
                    score_extraido = "A - B"
                elif letra in ["C", "D"]:
                    score_extraido = "C - D"
                elif letra in ["E", "F"]:
                    score_extraido = "E - F"
                break

        # ── Extração da Renda Presumida ───────────────────────────
        padroes_renda = [
            r"RENDA\s+PRESUMIDA[:\s]*R?\$?\s*([\d\.]+(?:,\d{2})?)",
            r"RENDA\s+ESTIMADA[:\s]*R?\$?\s*([\d\.]+(?:,\d{2})?)",
            r"RENDA[:\s]*R?\$?\s*([\d\.]+(?:,\d{2})?)",
        ]
        for padrao in padroes_renda:
            match = re.search(padrao, texto_upper)
            if match:
                valor_str = match.group(1).replace(".", "").replace(",", ".")
                try:
                    renda_extraida = float(valor_str)
                except:
                    pass
                break

    except Exception as e:
        st.warning(f"Erro ao ler PDF: {e}")

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
# INICIALIZAR SESSION STATE
# ─────────────────────────────────────────
if "scores_clientes" not in st.session_state:
    st.session_state.scores_clientes = [None]
if "rendas_clientes" not in st.session_state:
    st.session_state.rendas_clientes = [0.0]
if "num_clientes" not in st.session_state:
    st.session_state.num_clientes = 1

# ─────────────────────────────────────────
# FORMULÁRIO — EMPREENDIMENTO
# ─────────────────────────────────────────
st.subheader("🏗️ Dados do Empreendimento")
col_emp1, col_emp2, col_emp3 = st.columns(3)

with col_emp1:
    empreendimento = st.selectbox(
        "Empreendimento",
        options=[""] + list(EMPREENDIMENTOS.keys()),
        index=0
    )

with col_emp2:
    if empreendimento and empreendimento in EMPREENDIMENTOS:
        unidades_disponiveis = EMPREENDIMENTOS[empreendimento]["unidades"]
        unidade = st.selectbox("Unidade", options=[""] + unidades_disponiveis)
    else:
        unidade = st.selectbox("Unidade", options=[""], disabled=True)

with col_emp3:
    if empreendimento and empreendimento in EMPREENDIMENTOS:
        tipo_produto_auto = EMPREENDIMENTOS[empreendimento]["tipo"]
        st.text_input("Tipo de Produto", value=tipo_produto_auto, disabled=True)
        tipo_produto = tipo_produto_auto
    else:
        st.text_input("Tipo de Produto", value="", disabled=True)
        tipo_produto = ""

st.divider()

# ─────────────────────────────────────────
# FORMULÁRIO — DADOS DO CLIENTE PROPONENTE
# ─────────────────────────────────────────
st.subheader("👤 Dados do Cliente Proponente")

col1, col2 = st.columns(2)

with col1:
    nascimento = st.date_input(
        "Data de Nascimento",
        min_value=date(1930, 1, 1),
        max_value=date.today(),
        value=date(1990, 1, 1)
    )
    idade = calcular_idade(nascimento)
    faixa = faixa_etaria(idade)
    st.info(f"🎂 Idade: **{idade} anos** — Faixa: **{faixa}**")

    estado_civil = st.selectbox(
        "Estado Civil",
        ["SOLTEIRO(A)", "CASADO(A)", "DIVORCIADO(A)"]
    )

with col2:
    st.markdown("**📄 Upload do SPC — Proponente**")
    pdf_proponente = st.file_uploader(
        "Anexar PDF do SPC (Proponente)",
        type=["pdf"],
        key="pdf_prop"
    )

    score_prop = None
    renda_prop = 0.0

    if pdf_proponente:
        score_prop, renda_prop = extrair_dados_spc(pdf_proponente)
        if score_prop:
            st.success(f"✅ Score extraído: **{score_prop}**")
        else:
            st.warning("⚠️ Score não encontrado no PDF. Selecione manualmente.")
        if renda_prop and renda_prop > 0:
            st.success(f"✅ Renda Presumida extraída: **R$ {renda_prop:,.2f}**")
        else:
            st.warning("⚠️ Renda não encontrada no PDF. Informe manualmente.")

    opcoes_score = ["", "A - B", "C - D", "E - F"]
    idx_score = opcoes_score.index(score_prop) if score_prop in opcoes_score else 0
    score_proponente = st.selectbox(
        "Score de Crédito (SPC) — Proponente",
        opcoes_score,
        index=idx_score
    )

    renda_proponente = st.number_input(
        "Renda Presumida — Proponente (R$)",
        min_value=0.0,
        value=float(renda_prop) if renda_prop else 0.0,
        step=100.0,
        format="%.2f"
    )

# ─────────────────────────────────────────
# CLIENTES ADICIONAIS (até 4)
# ─────────────────────────────────────────
st.divider()
st.subheader("👥 Composição de Renda — Clientes Adicionais")

scores_adicionais = []
rendas_adicionais = []

for i in range(1, 5):
    adicionar = st.checkbox(f"Adicionar Cliente {i+1} para composição de renda", key=f"check_{i}")
    if adicionar:
        col_a, col_b = st.columns(2)
        with col_a:
            pdf_adicional = st.file_uploader(
                f"PDF do SPC — Cliente {i+1}",
                type=["pdf"],
                key=f"pdf_add_{i}"
            )
            score_add = None
            renda_add = 0.0
            if pdf_adicional:
                score_add, renda_add = extrair_dados_spc(pdf_adicional)
                if score_add:
                    st.success(f"✅ Score: **{score_add}**")
                if renda_add and renda_add > 0:
                    st.success(f"✅ Renda: **R$ {renda_add:,.2f}**")

            opcoes_s = ["", "A - B", "C - D", "E - F"]
            idx_s = opcoes_s.index(score_add) if score_add in opcoes_s else 0
            sc = st.selectbox(f"Score — Cliente {i+1}", opcoes_s, index=idx_s, key=f"score_add_{i}")
            scores_adicionais.append(sc)

        with col_b:
            rd = st.number_input(
                f"Renda — Cliente {i+1} (R$)",
                min_value=0.0,
                value=float(renda_add) if renda_add else 0.0,
                step=100.0,
                format="%.2f",
                key=f"renda_add_{i}"
            )
            rendas_adicionais.append(rd)
    else:
        break

# ─────────────────────────────────────────
# SCORE CONSOLIDADO E RENDA TOTAL
# ─────────────────────────────────────────
todos_scores = [score_proponente] + [s for s in scores_adicionais if s]
todos_scores_validos = [s for s in todos_scores if s]

# Melhor score entre todos os clientes
ORDEM_SCORE = {"A - B": 1, "C - D": 2, "E - F": 3}
if todos_scores_validos:
    score_consolidado = min(todos_scores_validos, key=lambda x: ORDEM_SCORE.get(x, 99))
else:
    score_consolidado = None

renda_total = renda_proponente + sum(rendas_adicionais)

st.divider()

# ─────────────────────────────────────────
# DADOS FINANCEIROS
# ─────────────────────────────────────────
st.subheader("💰 Dados Financeiros")
col3, col4 = st.columns(2)

with col3:
    ato_urba = st.number_input("Ato Urba (R$)", min_value=0.0, step=100.0, format="%.2f")
    valor_proposta = st.number_input("Valor da Proposta / Líquido CV (R$)", min_value=0.01, step=100.0, format="%.2f")

with col4:
    plano = st.selectbox("Plano", list(NOTAS_PLANO.keys()))
    primeira_mensal = st.number_input("Valor da 1ª Mensal (R$)", min_value=0.01, step=10.0, format="%.2f")

# ─────────────────────────────────────────
# CÁLCULOS AUTOMÁTICOS
# ─────────────────────────────────────────
perc_ato = (ato_urba / valor_proposta * 100) if valor_proposta > 0 else 0
perc_comprometimento = (primeira_mensal / renda_total * 100) if renda_total > 0 else 0
faixa_comp = faixa_comprometimento(perc_comprometimento)
faixa_at = faixa_ato(perc_ato)
faixa_rd = faixa_renda(renda_total)

# Abreviações para os cards
ABREV_RENDA = {
    "ACIMA DE R$ 15.000":    "> R$ 15k",
    "R$ 10.001 A R$ 15.000": "R$ 10k-15k",
    "R$ 7.501 A R$ 10.000":  "R$ 7,5k-10k",
    "R$ 5.001 A R$ 7.500":   "R$ 5k-7,5k",
    "R$ 2.501 A R$ 5.000":   "R$ 2,5k-5k",
    "ATÉ R$ 2.500":          "< R$ 2,5k",
}

st.divider()
col5, col6, col7, col8 = st.columns(4)
col5.metric("📊 % do Ato",              f"{perc_ato:.1f}%",              faixa_at)
col6.metric("📉 Comprometimento",        f"{perc_comprometimento:.1f}%",  faixa_comp)
col7.metric("💵 Renda Total",            f"R$ {renda_total:,.2f}",        ABREV_RENDA.get(faixa_rd, faixa_rd))
col8.metric("🎂 Faixa Etária",           faixa)

# ─────────────────────────────────────────
# BOTÃO CALCULAR
# ─────────────────────────────────────────
st.divider()

campos_ok = (
    empreendimento and
    unidade and
    tipo_produto and
    score_consolidado and
    renda_total > 0
)

if not campos_ok:
    st.info("ℹ️ Preencha todos os campos obrigatórios para calcular o score.")

if st.button("🎯 CALCULAR SCORE DA VENDA", use_container_width=True, type="primary", disabled=not campos_ok):

    notas = {
        "score_credito":         NOTAS_SCORE.get(score_consolidado, 0),
        "ato":                   NOTAS_ATO.get(faixa_at, 0),
        "comprometimento_renda": NOTAS_COMPROMETIMENTO.get(faixa_comp, 0),
        "faixa_renda":           NOTAS_RENDA.get(faixa_rd, 0),
        "plano":                 NOTAS_PLANO.get(plano, 0),
        "tipo_produto":          NOTAS_TIPO_PRODUTO.get(tipo_produto, 0),
        "idade":                 NOTAS_IDADE.get(faixa, 0),
        "estado_civil":          NOTAS_ESTADO_CIVIL.get(estado_civil, 0),
    }

    score_final = calcular_score_total(notas)
    classificacao, cor = classificar(score_final)

    st.divider()
    st.subheader("📊 Resultado do Score")

    col9, col10 = st.columns([1, 2])
    with col9:
        st.metric("Score Final", f"{score_final} / {SCORE_MAX}")
        if cor == "green":
            st.success(f"### {classificacao}")
        elif cor == "orange":
            st.warning(f"### {classificacao}")
        else:
            st.error(f"### {classificacao}")

    with col10:
        st.markdown("**Detalhamento por variável:**")
        detalhes = []
        for k, peso in PESOS.items():
            nota = notas[k]
            contribuicao = nota * peso
            detalhes.append({
                "Variável":      k.replace("_", " ").title(),
                "Nota":          nota,
                "Peso":          peso,
                "Contribuição":  contribuicao,
            })
        st.dataframe(pd.DataFrame(detalhes), use_container_width=True, hide_index=True)

    # ── SUGESTÕES INTELIGENTES ────────────────────────────────────
    if cor in ("red", "orange"):
        st.divider()
        titulo = "💡 Sugestões para sair do ALTO RISCO" if cor == "red" else "⚠️ Pontos de Melhoria"
        st.subheader(titulo)

        falta_moderado = max(0, LIMITE_MODERADO - score_final)
        falta_baixo    = max(0, LIMITE_BAIXO - score_final)

        if cor == "red":
            st.markdown(f"- Faltam **{falta_moderado} pontos** para RISCO MODERADO")
            st.markdown(f"- Faltam **{falta_baixo} pontos** para BAIXO RISCO")
        else:
            st.markdown(f"- Faltam **{falta_baixo} pontos** para BAIXO RISCO")

        sugestoes = []

        # Score de crédito
        if notas["score_credito"] < 5:
            ganho = (5 - notas["score_credito"]) * PESOS["score_credito"]
            sugestoes.append((ganho, f"📋 **Score de Crédito ({score_consolidado})** → Incluir titular com score A-B pode ganhar até **+{ganho} pontos**"))

        # Comprometimento de renda
        if notas["comprometimento_renda"] < 5:
            ganho = (5 - notas["comprometimento_renda"]) * PESOS["comprometimento_renda"]
            sugestoes.append((ganho, f"📉 **Comprometimento de Renda ({faixa_comp})** → Composição de renda ou redução da mensal pode ganhar até **+{ganho} pontos**"))

        # Ato
        if notas["ato"] < 5:
            ganho = (5 - notas["ato"]) * PESOS["ato"]
            sugestoes.append((ganho, f"💰 **% do Ato ({faixa_at})** → Aumentar o Ato Urba para acima de 4% pode ganhar até **+{ganho} pontos**"))

        # Faixa de renda
        if notas["faixa_renda"] < 5:
            ganho = (5 - notas["faixa_renda"]) * PESOS["faixa_renda"]
            sugestoes.append((ganho, f"💵 **Faixa de Renda ({ABREV_RENDA.get(faixa_rd, faixa_rd)})** → Composição com mais titulares pode ganhar até **+{ganho} pontos**"))

        # Plano
        if notas["plano"] < 5:
            ganho = (5 - notas["plano"]) * PESOS["plano"]
            sugestoes.append((ganho, f"📅 **Plano ({plano})** → Migrar para plano de menor prazo pode ganhar até **+{ganho} pontos**"))

        # Ordenar por maior ganho
        sugestoes.sort(key=lambda x: x[0], reverse=True)
        for _, texto in sugestoes:
            st.markdown(f"- {texto}")

    # ── SALVAR HISTÓRICO ──────────────────────────────────────────
    dados_registro = {
        "Data":                  datetime.now().strftime("%d/%m/%Y %H:%M"),
        "Empreendimento":        empreendimento,
        "Unidade":               unidade,
        "Tipo Produto":          tipo_produto,
        "Idade":                 idade,
        "Faixa Etária":          faixa,
        "Estado Civil":          estado_civil,
        "Score Crédito":         score_consolidado,
        "% Ato":                 round(perc_ato, 1),
        "Faixa Ato":             faixa_at,
        "Plano":                 plano,
        "Renda Total":           renda_total,
        "1ª Mensal":             primeira_mensal,
        "% Comprometimento":     round(perc_comprometimento, 1),
        "Faixa Comprometimento": faixa_comp,
        "Faixa Renda":           faixa_rd,
        "Score Final":           score_final,
        "Classificação":         classificacao,
    }
    salvar_historico(dados_registro)
    st.success("✅ Simulação salva no histórico!")

# ─────────────────────────────────────────
# HISTÓRICO
# ─────────────────────────────────────────
st.divider()
with st.expander("📂 Ver Histórico de Simulações"):
    if os.path.exists("historico.csv"):
        df_hist = pd.read_csv("historico.csv")
        st.dataframe(df_hist, use_container_width=True, hide_index=True)
        csv = df_hist.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Baixar Histórico em CSV", csv, "historico_simulacoes.csv", "text/csv")
    else:
        st.info("Nenhuma simulação registrada ainda.")

