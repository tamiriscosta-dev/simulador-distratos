import streamlit as st
import pandas as pd
from datetime import date, datetime
import os

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
# TABELAS DE PARÂMETROS (editáveis)
# ─────────────────────────────────────────

PESOS = {
    "faixa_etaria":         0.10,
    "estado_civil":         0.05,
    "score_credito":        0.25,
    "comprometimento_renda":0.25,
    "ato":                  0.20,
    "tipo_produto":         0.10,
    "plano":                0.05,
}

NOTAS_FAIXA_ETARIA = {
    "18 a 25 anos": 0.5,
    "26 a 35 anos": 1.0,
    "36 a 45 anos": 1.0,
    "46 a 55 anos": 0.8,
    "56 a 65 anos": 0.6,
    "Acima de 65 anos": 0.4,
}

NOTAS_ESTADO_CIVIL = {
    "Casado(a)": 1.0,
    "União Estável": 0.9,
    "Solteiro(a)": 0.7,
    "Divorciado(a)": 0.6,
    "Viúvo(a)": 0.6,
}

NOTAS_SCORE = {
    "A": 1.0,
    "B": 0.85,
    "C": 0.70,
    "D": 0.50,
    "E": 0.30,
    "F": 0.10,
}

NOTAS_COMPROMETIMENTO = {
    "Até 20%":       1.0,
    "21% a 30%":     0.85,
    "31% a 40%":     0.60,
    "Acima de 40%":  0.20,
}

NOTAS_ATO = {
    "Acima de 20%":  1.0,
    "15% a 20%":     0.80,
    "10% a 14%":     0.60,
    "5% a 9%":       0.40,
    "Abaixo de 5%":  0.20,
}

NOTAS_TIPO_PRODUTO = {
    "Alto Padrão":   1.0,
    "Médio Padrão":  0.85,
    "Econômico":     0.70,
    "MCMV":          0.55,
}

NOTAS_PLANO = {
    "À Vista":                    1.0,
    "Entrada Reforçada":          0.90,
    "Plano Padrão":               0.75,
    "Parcelamento Longo":         0.55,
    "Financiamento Máximo":       0.40,
}

CLASSIFICACAO = [
    (0.80, 1.00, "🟢 BAIXO RISCO",  "green"),
    (0.55, 0.79, "🟡 MÉDIO RISCO",  "orange"),
    (0.00, 0.54, "🔴 ALTO RISCO",   "red"),
]

# ─────────────────────────────────────────
# FUNÇÕES AUXILIARES
# ─────────────────────────────────────────

def calcular_idade(nascimento):
    hoje = date.today()
    return hoje.year - nascimento.year - ((hoje.month, hoje.day) < (nascimento.month, nascimento.day))

def faixa_etaria(idade):
    if idade <= 25: return "18 a 25 anos"
    elif idade <= 35: return "26 a 35 anos"
    elif idade <= 45: return "36 a 45 anos"
    elif idade <= 55: return "46 a 55 anos"
    elif idade <= 65: return "56 a 65 anos"
    else: return "Acima de 65 anos"

def faixa_comprometimento(perc):
    if perc <= 20: return "Até 20%"
    elif perc <= 30: return "21% a 30%"
    elif perc <= 40: return "31% a 40%"
    else: return "Acima de 40%"

def faixa_ato(perc):
    if perc >= 20: return "Acima de 20%"
    elif perc >= 15: return "15% a 20%"
    elif perc >= 10: return "10% a 14%"
    elif perc >= 5:  return "5% a 9%"
    else: return "Abaixo de 5%"

def calcular_score(notas):
    return sum(notas[k] * PESOS[k] for k in PESOS)

def classificar(score):
    for minv, maxv, label, cor in CLASSIFICACAO:
        if minv <= score <= maxv:
            return label, cor
    return "Indefinido", "gray"

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
# FORMULÁRIO
# ─────────────────────────────────────────

col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 Dados do Empreendimento")
    empreendimento = st.text_input("Empreendimento")
    unidade = st.text_input("Unidade")
    tipo_produto = st.selectbox("Tipo de Produto", list(NOTAS_TIPO_PRODUTO.keys()))

    st.subheader("💰 Dados Financeiros")
    ato_urba = st.number_input("Ato Urba (R$)", min_value=0.0, step=100.0, format="%.2f")
    valor_proposta = st.number_input("Valor da Proposta / Líquido CV (R$)", min_value=0.01, step=100.0, format="%.2f")
    plano = st.selectbox("Plano", list(NOTAS_PLANO.keys()))

with col2:
    st.subheader("👤 Dados do Cliente")
    nascimento = st.date_input("Data de Nascimento", min_value=date(1930,1,1), max_value=date.today())
    idade = calcular_idade(nascimento)
    faixa = faixa_etaria(idade)
    st.info(f"🎂 Idade calculada: **{idade} anos** — Faixa: **{faixa}**")

    estado_civil = st.selectbox("Estado Civil", list(NOTAS_ESTADO_CIVIL.keys()))
    score_credito = st.selectbox("Score de Crédito (SPC)", list(NOTAS_SCORE.keys()))

    st.subheader("💵 Renda e Comprometimento")
    renda_total = st.number_input("Renda Total (R$)", min_value=0.01, step=100.0, format="%.2f")
    primeira_mensal = st.number_input("Valor da 1ª Mensal (R$)", min_value=0.01, step=10.0, format="%.2f")

# ─────────────────────────────────────────
# CÁLCULOS AUTOMÁTICOS
# ─────────────────────────────────────────

