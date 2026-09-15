# app.py — V7.1
# Simulador de Score de Vendas — Projeto Defensores do Contrato
# V7.1: score exclusivamente do proponente + horário de Brasília + histórico por usuário
# + leitura robusta do SPC + cadastro por empreendimentos.xlsx.

import io
import os
import re
import unicodedata
from datetime import date, datetime
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st
import pdfplumber


# ============================================================
# PILOTO V7.1 — IDENTIFICAÇÃO DO VENDEDOR E ADMINISTRAÇÃO
# ============================================================
def email_valido(email):
    """Valida somente o formato do e-mail informado no piloto."""
    email = str(email or "").strip().lower()
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email))


def obter_senha_admin():
    """Lê a senha administrativa dos Secrets; nunca do GitHub."""
    try:
        return str(st.secrets["admin"]["senha"])
    except Exception:
        return ""


if "admin_autenticado_v71" not in st.session_state:
    st.session_state.admin_autenticado_v71 = False

with st.sidebar:
    st.subheader("👤 Vendedor")
    vendedor_email = st.text_input(
        "E-mail do vendedor *",
        placeholder="nome@empresa.com.br",
        key="vendedor_email_v71",
    ).strip().lower()

    if vendedor_email:
        if email_valido(vendedor_email):
            st.success("E-mail informado.")
        else:
            st.error("Informe um e-mail válido.")

    st.divider()
    st.subheader("🔐 Administração")

    if not st.session_state.admin_autenticado_v71:
        senha_digitada = st.text_input(
            "Senha administrativa",
            type="password",
            key="senha_admin_v71",
        )
        if st.button("Entrar como administrador", key="login_admin_v71"):
            senha_correta = obter_senha_admin()
            if not senha_correta:
                st.error(
                    "A senha administrativa ainda não foi configurada "
                    "nos Secrets do Streamlit."
                )
            elif senha_digitada == senha_correta:
                st.session_state.admin_autenticado_v71 = True
                st.rerun()
            else:
                st.error("Senha administrativa incorreta.")
    else:
        st.success("Perfil: ADMINISTRADOR")
        if st.button("Sair da administração", key="logout_admin_v71"):
            st.session_state.admin_autenticado_v71 = False
            st.rerun()


# ============================================================
# CONFIGURAÇÃO
# ============================================================
st.set_page_config(
    page_title="Simulador de Score de Vendas",
    page_icon="🏠",
    layout="wide",
)

st.title("🏠 Simulador de Score de Vendas")
st.markdown("**Projeto Defensores do Contrato — Avaliação de Risco de Distrato**")
st.divider()


# ============================================================
# CADASTRO DE EMPREENDIMENTOS E UNIDADES — V7.1
# ============================================================
# O app procura primeiro por empreendimentos.xlsx.
# Se o nome do arquivo variar, procura automaticamente outros .xlsx do
# repositório e usa o primeiro que contenha Empreendimento e Unidade.

TIMEZONE_BRASILIA = ZoneInfo("America/Sao_Paulo")


def _chave_coluna(nome):
    nome = str(nome or "").strip()
    nome = unicodedata.normalize("NFKD", nome)
    nome = "".join(c for c in nome if not unicodedata.combining(c))
    nome = nome.lower()
    nome = re.sub(r"[_\-]+", " ", nome)
    nome = re.sub(r"\s+", " ", nome).strip()
    return nome


@st.cache_data(show_spinner=False)
def carregar_cadastro():
    candidatos = []

    # Prioridade absoluta para o arquivo oficial.
    if os.path.exists("empreendimentos.xlsx"):
        candidatos.append("empreendimentos.xlsx")

    # Fallback robusto: detecta qualquer outro Excel do repositório.
    for nome in sorted(os.listdir(".")):
        if nome.lower().endswith(".xlsx") and nome not in candidatos:
            candidatos.append(nome)

    erros = []

    for arquivo in candidatos:
        try:
            excel = pd.ExcelFile(arquivo, engine="openpyxl")

            # Procura uma aba que tenha as colunas necessárias.
            for aba in excel.sheet_names:
                df = pd.read_excel(
                    arquivo,
                    sheet_name=aba,
                    engine="openpyxl",
                )

                mapa = {}
                for col in df.columns:
                    chave = _chave_coluna(col)

                    if chave in {
                        "empreendimento",
                        "empreendimentos",
                        "nome empreendimento",
                    }:
                        mapa[col] = "Empreendimento"

                    elif chave in {
                        "unidade",
                        "unidades",
                        "quadra lote",
                        "quadra/lote",
                    }:
                        mapa[col] = "Unidade"

                    elif chave in {
                        "tipo produto",
                        "tipo de produto",
                        "produto",
                    }:
                        mapa[col] = "Tipo_Produto"

                df = df.rename(columns=mapa)

                # Empreendimento e Unidade são obrigatórios.
                if {"Empreendimento", "Unidade"}.issubset(df.columns):
                    if "Tipo_Produto" not in df.columns:
                        df["Tipo_Produto"] = ""

                    df = df[
                        ["Empreendimento", "Unidade", "Tipo_Produto"]
                    ].copy()

                    # Mantém unidades numéricas sem transformar 1 em "1.0".
                    def texto_limpo(valor):
                        if pd.isna(valor):
                            return ""
                        if isinstance(valor, float) and valor.is_integer():
                            return str(int(valor))
                        return str(valor).strip()

                    for col in [
                        "Empreendimento",
                        "Unidade",
                        "Tipo_Produto",
                    ]:
                        df[col] = df[col].apply(texto_limpo)

                    df = df[
                        (df["Empreendimento"] != "")
                        & (df["Unidade"] != "")
                    ].drop_duplicates()

                    if not df.empty:
                        return df, arquivo, aba, None

        except Exception as erro:
            erros.append(f"{arquivo}: {erro}")

    detalhe = " | ".join(erros) if erros else "Nenhum Excel compatível encontrado."
    return (
        pd.DataFrame(
            columns=["Empreendimento", "Unidade", "Tipo_Produto"]
        ),
        None,
        None,
        detalhe,
    )


