# app.py — V16.4
# Simulador de Score de Vendas — Projeto Defensores do Contrato
# V16.4: Design Urba profissional, fundo branco, sem HTML problemático,
#        autenticação via Neon PostgreSQL, histórico no banco.

import io
import os
import re
import unicodedata
from datetime import date, datetime
from zoneinfo import ZoneInfo

import bcrypt
import pandas as pd
import psycopg2
import psycopg2.extras
import pdfplumber
import streamlit as st

# ============================================================
# CONFIG DA PÁGINA — DEVE SER O PRIMEIRO COMANDO
# ============================================================
st.set_page_config(
    page_title="Urba · Simulador de Score",
    page_icon="https://i.imgur.com/placeholder.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# CSS GLOBAL — DESIGN URBA V16.4
# ============================================================
URBA_GREEN      = "#079D56"
URBA_GREEN_DARK = "#056B3A"
URBA_ORANGE     = "#FF8C23"
URBA_TEXT       = "#2D2D2D"
URBA_MUTED      = "#6B7280"
URBA_BG         = "#FFFFFF"
URBA_CARD       = "#F4F6F8"
URBA_BORDER     = "#E2E8F0"

st.markdown(f"""
<style>
/* ── Reset geral ── */
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {{
    background-color: {URBA_BG} !important;
    color: {URBA_TEXT} !important;
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif !important;
}}

/* ── Remove tira preta do topo ── */
#MainMenu, header[data-testid="stHeader"], footer {{
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
}}
[data-testid="stToolbar"] {{ display: none !important; }}
.stDeployButton {{ display: none !important; }}

/* ── Sidebar ── */
[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, {URBA_GREEN_DARK} 0%, {URBA_GREEN} 100%) !important;
    border-right: none !important;
}}
[data-testid="stSidebar"] * {{
    color: #FFFFFF !important;
}}
[data-testid="stSidebar"] .stButton > button {{
    background: rgba(255,255,255,0.15) !important;
    color: #FFFFFF !important;
    border: 1px solid rgba(255,255,255,0.3) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: background 0.2s !important;
}}
[data-testid="stSidebar"] .stButton > button:hover {{
    background: rgba(255,255,255,0.25) !important;
}}
[data-testid="stSidebar"] hr {{
    border-color: rgba(255,255,255,0.2) !important;
}}

/* ── Inputs e selects — fundo branco, texto escuro ── */
[data-baseweb="input"] input,
[data-baseweb="textarea"] textarea {{
    background-color: #FFFFFF !important;
    color: {URBA_TEXT} !important;
    border-color: {URBA_BORDER} !important;
    border-radius: 8px !important;
}}
[data-baseweb="input"] > div,
[data-baseweb="textarea"] > div {{
    background-color: #FFFFFF !important;
    border-color: {URBA_BORDER} !important;
    border-radius: 8px !important;
}}
[data-baseweb="input"] input:focus,
[data-baseweb="textarea"] textarea:focus {{
    border-color: {URBA_GREEN} !important;
    box-shadow: 0 0 0 2px rgba(7,157,86,0.15) !important;
}}

/* ── Select / Dropdown ── */
[data-baseweb="select"] > div {{
    background-color: #FFFFFF !important;
    border-color: {URBA_BORDER} !important;
    border-radius: 8px !important;
    color: {URBA_TEXT} !important;
}}
[data-baseweb="select"] span {{
    color: {URBA_TEXT} !important;
}}
[data-baseweb="popover"] li {{
    color: {URBA_TEXT} !important;
    background: #FFFFFF !important;
}}
[data-baseweb="popover"] li:hover {{
    background: #F0FBF5 !important;
}}

/* ── Number input ── */
[data-testid="stNumberInput"] input {{
    background-color: #FFFFFF !important;
    color: {URBA_TEXT} !important;
    border-color: {URBA_BORDER} !important;
    border-radius: 8px !important;
}}
[data-testid="stNumberInput"] > div {{
    background-color: #FFFFFF !important;
    border-color: {URBA_BORDER} !important;
    border-radius: 8px !important;
}}
[data-testid="stNumberInput"] button {{
    background-color: {URBA_CARD} !important;
    color: {URBA_TEXT} !important;
    border-color: {URBA_BORDER} !important;
}}

/* ── File uploader ── */
[data-testid="stFileUploader"] {{
    background-color: #F0FBF5 !important;
    border: 2px dashed {URBA_GREEN} !important;
    border-radius: 10px !important;
    padding: 8px !important;
}}
[data-testid="stFileUploader"] * {{
    color: {URBA_TEXT} !important;
}}
[data-testid="stFileUploader"] button {{
    background-color: {URBA_GREEN} !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 6px !important;
}}

/* ── Botões primários ── */
.stButton > button[kind="primary"] {{
    background-color: {URBA_GREEN} !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    padding: 10px 20px !important;
    transition: background 0.2s, transform 0.1s !important;
}}
.stButton > button[kind="primary"]:hover {{
    background-color: {URBA_GREEN_DARK} !important;
    transform: translateY(-1px) !important;
}}

/* ── Botões secundários ── */
.stButton > button[kind="secondary"] {{
    background-color: #FFFFFF !important;
    color: {URBA_GREEN} !important;
    border: 2px solid {URBA_GREEN} !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: all 0.2s !important;
}}
.stButton > button[kind="secondary"]:hover {{
    background-color: #F0FBF5 !important;
}}

/* ── Download button ── */
.stDownloadButton > button {{
    background-color: {URBA_ORANGE} !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
}}
.stDownloadButton > button:hover {{
    background-color: #E07A1A !important;
}}

/* ── Métricas ── */
[data-testid="stMetric"] {{
    background-color: {URBA_CARD} !important;
    border: 1px solid {URBA_BORDER} !important;
    border-radius: 12px !important;
    padding: 16px !important;
}}
[data-testid="stMetricLabel"] p {{
    color: {URBA_MUTED} !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}}
[data-testid="stMetricValue"] {{
    color: {URBA_TEXT} !important;
    font-size: 1.5rem !important;
    font-weight: 700 !important;
}}
[data-testid="stMetricDelta"] {{
    font-size: 0.8rem !important;
    font-weight: 600 !important;
}}

/* ── Alertas / Warnings / Errors ── */
[data-testid="stAlert"] {{
    border-radius: 10px !important;
    border-left-width: 4px !important;
}}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {{
    border: 1px solid {URBA_BORDER} !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}}

/* ── Expander ── */
[data-testid="stExpander"] {{
    border: 1px solid {URBA_BORDER} !important;
    border-radius: 10px !important;
    background: {URBA_CARD} !important;
}}

/* ── Divider ── */
hr {{
    border-color: {URBA_BORDER} !important;
    margin: 1.5rem 0 !important;
}}

/* ── Labels dos inputs ── */
label, .stTextInput label, .stSelectbox label,
.stFileUploader label, .stNumberInput label {{
    color: {URBA_TEXT} !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.04em !important;
}}

/* ── Caption / help text ── */
.stCaption, [data-testid="stCaptionContainer"] p,
small, .stMarkdown small {{
    color: {URBA_MUTED} !important;
}}

/* ── Checkbox ── */
[data-testid="stCheckbox"] label span {{
    color: {URBA_TEXT} !important;
}}

/* ── Container com borda ── */
[data-testid="stVerticalBlockBorderWrapper"] {{
    border: 1px solid {URBA_BORDER} !important;
    border-radius: 12px !important;
    background: {URBA_CARD} !important;
    padding: 4px !important;
}}

/* ── Block container ── */
.block-container {{
    max-width: 1400px !important;
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
}}

/* ── Spinner ── */
[data-testid="stSpinner"] {{
    color: {URBA_GREEN} !important;
}}
</style>
""", unsafe_allow_html=True)

# ============================================================
# BANCO DE DADOS — NEON POSTGRESQL
# ============================================================
TIMEZONE_BRASILIA = ZoneInfo("America/Sao_Paulo")


@st.cache_resource
def get_connection():
    return psycopg2.connect(
        st.secrets["NEON_DATABASE_URL"],
        cursor_factory=psycopg2.extras.RealDictCursor,
    )


def get_conn():
    try:
        conn = get_connection()
        conn.isolation_level  # testa se está viva
        return conn
    except Exception:
        get_connection.clear()
        return get_connection()


def db_query(sql, params=None, fetch=True):
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(sql, params or ())
        if fetch:
            return cur.fetchall()
        conn.commit()
        return None


def db_execute(sql, params=None):
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(sql, params or ())
    conn.commit()


# ============================================================
# AUTENTICAÇÃO
# ============================================================
def verificar_login(email, senha):
    rows = db_query(
        "SELECT id, nome, email, senha_hash, perfil, ativo FROM usuarios WHERE email = %s",
        (email.strip().lower(),),
    )
    if not rows:
        return None, "E-mail não encontrado."
    u = rows[0]
    if not u["ativo"]:
        return None, "Usuário inativo. Contate o administrador."
    if not bcrypt.checkpw(senha.encode(), u["senha_hash"].encode()):
        return None, "Senha incorreta."
    return dict(u), None


def hash_senha(senha):
    return bcrypt.hashpw(senha.encode(), bcrypt.gensalt(12)).decode()


# ============================================================
# ESTADO DE SESSÃO
# ============================================================
for k, v in {
    "logado": False,
    "usuario": None,
    "pagina": "Simulador",
    "resultado": None,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ============================================================
# TELA DE LOGIN
# ============================================================
if not st.session_state.logado:
    st.markdown(f"""
    <style>
    html, body, [data-testid="stAppViewContainer"] {{
        background-color: #F4F6F8 !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    _, col, _ = st.columns([1.5, 1, 1.5])
    with col:
        # Logo textual Urba
        st.markdown(f"""
        <div style="text-align:center; margin-bottom:8px; margin-top:40px;">
            <div style="display:inline-block; background:{URBA_GREEN}; border-radius:16px;
                        padding:14px 28px; margin-bottom:12px;">
                <span style="color:#FFFFFF; font-size:2rem; font-weight:900;
                             letter-spacing:-0.02em;">Urba</span>
            </div>
            <div style="color:{URBA_MUTED}; font-size:0.78rem; font-weight:700;
                        letter-spacing:0.12em; text-transform:uppercase;
                        margin-bottom:4px;">Simulador de Score de Vendas</div>
        </div>
        """, unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown(f"""
            <div style="text-align:center; padding:8px 0 16px;">
                <div style="font-size:1.4rem; font-weight:800; color:{URBA_TEXT};">
                    Bem-vindo de volta
                </div>
                <div style="color:{URBA_MUTED}; font-size:0.9rem; margin-top:4px;">
                    Acesse com suas credenciais para continuar.
                </div>
            </div>
            """, unsafe_allow_html=True)

            email_in = st.text_input(
                "E-mail",
                placeholder="nome@urba.com.br",
                key="login_email",
            )
            senha_in = st.text_input(
                "Senha",
                type="password",
                placeholder="••••••••",
                key="login_senha",
            )

            if st.button("ENTRAR", type="primary", use_container_width=True, key="btn_login"):
                if not email_in or not senha_in:
                    st.error("Preencha e-mail e senha.")
                else:
                    usuario, erro = verificar_login(email_in, senha_in)
                    if erro:
                        st.error(erro)
                    else:
                        st.session_state.logado  = True
                        st.session_state.usuario = usuario
                        st.session_state.pagina  = "Simulador"
                        st.rerun()

        st.markdown(f"""
        <div style="text-align:center; margin-top:16px; color:{URBA_MUTED};
                    font-size:0.78rem;">
            Projeto Defensores do Contrato · Urba
        </div>
        """, unsafe_allow_html=True)

    st.stop()


# ============================================================
# SIDEBAR — PÓS LOGIN
# ============================================================
usuario = st.session_state.usuario
is_admin = usuario["perfil"] == "ADMINISTRADOR"

with st.sidebar:
    # Logo na sidebar
    st.markdown(f"""
    <div style="text-align:center; padding:20px 0 16px;">
        <div style="display:inline-block; background:rgba(255,255,255,0.15);
                    border-radius:12px; padding:10px 22px; margin-bottom:10px;">
            <span style="color:#FFFFFF; font-size:1.6rem; font-weight:900;
                         letter-spacing:-0.02em;">Urba</span>
        </div>
        <div style="color:rgba(255,255,255,0.7); font-size:0.68rem; font-weight:700;
                    letter-spacing:0.1em; text-transform:uppercase;">
            Simulador de Score
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.markdown(f"""
    <div style="padding:0 4px 12px;">
        <div style="font-size:0.95rem; font-weight:700; color:#FFFFFF;">
            {usuario['nome']}
        </div>
        <div style="font-size:0.78rem; color:rgba(255,255,255,0.7); margin-top:2px;">
            {usuario['email']}
        </div>
        <div style="display:inline-block; margin-top:8px; background:rgba(255,255,255,0.2);
                    border-radius:20px; padding:3px 12px; font-size:0.72rem;
                    font-weight:700; color:#FFFFFF; letter-spacing:0.05em;">
            {'Administrador' if is_admin else 'Vendedor'}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    if st.button("Sair", use_container_width=True, key="btn_sair"):
        for k in ["logado", "usuario", "pagina", "resultado"]:
            st.session_state[k] = {"logado": False, "usuario": None,
                                    "pagina": "Simulador", "resultado": None}[k]
        st.rerun()


# ============================================================
# HEADER PRINCIPAL
# ============================================================
st.markdown(f"""
<div style="background:linear-gradient(135deg, {URBA_GREEN_DARK} 0%, {URBA_GREEN} 100%);
            border-radius:16px; padding:24px 32px; margin-bottom:24px;
            box-shadow:0 4px 20px rgba(7,157,86,0.2);">
    <div style="display:flex; align-items:center; justify-content:space-between;">
        <div>
            <div style="color:rgba(255,255,255,0.75); font-size:0.72rem; font-weight:700;
                        letter-spacing:0.12em; text-transform:uppercase; margin-bottom:6px;">
                Projeto Defensores do Contrato
            </div>
            <div style="color:#FFFFFF; font-size:clamp(1.5rem,3vw,2.2rem);
                        font-weight:800; line-height:1.1; letter-spacing:-0.02em;">
                Simulador de Score de Vendas
            </div>
            <div style="color:rgba(255,255,255,0.8); font-size:0.9rem; margin-top:6px;">
                Avaliação estruturada do risco de distrato no momento da venda.
            </div>
        </div>
        <div style="background:rgba(255,255,255,0.15); border-radius:8px;
                    padding:6px 14px; font-size:0.78rem; font-weight:700;
                    color:#FFFFFF; letter-spacing:0.05em;">
            V16.4
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# NAVEGAÇÃO
# ============================================================
nav_cols = st.columns([1, 1, 1, 4])
with nav_cols[0]:
    if st.button(
        "Simulador",
        type="primary" if st.session_state.pagina == "Simulador" else "secondary",
        use_container_width=True,
        key="nav_sim",
    ):
        st.session_state.pagina = "Simulador"
        st.rerun()

with nav_cols[1]:
    if is_admin:
        if st.button(
            "Historico",
            type="primary" if st.session_state.pagina == "Historico" else "secondary",
            use_container_width=True,
            key="nav_hist",
        ):
            st.session_state.pagina = "Historico"
            st.rerun()
    else:
        st.button("Historico", disabled=True, use_container_width=True, key="nav_hist_off")

with nav_cols[2]:
    if is_admin:
        if st.button(
            "Usuarios",
            type="primary" if st.session_state.pagina == "Usuarios" else "secondary",
            use_container_width=True,
            key="nav_usr",
        ):
            st.session_state.pagina = "Usuarios"
            st.rerun()
    else:
        st.button("Usuarios", disabled=True, use_container_width=True, key="nav_usr_off")

with nav_cols[3]:
    if is_admin:
        st.caption("Perfil: Administrador · Acesso total liberado")
    else:
        st.caption(f"Perfil: Vendedor · {usuario['email']}")

st.divider()


# ============================================================
# CADASTRO DE EMPREENDIMENTOS
# ============================================================
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
    if os.path.exists("empreendimentos.xlsx"):
        candidatos.append("empreendimentos.xlsx")
    for nome in sorted(os.listdir(".")):
        if nome.lower().endswith(".xlsx") and nome not in candidatos:
            candidatos.append(nome)

    erros = []
    for arquivo in candidatos:
        try:
            excel = pd.ExcelFile(arquivo, engine="openpyxl")
            for aba in excel.sheet_names:
                df = pd.read_excel(arquivo, sheet_name=aba, engine="openpyxl")
                mapa = {}
                for col in df.columns:
                    chave = _chave_coluna(col)
                    if chave in {"empreendimento", "empreendimentos", "nome empreendimento"}:
                        mapa[col] = "Empreendimento"
                    elif chave in {"unidade", "unidades", "quadra lote", "quadra/lote"}:
                        mapa[col] = "Unidade"
                df = df.rename(columns=mapa)
                if {"Empreendimento", "Unidade"}.issubset(df.columns):
                    df = df[["Empreendimento", "Unidade"]].copy()

                    def texto_limpo(valor):
                        if pd.isna(valor):
                            return ""
                        if isinstance(valor, float) and valor.is_integer():
                            return str(int(valor))
                        return str(valor).strip()

                    for col in ["Empreendimento", "Unidade"]:
                        df[col] = df[col].apply(texto_limpo)
                    df = df[(df["Empreendimento"] != "") & (df["Unidade"] != "")].drop_duplicates()
                    if not df.empty:
                        return df, arquivo, aba, None
        except Exception as erro:
            erros.append(f"{arquivo}: {erro}")

    detalhe = " | ".join(erros) if erros else "Nenhum Excel compatível encontrado."
    return pd.DataFrame(columns=["Empreendimento", "Unidade"]), None, None, detalhe


cadastro, arquivo_cadastro, aba_cadastro, erro_cadastro = carregar_cadastro()


# ============================================================
# PARÂMETROS DO SCORE — V15.0 (preservados)
# ============================================================
PESOS = {
    "score_credito":         5,
    "ato":                   5,
    "comprometimento_renda": 4,
    "idade":                 1,
    "estado_civil":          1,
}

NOTAS_SCORE = {"A - B": 5, "C - D": 3, "E - F": 1}

NOTAS_ATO = {
    "ACIMA DE 4%":  5,
    "3% A 4%":      4,
    "2% A 3%":      3,
    "1% A 2%":      2,
    "ABAIXO DE 1%": 1,
}

NOTAS_COMPROMETIMENTO = {
    "ATE 10%":       5,
    "10% A 20%":     4,
    "20% A 30%":     3,
    "30% A 50%":     2,
    "50% A 100%":    1,
    "ACIMA DE 100%": 1,
}

NOTAS_IDADE = {
    "60+ ANOS":     5,
    "45 A 60 ANOS": 4,
    "35 A 45 ANOS": 3,
    "ATE 25 ANOS":  2,
    "25 A 35 ANOS": 1,
}

NOTAS_ESTADO_CIVIL = {
    "CASADO(A)":     3,
    "DIVORCIADO(A)": 2,
    "SOLTEIRO(A)":   1,
}

SCORE_MAX       = 78
LIMITE_BAIXO    = 54
LIMITE_MODERADO = 33


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================
def brl(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def normalizar(texto):
    texto = texto or ""
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = texto.upper().replace("\xa0", " ")
    texto = re.sub(r"[ \t]+", " ", texto)
    return texto


def moeda_para_float(valor):
    if valor is None:
        return 0.0
    s = str(valor).strip().replace("R$", "").replace(" ", "")
    if not s:
        return 0.0
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    else:
        if s.count(".") > 1:
            s = s.replace(".", "")
    try:
        return max(0.0, float(s))
    except (TypeError, ValueError):
        return 0.0


def float_para_moeda_input(valor):
    return f"{float(valor or 0):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _normalizar_campo_moeda(chave):
    st.session_state[chave] = float_para_moeda_input(
        moeda_para_float(st.session_state.get(chave, "0,00"))
    )


def campo_moeda(label, chave, valor_inicial=0.0, ajuda=None):
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


def calcular_idade(nascimento):
    hoje = datetime.now(TIMEZONE_BRASILIA).date()
    return hoje.year - nascimento.year - (
        (hoje.month, hoje.day) < (nascimento.month, nascimento.day)
    )


def faixa_etaria(idade):
    if idade <= 25:
        return "ATE 25 ANOS"
    if idade <= 35:
        return "25 A 35 ANOS"
    if idade <= 45:
        return "35 A 45 ANOS"
    if idade <= 60:
        return "45 A 60 ANOS"
    return "60+ ANOS"


def faixa_comprometimento(perc):
    if perc <= 10:
        return "ATE 10%"
    if perc <= 20:
        return "10% A 20%"
    if perc <= 30:
        return "20% A 30%"
    if perc <= 50:
        return "30% A 50%"
    if perc <= 100:
        return "50% A 100%"
    return "ACIMA DE 100%"


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
        return "BAIXO RISCO", "green"
    if score >= LIMITE_MODERADO:
        return "RISCO MODERADO", "orange"
    return "ALTO RISCO", "red"


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


def formatar_cpf(digitos):
    return f"{digitos[:3]}.{digitos[3:6]}.{digitos[6:9]}-{digitos[9:]}"


# ============================================================
# EXTRAÇÃO DO SPC (preservada do V15.0)
# ============================================================
def extrair_dados_spc(pdf_file):
    pdf_file.seek(0)
    paginas = []
    tabelas = []

    with pdfplumber.open(pdf_file) as pdf:
        for numero, page in enumerate(pdf.pages, start=1):
            texto = page.extract_text(x_tolerance=2, y_tolerance=3) or ""
            paginas.append(texto)
            try:
                for tabela in page.extract_tables() or []:
                    tabelas.append((numero, tabela))
            except Exception:
                pass

    texto_completo = "\n".join(paginas)
    texto_norm = normalizar(texto_completo)

    # Score
    score_letra = None
    for padrao in [
        r"\bRISCO\s+DE\s+CREDITO\s*[:\-]?\s*([A-F])\b",
        r"\bRISCO\s+DE\s+CREDITO\b[\s\S]{0,80}?\b([A-F])\b",
    ]:
        m = re.search(padrao, texto_norm, flags=re.I)
        if m:
            score_letra = m.group(1).upper()
            break
    score_faixa = mapear_score(score_letra)

    # Renda
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

    if not renda:
        for padrao in [
            r"RENDA\s+PRESUMIDA\s*-\s*SPC\s+BRASIL[\s\S]{0,160}?(?:R\$\s*)?(\d{1,3}(?:\.\d{3})*,\d{2})",
            r"RENDA\s+PRESUMIDA\s*:?\s*(?:_+\s*)?(?:R\$\s*)?(\d{1,3}(?:\.\d{3})*,\d{2})",
        ]:
            m = re.search(padrao, texto_norm, flags=re.I)
            if m:
                renda = moeda_para_float(m.group(1))
                if renda and renda > 0:
                    break

    # Data de nascimento
    data_nascimento = None
    for padrao in [
        r"(?:DATA\s+DE\s+NASCIMENTO|DT\.?\s*NASCIMENTO|NASCIMENTO)\s*[:\-]?\s*(\d{1,2}/\d{1,2}/\d{4})",
        r"(?:DATA\s+DE\s+NASCIMENTO|DT\.?\s*NASCIMENTO|NASCIMENTO)[\s\S]{0,50}?(\d{1,2}/\d{1,2}/\d{4})",
    ]:
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

    # CPF
    cpf = None
    for padrao in [
        r"\bCPF\s*[:\-]?\s*(\d{3}[\.\-]?\d{3}[\.\-]?\d{3}[\.\-\/]?\d{2})\b",
        r"\b(\d{3}\.\d{3}\.\d{3}[-\/]\d{2})\b",
    ]:
        m_cpf = re.search(padrao, texto_norm, flags=re.I)
        if m_cpf:
            digitos = re.sub(r"\D", "", m_cpf.group(1))
            if len(digitos) == 11:
                cpf = formatar_cpf(digitos)
                break

    return {
        "score_letra":     score_letra,
        "score_faixa":     score_faixa,
        "renda_presumida": renda,
        "data_nascimento": data_nascimento,
        "cpf":             cpf,
        "texto_extraido":  texto_completo,
    }


# ============================================================
# CENÁRIOS (preservados do V15.0)
# ============================================================
def renda_minima_para_comprometimento(mensal, limite_pct):
    if mensal <= 0 or limite_pct <= 0:
        return 0
    return mensal / (limite_pct / 100)


def mensal_maxima_para_comprometimento(renda, limite_pct):
    return renda * limite_pct / 100


def ato_minimo_para_percentual(valor_proposta, pct):
    return valor_proposta * pct / 100


def montar_cenarios(score_atual, notas, renda_total, mensal, ato, valor_proposta):
    cenarios = []

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
                "Variavel": "Ato",
                "Ajuste": f"Aumentar o ato para aprox. {brl(ato_alvo)} (+{brl(adicional)}; ~{pct_meta:.2f}% da proposta)",
                "Ganho": ganho,
                "NovoScore": score_atual + ganho,
            })

    metas_comp = [
        (50, "30% A 50%"),
        (30, "20% A 30%"),
        (20, "10% A 20%"),
        (10, "ATE 10%"),
    ]
    for limite, faixa_meta in metas_comp:
        nova_nota = NOTAS_COMPROMETIMENTO[faixa_meta]
        ganho = (nova_nota - notas["comprometimento_renda"]) * PESOS["comprometimento_renda"]
        if ganho > 0:
            renda_alvo = renda_minima_para_comprometimento(mensal, limite)
            mensal_alvo = mensal_maxima_para_comprometimento(renda_total, limite)
            cenarios.append({
                "Variavel": "Renda / Mensal",
                "Ajuste": f"Para comprometimento <= {limite}%: renda total ~{brl(renda_alvo)} OU mensal <= {brl(mensal_alvo)}",
                "Ganho": ganho,
                "NovoScore": score_atual + ganho,
            })

    for c in cenarios:
        c["NovaClassificacao"] = classificar(c["NovoScore"])[0]
        c["AtingeModerado"] = c["NovoScore"] >= LIMITE_MODERADO
        c["AtingeBaixo"]    = c["NovoScore"] >= LIMITE_BAIXO

    return sorted(cenarios, key=lambda c: (not c["AtingeModerado"], not c["AtingeBaixo"], -c["Ganho"]))


# ============================================================
# HELPERS DE UI
# ============================================================
def secao(titulo):
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:10px; margin:20px 0 8px;">
        <div style="width:4px; height:22px; background:{URBA_GREEN};
                    border-radius:2px; flex-shrink:0;"></div>
        <span style="font-size:1rem; font-weight:700; color:{URBA_TEXT};
                     letter-spacing:-0.01em;">{titulo}</span>
    </div>
    """, unsafe_allow_html=True)


def card_resumo(col, titulo, valor):
    with col:
        st.markdown(f"""
        <div style="background:{URBA_CARD}; border:1px solid {URBA_BORDER};
                    border-radius:10px; padding:14px 16px; height:80px;">
            <div style="font-size:0.72rem; font-weight:700; color:{URBA_MUTED};
                        text-transform:uppercase; letter-spacing:0.05em;
                        margin-bottom:6px;">{titulo}</div>
            <div style="font-size:0.95rem; font-weight:700; color:{URBA_TEXT};
                        overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">
                {valor if valor not in (None, '', '—') else '—'}
            </div>
        </div>
        """, unsafe_allow_html=True)


def badge_classificacao(classificacao, score, score_max):
    cores = {
        "BAIXO RISCO":    (URBA_GREEN,      "#E8F8EF", "Baixo Risco"),
        "RISCO MODERADO": (URBA_ORANGE,     "#FFF4E8", "Risco Moderado"),
        "ALTO RISCO":     (URBA_GREEN_DARK, "#E8F8EF", "Alto Risco"),
    }
    cor_texto, cor_bg, label = cores.get(classificacao, ("#6B7280", "#F4F6F8", classificacao))
    st.markdown(f"""
    <div style="background:{cor_bg}; border:2px solid {cor_texto};
                border-radius:14px; padding:20px 24px; text-align:center;">
        <div style="font-size:2.2rem; font-weight:900; color:{cor_texto};
                    letter-spacing:-0.02em;">{score}</div>
        <div style="font-size:0.78rem; color:{URBA_MUTED}; margin:2px 0 10px;">
            de {score_max} pontos
        </div>
        <div style="background:{cor_texto}; color:#FFFFFF; border-radius:20px;
                    padding:6px 18px; font-size:0.85rem; font-weight:800;
                    display:inline-block; letter-spacing:0.04em;">
            {label}
        </div>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# PÁGINA: SIMULADOR
# ============================================================
if st.session_state.pagina == "Simulador":

    secao("Dados da Simulação")
    st.caption("Preencha as informações abaixo para calcular o score de risco da venda.")

    col_emp, col_cli, col_prop, col_renda = st.columns(4, gap="large")

    # ── EMPREENDIMENTO ──
    with col_emp:
        st.markdown(f"**Empreendimento**")
        st.caption("Selecione o empreendimento e a unidade.")

        if cadastro.empty:
            st.error("Cadastro de empreendimentos nao carregado.")
            if erro_cadastro:
                with st.expander("Detalhes"):
                    st.code(erro_cadastro)

        empreendimentos = sorted(
            cadastro["Empreendimento"].dropna().astype(str).str.strip()
            .loc[lambda x: x.ne("")].unique().tolist()
        )

        empreendimento = st.selectbox(
            "Empreendimento *",
            [""] + empreendimentos,
            index=0,
            key="empreendimento_v16",
        )

        if empreendimento:
            cad_emp = cadastro[
                cadastro["Empreendimento"].astype(str).str.strip() == str(empreendimento).strip()
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
            key="unidade_v16",
            format_func=rotulo_unidade,
        )
        if unidade:
            st.caption(f"Unidade: {rotulo_unidade(unidade)}")

    # ── PERFIL DO CLIENTE ──
    with col_cli:
        st.markdown(f"**Perfil do Cliente**")
        st.caption("Anexe o relatorio SPC do proponente.")

        pdf_prop = st.file_uploader(
            "SPC do Proponente *",
            type=["pdf"],
            key="pdf_prop_v16",
        )

        dados_spc_prop  = None
        score_proponente = None
        renda_proponente = 0.0
        nascimento       = None
        idade            = None
        faixa_idade      = None
        cpf_proponente   = ""

        if pdf_prop:
            try:
                with st.spinner("Lendo SPC..."):
                    dados_spc_prop = extrair_dados_spc(pdf_prop)

                score_proponente = dados_spc_prop.get("score_faixa")
                renda_proponente = float(dados_spc_prop.get("renda_presumida") or 0)
                nascimento       = dados_spc_prop.get("data_nascimento")
                idade            = calcular_idade(nascimento) if nascimento else None
                faixa_idade      = faixa_etaria(idade) if idade is not None else None
                cpf_proponente   = dados_spc_prop.get("cpf") or ""

                st.markdown("**Dados identificados no SPC**")
                with st.container(border=True):
                    if cpf_proponente:
                        st.caption("CPF")
                        st.markdown(f"**{cpf_proponente}**")
                    else:
                        st.warning("CPF nao localizado.")

                    if nascimento:
                        st.caption("Nascimento / Idade")
                        st.markdown(f"**{nascimento.strftime('%d/%m/%Y')}** · {idade} anos · {faixa_idade}")
                    else:
                        st.warning("Data de nascimento nao localizada.")

                    if score_proponente:
                        st.caption("Score")
                        st.markdown(f"**{dados_spc_prop.get('score_letra')} → {score_proponente}**")
                    else:
                        st.warning("Score nao localizado.")

                    if renda_proponente > 0:
                        st.caption("Renda Presumida")
                        st.markdown(f"**{brl(renda_proponente)}**")
                    else:
                        st.warning("Renda nao localizada.")

            except Exception as e:
                st.error(f"Falha na leitura do SPC: {e}")

        if pdf_prop and not cpf_proponente:
            cpf_proponente = st.text_input(
                "CPF (manual)",
                placeholder="000.000.000-00",
                key="cpf_manual_v16",
            ).strip()

        if pdf_prop and not score_proponente:
            score_proponente = st.selectbox(
                "Score SPC (manual)",
                ["", "A - B", "C - D", "E - F"],
                key="score_manual_v16",
            )

        if pdf_prop and renda_proponente <= 0:
            renda_proponente = campo_moeda(
                "Renda Presumida (manual) R$",
                "renda_manual_v16",
            )

        estado_civil = st.selectbox(
            "Estado Civil *",
            ["", "SOLTEIRO(A)", "DIVORCIADO(A)", "CASADO(A)"],
            key="estado_civil_v16",
        )

    # ── DADOS DA PROPOSTA ──
    with col_prop:
        st.markdown(f"**Dados da Proposta**")
        st.caption("Valores financeiros da operacao.")

        ato_urba       = campo_moeda("Ato Urba (R$) *",                  "ato_urba_v16")
        valor_proposta = campo_moeda("Valor da Proposta / Liquido CV (R$) *", "valor_proposta_v16")
        primeira_mensal = campo_moeda("Valor da 1a Mensal (R$) *",        "primeira_mensal_v16")

    # ── COMPOSIÇÃO DE RENDA ──
    with col_renda:
        st.markdown(f"**Composicao de Renda**")
        st.caption("Use somente quando houver cliente adicional compondo renda.")

        qtd_adicionais = st.number_input(
            "Clientes adicionais",
            min_value=0,
            max_value=4,
            value=0,
            step=1,
            key="qtd_adicionais_v16",
        )

        rendas_adicionais = []
        for i in range(int(qtd_adicionais)):
            numero = i + 2
            with st.expander(f"Cliente {numero}", expanded=True):
                pdf_add = st.file_uploader(
                    f"SPC — Cliente {numero}",
                    type=["pdf"],
                    key=f"pdf_add_v16_{numero}",
                )
                renda_add = 0.0
                if pdf_add:
                    try:
                        d_add = extrair_dados_spc(pdf_add)
                        renda_add = float(d_add["renda_presumida"] or 0)
                        if renda_add:
                            st.success(f"Renda: {brl(renda_add)}")
                        else:
                            st.warning("Renda nao localizada.")
                    except Exception as e:
                        st.error(f"Falha: {e}")
                if pdf_add and renda_add <= 0:
                    renda_add = campo_moeda(
                        f"Renda manual — Cliente {numero} (R$)",
                        f"renda_add_v16_{numero}",
                    )
                rendas_adicionais.append(renda_add)

    # ── INDICADORES INSTANTÂNEOS ──
    renda_total = renda_proponente + sum(rendas_adicionais)
    perc_ato    = ato_urba / valor_proposta * 100 if valor_proposta > 0 else 0
    perc_comp   = primeira_mensal / renda_total * 100 if renda_total > 0 else 0
    faixa_at    = faixa_ato(perc_ato)
    faixa_comp  = faixa_comprometimento(perc_comp)

    st.divider()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("% do Ato",       f"{perc_ato:.2f}%",  faixa_at)
    m2.metric("Comprometimento", f"{perc_comp:.2f}%", faixa_comp)
    m3.metric("Renda Total",     brl(renda_total))
    m4.metric("Faixa Etaria",    faixa_idade or "—")

    # ── VALIDAÇÃO ──
    faltando = []
    if not empreendimento:    faltando.append("Empreendimento")
    if not unidade:           faltando.append("Unidade")
    if not nascimento:        faltando.append("Data de Nascimento")
    if not estado_civil:      faltando.append("Estado Civil")
    if not pdf_prop:          faltando.append("SPC do Proponente")
    if not score_proponente:  faltando.append("Score SPC")
    if renda_total <= 0:      faltando.append("Renda Presumida")
    if valor_proposta <= 0:   faltando.append("Valor da Proposta")
    if primeira_mensal <= 0:  faltando.append("1a Mensal")

    if faltando:
        st.info(f"Preencha para calcular: {', '.join(faltando)}")

    _, btn_col = st.columns([3, 1])
    with btn_col:
        calcular = st.button(
            "CALCULAR SIMULACAO",
            type="primary",
            use_container_width=True,
            disabled=bool(faltando),
            key="calcular_v16",
        )

    if calcular:
        notas = {
            "score_credito":         NOTAS_SCORE[score_proponente],
            "ato":                   NOTAS_ATO[faixa_at],
            "comprometimento_renda": NOTAS_COMPROMETIMENTO[faixa_comp],
            "idade":                 NOTAS_IDADE[faixa_idade],
            "estado_civil":          NOTAS_ESTADO_CIVIL[estado_civil],
        }
        score_final = calcular_score_total(notas)
        classificacao, cor = classificar(score_final)

        st.session_state.resultado = {
            "notas":                   notas,
            "score_final":             score_final,
            "classificacao":           classificacao,
            "cor":                     cor,
            "empreendimento":          empreendimento,
            "unidade":                 unidade,
            "cpf_proponente":          cpf_proponente,
            "idade":                   idade,
            "faixa_idade":             faixa_idade,
            "estado_civil":            estado_civil,
            "score_proponente":        score_proponente,
            "renda_proponente":        renda_proponente,
            "qtd_clientes_adicionais": int(qtd_adicionais),
            "renda_adicionais":        sum(rendas_adicionais),
            "renda_total":             renda_total,
            "ato_urba":                ato_urba,
            "valor_proposta":          valor_proposta,
            "perc_ato":                perc_ato,
            "faixa_at":                faixa_at,
            "primeira_mensal":         primeira_mensal,
            "perc_comp":               perc_comp,
            "faixa_comp":              faixa_comp,
        }

    # ── RESULTADO ──
    if st.session_state.resultado:
        d = st.session_state.resultado
        st.divider()

        secao("Resumo da Simulacao")
        q1, q2, q3, q4 = st.columns(4)
        card_resumo(q1, "Empreendimento", d.get("empreendimento"))
        unidade_r = d.get("unidade", "")
        emp_r = d.get("empreendimento", "")
        if emp_r and unidade_r.upper().startswith(emp_r.upper()):
            unidade_r = unidade_r[len(emp_r):].lstrip(" -–—") or unidade_r
        card_resumo(q2, "Unidade", unidade_r)
        card_resumo(q3, "CPF do Proponente", d.get("cpf_proponente"))
        card_resumo(q4, "Renda Total", brl(d.get("renda_total", 0)))

        p1, p2, p3, p4 = st.columns(4)
        card_resumo(p1, "Faixa Etaria",       d.get("faixa_idade"))
        card_resumo(p2, "Estado Civil",        d.get("estado_civil"))
        card_resumo(p3, "Score do Proponente", d.get("score_proponente"))
        card_resumo(p4, "Ato Urba",            brl(d.get("ato_urba", 0)))

        c1, c2, c3, c4 = st.columns(4)
        card_resumo(c1, "% do Ato",         f"{d.get('perc_ato', 0):.2f}%")
        card_resumo(c2, "1a Mensal",         brl(d.get("primeira_mensal", 0)))
        card_resumo(c3, "Comprometimento",   f"{d.get('perc_comp', 0):.2f}%")
        card_resumo(c4, "Valor da Proposta", brl(d.get("valor_proposta", 0)))

        st.divider()
        secao("Avaliacao de Risco")

        r1, r2 = st.columns([1, 2])
        with r1:
            badge_classificacao(d["classificacao"], d["score_final"], SCORE_MAX)

        with r2:
            labels = {
                "score_credito":         "Score de Credito",
                "ato":                   "% do Ato",
                "comprometimento_renda": "Comprometimento de Renda",
                "idade":                 "Faixa Etaria",
                "estado_civil":          "Estado Civil",
            }
            max_nota = {
                "score_credito":         5,
                "ato":                   5,
                "comprometimento_renda": 5,
                "idade":                 5,
                "estado_civil":          3,
            }
            detalhes = []
            for var, peso in PESOS.items():
                nota = d["notas"][var]
                detalhes.append({
                    "Variavel": labels[var],
                    "Nota":     f"{nota}/{max_nota[var]}",
                    "Peso":     peso,
                    "Pontos":   nota * peso,
                    "Maximo":   max_nota[var] * peso,
                })
            st.dataframe(
                pd.DataFrame(detalhes),
                use_container_width=True,
                hide_index=True,
            )

        # ── ESTRATÉGIAS ──
        if d["classificacao"] != "BAIXO RISCO":
            st.divider()
            secao("Estrategias de Estruturacao da Venda")

            falta_mod   = max(0, LIMITE_MODERADO - d["score_final"])
            falta_baixo = max(0, LIMITE_BAIXO    - d["score_final"])
            e1, e2 = st.columns(2)
            e1.metric("Pontos para Risco Moderado", f"+{falta_mod}")
            e2.metric("Pontos para Baixo Risco",    f"+{falta_baixo}")

            cenarios = montar_cenarios(
                score_atual=d["score_final"],
                notas=d["notas"],
                renda_total=d["renda_total"],
                mensal=d["primeira_mensal"],
                ato=d["ato_urba"],
                valor_proposta=d["valor_proposta"],
            )
            if cenarios:
                df_c = pd.DataFrame(cenarios)
                df_c["Ganho"]     = df_c["Ganho"].map(lambda x: f"+{x}")
                df_c["NovoScore"] = df_c["NovoScore"].map(str)
                st.dataframe(
                    df_c[["Variavel", "Ajuste", "Ganho", "NovoScore", "NovaClassificacao"]].head(12),
                    use_container_width=True,
                    hide_index=True,
                )
                st.caption("Sugestoes sao simulacoes contrafactuais. Nao alteram dados cadastrais do cliente.")

        # ── SALVAR ──
        st.divider()
        secao("Salvar no Historico")
        st.caption("Confirme para registrar esta simulacao no banco de dados.")

        if st.button(
            "CONFIRMAR E SALVAR NO HISTORICO",
            type="primary",
            key="salvar_v16",
        ):
            try:
                db_execute("""
                    INSERT INTO historico_simulacoes (
                        vendedor_email, empreendimento, unidade, cpf_proponente,
                        idade, faixa_etaria, estado_civil, score_proponente,
                        renda_proponente, qtd_clientes_adicionais,
                        renda_clientes_adicionais, renda_total,
                        ato_urba, percentual_ato, faixa_ato,
                        valor_proposta, primeira_mensal,
                        percentual_comprometimento, faixa_comprometimento,
                        score_final, classificacao
                    ) VALUES (
                        %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
                    )
                """, (
                    usuario["email"],
                    d.get("empreendimento", ""),
                    d.get("unidade", ""),
                    d.get("cpf_proponente", ""),
                    d.get("idade"),
                    d.get("faixa_idade", ""),
                    d.get("estado_civil", ""),
                    d.get("score_proponente", ""),
                    d.get("renda_proponente", 0),
                    d.get("qtd_clientes_adicionais", 0),
                    d.get("renda_adicionais", 0),
                    d.get("renda_total", 0),
                    d.get("ato_urba", 0),
                    d.get("perc_ato", 0),
                    d.get("faixa_at", ""),
                    d.get("valor_proposta", 0),
                    d.get("primeira_mensal", 0),
                    d.get("perc_comp", 0),
                    d.get("faixa_comp", ""),
                    d.get("score_final", 0),
                    d.get("classificacao", ""),
                ))
                st.success("Simulacao salva com sucesso!")
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")


# ============================================================
# PÁGINA: HISTÓRICO
# ============================================================
elif st.session_state.pagina == "Historico" and is_admin:

    secao("Historico de Simulacoes")

    try:
        rows = db_query("""
            SELECT * FROM historico_simulacoes
            ORDER BY data_hora DESC
        """)
        hist = pd.DataFrame(rows) if rows else pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao carregar historico: {e}")
        hist = pd.DataFrame()

    if hist.empty:
        st.info("Nenhuma simulacao registrada ainda.")
    else:
        f1, f2, f3 = st.columns(3)
        with f1:
            vendedores = ["TODOS"] + sorted(hist["vendedor_email"].dropna().unique().tolist())
            filtro_v = st.selectbox("Vendedor", vendedores, key="filt_v")
        with f2:
            emps = ["TODOS"] + sorted(hist["empreendimento"].dropna().unique().tolist())
            filtro_e = st.selectbox("Empreendimento", emps, key="filt_e")
        with f3:
            classes = ["TODAS"] + sorted(hist["classificacao"].dropna().unique().tolist())
            filtro_c = st.selectbox("Classificacao", classes, key="filt_c")

        exib = hist.copy()
        if filtro_v != "TODOS":
            exib = exib[exib["vendedor_email"] == filtro_v]
        if filtro_e != "TODOS":
            exib = exib[exib["empreendimento"] == filtro_e]
        if filtro_c != "TODAS":
            exib = exib[exib["classificacao"] == filtro_c]

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total",        len(exib))
        k2.metric("Baixo Risco",  int(exib["classificacao"].str.contains("BAIXO",    na=False).sum()))
        k3.metric("Moderado",     int(exib["classificacao"].str.contains("MODERADO", na=False).sum()))
        k4.metric("Alto Risco",   int(exib["classificacao"].str.contains("ALTO",     na=False).sum()))

        st.dataframe(exib, use_container_width=True, hide_index=True)

        st.download_button(
            "BAIXAR HISTORICO (CSV)",
            exib.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"historico_score_{datetime.now(TIMEZONE_BRASILIA).strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    st.divider()
    with st.expander("Excluir historico completo", expanded=False):
        st.warning("Esta acao nao pode ser desfeita.")
        confirmar = st.checkbox("Confirmo que desejo excluir TODO o historico", key="conf_del")
        if st.button(
            "EXCLUIR TODO O HISTORICO",
            type="primary",
            disabled=not confirmar,
            key="del_hist",
        ):
            try:
                db_execute("DELETE FROM historico_simulacoes")
                st.success("Historico excluido.")
                st.rerun()
            except Exception as e:
                st.error(f"Erro: {e}")


# ============================================================
# PÁGINA: GESTÃO DE USUÁRIOS
# ============================================================
elif st.session_state.pagina == "Usuarios" and is_admin:

    secao("Gestao de Usuarios")

    try:
        rows = db_query("SELECT id, nome, email, perfil, ativo, criado_em FROM usuarios ORDER BY criado_em DESC")
        df_users = pd.DataFrame(rows) if rows else pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao carregar usuarios: {e}")
        df_users = pd.DataFrame()

    if not df_users.empty:
        st.dataframe(df_users, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum usuario cadastrado.")

    st.divider()
    secao("Adicionar Novo Usuario")

    with st.form("form_novo_usuario", clear_on_submit=True):
        n1, n2 = st.columns(2)
        with n1:
            novo_nome  = st.text_input("Nome completo *")
            novo_email = st.text_input("E-mail *")
        with n2:
            novo_perfil = st.selectbox("Perfil *", ["VENDEDOR", "ADMINISTRADOR"])
            nova_senha  = st.text_input("Senha *", type="password")

        if st.form_submit_button("ADICIONAR USUARIO", type="primary"):
            if not all([novo_nome, novo_email, nova_senha]):
                st.error("Preencha todos os campos.")
            else:
                try:
                    db_execute(
                        "INSERT INTO usuarios (nome, email, senha_hash, perfil) VALUES (%s,%s,%s,%s)",
                        (novo_nome.strip(), novo_email.strip().lower(),
                         hash_senha(nova_senha), novo_perfil),
                    )
                    st.success(f"Usuario {novo_nome} adicionado com sucesso!")
                    st.rerun()
                except psycopg2.errors.UniqueViolation:
                    st.error("E-mail ja cadastrado.")
                except Exception as e:
                    st.error(f"Erro: {e}")

    st.divider()
    secao("Alterar Senha de Usuario")

    with st.form("form_alterar_senha", clear_on_submit=True):
        email_alt  = st.text_input("E-mail do usuario")
        nova_senha_alt = st.text_input("Nova senha", type="password")
        if st.form_submit_button("ALTERAR SENHA", type="primary"):
            if not email_alt or not nova_senha_alt:
                st.error("Preencha e-mail e nova senha.")
            else:
                try:
                    db_execute(
                        "UPDATE usuarios SET senha_hash=%s, atualizado_em=NOW() WHERE email=%s",
                        (hash_senha(nova_senha_alt), email_alt.strip().lower()),
                    )
                    st.success("Senha alterada com sucesso!")
                except Exception as e:
                    st.error(f"Erro: {e}")

    st.divider()
    secao("Ativar / Desativar Usuario")

    with st.form("form_toggle_usuario", clear_on_submit=True):
        email_tog = st.text_input("E-mail do usuario")
        acao_tog  = st.selectbox("Acao", ["Desativar", "Ativar"])
        if st.form_submit_button("APLICAR", type="primary"):
            if not email_tog:
                st.error("Informe o e-mail.")
            else:
                ativo_novo = acao_tog == "Ativar"
                try:
                    db_execute(
                        "UPDATE usuarios SET ativo=%s, atualizado_em=NOW() WHERE email=%s",
                        (ativo_novo, email_tog.strip().lower()),
                    )
                    st.success(f"Usuario {email_tog} {'ativado' if ativo_novo else 'desativado'}.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")


# ============================================================
# RODAPÉ
# ============================================================
st.divider()
st.markdown(f"""
<div style="text-align:center; padding:12px 0; color:{URBA_MUTED}; font-size:0.78rem;">
    <span style="color:{URBA_GREEN}; font-weight:700;">Urba</span>
    &nbsp;·&nbsp; Simulador de Score de Vendas V16.4
    &nbsp;·&nbsp; Projeto Defensores do Contrato
</div>
""", unsafe_allow_html=True)
