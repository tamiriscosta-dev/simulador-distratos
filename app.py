# app.py — V14.0
# Simulador de Score de Vendas — Projeto Defensores do Contrato
# V14.0: SPC primeiro no perfil + preenchimento automático + tabelas responsivas
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


st.set_page_config(
    page_title="Simulador de Score de Vendas",
    page_icon="🏠",
    layout="wide",
)


# ============================================================
# PILOTO V7.1 — IDENTIFICAÇÃO DO VENDEDOR E ADMINISTRAÇÃO
# ============================================================
def email_valido(email):
    """Valida somente o formato do e-mail informado no piloto."""
    email = str(email or "").strip().lower()
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email))



def _lista_emails_secret(nome):
    """Lê e normaliza uma lista de e-mails cadastrada nos Secrets."""
    try:
        bruto = st.secrets.get(nome, [])
    except Exception:
        bruto = []

    if isinstance(bruto, str):
        itens = re.split(r"[,;\n]+", bruto)
    else:
        try:
            itens = list(bruto)
        except Exception:
            itens = []

    return {str(x).strip().lower() for x in itens if str(x).strip()}


def obter_acessos_autorizados():
    return (
        _lista_emails_secret("VENDEDORES_AUTORIZADOS"),
        _lista_emails_secret("ADMINISTRADORES_AUTORIZADOS"),
    )


def perfil_email(email):
    email = str(email or "").strip().lower()
    vendedores, administradores = obter_acessos_autorizados()
    if email in administradores:
        return "ADMINISTRADOR"
    if email in vendedores:
        return "VENDEDOR"
    return None


def obter_senha_admin():
    """Lê a senha administrativa dos Secrets do Streamlit."""
    try:
        # Formato atual do piloto:
        # DB_TOKEN = "sua_senha"
        senha = str(st.secrets.get("DB_TOKEN", "")).strip()
        if senha:
            return senha
    except Exception:
        pass

    # Compatibilidade opcional com o formato estruturado.
    try:
        return str(st.secrets["admin"]["senha"]).strip()
    except Exception:
        return ""


if "usuario_identificado_v10" not in st.session_state:
    st.session_state.usuario_identificado_v10 = False
if "vendedor_email_confirmado_v10" not in st.session_state:
    st.session_state.vendedor_email_confirmado_v10 = ""
if "admin_autenticado_v11" not in st.session_state:
    st.session_state.admin_autenticado_v11 = False

# A aplicação SEMPRE inicia pela identificação do vendedor.
if not st.session_state.usuario_identificado_v10:
    st.markdown("""
    <style>
    .login-card {
        border: 1px solid rgba(128,128,128,.22);
        border-radius: 18px;
        padding: 26px 28px 18px 28px;
        background: rgba(128,128,128,.045);
        margin-top: 8vh;
    }
    .login-kicker {
        font-size: .78rem; font-weight: 800; letter-spacing: .12em;
        text-transform: uppercase; opacity: .72;
    }
    .login-title { font-size: 2rem; font-weight: 800; margin: 6px 0 6px; }
    .login-sub { opacity: .72; margin-bottom: 18px; }
    </style>
    """, unsafe_allow_html=True)

    _, login_col, _ = st.columns([1.2, 1.6, 1.2])
    with login_col:
        st.markdown("""
        <div class="login-card">
          <div class="login-kicker">Projeto Defensores do Contrato</div>
          <div class="login-title">🏠 Simulador de Score de Vendas</div>
          <div class="login-sub">Identifique-se para iniciar uma nova simulação.</div>
        </div>
        """, unsafe_allow_html=True)

        email_login = st.text_input(
            "E-mail do vendedor *",
            placeholder="nome@empresa.com.br",
            key="email_login_v10",
        ).strip().lower()

        entrar = st.button(
            "ENTRAR NO SIMULADOR",
            type="primary",
            use_container_width=True,
            key="entrar_simulador_v10",
        )
        if entrar:
            if not email_valido(email_login):
                st.error("Informe um e-mail válido para continuar.")
            else:
                vendedores_aut, administradores_aut = obter_acessos_autorizados()
                if not vendedores_aut and not administradores_aut:
                    st.error("A lista de usuários autorizados ainda não foi configurada nos Secrets.")
                else:
                    perfil = perfil_email(email_login)
                    if perfil is None:
                        st.error("E-mail não autorizado. Solicite o cadastro ao responsável pelo simulador.")
                    else:
                        st.session_state.vendedor_email_confirmado_v10 = email_login
                        st.session_state.usuario_identificado_v10 = True
                        st.session_state.perfil_email_v13 = perfil
                        st.session_state.admin_autenticado_v11 = False
                        st.rerun()
    st.stop()