cadastro, arquivo_cadastro, aba_cadastro, erro_cadastro = carregar_cadastro()

# ============================================================
# PARÂMETROS DO SCORE
# ============================================================
PESOS = {
    "score_credito": 5,
    "ato": 5,
    "comprometimento_renda": 4,
    "faixa_renda": 4,
    "plano": 4,
    "tipo_produto": 3,
    "idade": 1,
    "estado_civil": 1,
}

NOTAS_SCORE = {"A - B": 5, "C - D": 3, "E - F": 1}

# Mantidas as premissas registradas no histórico.
NOTAS_ATO = {
    "ACIMA DE 4%": 5,
    "3% A 4%": 4,
    "2% A 3%": 3,
    "1% A 2%": 2,
    "ABAIXO DE 1%": 1,
}

NOTAS_COMPROMETIMENTO = {
    "ATÉ 10%": 5,
    "10% A 20%": 4,
    "20% A 30%": 3,
    "30% A 50%": 2,
    "50% A 100%": 1,
    "ACIMA DE 100%": 1,
}

NOTAS_RENDA = {
    "ACIMA DE R$ 15.000": 5,
    "R$ 10.001 A R$ 15.000": 4,
    "R$ 7.501 A R$ 10.000": 3,
    "R$ 5.001 A R$ 7.500": 2,
    "R$ 2.501 A R$ 5.000": 1,
    "ATÉ R$ 2.500": 1,
}

NOTAS_PLANO = {
    "CURTO PRAZO (1 A 48X)": 5,
    "MÉDIO PRAZO (49 A 70X)": 3,
    "MÉDIO LONGO (71 A 144X)": 2,
    "LONGO PRAZO (145 A 180X)": 1,
}

NOTAS_TIPO_PRODUTO = {
    "LOTEAMENTO FECHADO": 4,
    "SMART": 3,
    "CONDOMÍNIO SMART": 2,
    "LOTEAMENTO ABERTO": 1,
}

NOTAS_IDADE = {
    "60+ ANOS": 5,
    "45 A 60 ANOS": 4,
    "35 A 45 ANOS": 3,
    "ATÉ 25 ANOS": 2,
    "25 A 35 ANOS": 1,
}

NOTAS_ESTADO_CIVIL = {
    "CASADO(A)": 3,
    "DIVORCIADO(A)": 2,
    "SOLTEIRO(A)": 1,
}

# Máximo teórico com as tabelas acima = 130.
SCORE_MAX = sum([
    5 * PESOS["score_credito"],
    5 * PESOS["ato"],
    5 * PESOS["comprometimento_renda"],
    5 * PESOS["faixa_renda"],
    5 * PESOS["plano"],
    4 * PESOS["tipo_produto"],
    5 * PESOS["idade"],
    3 * PESOS["estado_civil"],
])

LIMITE_BAIXO = 90
LIMITE_MODERADO = 61

ABREV_RENDA = {
    "ACIMA DE R$ 15.000": "> R$ 15k",
    "R$ 10.001 A R$ 15.000": "R$ 10k–15k",
    "R$ 7.501 A R$ 10.000": "R$ 7,5k–10k",
    "R$ 5.001 A R$ 7.500": "R$ 5k–7,5k",
    "R$ 2.501 A R$ 5.000": "R$ 2,5k–5k",
    "ATÉ R$ 2.500": "≤ R$ 2,5k",
}