perc_ato = (ato_urba / valor_proposta * 100) if valor_proposta > 0 else 0
perc_comprometimento = (primeira_mensal / renda_total * 100) if renda_total > 0 else 0
faixa_comp = faixa_comprometimento(perc_comprometimento)
faixa_at = faixa_ato(perc_ato)

st.divider()
col3, col4, col5 = st.columns(3)
col3.metric("📊 % do Ato", f"{perc_ato:.1f}%", faixa_at)
col4.metric("📉 Comprometimento de Renda", f"{perc_comprometimento:.1f}%", faixa_comp)
col5.metric("🎂 Faixa Etária", faixa)

# ─────────────────────────────────────────
# BOTÃO CALCULAR
# ─────────────────────────────────────────

st.divider()
if st.button("🎯 CALCULAR SCORE DA VENDA", use_container_width=True, type="primary"):

    notas = {
        "faixa_etaria":          NOTAS_FAIXA_ETARIA[faixa],
        "estado_civil":          NOTAS_ESTADO_CIVIL[estado_civil],
        "score_credito":         NOTAS_SCORE[score_credito],
        "comprometimento_renda": NOTAS_COMPROMETIMENTO[faixa_comp],
        "ato":                   NOTAS_ATO[faixa_at],
        "tipo_produto":          NOTAS_TIPO_PRODUTO[tipo_produto],
        "plano":                 NOTAS_PLANO[plano],
    }

    score_final = calcular_score(notas)
    classificacao, cor = classificar(score_final)

    st.divider()
    st.subheader("📊 Resultado do Score")

    col6, col7 = st.columns([1,2])
    with col6:
        st.metric("Score Final", f"{score_final:.2f} / 1.00")
        if cor == "green":
            st.success(f"### {classificacao}")
        elif cor == "orange":
            st.warning(f"### {classificacao}")
        else:
            st.error(f"### {classificacao}")

    with col7:
        st.markdown("**Detalhamento por variável:**")
        detalhes = []
        for k, peso in PESOS.items():
            nota = notas[k]
            contribuicao = nota * peso
            detalhes.append({"Variável": k.replace("_"," ").title(),
                              "Nota": round(nota,2),
                              "Peso": f"{peso*100:.0f}%",
                              "Contribuição": round(contribuicao,3)})
        st.dataframe(pd.DataFrame(detalhes), use_container_width=True, hide_index=True)

    # ── SUGESTÕES SE ALTO RISCO ──────────────────────────────
    if cor == "red":
        st.divider()
        st.subheader("💡 Sugestões para Reduzir o Risco")
        st.markdown("As variáveis abaixo podem ser ajustadas para melhorar o score:")

        sugestoes = []

        if notas["comprometimento_renda"] < 0.85:
            sugestoes.append("📉 **Comprometimento de Renda alto** → Sugerir composição de renda com cônjuge/familiar ou reduzir o valor da mensal negociando o plano.")
        if notas["ato"] < 0.80:
            sugestoes.append("💰 **Ato abaixo do ideal** → Aumentar o valor de entrada (Ato Urba) para acima de 15% do valor da proposta.")
        if notas["score_credito"] < 0.70:
            sugestoes.append("📋 **Score de crédito baixo** → Avaliar inclusão de um segundo titular com score mais alto.")
        if notas["plano"] < 0.75:
            sugestoes.append("📅 **Plano com alto parcelamento** → Considerar plano com entrada reforçada ou redução do prazo.")
        if notas["faixa_etaria"] < 0.8:
            sugestoes.append("🎂 **Faixa etária de atenção** → Avaliar composição com titular mais jovem se possível.")

        if sugestoes:
            for s in sugestoes:
                st.markdown(f"- {s}")
        else:
            st.info("Nenhuma sugestão automática disponível. Avalie manualmente com o gestor.")

    elif cor == "orange":
        st.divider()
        st.subheader("⚠️ Atenção — Pontos de Melhoria")
        if notas["comprometimento_renda"] < 0.85:
            st.markdown("- 📉 Comprometimento de renda pode ser reduzido com composição de renda.")
        if notas["ato"] < 0.80:
            st.markdown("- 💰 Aumentar o Ato pode elevar o score para BAIXO RISCO.")

    # ── SALVAR HISTÓRICO ─────────────────────────────────────
    dados_registro = {
        "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "Empreendimento": empreendimento,
        "Unidade": unidade,
        "Tipo Produto": tipo_produto,
        "Idade": idade,
        "Faixa Etária": faixa,
        "Estado Civil": estado_civil,
        "Score Crédito": score_credito,
        "% Ato": round(perc_ato,1),
        "Faixa Ato": faixa_at,
        "Plano": plano,
        "Renda Total": renda_total,
        "1ª Mensal": primeira_mensal,
        "% Comprometimento": round(perc_comprometimento,1),
        "Faixa Comprometimento": faixa_comp,
        "Score Final": round(score_final,3),
        "Classificação": classificacao,
    }
    salvar_historico(dados_registro)
    st.success("✅ Simulação salva no histórico!")

# ─────────────────────────────────────────
# ABA DE HISTÓRICO
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


# Para executar no anaconda prompt
#cd "C:\Users\tamiris.costa\OneDrive - MRV\Documentos\Projeto Defensores do Contrato\simulador-distratos"
#streamlit run app.py
#Vai aparecer:
#  Local URL: http://localhost:8501
# Network URL: http://192.168.x.x:8501