vendedor_email = st.session_state.vendedor_email_confirmado_v10

with st.sidebar:
    st.markdown("### 👤 Usuário")
    st.caption("Vendedor identificado")
    st.write(f"**{vendedor_email}**")

    if st.button("Trocar usuário", key="trocar_usuario_v10", use_container_width=True):
        st.session_state.usuario_identificado_v10 = False
        st.session_state.vendedor_email_confirmado_v10 = ""
        st.session_state.pop("perfil_email_v13", None)
        st.session_state.admin_autenticado_v11 = False
        st.session_state.pop("resultado", None)
        st.rerun()

    st.divider()
    perfil_atual = perfil_email(vendedor_email)

    if perfil_atual == "ADMINISTRADOR":
        st.markdown("### 🔐 Administração")
        if not st.session_state.admin_autenticado_v11:
            st.caption("E-mail administrativo reconhecido. Informe a senha para liberar o histórico.")
            senha_digitada = st.text_input(
                "Senha administrativa",
                type="password",
                key="senha_admin_v11",
            )
            if st.button("Entrar como administrador", key="login_admin_v11", use_container_width=True):
                senha_correta = obter_senha_admin()
                if not senha_correta:
                    st.error("A senha administrativa ainda não foi configurada nos Secrets.")
                elif senha_digitada == senha_correta:
                    st.session_state.admin_autenticado_v11 = True
                    st.rerun()
                else:
                    st.error("Senha administrativa incorreta.")
        else:
            st.success("Perfil: ADMINISTRADOR")
            if st.button("Sair da administração", key="logout_admin_v11", use_container_width=True):
                st.session_state.admin_autenticado_v11 = False
                st.session_state.pagina_v11 = "Simulador"
                st.rerun()
    else:
        st.caption("Perfil: VENDEDOR")


# ============================================================
# CONFIGURAÇÃO
# ============================================================

# ============================================================
# IDENTIDADE VISUAL — V9
# ============================================================
st.markdown("""
<style>
:root {
  --card-border: rgba(128,128,128,.20);
  --card-bg: rgba(128,128,128,.045);
  --muted: rgba(180,188,200,.78);
}
.block-container {
    max-width: 1380px;
    padding-top: 1.7rem;
    padding-bottom: 3rem;
}
h1, h2, h3 { letter-spacing: -0.02em; }
[data-testid="stSidebar"] {
    border-right: 1px solid var(--card-border);
}
[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 14px !important;
    border-color: var(--card-border) !important;
    background: var(--card-bg);
}
div[data-testid="stMetric"] {
    min-height: 108px;
    padding: 13px 15px;
    border: 1px solid var(--card-border);
    border-radius: 12px;
    overflow: hidden;
}
div[data-testid="stMetricLabel"] p,
div[data-testid="stMetricValue"] {
    white-space: normal !important;
    overflow-wrap: anywhere !important;
    line-height: 1.15 !important;
}
div[data-testid="stMetricValue"] {
    font-size: clamp(1rem, 1.5vw, 1.45rem) !important;
}
.stButton > button, .stDownloadButton > button {
    border-radius: 9px;
    min-height: 42px;
    font-weight: 700;
}
[data-baseweb="input"] > div,
[data-baseweb="select"] > div {
    border-radius: 9px !important;
}
.v9-hero {
    border: 1px solid var(--card-border);
    border-radius: 18px;
    padding: 22px 24px 20px 24px;
    margin-bottom: 22px;
    background: linear-gradient(135deg, rgba(35,74,150,.14), rgba(92,52,140,.08));
}
.v9-kicker {
    font-size: .78rem;
    font-weight: 800;
    letter-spacing: .12em;
    text-transform: uppercase;
    color: #8ea9ff;
    margin-bottom: 5px;
}
.v9-title {
    font-size: clamp(1.7rem, 3vw, 2.45rem);
    font-weight: 800;
    line-height: 1.08;
    margin: 0;
}
.v9-subtitle {
    color: var(--muted);
    font-size: .98rem;
    margin-top: 8px;
}
.v9-section-note {
    color: var(--muted);
    margin-top: -8px;
    margin-bottom: 14px;
    font-size: .9rem;
}

/* V11 — textos longos */
[data-testid="stVerticalBlockBorderWrapper"] p,
[data-testid="stVerticalBlockBorderWrapper"] strong {
    white-space: normal !important;
    overflow-wrap: anywhere !important;
    word-break: break-word !important;
}
[data-baseweb="select"] span {
    max-width: 100% !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="v9-hero">
  <div class="v9-kicker">Projeto Defensores do Contrato</div>
  <div class="v9-title">🏠 Simulador de Score de Vendas</div>
  <div class="v9-subtitle">Avaliação estruturada do risco de distrato no momento da venda.</div>
</div>
""", unsafe_allow_html=True)