# ============================================================
# FUNÇÕES
# ============================================================
def brl(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def normalizar(texto):
    texto = texto or ""
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = texto.upper()
    texto = texto.replace("\xa0", " ")
    texto = re.sub(r"[ \t]+", " ", texto)
    return texto


def moeda_para_float(valor):
    if valor is None:
        return None
    s = str(valor).strip()
    s = re.sub(r"[^\d,.\-]", "", s)
    if not s:
        return None
    # padrão brasileiro 8.870,00
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def calcular_idade(nascimento):
    hoje = datetime.now(TIMEZONE_BRASILIA).date()
    return hoje.year - nascimento.year - (
        (hoje.month, hoje.day) < (nascimento.month, nascimento.day)
    )


def faixa_etaria(idade):
    if idade <= 25:
        return "ATÉ 25 ANOS"
    if idade <= 35:
        return "25 A 35 ANOS"
    if idade <= 45:
        return "35 A 45 ANOS"
    if idade <= 60:
        return "45 A 60 ANOS"
    return "60+ ANOS"


def faixa_comprometimento(perc):
    if perc <= 10:
        return "ATÉ 10%"
    if perc <= 20:
        return "10% A 20%"
    if perc <= 30:
        return "20% A 30%"
    if perc <= 50:
        return "30% A 50%"
    if perc <= 100:
        return "50% A 100%"
    return "ACIMA DE 100%"


def faixa_renda(valor):
    if valor > 15000:
        return "ACIMA DE R$ 15.000"
    if valor > 10000:
        return "R$ 10.001 A R$ 15.000"
    if valor > 7500:
        return "R$ 7.501 A R$ 10.000"
    if valor > 5000:
        return "R$ 5.001 A R$ 7.500"
    if valor > 2500:
        return "R$ 2.501 A R$ 5.000"
    return "ATÉ R$ 2.500"


def faixa_ato(perc):
    if perc > 4:
        return "ACIMA DE 4%"
    if perc >= 3:
        return "3% A 4%"
    if perc >= 2:
        return "2% A 3%"
    if perc >= 1:
        return "1% A 2%"
    return "ABAIXO DE 1%"


def classificar(score):
    if score >= LIMITE_BAIXO:
        return "🟢 BAIXO RISCO", "green"
    if score >= LIMITE_MODERADO:
        return "🟡 RISCO MODERADO", "orange"
    return "🔴 ALTO RISCO", "red"


def calcular_score_total(notas):
    return sum(notas[k] * PESOS[k] for k in PESOS)


def mapear_score(letra):
    letra = (letra or "").upper()
    if letra in ("A", "B"):
        return "A - B"
    if letra in ("C", "D"):
        return "C - D"
    if letra in ("E", "F"):
        return "E - F"
    return None


def extrair_dados_spc(pdf_file):
    """
    Modelo SPC observado:
    - A expressão 'SPC SCORE 12 meses' pode estar em uma página e o resultado
      'RISCO DE CRÉDITO C' em outra. Por isso concatenamos TODAS as páginas.
    - Renda Presumida pode aparecer na tabela como:
      'Renda Presumida - SPC Brasil ... 8.870,00'
      e também como 'Renda Presumida: R$ 8.870,00'.
    """
    pdf_file.seek(0)
    paginas = []
    tabelas = []

    with pdfplumber.open(pdf_file) as pdf:
        for numero, page in enumerate(pdf.pages, start=1):
            texto = page.extract_text(x_tolerance=2, y_tolerance=3) or ""
            paginas.append(texto)

            # Extração de tabelas como reforço para a linha Renda Presumida.
            try:
                for tabela in page.extract_tables() or []:
                    tabelas.append((numero, tabela))
            except Exception:
                pass

    texto_completo = "\n".join(paginas)
    texto_norm = normalizar(texto_completo)

    # 1) SCORE: usar prioritariamente o resultado literal RISCO DE CREDITO.
    score_letra = None
    padroes_score = [
        r"\bRISCO\s+DE\s+CREDITO\s*[:\-]?\s*([A-F])\b",
        r"\bRISCO\s+DE\s+CREDITO\b[\s\S]{0,80}?\b([A-F])\b",
    ]
    for padrao in padroes_score:
        m = re.search(padrao, texto_norm, flags=re.I)
        if m:
            score_letra = m.group(1).upper()
            break

    score_faixa = mapear_score(score_letra)

    # 2) RENDA: primeiro tenta encontrar a linha/tabela específica.
    renda = None

    for _, tabela in tabelas:
        for linha in tabela:
            celulas = [normalizar(str(x)) if x is not None else "" for x in linha]
            linha_norm = " | ".join(celulas)
            if "RENDA PRESUMIDA" in linha_norm and "SPC BRASIL" in linha_norm:
                candidatos = re.findall(r"(?:R\$\s*)?(\d{1,3}(?:\.\d{3})*,\d{2})", linha_norm)
                if candidatos:
                    renda = moeda_para_float(candidatos[-1])
                    if renda and renda > 0:
                        break
        if renda and renda > 0:
            break

    # Fallback textual. Procuramos a ocorrência inteira, não apenas texto adjacente
    # à expressão "SPC SCORE".
    if not renda:
        padroes_renda = [
            r"RENDA\s+PRESUMIDA\s*-\s*SPC\s+BRASIL[\s\S]{0,160}?(?:R\$\s*)?(\d{1,3}(?:\.\d{3})*,\d{2})",
            r"RENDA\s+PRESUMIDA\s*:?\s*(?:_+\s*)?(?:R\$\s*)?(\d{1,3}(?:\.\d{3})*,\d{2})",
        ]
        for padrao in padroes_renda:
            m = re.search(padrao, texto_norm, flags=re.I)
            if m:
                renda = moeda_para_float(m.group(1))
                if renda and renda > 0:
                    break

    # Campos adicionais úteis para conferência/estratégia.
    taxa_inadimplencia = None
    m = re.search(
        r"TAXA\s+DE\s+INADIMPLENCIA\s*[:\-]?\s*([\d.,]+)\s*%",
        texto_norm,
        flags=re.I,
    )
    if m:
        taxa_inadimplencia = moeda_para_float(m.group(1))

    renda_comprometida_spc = bool(
        re.search(r"RENDA\s+TOTALMENTE\s+COMPROMETIDA", texto_norm, flags=re.I)
    )

    consultas_30d = None
    consultas_90d = None
    m30 = re.search(r"ULTIMOS\s+30\s+DIAS\s+(\d+)", texto_norm)
    m90 = re.search(r"ULTIMOS\s+90\s+DIAS\s+(\d+)", texto_norm)
    if m30:
        consultas_30d = int(m30.group(1))
    if m90:
        consultas_90d = int(m90.group(1))

    return {
        "score_letra": score_letra,
        "score_faixa": score_faixa,
        "renda_presumida": renda,
        "taxa_inadimplencia": taxa_inadimplencia,
        "renda_comprometida_spc": renda_comprometida_spc,
        "consultas_30d": consultas_30d,
        "consultas_90d": consultas_90d,
        "texto_extraido": texto_completo,
    }


def renda_minima_para_comprometimento(mensal, limite_pct):
    if mensal <= 0 or limite_pct <= 0:
        return 0
    return mensal / (limite_pct / 100)


def mensal_maxima_para_comprometimento(renda, limite_pct):
    return renda * limite_pct / 100


def ato_minimo_para_percentual(valor_proposta, pct):
    return valor_proposta * pct / 100


def montar_cenarios(
    score_atual,
    notas,
    renda_total,
    mensal,
    ato,
    valor_proposta,
    plano,
):
    """
    Contrafactuais apenas sobre variáveis potencialmente acionáveis:
    ato, mensal/comprometimento, composição de renda e plano.
    Não recomenda alterar idade, estado civil ou score cadastral do cliente.
    """
    cenarios = []

    # ATO: simula patamares mínimos para faixas superiores.
    metas_ato = [
        (1.00, "1% A 2%"),
        (2.00, "2% A 3%"),
        (3.00, "3% A 4%"),
        (4.01, "ACIMA DE 4%"),
    ]
    for pct_meta, faixa_meta in metas_ato:
        nova_nota = NOTAS_ATO[faixa_meta]
        ganho = (nova_nota - notas["ato"]) * PESOS["ato"]
        ato_alvo = ato_minimo_para_percentual(valor_proposta, pct_meta)
        adicional = max(0, ato_alvo - ato)
        if ganho > 0 and adicional > 0:
            cenarios.append({
                "Variável": "Ato",
                "Ajuste": f"Aumentar o ato para aproximadamente {brl(ato_alvo)} "
                          f"(+{brl(adicional)}; ≈ {pct_meta:.2f}% da proposta)",
                "Ganho": ganho,
                "NovoScore": score_atual + ganho,
            })

    # COMPROMETIMENTO: duas formas equivalentes de chegar ao patamar.
    metas_comp = [
        (50, "30% A 50%"),
        (30, "20% A 30%"),
        (20, "10% A 20%"),
        (10, "ATÉ 10%"),
    ]
    for limite, faixa_meta in metas_comp:
        nova_nota = NOTAS_COMPROMETIMENTO[faixa_meta]
        ganho = (nova_nota - notas["comprometimento_renda"]) * PESOS["comprometimento_renda"]
        if ganho > 0:
            renda_alvo = renda_minima_para_comprometimento(mensal, limite)
            mensal_alvo = mensal_maxima_para_comprometimento(renda_total, limite)
            cenarios.append({
                "Variável": "Renda / Mensal",
                "Ajuste": (
                    f"Para comprometimento ≤ {limite}%: renda total ≈ {brl(renda_alvo)} "
                    f"OU mensal ≤ {brl(mensal_alvo)}"
                ),
                "Ganho": ganho,
                "NovoScore": score_atual + ganho,
            })

    # FAIXA DE RENDA: composição de renda, quando comercialmente permitida.
    metas_renda = [
        (5001, "R$ 5.001 A R$ 7.500"),
        (7501, "R$ 7.501 A R$ 10.000"),
        (10001, "R$ 10.001 A R$ 15.000"),
        (15001, "ACIMA DE R$ 15.000"),
    ]
    for renda_meta, faixa_meta in metas_renda:
        nova_nota = NOTAS_RENDA[faixa_meta]
        ganho = (nova_nota - notas["faixa_renda"]) * PESOS["faixa_renda"]
        adicional = max(0, renda_meta - renda_total)
        if ganho > 0 and adicional > 0:
            cenarios.append({
                "Variável": "Composição de renda",
                "Ajuste": f"Elevar a renda total para pelo menos {brl(renda_meta)} "
                          f"(+{brl(adicional)}), se houver outro proponente elegível",
                "Ganho": ganho,
                "NovoScore": score_atual + ganho,
            })

    # PLANO
    ordem_planos = [
        "LONGO PRAZO (145 A 180X)",
        "MÉDIO LONGO (71 A 144X)",
        "MÉDIO PRAZO (49 A 70X)",
        "CURTO PRAZO (1 A 48X)",
    ]
    for plano_meta in ordem_planos:
        nova_nota = NOTAS_PLANO[plano_meta]
        ganho = (nova_nota - notas["plano"]) * PESOS["plano"]
        if ganho > 0:
            cenarios.append({
                "Variável": "Plano",
                "Ajuste": f"Reestruturar para {plano_meta}",
                "Ganho": ganho,
                "NovoScore": score_atual + ganho,
            })

    # Ordena primeiro pelo menor ajuste de pontos que já cruza um limiar,
    # depois pelo maior ganho.
    for c in cenarios:
        c["NovaClassificacao"] = classificar(c["NovoScore"])[0]
        c["AtingeModerado"] = c["NovoScore"] >= LIMITE_MODERADO
        c["AtingeBaixo"] = c["NovoScore"] >= LIMITE_BAIXO

    return sorted(
        cenarios,
        key=lambda c: (
            not c["AtingeModerado"],
            not c["AtingeBaixo"],
            -c["Ganho"],
        )
    )


def obter_usuario_autenticado():
    """
    V7.1: usa st.user somente quando a autenticação OIDC do app disponibiliza
    a identidade ao código. A lista de viewers do Community Cloud, sozinha,
    controla acesso ao app, mas não deve ser usada como fonte do e-mail aqui.
    """
    try:
        info = st.user.to_dict()
    except Exception:
        info = {}

    email = str(
        info.get("email")
        or info.get("preferred_username")
        or ""
    ).strip().lower()

    nome = str(
        info.get("name")
        or info.get("given_name")
        or ""
    ).strip()

    return {
        "email": email,
        "nome": nome,
        "identificado": bool(email),
        "administrador": bool(email and email in ADMINISTRADORES),
    }


usuario_atual = obter_usuario_autenticado()


def salvar_historico(dados):
    arquivo = "historico.csv"

    # Horário oficial da V7.1: Brasília.
    dados = dict(dados)
    dados["Data"] = datetime.now(TIMEZONE_BRASILIA).strftime("%d/%m/%Y %H:%M:%S")
    dados["Usuario_Email"] = usuario_atual["email"]
    dados["Usuario_Nome"] = usuario_atual["nome"]

    novo = pd.DataFrame([dados])
    if os.path.exists(arquivo):
        antigo = pd.read_csv(arquivo)
        novo = pd.concat([antigo, novo], ignore_index=True)
    novo.to_csv(arquivo, index=False, encoding="utf-8-sig")


# ============================================================
# ESTADO DA SESSÃO
# ============================================================
if "resultado" not in st.session_state:
    st.session_state.resultado = None


# ============================================================
# 1. EMPREENDIMENTO
# ============================================================
st.subheader("🏗 Dados do Empreendimento")

if cadastro.empty:
    st.error(
        "Não consegui carregar a relação de empreendimentos e unidades. "
        "Confirme se o arquivo Excel está no mesmo repositório do app.py "
        "e contém as colunas Empreendimento e Unidade."
    )
    if erro_cadastro:
        with st.expander("Detalhes técnicos do cadastro"):
            st.code(erro_cadastro)

c1, c2, c3 = st.columns(3)

empreendimentos = sorted(
    cadastro["Empreendimento"]
    .dropna()
    .astype(str)
    .str.strip()
    .loc[lambda x: x.ne("")]
    .unique()
    .tolist()
)

with c1:
    empreendimento = st.selectbox(
        "Empreendimento *",
        [""] + empreendimentos,
        index=0,
        key="empreendimento_v71",
    )

# A partir daqui, Unidade e Tipo de Produto usam SOMENTE o empreendimento.
if empreendimento:
    cad_emp = cadastro[
        cadastro["Empreendimento"].astype(str).str.strip()
        == str(empreendimento).strip()
    ].copy()
else:
    cad_emp = cadastro.iloc[0:0].copy()

# ------------------------------------------------------------
# UNIDADE: lista vinculada ao empreendimento selecionado.
# ------------------------------------------------------------
with c2:
    unidades = sorted(
        cad_emp["Unidade"]
        .dropna()
        .astype(str)
        .str.strip()
        .loc[lambda x: x.ne("")]
        .unique()
        .tolist(),
        key=lambda x: x.zfill(30),
    )

    unidade = st.selectbox(
        "Unidade *",
        [""] + unidades,
        index=0,
        disabled=not bool(empreendimento),
        key="unidade_v71",
    )

# ------------------------------------------------------------
# TIPO DE PRODUTO: vinculado EXCLUSIVAMENTE ao empreendimento.
# Não depende da unidade selecionada.
# ------------------------------------------------------------
with c3:
    tipo_produto = ""

    if empreendimento and not cad_emp.empty:
        tipos_emp = (
            cad_emp["Tipo_Produto"]
            .dropna()
            .astype(str)
            .str.strip()
        )
        tipos_emp = [
            x for x in tipos_emp.unique().tolist()
            if x
        ]

        # Regra oficial:
        # o empreendimento possui o Tipo de Produto associado no cadastro.
        if tipos_emp:
            tipo_produto = tipos_emp[0]

    st.text_input(
        "Tipo de Produto",
        value=tipo_produto,
        disabled=True,
        key="tipo_produto_v71",
    )

st.divider()


# ============================================================
# 2. PROPONENTE
# ============================================================
st.subheader("👤 Cliente Proponente")

p1, p2 = st.columns(2)

with p1:
    nascimento = st.date_input(
        "Data de Nascimento *",
        value=None,
        min_value=date(1930, 1, 1),
        max_value=datetime.now(TIMEZONE_BRASILIA).date(),
        format="DD/MM/YYYY",
    )

    idade = calcular_idade(nascimento) if nascimento else None
    faixa_idade = faixa_etaria(idade) if idade is not None else None

    if idade is not None:
        st.info(f"Idade: **{idade} anos** | Faixa: **{faixa_idade}**")

    estado_civil = st.selectbox(
        "Estado Civil *",
        ["", "SOLTEIRO(A)", "DIVORCIADO(A)", "CASADO(A)"],
        index=0,
    )

with p2:
    pdf_prop = st.file_uploader(
        "Anexar PDF do SPC — Proponente *",
        type=["pdf"],
        key="pdf_prop",
    )

    dados_spc_prop = None
    if pdf_prop:
        try:
            with st.spinner("Lendo todas as páginas do SPC..."):
                dados_spc_prop = extrair_dados_spc(pdf_prop)

            if dados_spc_prop["score_faixa"]:
                st.success(
                    f"RISCO DE CRÉDITO identificado: "
                    f"**{dados_spc_prop['score_letra']}** → "
                    f"**{dados_spc_prop['score_faixa']}**"
                )
            else:
                st.warning("Não foi possível identificar o campo RISCO DE CRÉDITO.")

            if dados_spc_prop["renda_presumida"]:
                st.success(
                    "Renda Presumida - SPC Brasil: "
                    f"**{brl(dados_spc_prop['renda_presumida'])}**"
                )
            else:
                st.warning("Não foi possível identificar a Renda Presumida - SPC Brasil.")

            with st.expander("Conferência da leitura do SPC"):
                st.write("Score literal:", dados_spc_prop["score_letra"] or "Não localizado")
                st.write(
                    "Taxa de inadimplência:",
                    f"{dados_spc_prop['taxa_inadimplencia']:.2f}%"
                    if dados_spc_prop["taxa_inadimplencia"] is not None else "Não localizada",
                )
                st.write("Consultas 30 dias:", dados_spc_prop["consultas_30d"])
                st.write("Consultas 90 dias:", dados_spc_prop["consultas_90d"])
                st.write(
                    "Aviso de renda totalmente comprometida no SPC:",
                    "Sim" if dados_spc_prop["renda_comprometida_spc"] else "Não",
                )
        except Exception as e:
            st.error(f"Falha na leitura do PDF: {e}")

score_proponente = dados_spc_prop["score_faixa"] if dados_spc_prop else None
renda_proponente = (
    float(dados_spc_prop["renda_presumida"])
    if dados_spc_prop and dados_spc_prop["renda_presumida"] else 0.0
)

# Fallback manual só aparece quando a leitura não encontrou o campo.
if pdf_prop and not score_proponente:
    score_proponente = st.selectbox(
        "Score SPC — preenchimento manual",
        ["", "A - B", "C - D", "E - F"],
        index=0,
    )

if pdf_prop and renda_proponente <= 0:
    renda_proponente = st.number_input(
        "Renda Presumida — preenchimento manual (R$)",
        min_value=0.0,
        value=0.0,
        step=100.0,
    )

st.divider()


# ============================================================
# 3. CLIENTES ADICIONAIS — máximo total de 5 clientes
# ============================================================
st.subheader("👥 Composição de Renda")

qtd_adicionais = st.number_input(
    "Quantos clientes adicionais participarão da proposta?",
    min_value=0,
    max_value=4,
    value=0,
    step=1,
)

rendas_adicionais = []

for i in range(int(qtd_adicionais)):
    numero = i + 2
    with st.expander(f"Cliente {numero}", expanded=True):
        pdf_add = st.file_uploader(
            f"Anexar PDF SPC — Cliente {numero}",
            type=["pdf"],
            key=f"pdf_cliente_{numero}",
        )

        score_add = None
        renda_add = 0.0

        if pdf_add:
            try:
                d_add = extrair_dados_spc(pdf_add)
                score_add = d_add["score_faixa"]
                renda_add = float(d_add["renda_presumida"] or 0)

                a, b = st.columns(2)
                a.metric(
                    "Score SPC",
                    f"{d_add['score_letra']} → {score_add}" if score_add else "Não localizado",
                )
                b.metric("Renda Presumida", brl(renda_add) if renda_add else "Não localizada")
            except Exception as e:
                st.error(f"Falha na leitura do Cliente {numero}: {e}")

        if pdf_add and not score_add:
            score_add = st.selectbox(
                f"Score manual — Cliente {numero}",
                ["", "A - B", "C - D", "E - F"],
                key=f"score_manual_{numero}",
            )

        if pdf_add and renda_add <= 0:
            renda_add = st.number_input(
                f"Renda manual — Cliente {numero} (R$)",
                min_value=0.0,
                value=0.0,
                key=f"renda_manual_{numero}",
            )

        # O score do cliente adicional NÃO participa da pontuação da venda.
        # Sua renda presumida participa da composição da renda.
        rendas_adicionais.append(renda_add)

# REGRA OFICIAL V7.1:
# O score utilizado na análise é EXCLUSIVAMENTE o score do PROPONENTE.
# Os clientes adicionais participam somente da composição da renda.
score_analise = score_proponente
renda_total = renda_proponente + sum(rendas_adicionais)

m1, m2 = st.columns(2)
m1.metric("Score usado na análise — Proponente", score_analise or "—")
m2.metric("Renda total da proposta", brl(renda_total))
st.divider()


# ============================================================
# 4. DADOS FINANCEIROS
# ============================================================
st.subheader("💰 Dados Financeiros")

f1, f2 = st.columns(2)

with f1:
    ato_urba = st.number_input(
        "Ato Urba (R$) *",
        min_value=0.0,
        value=0.0,
        step=100.0,
        format="%.2f",
    )
    valor_proposta = st.number_input(
        "Valor da Proposta / Líquido CV (R$) *",
        min_value=0.0,
        value=0.0,
        step=100.0,
        format="%.2f",
    )

with f2:
    plano = st.selectbox(
        "Plano *",
        [
            "",
            "CURTO PRAZO (1 A 48X)",
            "MÉDIO PRAZO (49 A 70X)",
            "MÉDIO LONGO (71 A 144X)",
            "LONGO PRAZO (145 A 180X)",
        ],
        index=0,
    )
    primeira_mensal = st.number_input(
        "Valor da 1ª Mensal (R$) *",
        min_value=0.0,
        value=0.0,
        step=10.0,
        format="%.2f",
    )

perc_ato = ato_urba / valor_proposta * 100 if valor_proposta > 0 else 0
perc_comp = primeira_mensal / renda_total * 100 if renda_total > 0 else 0

faixa_at = faixa_ato(perc_ato)
faixa_comp = faixa_comprometimento(perc_comp)
faixa_rd = faixa_renda(renda_total)

st.divider()
k1, k2, k3, k4 = st.columns(4)
k1.metric("% do Ato", f"{perc_ato:.2f}%", faixa_at)
k2.metric("Comprometimento", f"{perc_comp:.2f}%", faixa_comp)
k3.metric("Renda Total", brl(renda_total), ABREV_RENDA[faixa_rd])
k4.metric("Faixa Etária", faixa_idade or "—")


# ============================================================
# 5. VALIDAÇÃO E CÁLCULO
# ============================================================
faltando = []

if not empreendimento:
    faltando.append("Empreendimento")
if not unidade:
    faltando.append("Unidade")
if not tipo_produto:
    faltando.append("Tipo de Produto")
if not nascimento:
    faltando.append("Data de Nascimento")
if not estado_civil:
    faltando.append("Estado Civil")
if not pdf_prop:
    faltando.append("PDF SPC do Proponente")
if not score_analise:
    faltando.append("Score SPC do Proponente")
if renda_total <= 0:
    faltando.append("Renda Presumida")
if valor_proposta <= 0:
    faltando.append("Valor da Proposta")
if not plano:
    faltando.append("Plano")
if primeira_mensal <= 0:
    faltando.append("1ª Mensal")

st.divider()

if faltando:
    st.warning("Preencha/valide: **" + ", ".join(faltando) + "**")

if st.button(
    "🎯 CALCULAR SCORE DA VENDA",
    type="primary",
    use_container_width=True,
    disabled=bool(faltando),
):
    notas = {
        "score_credito": NOTAS_SCORE[score_analise],
        "ato": NOTAS_ATO[faixa_at],
        "comprometimento_renda": NOTAS_COMPROMETIMENTO[faixa_comp],
        "faixa_renda": NOTAS_RENDA[faixa_rd],
        "plano": NOTAS_PLANO[plano],
        "tipo_produto": NOTAS_TIPO_PRODUTO.get(tipo_produto, 0),
        "idade": NOTAS_IDADE[faixa_idade],
        "estado_civil": NOTAS_ESTADO_CIVIL[estado_civil],
    }

    score_final = calcular_score_total(notas)
    classificacao, cor = classificar(score_final)

    st.session_state.resultado = {
        "notas": notas,
        "score_final": score_final,
        "classificacao": classificacao,
        "cor": cor,
        "empreendimento": empreendimento,
        "unidade": unidade,
        "tipo_produto": tipo_produto,
        "idade": idade,
        "faixa_idade": faixa_idade,
        "estado_civil": estado_civil,
        "score_proponente": score_analise,
        "renda_total": renda_total,
        "ato_urba": ato_urba,
        "valor_proposta": valor_proposta,
        "perc_ato": perc_ato,
        "faixa_at": faixa_at,
        "plano": plano,
        "primeira_mensal": primeira_mensal,
        "perc_comp": perc_comp,
        "faixa_comp": faixa_comp,
        "faixa_rd": faixa_rd,
    }


# ============================================================
# 6. RESULTADO E ESTRATÉGIA
# ============================================================
# 7. HISTÓRICO — PILOTO V7.1
# ============================================================
if st.session_state.get("resultado_v7"):
    d = st.session_state["resultado_v7"]

    st.divider()
    st.subheader("💾 Histórico")
    st.caption(
        "O e-mail identifica o vendedor. Durante o piloto, "
        "somente o administrador consulta o histórico."
    )

    if not email_valido(vendedor_email):
        st.warning("Informe um e-mail válido do vendedor para salvar.")
    elif st.button(
        "✅ CONFIRMAR E SALVAR NO HISTÓRICO",
        type="primary",
        key="salvar_historico_v71",
    ):
        registro = {
            "Data_Hora": datetime.now(TIMEZONE_BRASILIA).strftime("%d/%m/%Y %H:%M:%S"),
            "Vendedor_Email": vendedor_email,
            "Empreendimento": d.get("empreendimento", ""),
            "Unidade": d.get("unidade", ""),
            "Tipo_Produto": d.get("tipo_produto", ""),
            "Idade": d.get("idade", ""),
            "Faixa_Etaria": d.get("faixa_idade", ""),
            "Estado_Civil": d.get("estado_civil", ""),
            "Score_Proponente": d.get("score_proponente", ""),
            "Renda_Proponente": d.get("renda_proponente", 0),
            "Renda_Total": d.get("renda_total", 0),
            "Ato_Urba": d.get("ato", 0),
            "Percentual_Ato": d.get("pct_ato", 0),
            "Valor_Proposta": d.get("valor_proposta", 0),
            "Plano": d.get("plano", ""),
            "Primeira_Mensal": d.get("primeira_mensal", 0),
            "Percentual_Comprometimento": d.get("comprometimento", 0),
            "Score_Final": d.get("score_final", 0),
            "Classificacao": d.get("classificacao", ""),
        }

        arquivo = "historico.csv"
        novo = pd.DataFrame([registro])

        if os.path.exists(arquivo):
            try:
                antigo = pd.read_csv(arquivo)
                novo = pd.concat([antigo, novo], ignore_index=True)
            except Exception:
                pass

        novo.to_csv(arquivo, index=False, encoding="utf-8-sig")
        st.success("Simulação salva no histórico temporário do piloto.")


# ============================================================
# 8. HISTÓRICO ADMINISTRATIVO — PILOTO V7.1
# ============================================================
st.divider()
st.subheader("📂 Histórico de Simulações")

if not st.session_state.admin_autenticado_v71:
    st.info(
        "O histórico é restrito ao administrador. "
        "Use a área 🔐 Administração na barra lateral."
    )
elif not os.path.exists("historico.csv"):
    st.info("Nenhuma simulação oficial registrada.")
else:
    try:
        hist = pd.read_csv("historico.csv")
    except Exception as erro:
        hist = pd.DataFrame()
        st.error(f"Não foi possível ler o histórico: {erro}")

    if hist.empty:
        st.info("Nenhuma simulação oficial registrada.")
    else:
        # Compatibilidade com arquivo de teste/versão anterior.
        if "Vendedor_Email" not in hist.columns:
            hist["Vendedor_Email"] = ""
        if "Empreendimento" not in hist.columns:
            hist["Empreendimento"] = ""
        if "Classificacao" not in hist.columns:
            if "Classificação" in hist.columns:
                hist["Classificacao"] = hist["Classificação"]
            else:
                hist["Classificacao"] = ""

        st.success("Visão administrativa — histórico consolidado")

        c1, c2, c3 = st.columns(3)

        with c1:
            vendedores = sorted(
                x for x in hist["Vendedor_Email"].fillna("").astype(str).unique().tolist()
                if x
            )
            filtro_vendedor = st.selectbox(
                "Vendedor",
                ["TODOS"] + vendedores,
                key="filtro_vendedor_v71",
            )

        with c2:
            empreendimentos_hist = sorted(
                x for x in hist["Empreendimento"].fillna("").astype(str).unique().tolist()
                if x
            )
            filtro_emp = st.selectbox(
                "Empreendimento",
                ["TODOS"] + empreendimentos_hist,
                key="filtro_emp_v71",
            )

        with c3:
            classes = sorted(
                x for x in hist["Classificacao"].fillna("").astype(str).unique().tolist()
                if x
            )
            filtro_class = st.selectbox(
                "Classificação",
                ["TODAS"] + classes,
                key="filtro_class_v71",
            )

        exibicao = hist.copy()

        if filtro_vendedor != "TODOS":
            exibicao = exibicao[exibicao["Vendedor_Email"].astype(str) == filtro_vendedor]
        if filtro_emp != "TODOS":
            exibicao = exibicao[exibicao["Empreendimento"].astype(str) == filtro_emp]
        if filtro_class != "TODAS":
            exibicao = exibicao[exibicao["Classificacao"].astype(str) == filtro_class]

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Simulações", len(exibicao))
        k2.metric(
            "Baixo Risco",
            int(exibicao["Classificacao"].astype(str).str.contains("BAIXO", na=False).sum()),
        )
        k3.metric(
            "Moderado",
            int(exibicao["Classificacao"].astype(str).str.contains("MODERADO", na=False).sum()),
        )
        k4.metric(
            "Alto Risco",
            int(exibicao["Classificacao"].astype(str).str.contains("ALTO", na=False).sum()),
        )

        st.dataframe(exibicao, use_container_width=True, hide_index=True)

        st.download_button(
            "⬇ BAIXAR HISTÓRICO PARA BACKUP NO ONEDRIVE",
            exibicao.to_csv(index=False).encode("utf-8-sig"),
            file_name=(
                "historico_score_vendas_"
                + datetime.now(TIMEZONE_BRASILIA).strftime("%Y%m%d_%H%M")
                + ".csv"
            ),
            mime="text/csv",
            use_container_width=True,
        )

        st.warning(
            "⚠️ O histórico armazenado no servidor do Streamlit é temporário. "
            "Faça o backup no OneDrive corporativo."
        )


# ============================================================
# RODAPÉ
# ============================================================
st.divider()
st.caption(
    "V7.1 — Projeto Defensores do Contrato | "
    "Score SPC exclusivamente do proponente | Histórico administrativo do piloto"
)

# ============================================================
# CONFIGURAÇÃO NECESSÁRIA NO STREAMLIT CLOUD
# ============================================================
# Em App > Settings > Secrets:
#
# [admin]
# senha = "ESCOLHA_UMA_SENHA_FORTE"
#
# Nunca coloque essa senha no GitHub.
#
# O arquivo de cadastro esperado é:
# empreendimentos.xlsx
#
# requirements.txt:
# streamlit
# pandas
# openpyxl
# pdfplumber
#
# O historico.csv é temporário. Baixe backups periódicos e salve no OneDrive.