if "pagina_v11" not in st.session_state:
    st.session_state.pagina_v11 = "Simulador"

nav1, nav2, nav3 = st.columns([1, 1, 4])
with nav1:
    if st.button(
        "▣  Simulador",
        type="primary" if st.session_state.pagina_v11 == "Simulador" else "secondary",
        use_container_width=True,
        key="nav_simulador_v11",
    ):
        st.session_state.pagina_v11 = "Simulador"
        st.rerun()
with nav2:
    if st.session_state.admin_autenticado_v11:
        if st.button(
            "▣  Histórico",
            type="primary" if st.session_state.pagina_v11 == "Histórico" else "secondary",
            use_container_width=True,
            key="nav_historico_v11",
        ):
            st.session_state.pagina_v11 = "Histórico"
            st.rerun()
    else:
        st.button("🔒  Histórico", use_container_width=True, disabled=True, key="nav_hist_bloq_v11")
with nav3:
    if st.session_state.admin_autenticado_v11:
        st.caption("🔐 Área Administrativa ativa • Histórico liberado")
    else:
        st.caption("Simulação atual • vendedor identificado")
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

    # 3) DATA DE NASCIMENTO: leitura automática do SPC do proponente.
    # A busca fica restrita a rótulos explícitos para não confundir com
    # datas de consulta/emissão do relatório.
    data_nascimento = None
    padroes_nascimento = [
        r"(?:DATA\s+DE\s+NASCIMENTO|DT\.?\s*NASCIMENTO|NASCIMENTO)\s*[:\-]?\s*(\d{1,2}/\d{1,2}/\d{4})",
        r"(?:DATA\s+DE\s+NASCIMENTO|DT\.?\s*NASCIMENTO|NASCIMENTO)[\s\S]{0,50}?(\d{1,2}/\d{1,2}/\d{4})",
    ]
    for padrao in padroes_nascimento:
        m_nasc = re.search(padrao, texto_norm, flags=re.I)
        if m_nasc:
            try:
                data_nascimento = datetime.strptime(m_nasc.group(1), "%d/%m/%Y").date()
                hoje_spc = datetime.now(TIMEZONE_BRASILIA).date()
                if data_nascimento > hoje_spc or data_nascimento.year < 1900:
                    data_nascimento = None
                else:
                    break
            except ValueError:
                data_nascimento = None

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
        "data_nascimento": data_nascimento,
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
# FORMATAÇÃO MONETÁRIA BRASILEIRA — V8
# ============================================================
def moeda_para_float(valor):
    """Converte 3.000,00 / 3000,00 / 3000 para float."""
    texto = str(valor or "").strip().replace("R$", "").replace(" ", "")
    if not texto:
        return 0.0
    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    else:
        # Se houver apenas ponto, aceita como decimal digitado.
        # A formatação de saída sempre volta ao padrão brasileiro.
        if texto.count(".") > 1:
            texto = texto.replace(".", "")
    try:
        return max(0.0, float(texto))
    except (TypeError, ValueError):
        return 0.0


def float_para_moeda_input(valor):
    return f"{float(valor or 0):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _normalizar_campo_moeda(chave):
    st.session_state[chave] = float_para_moeda_input(
        moeda_para_float(st.session_state.get(chave, "0,00"))
    )


def campo_moeda(label, chave, valor_inicial=0.0, ajuda=None):
    """Campo monetário que, ao sair/confirmar, exibe 1.234,56."""
    if chave not in st.session_state:
        st.session_state[chave] = float_para_moeda_input(valor_inicial)

    texto = st.text_input(
        label,
        key=chave,
        on_change=_normalizar_campo_moeda,
        args=(chave,),
        help=ajuda,
        placeholder="0,00",
    )
    return moeda_para_float(texto)


if st.session_state.get("pagina_v11") == "Simulador":
    # ============================================================
    # DADOS DA SIMULAÇÃO — LAYOUT EXECUTIVO V10
    # ============================================================
    st.markdown("## 📋 Dados da Simulação")
    st.markdown(
        '<div class="v9-section-note">Preencha as informações abaixo para calcular o score de risco da venda.</div>',
        unsafe_allow_html=True,
    )

    bloco_emp, bloco_cliente, bloco_proposta, bloco_renda = st.columns(4, gap="large")

    # ------------------------- EMPREENDIMENTO -------------------------
    with bloco_emp:
        st.markdown("### 🏢 Empreendimento")

        if cadastro.empty:
            st.error("Cadastro de empreendimentos não carregado.")
            if erro_cadastro:
                with st.expander("Detalhes técnicos"):
                    st.code(erro_cadastro)

        empreendimentos = sorted(
            cadastro["Empreendimento"].dropna().astype(str).str.strip()
            .loc[lambda x: x.ne("")].unique().tolist()
        )

        empreendimento = st.selectbox(
            "Empreendimento *",
            [""] + empreendimentos,
            index=0,
            key="empreendimento_v10",
        )

        if empreendimento:
            cad_emp = cadastro[
                cadastro["Empreendimento"].astype(str).str.strip()
                == str(empreendimento).strip()
            ].copy()
        else:
            cad_emp = cadastro.iloc[0:0].copy()

        unidades = sorted(
            cad_emp["Unidade"].dropna().astype(str).str.strip()
            .loc[lambda x: x.ne("")].unique().tolist(),
            key=lambda x: x.zfill(30),
        )
        def rotulo_unidade(valor):
            if not valor:
                return "Selecione a unidade"
            texto = str(valor).strip()
            emp = str(empreendimento or "").strip()
            # Se a planilha gravar "EMPREENDIMENTO - QUADRA ...", retiramos
            # apenas o prefixo visual. O valor original continua sendo salvo.
            if emp and texto.upper().startswith(emp.upper()):
                curto = texto[len(emp):].lstrip(" -–—")
                if curto:
                    return curto
            return texto

        unidade = st.selectbox(
            "Unidade *",
            [""] + unidades,
            index=0,
            disabled=not bool(empreendimento),
            key="unidade_v12",
            format_func=rotulo_unidade,
            help="O cadastro completo da unidade continua preservado no histórico.",
        )
        if unidade:
            st.caption(f"📍 **{rotulo_unidade(unidade)}**")

        tipo_produto = ""
        if empreendimento and not cad_emp.empty and "Tipo_Produto" in cad_emp.columns:
            serie_tipo = cad_emp["Tipo_Produto"].fillna("").astype(str).str.strip()
            serie_tipo = serie_tipo[serie_tipo.ne("")]
            if not serie_tipo.empty:
                tipo_produto = serie_tipo.iloc[0]

        st.text_input(
            "Tipo de Produto",
            value=tipo_produto,
            disabled=True,
            key=f"tipo_produto_v10_{empreendimento}",
        )

    # ------------------------- PROPONENTE -------------------------
    with bloco_cliente:
        st.markdown("### 👤 Perfil do Cliente")
        st.caption("Anexe o relatório do SPC do cliene proponente.")

        pdf_prop = st.file_uploader(
            "SPC do Proponente *",
            type=["pdf"],
            key="pdf_prop_v14",
        )

        dados_spc_prop = None
        score_proponente = None
        renda_proponente = 0.0
        nascimento = None
        idade = None
        faixa_idade = None

        if pdf_prop:
            try:
                with st.spinner("Lendo SPC do proponente..."):
                    dados_spc_prop = extrair_dados_spc(pdf_prop)

                score_proponente = dados_spc_prop.get("score_faixa")
                renda_proponente = float(dados_spc_prop.get("renda_presumida") or 0)
                nascimento = dados_spc_prop.get("data_nascimento")
                idade = calcular_idade(nascimento) if nascimento else None
                faixa_idade = faixa_etaria(idade) if idade is not None else None

                st.markdown("##### Dados identificados no SPC")
                with st.container(border=True):
                    if nascimento:
                        st.caption("Data de Nascimento")
                        st.markdown(f"**{nascimento.strftime('%d/%m/%Y')}**")
                        st.caption(f"Idade: **{idade} anos** • Faixa: **{faixa_idade}**")
                    else:
                        st.warning("Data de nascimento não localizada no SPC.")

                    st.caption("Score do Proponente")
                    if score_proponente:
                        st.markdown(f"**{dados_spc_prop.get('score_letra') or '—'} → {score_proponente}**")
                    else:
                        st.warning("Score não localizado no SPC.")

                    st.caption("Renda Presumida")
                    if renda_proponente > 0:
                        st.markdown(f"**{brl(renda_proponente)}**")
                    else:
                        st.warning("Renda Presumida não localizada no SPC.")

            except Exception as e:
                st.error(f"Falha na leitura do SPC: {e}")

        # Preenchimento manual somente como contingência quando o PDF não trouxer o campo.
        if pdf_prop and not score_proponente:
            score_proponente = st.selectbox(
                "Score SPC — preenchimento manual",
                ["", "A - B", "C - D", "E - F"],
                key="score_prop_manual_v14",
            )

        if pdf_prop and renda_proponente <= 0:
            renda_proponente = campo_moeda(
                "Renda Presumida — preenchimento manual (R$)",
                "renda_prop_manual_v14",
            )

        estado_civil = st.selectbox(
            "Estado Civil *",
            ["", "SOLTEIRO(A)", "DIVORCIADO(A)", "CASADO(A)"],
            index=0,
            key="estado_civil_v14",
        )

    # ------------------------- PROPOSTA -------------------------
    with bloco_proposta:
        st.markdown("### 📄 Dados da Proposta")

        ato_urba = campo_moeda("Ato Urba (R$) *", "ato_urba_v10")
        valor_proposta = campo_moeda(
            "Valor da Proposta / Líquido CV (R$) *",
            "valor_proposta_v10",
        )
        plano = st.selectbox(
            "Plano *",
            [
                "",
                "CURTO PRAZO (1 A 48X)",
                "MÉDIO PRAZO (49 A 70X)",
                "MÉDIO LONGO (71 A 144X)",
                "LONGO PRAZO (145 A 180X)",
            ],
            key="plano_v10",
        )
        primeira_mensal = campo_moeda(
            "Valor da 1ª Mensal (R$) *",
            "primeira_mensal_v10",
        )

    # ------------------------- COMPOSIÇÃO DE RENDA -------------------------
    with bloco_renda:
        st.markdown("### 👥 Composição de Renda")
        st.caption("Use somente quando houver cliente adicional compondo renda. O score permanece o do proponente.")

        qtd_adicionais = st.number_input(
            "Clientes adicionais",
            min_value=0,
            max_value=4,
            value=0,
            step=1,
            key="qtd_adicionais_v10",
        )

        rendas_adicionais = []
        for i in range(int(qtd_adicionais)):
            numero = i + 2
            with st.expander(f"Cliente {numero}", expanded=True):
                pdf_add = st.file_uploader(
                    f"SPC — Cliente {numero}",
                    type=["pdf"],
                    key=f"pdf_cliente_v10_{numero}",
                )
                renda_add = 0.0

                if pdf_add:
                    try:
                        d_add = extrair_dados_spc(pdf_add)
                        renda_add = float(d_add["renda_presumida"] or 0)
                        if renda_add:
                            st.success(f"Renda: {brl(renda_add)}")
                        else:
                            st.warning("Renda não localizada.")
                    except Exception as e:
                        st.error(f"Falha na leitura: {e}")

                if pdf_add and renda_add <= 0:
                    renda_add = campo_moeda(
                        f"Renda manual — Cliente {numero} (R$)",
                        f"renda_manual_v10_{numero}",
                    )

                rendas_adicionais.append(renda_add)

    # REGRA OFICIAL: score exclusivamente do proponente.
    score_analise = score_proponente
    renda_total = renda_proponente + sum(rendas_adicionais)

    perc_ato = ato_urba / valor_proposta * 100 if valor_proposta > 0 else 0
    perc_comp = primeira_mensal / renda_total * 100 if renda_total > 0 else 0

    faixa_at = faixa_ato(perc_ato)
    faixa_comp = faixa_comprometimento(perc_comp)
    faixa_rd = faixa_renda(renda_total)

    st.divider()

    # Indicadores instantâneos abaixo do formulário.
    i1, i2, i3, i4 = st.columns(4)
    i1.metric("% do Ato", f"{perc_ato:.2f}%", faixa_at)
    i2.metric("Comprometimento", f"{perc_comp:.2f}%", faixa_comp)
    i3.metric("Renda Total", brl(renda_total), ABREV_RENDA[faixa_rd])
    i4.metric("Faixa Etária", faixa_idade or "—")

    faltando = []
    if not empreendimento: faltando.append("Empreendimento")
    if not unidade: faltando.append("Unidade")
    if not tipo_produto: faltando.append("Tipo de Produto")
    if not nascimento: faltando.append("Data de Nascimento")
    if not estado_civil: faltando.append("Estado Civil")
    if not pdf_prop: faltando.append("SPC do Proponente")
    if not score_analise: faltando.append("Score SPC do Proponente")
    if renda_total <= 0: faltando.append("Renda Presumida")
    if valor_proposta <= 0: faltando.append("Valor da Proposta")
    if not plano: faltando.append("Plano")
    if primeira_mensal <= 0: faltando.append("1ª Mensal")

    if faltando:
        st.warning("Preencha/valide: **" + ", ".join(faltando) + "**")

    _, botao_calc = st.columns([3, 1])
    with botao_calc:
        calcular = st.button(
            "📊 CALCULAR SIMULAÇÃO",
            type="primary",
            use_container_width=True,
            disabled=bool(faltando),
            key="calcular_v10",
        )

    if calcular:
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
            "renda_proponente": renda_proponente,
            "qtd_clientes_adicionais": int(qtd_adicionais),
            "renda_adicionais": sum(rendas_adicionais),
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
    # RESULTADO E ESTRATÉGIA — V10
    # ============================================================
    if st.session_state.resultado:
        d = st.session_state.resultado

        st.divider()
        st.subheader("🧾 Resumo da Simulação")
        st.markdown('<div class="v9-section-note">Consolidação dos dados utilizados na avaliação.</div>', unsafe_allow_html=True)



        def resumo_card(coluna, titulo, valor):
            with coluna:
                with st.container(border=True):
                    st.caption(titulo)
                    st.markdown(f"**{valor if valor not in (None, '') else '—'}**")

        q1, q2, q3, q4 = st.columns(4)
        resumo_card(q1, "Empreendimento", d.get("empreendimento"))
        unidade_resumo = d.get("unidade") or ""
        emp_resumo = d.get("empreendimento") or ""
        if emp_resumo and unidade_resumo.upper().startswith(emp_resumo.upper()):
            unidade_resumo = unidade_resumo[len(emp_resumo):].lstrip(" -–—") or unidade_resumo
        resumo_card(q2, "Unidade", unidade_resumo)
        resumo_card(q3, "Tipo de Produto", d.get("tipo_produto"))
        resumo_card(q4, "Renda Total", brl(d.get("renda_total", 0)))

        p1, p2, p3, p4 = st.columns(4)
        resumo_card(p1, "Faixa Etária", d.get("faixa_idade"))
        resumo_card(p2, "Estado Civil", d.get("estado_civil"))
        resumo_card(p3, "Score do Proponente", d.get("score_proponente"))
        resumo_card(p4, "Plano", d.get("plano"))

        c1, c2, c3, c4 = st.columns(4)
        resumo_card(c1, "% do Ato", f"{d.get('perc_ato', 0):.2f}%")
        resumo_card(c2, "Ato Urba", brl(d.get("ato_urba", 0)))
        resumo_card(c3, "1ª Mensal", brl(d.get("primeira_mensal", 0)))
        resumo_card(c4, "Valor da Proposta", brl(d.get("valor_proposta", 0)))

        st.subheader("📈 Avaliação de Risco")
        r1, r2 = st.columns([1, 2])

        with r1:
            st.metric("Score Final", f"{d['score_final']} / 130")
            if d["cor"] == "green":
                st.success(f"### {d['classificacao']}")
            elif d["cor"] == "orange":
                st.warning(f"### {d['classificacao']}")
            else:
                st.error(f"### {d['classificacao']}")

        with r2:
            labels = {
                "score_credito": "Score de Crédito",
                "ato": "% do Ato",
                "comprometimento_renda": "Comprometimento de Renda",
                "faixa_renda": "Faixa de Renda",
                "plano": "Plano",
                "tipo_produto": "Tipo de Produto",
                "idade": "Faixa Etária",
                "estado_civil": "Estado Civil",
            }
            max_nota = {
                "score_credito": 5,
                "ato": 5,
                "comprometimento_renda": 5,
                "faixa_renda": 5,
                "plano": 5,
                "tipo_produto": 4,
                "idade": 5,
                "estado_civil": 3,
            }
            detalhes = []
            for var, peso in PESOS.items():
                nota = d["notas"][var]
                detalhes.append({
                    "Variável": labels[var],
                    "Nota": f"{nota}/{max_nota[var]}",
                    "Peso": peso,
                    "Pontos": nota * peso,
                    "Máximo": max_nota[var] * peso,
                })
            st.dataframe(
                pd.DataFrame(detalhes),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Variável": st.column_config.TextColumn("Variável", width="medium"),
                    "Nota": st.column_config.TextColumn("Nota", width="small"),
                    "Peso": st.column_config.NumberColumn("Peso", width="small"),
                    "Pontos": st.column_config.NumberColumn("Pontos", width="small"),
                    "Máximo": st.column_config.NumberColumn("Máximo", width="small"),
                },
            )

        if d["classificacao"] != "🟢 BAIXO RISCO":
            st.divider()
            st.subheader("💡 Estratégias de Estruturação da Venda")

            falta_mod = max(0, LIMITE_MODERADO - d["score_final"])
            falta_baixo = max(0, LIMITE_BAIXO - d["score_final"])

            a1, b1 = st.columns(2)
            a1.metric("Pontos para Risco Moderado", f"+{falta_mod}")
            b1.metric("Pontos para Baixo Risco", f"+{falta_baixo}")

            cenarios = montar_cenarios(
                score_atual=d["score_final"],
                notas=d["notas"],
                renda_total=d["renda_total"],
                mensal=d["primeira_mensal"],
                ato=d["ato_urba"],
                valor_proposta=d["valor_proposta"],
                plano=d["plano"],
            )

            if cenarios:
                df_cenarios = pd.DataFrame(cenarios)
                df_cenarios["Ganho"] = df_cenarios["Ganho"].map(lambda x: f"+{x}")
                df_cenarios["NovoScore"] = df_cenarios["NovoScore"].map(lambda x: f"{x}")
                df_exibicao = df_cenarios[
                    ["Variável", "Ajuste", "Ganho", "NovoScore", "NovaClassificacao"]
                ].head(12).rename(columns={
                    "NovoScore": "Novo Score",
                    "NovaClassificacao": "Nova Classificação",
                })

                st.dataframe(
                    df_exibicao,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Variável": st.column_config.TextColumn(
                            "Variável",
                            width="medium",
                            help="Variável comercial simulada",
                        ),
                        "Ajuste": st.column_config.TextColumn(
                            "Ajuste",
                            width="large",
                        ),
                        "Ganho": st.column_config.TextColumn(
                            "Ganho",
                            width="small",
                        ),
                        "Novo Score": st.column_config.TextColumn(
                            "Novo Score",
                            width="small",
                        ),
                        "Nova Classificação": st.column_config.TextColumn(
                            "Nova Classificação",
                            width="medium",
                        ),
                    },
                )
                st.caption(
                    "As sugestões são simulações contrafactuais. Não são propostas "
                    "alterações de idade, estado civil ou score cadastral do cliente."
                )

    # 7. HISTÓRICO — PILOTO V8
    # ============================================================
    if st.session_state.get("resultado"):
        d = st.session_state["resultado"]

        st.divider()
        st.subheader("💾 Histórico")
        st.caption(
            "O e-mail identifica o vendedor. Somente o administrador consulta "
            "o histórico consolidado."
        )

        if not email_valido(vendedor_email):
            st.warning("Informe um e-mail válido do vendedor para salvar.")
        elif st.button(
            "✅ CONFIRMAR E SALVAR NO HISTÓRICO",
            type="primary",
            key="salvar_historico_v8",
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
                "Qtd_Clientes_Adicionais": d.get("qtd_clientes_adicionais", 0),
                "Renda_Clientes_Adicionais": d.get("renda_adicionais", 0),
                "Renda_Total": d.get("renda_total", 0),
                "Ato_Urba": d.get("ato_urba", 0),
                "Percentual_Ato": d.get("perc_ato", 0),
                "Faixa_Ato": d.get("faixa_at", ""),
                "Valor_Proposta": d.get("valor_proposta", 0),
                "Plano": d.get("plano", ""),
                "Primeira_Mensal": d.get("primeira_mensal", 0),
                "Percentual_Comprometimento": d.get("perc_comp", 0),
                "Faixa_Comprometimento": d.get("faixa_comp", ""),
                "Faixa_Renda": d.get("faixa_rd", ""),
                "Score_Final": d.get("score_final", 0),
                "Classificacao": d.get("classificacao", ""),
            }

            arquivo = "historico.csv"
            novo = pd.DataFrame([registro])

            if os.path.exists(arquivo):
                try:
                    antigo = pd.read_csv(arquivo)
                    # Garante o mesmo esquema mesmo se existir CSV de versão anterior.
                    todas_colunas = list(dict.fromkeys(list(novo.columns) + list(antigo.columns)))
                    novo = pd.concat(
                        [
                            antigo.reindex(columns=todas_colunas),
                            novo.reindex(columns=todas_colunas),
                        ],
                        ignore_index=True,
                    )
                except Exception:
                    pass

            novo.to_csv(arquivo, index=False, encoding="utf-8-sig")
            st.success("Simulação salva no histórico.")


# ============================================================
# HISTÓRICO ADMINISTRATIVO — V11
# Só aparece após autenticação administrativa e ao abrir a aba Histórico.
# ============================================================
if st.session_state.admin_autenticado_v11 and st.session_state.get("pagina_v11") == "Histórico":
    # ============================================================
    # 8. HISTÓRICO ADMINISTRATIVO — PILOTO V7.1
    # ============================================================
    st.divider()
    st.subheader("📂 Histórico de Simulações")

    if st.session_state.admin_autenticado_v11:
        with st.expander("🗑️ Excluir histórico", expanded=False):
            st.warning(
                "Esta ação exclui todo o histórico armazenado nesta instância "
                "do Streamlit e não pode ser desfeita."
            )
            confirmar_exclusao = st.checkbox(
                "Confirmo que desejo excluir TODO o histórico",
                key="confirmar_exclusao_historico_v8",
            )
            if st.button(
                "🗑️ EXCLUIR TODO O HISTÓRICO",
                type="primary",
                disabled=not confirmar_exclusao,
                key="excluir_historico_v8",
            ):
                if os.path.exists("historico.csv"):
                    os.remove("historico.csv")
                st.session_state.pop("resultado", None)
                st.success("Histórico excluído. O próximo registro iniciará um novo arquivo.")
                st.rerun()

    if not st.session_state.admin_autenticado_v11:
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
                    key="filtro_vendedor_v11",
                )

            with c2:
                empreendimentos_hist = sorted(
                    x for x in hist["Empreendimento"].fillna("").astype(str).unique().tolist()
                    if x
                )
                filtro_emp = st.selectbox(
                    "Empreendimento",
                    ["TODOS"] + empreendimentos_hist,
                    key="filtro_emp_v11",
                )

            with c3:
                classes = sorted(
                    x for x in hist["Classificacao"].fillna("").astype(str).unique().tolist()
                    if x
                )
                filtro_class = st.selectbox(
                    "Classificação",
                    ["TODAS"] + classes,
                    key="filtro_class_v11",
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
        "V14.0 — Projeto Defensores do Contrato | "
        "Score SPC exclusivamente do proponente | Histórico administrativo do piloto"
    )

    # ============================================================
    # CONFIGURAÇÃO NECESSÁRIA NO STREAMLIT CLOUD
    # ============================================================
    # Em App > Settings > Secrets:
    #
    # DB_TOKEN = "ESCOLHA_UMA_SENHA_FORTE"
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
