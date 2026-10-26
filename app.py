# app.py — V16.5
# Simulador de Score de Vendas — Projeto Defensores do Contrato
# V16.5: Fundo branco forçado em TODOS os elementos, independente do tema do SO/navegador.
#        Clientes adicionais com campos legíveis. Identidade visual Urba.

import io
import os
import re
import unicodedata
from datetime import date, datetime
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st
import pdfplumber
import psycopg2
import bcrypt

st.set_page_config(
    page_title="Simulador de Score — Urba",
    page_icon="https://i.imgur.com/0y0y0y0.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# CSS GLOBAL — FORÇA TEMA CLARO EM TUDO
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* ── RESET TEMA ESCURO ── */
html, body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
.main, .block-container,
section[data-testid="stSidebar"] > div,
[data-testid="stVerticalBlock"],
[data-testid="stHorizontalBlock"] {
    background-color: #FFFFFF !important;
    color: #2D2D2D !important;
    font-family: 'Inter', sans-serif !important;
}

/* ── TIRA PRETA DO TOPO ── */
#MainMenu, header[data-testid="stHeader"], footer,
[data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"] {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
}

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #056B3A 0%, #079D56 100%) !important;
    border-right: none !important;
}
section[data-testid="stSidebar"] * {
    color: #FFFFFF !important;
}
section[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.25) !important;
}
section[data-testid="stSidebar"] button {
    background: rgba(255,255,255,0.15) !important;
    color: #FFFFFF !important;
    border: 1px solid rgba(255,255,255,0.3) !important;
    border-radius: 8px !important;
}
section[data-testid="stSidebar"] button:hover {
    background: rgba(255,255,255,0.25) !important;
}

/* ── INPUTS, SELECTS, TEXTAREAS ── */
input, textarea,
[data-baseweb="input"] input,
[data-baseweb="textarea"] textarea,
[data-baseweb="base-input"] input,
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input {
    background-color: #FFFFFF !important;
    color: #2D2D2D !important;
    border: 1.5px solid #CBD5E0 !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
}
[data-baseweb="input"],
[data-baseweb="base-input"],
[data-baseweb="input"] > div,
[data-baseweb="base-input"] > div {
    background-color: #FFFFFF !important;
    border: 1.5px solid #CBD5E0 !important;
    border-radius: 8px !important;
}
input:focus,
[data-baseweb="input"]:focus-within,
[data-baseweb="base-input"]:focus-within {
    border-color: #079D56 !important;
    box-shadow: 0 0 0 3px rgba(7,157,86,0.15) !important;
}

/* ── SELECT / DROPDOWN ── */
[data-baseweb="select"] > div,
[data-baseweb="select"] > div > div {
    background-color: #FFFFFF !important;
    color: #2D2D2D !important;
    border: 1.5px solid #CBD5E0 !important;
    border-radius: 8px !important;
}
[data-baseweb="select"] span,
[data-baseweb="select"] div {
    color: #2D2D2D !important;
    background-color: #FFFFFF !important;
}
[data-baseweb="popover"],
[data-baseweb="menu"],
[role="listbox"],
[data-baseweb="menu"] ul {
    background-color: #FFFFFF !important;
    border: 1px solid #CBD5E0 !important;
    border-radius: 8px !important;
    box-shadow: 0 4px 16px rgba(0,0,0,0.10) !important;
}
[role="option"],
[data-baseweb="menu"] li {
    background-color: #FFFFFF !important;
    color: #2D2D2D !important;
}
[role="option"]:hover,
[data-baseweb="menu"] li:hover {
    background-color: #F0FBF5 !important;
    color: #056B3A !important;
}

/* ── NUMBER INPUT ── */
[data-testid="stNumberInput"] {
    background-color: #FFFFFF !important;
}
[data-testid="stNumberInput"] > div {
    background-color: #FFFFFF !important;
    border: 1.5px solid #CBD5E0 !important;
    border-radius: 8px !important;
}
[data-testid="stNumberInput"] button {
    background-color: #F4F6F8 !important;
    color: #2D2D2D !important;
    border: 1px solid #CBD5E0 !important;
}
[data-testid="stNumberInput"] button:hover {
    background-color: #E8F5EE !important;
    color: #056B3A !important;
}

/* ── FILE UPLOADER ── */
[data-testid="stFileUploader"],
[data-testid="stFileUploader"] > div,
[data-testid="stFileUploaderDropzone"] {
    background-color: #F0FBF5 !important;
    border: 2px dashed #079D56 !important;
    border-radius: 10px !important;
    color: #2D2D2D !important;
}
[data-testid="stFileUploaderDropzone"] * {
    color: #2D2D2D !important;
}
[data-testid="stFileUploaderDropzone"] button {
    background-color: #079D56 !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 6px !important;
}

/* ── EXPANDER ── */
[data-testid="stExpander"],
[data-testid="stExpander"] > div,
details, details > div,
details > summary {
    background-color: #FFFFFF !important;
    color: #2D2D2D !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 10px !important;
}
details > summary {
    font-weight: 600 !important;
    color: #2D2D2D !important;
    padding: 10px 14px !important;
}
details[open] > summary {
    border-bottom: 1px solid #E2E8F0 !important;
    border-radius: 10px 10px 0 0 !important;
}

/* ── CONTAINERS / CARDS ── */
[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #F8FAFB !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 12px !important;
    color: #2D2D2D !important;
}
[data-testid="stVerticalBlockBorderWrapper"] * {
    color: #2D2D2D !important;
}

/* ── MÉTRICAS ── */
[data-testid="stMetric"] {
    background-color: #F8FAFB !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 12px !important;
    padding: 14px 16px !important;
}
[data-testid="stMetricLabel"] p { color: #6B7280 !important; font-size: .82rem !important; }
[data-testid="stMetricValue"]   { color: #2D2D2D !important; font-size: 1.4rem !important; font-weight: 700 !important; }
[data-testid="stMetricDelta"]   { color: #079D56 !important; }

/* ── DATAFRAME / TABELA ── */
[data-testid="stDataFrame"],
[data-testid="stDataFrame"] *,
.stDataFrame, iframe {
    background-color: #FFFFFF !important;
    color: #2D2D2D !important;
}

/* ── ALERTAS ── */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    border-left-width: 4px !important;
}
[data-testid="stAlert"][data-baseweb="notification"] {
    background-color: #F0FBF5 !important;
    border-left-color: #079D56 !important;
    color: #2D2D2D !important;
}

/* ── BOTÕES ── */
.stButton > button {
    font-family: 'Inter', sans-serif !important;
    font-weight: 700 !important;
    border-radius: 8px !important;
    min-height: 42px !important;
    transition: all .18s ease !important;
}
.stButton > button[kind="primary"] {
    background-color: #079D56 !important;
    color: #FFFFFF !important;
    border: none !important;
}
.stButton > button[kind="primary"]:hover {
    background-color: #056B3A !important;
    box-shadow: 0 4px 12px rgba(7,157,86,0.30) !important;
}
.stButton > button[kind="secondary"] {
    background-color: #FFFFFF !important;
    color: #079D56 !important;
    border: 1.5px solid #079D56 !important;
}
.stButton > button[kind="secondary"]:hover {
    background-color: #F0FBF5 !important;
}
/* Botões destrutivos — verde escuro no lugar do vermelho */
.stButton > button[kind="primary"][data-destructive="true"],
button[data-testid*="excluir"], button[data-testid*="delete"] {
    background-color: #056B3A !important;
    color: #FFFFFF !important;
}
.stDownloadButton > button {
    background-color: #FF8C23 !important;
    color: #FFFFFF !important;
    border: none !important;
    font-weight: 700 !important;
    border-radius: 8px !important;
}
.stDownloadButton > button:hover {
    background-color: #e07a1a !important;
}

/* ── DIVIDER ── */
hr { border-color: #E2E8F0 !important; }

/* ── CAPTION / SMALL TEXT ── */
[data-testid="stCaptionContainer"] p,
small, .caption { color: #6B7280 !important; }

/* ── LABELS ── */
label, [data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] span {
    color: #374151 !important;
    font-weight: 600 !important;
    font-size: .85rem !important;
}

/* ── MARKDOWN GERAL ── */
p, li, span, td, th { color: #2D2D2D !important; }
h1, h2, h3, h4 { color: #056B3A !important; font-weight: 800 !important; }

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #F4F6F8; }
::-webkit-scrollbar-thumb { background: #CBD5E0; border-radius: 3px; }

/* ── LAYOUT ── */
.block-container {
    max-width: 1380px !important;
    padding-top: 1.5rem !important;
    padding-bottom: 3rem !important;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# BANCO DE DADOS — NEON
# ============================================================
TIMEZONE_BRASILIA = ZoneInfo("America/Sao_Paulo")

def get_conn():
    return psycopg2.connect(st.secrets["NEON_DATABASE_URL"])

def init_db():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id            SERIAL PRIMARY KEY,
                    email         TEXT UNIQUE NOT NULL,
                    nome          TEXT NOT NULL,
                    senha_hash    TEXT NOT NULL,
                    perfil        TEXT NOT NULL CHECK (perfil IN ('VENDEDOR','ADMINISTRADOR')),
                    ativo         BOOLEAN DEFAULT TRUE,
                    criado_em     TIMESTAMPTZ DEFAULT NOW(),
                    atualizado_em TIMESTAMPTZ DEFAULT NOW()
                );
                CREATE TABLE IF NOT EXISTS historico_simulacoes (
                    id                         SERIAL PRIMARY KEY,
                    data_hora                  TIMESTAMPTZ DEFAULT NOW(),
                    vendedor_email             TEXT,
                    empreendimento             TEXT,
                    unidade                    TEXT,
                    cpf_proponente             TEXT,
                    idade                      INT,
                    faixa_etaria               TEXT,
                    estado_civil               TEXT,
                    score_proponente           TEXT,
                    renda_proponente           NUMERIC,
                    qtd_clientes_adicionais    INT,
                    renda_clientes_adicionais  NUMERIC,
                    renda_total                NUMERIC,
                    ato_urba                   NUMERIC,
                    percentual_ato             NUMERIC,
                    faixa_ato                  TEXT,
                    valor_proposta             NUMERIC,
                    primeira_mensal            NUMERIC,
                    percentual_comprometimento NUMERIC,
                    faixa_comprometimento      TEXT,
                    score_final                INT,
                    classificacao              TEXT
                );
            """)
        conn.commit()

try:
    init_db()
except Exception as e:
    st.error(f"Erro ao conectar ao banco: {e}")
    st.stop()

def autenticar_usuario(email, senha):
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT nome, senha_hash, perfil, ativo FROM usuarios WHERE email=%s",
                    (email.strip().lower(),)
                )
                row = cur.fetchone()
        if not row:
            return None
        nome, senha_hash, perfil, ativo = row
        if not ativo:
            return None
        if bcrypt.checkpw(senha.encode(), senha_hash.encode()):
            return {"nome": nome, "email": email.strip().lower(), "perfil": perfil}
        return None
    except Exception:
        return None

def listar_usuarios():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, nome, email, perfil, ativo, criado_em FROM usuarios ORDER BY criado_em DESC")
            cols = [d[0] for d in cur.description]
            rows = cur.fetchall()
    return pd.DataFrame(rows, columns=cols)

def criar_usuario(nome, email, senha, perfil):
    h = bcrypt.hashpw(senha.encode(), bcrypt.gensalt(12)).decode()
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO usuarios (nome, email, senha_hash, perfil) VALUES (%s,%s,%s,%s)",
                (nome.strip(), email.strip().lower(), h, perfil)
            )
        conn.commit()

def toggle_usuario(uid, ativo):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE usuarios SET ativo=%s, atualizado_em=NOW() WHERE id=%s", (ativo, uid))
        conn.commit()

def redefinir_senha(uid, nova_senha):
    h = bcrypt.hashpw(nova_senha.encode(), bcrypt.gensalt(12)).decode()
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE usuarios SET senha_hash=%s, atualizado_em=NOW() WHERE id=%s", (h, uid))
        conn.commit()

def salvar_simulacao(d, vendedor_email):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO historico_simulacoes
                (vendedor_email,empreendimento,unidade,cpf_proponente,idade,faixa_etaria,
                 estado_civil,score_proponente,renda_proponente,qtd_clientes_adicionais,
                 renda_clientes_adicionais,renda_total,ato_urba,percentual_ato,faixa_ato,
                 valor_proposta,primeira_mensal,percentual_comprometimento,faixa_comprometimento,
                 score_final,classificacao)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                vendedor_email,
                d.get("empreendimento",""), d.get("unidade",""), d.get("cpf_proponente",""),
                d.get("idade"), d.get("faixa_idade",""), d.get("estado_civil",""),
                d.get("score_proponente",""), d.get("renda_proponente",0),
                d.get("qtd_clientes_adicionais",0), d.get("renda_adicionais",0),
                d.get("renda_total",0), d.get("ato_urba",0), d.get("perc_ato",0),
                d.get("faixa_at",""), d.get("valor_proposta",0), d.get("primeira_mensal",0),
                d.get("perc_comp",0), d.get("faixa_comp",""),
                d.get("score_final",0), d.get("classificacao",""),
            ))
        conn.commit()

def carregar_historico():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM historico_simulacoes ORDER BY data_hora DESC")
            cols = [d[0] for d in cur.description]
            rows = cur.fetchall()
    return pd.DataFrame(rows, columns=cols)

# ============================================================
# LOGIN
# ============================================================
if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None

if not st.session_state.usuario_logado:
    st.markdown("""
    <style>
    [data-testid="stApp"],
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    .main, .block-container {
        background-color: #F4F6F8 !important;
    }
    .login-wrapper {
        display: flex;
        justify-content: center;
        align-items: flex-start;
        padding-top: 6vh;
    }
    .login-card {
        background: #FFFFFF;
        border-radius: 20px;
        box-shadow: 0 4px 32px rgba(0,0,0,0.10);
        padding: 40px 36px 32px;
        max-width: 420px;
        width: 100%;
        text-align: center;
    }
    .login-logo {
        font-size: 2.2rem;
        font-weight: 900;
        color: #079D56;
        letter-spacing: -0.03em;
        margin-bottom: 2px;
    }
    .login-logo span { color: #FF8C23; }
    .login-sub {
        font-size: .78rem;
        font-weight: 700;
        letter-spacing: .12em;
        text-transform: uppercase;
        color: #6B7280;
        margin-bottom: 20px;
    }
    .login-title {
        font-size: 1.35rem;
        font-weight: 800;
        color: #1A1A1A;
        margin-bottom: 4px;
    }
    .login-desc {
        font-size: .9rem;
        color: #6B7280;
        margin-bottom: 24px;
    }
    </style>
    """, unsafe_allow_html=True)

    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        st.markdown("""
        <div class="login-card">
            <div class="login-logo">Urba</div>
            <div class="login-sub">Simulador de Score de Vendas</div>
            <div class="login-title">Bem-vindo de volta</div>
            <div class="login-desc">Acesse com suas credenciais para continuar.</div>
        </div>
        """, unsafe_allow_html=True)

        email_in = st.text_input("E-MAIL", placeholder="nome@urba.com.br", key="login_email")
        senha_in = st.text_input("SENHA", type="password", key="login_senha")

        if st.button("ENTRAR", type="primary", use_container_width=True, key="btn_entrar"):
            if not email_in or not senha_in:
                st.error("Preencha e-mail e senha.")
            else:
                usuario = autenticar_usuario(email_in, senha_in)
                if usuario:
                    st.session_state.usuario_logado = usuario
                    st.session_state.pagina_atual = "Simulador"
                    st.rerun()
                else:
                    st.error("E-mail ou senha incorretos, ou usuário inativo.")
    st.stop()

# ============================================================
# USUÁRIO LOGADO
# ============================================================
usuario = st.session_state.usuario_logado
vendedor_email = usuario["email"]
vendedor_nome  = usuario["nome"]
perfil_atual   = usuario["perfil"]
eh_admin       = perfil_atual == "ADMINISTRADOR"

# ── SIDEBAR ──
with st.sidebar:
    st.markdown(f"""
    <div style="padding:8px 0 16px;">
        <div style="font-size:1.7rem;font-weight:900;color:#FFFFFF;letter-spacing:-0.03em;margin-bottom:2px;">Urba</div>
        <div style="font-size:.68rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;
                    color:rgba(255,255,255,.75);margin-bottom:18px;">Simulador de Score</div>
        <hr style="border-color:rgba(255,255,255,.25);margin-bottom:16px;">
        <div style="font-size:.95rem;font-weight:700;color:#FFFFFF;">{vendedor_nome}</div>
        <div style="font-size:.78rem;color:rgba(255,255,255,.80);margin-bottom:6px;">{vendedor_email}</div>
        <div style="display:inline-block;background:rgba(255,255,255,.20);border-radius:20px;
                    padding:2px 10px;font-size:.72rem;font-weight:700;color:#FFFFFF;letter-spacing:.06em;">
            {perfil_atual}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    if st.button("Sair", use_container_width=True, key="btn_sair"):
        st.session_state.usuario_logado = None
        st.session_state.pop("resultado", None)
        st.rerun()

# ── HEADER ──
st.markdown("""
<div style="background:linear-gradient(135deg,#056B3A,#079D56);border-radius:16px;
            padding:24px 28px;margin-bottom:20px;display:flex;align-items:center;gap:18px;">
    <div>
        <div style="font-size:.72rem;font-weight:700;letter-spacing:.14em;text-transform:uppercase;
                    color:rgba(255,255,255,.80);margin-bottom:4px;">Projeto Defensores do Contrato</div>
        <div style="font-size:clamp(1.5rem,3vw,2.1rem);font-weight:900;color:#FFFFFF;
                    letter-spacing:-0.02em;line-height:1.1;">Simulador de Score de Vendas</div>
        <div style="color:rgba(255,255,255,.82);font-size:.92rem;margin-top:6px;">
            Avaliação estruturada do risco de distrato no momento da venda.</div>
    </div>
    <div style="margin-left:auto;">
        <span style="background:rgba(255,255,255,.18);border-radius:20px;padding:4px 14px;
                     font-size:.78rem;font-weight:700;color:#FFFFFF;">V16.5</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── NAVEGAÇÃO ──
if "pagina_atual" not in st.session_state:
    st.session_state.pagina_atual = "Simulador"

nav_cols = st.columns([1, 1, 1, 4])
with nav_cols[0]:
    if st.button("Simulador",
                 type="primary" if st.session_state.pagina_atual == "Simulador" else "secondary",
                 use_container_width=True, key="nav_sim"):
        st.session_state.pagina_atual = "Simulador"; st.rerun()
with nav_cols[1]:
    if eh_admin:
        if st.button("Histórico",
                     type="primary" if st.session_state.pagina_atual == "Histórico" else "secondary",
                     use_container_width=True, key="nav_hist"):
            st.session_state.pagina_atual = "Histórico"; st.rerun()
    else:
        st.button("Histórico", disabled=True, use_container_width=True, key="nav_hist_off")
with nav_cols[2]:
    if eh_admin:
        if st.button("Usuários",
                     type="primary" if st.session_state.pagina_atual == "Usuários" else "secondary",
                     use_container_width=True, key="nav_usr"):
            st.session_state.pagina_atual = "Usuários"; st.rerun()
    else:
        st.button("Usuários", disabled=True, use_container_width=True, key="nav_usr_off")

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
                    if chave in {"empreendimento","empreendimentos","nome empreendimento"}:
                        mapa[col] = "Empreendimento"
                    elif chave in {"unidade","unidades","quadra lote","quadra/lote"}:
                        mapa[col] = "Unidade"
                df = df.rename(columns=mapa)
                if {"Empreendimento","Unidade"}.issubset(df.columns):
                    df = df[["Empreendimento","Unidade"]].copy()
                    def texto_limpo(v):
                        if pd.isna(v): return ""
                        if isinstance(v, float) and v.is_integer(): return str(int(v))
                        return str(v).strip()
                    for col in ["Empreendimento","Unidade"]:
                        df[col] = df[col].apply(texto_limpo)
                    df = df[(df["Empreendimento"]!="")&(df["Unidade"]!="")].drop_duplicates()
                    if not df.empty:
                        return df, arquivo, aba, None
        except Exception as e:
            erros.append(f"{arquivo}: {e}")
    detalhe = " | ".join(erros) if erros else "Nenhum Excel compatível encontrado."
    return pd.DataFrame(columns=["Empreendimento","Unidade"]), None, None, detalhe

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
NOTAS_SCORE          = {"A - B": 5, "C - D": 3, "E - F": 1}
NOTAS_ATO            = {"ACIMA DE 4%": 5, "3% A 4%": 4, "2% A 3%": 3, "1% A 2%": 2, "ABAIXO DE 1%": 1}
NOTAS_COMPROMETIMENTO= {"ATÉ 10%": 5, "10% A 20%": 4, "20% A 30%": 3, "30% A 50%": 2, "50% A 100%": 1, "ACIMA DE 100%": 1}
NOTAS_IDADE          = {"60+ ANOS": 5, "45 A 60 ANOS": 4, "35 A 45 ANOS": 3, "ATÉ 25 ANOS": 2, "25 A 35 ANOS": 1}
NOTAS_ESTADO_CIVIL   = {"CASADO(A)": 3, "DIVORCIADO(A)": 2, "SOLTEIRO(A)": 1}

SCORE_MAX       = sum([5*PESOS["score_credito"], 5*PESOS["ato"], 5*PESOS["comprometimento_renda"],
                       5*PESOS["idade"], 3*PESOS["estado_civil"]])
LIMITE_BAIXO    = 54
LIMITE_MODERADO = 33

# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================
def brl(v):
    return f"R$ {v:,.2f}".replace(",","X").replace(".",",").replace("X",".")

def normalizar(t):
    t = t or ""
    t = unicodedata.normalize("NFKD", t)
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = t.upper().replace("\xa0"," ")
    t = re.sub(r"[ \t]+"," ", t)
    return t

def moeda_para_float(valor):
    if valor is None: return 0.0
    s = str(valor).strip().replace("R$","").replace(" ","")
    if not s: return 0.0
    if "," in s:
        s = s.replace(".","").replace(",",".")
    else:
        if s.count(".") > 1:
            s = s.replace(".","")
    try:
        return max(0.0, float(s))
    except:
        return 0.0

def float_para_moeda_input(v):
    return f"{float(v or 0):,.2f}".replace(",","X").replace(".",",").replace("X",".")

def _normalizar_campo_moeda(chave):
    st.session_state[chave] = float_para_moeda_input(moeda_para_float(st.session_state.get(chave,"0,00")))

def campo_moeda(label, chave, valor_inicial=0.0, ajuda=None):
    if chave not in st.session_state:
        st.session_state[chave] = float_para_moeda_input(valor_inicial)
    texto = st.text_input(label, key=chave, on_change=_normalizar_campo_moeda,
                          args=(chave,), help=ajuda, placeholder="0,00")
    return moeda_para_float(texto)

def calcular_idade(nascimento):
    hoje = datetime.now(TIMEZONE_BRASILIA).date()
    return hoje.year - nascimento.year - ((hoje.month, hoje.day) < (nascimento.month, nascimento.day))

def faixa_etaria(idade):
    if idade <= 25: return "ATÉ 25 ANOS"
    if idade <= 35: return "25 A 35 ANOS"
    if idade <= 45: return "35 A 45 ANOS"
    if idade <= 60: return "45 A 60 ANOS"
    return "60+ ANOS"

def faixa_comprometimento(p):
    if p <= 10:  return "ATÉ 10%"
    if p <= 20:  return "10% A 20%"
    if p <= 30:  return "20% A 30%"
    if p <= 50:  return "30% A 50%"
    if p <= 100: return "50% A 100%"
    return "ACIMA DE 100%"

def faixa_ato(p):
    if p > 4:  return "ACIMA DE 4%"
    if p >= 3: return "3% A 4%"
    if p >= 2: return "2% A 3%"
    if p >= 1: return "1% A 2%"
    return "ABAIXO DE 1%"

def classificar(score):
    if score >= LIMITE_BAIXO:    return "BAIXO RISCO",    "green"
    if score >= LIMITE_MODERADO: return "RISCO MODERADO", "orange"
    return "ALTO RISCO", "red"

def calcular_score_total(notas):
    return sum(notas[k] * PESOS[k] for k in PESOS)

def mapear_score(letra):
    letra = (letra or "").upper()
    if letra in ("A","B"): return "A - B"
    if letra in ("C","D"): return "C - D"
    if letra in ("E","F"): return "E - F"
    return None

def formatar_cpf(digitos):
    return f"{digitos[:3]}.{digitos[3:6]}.{digitos[6:9]}-{digitos[9:]}"

# ============================================================
# EXTRAÇÃO DO SPC (preservada do V15.0)
# ============================================================
def extrair_dados_spc(pdf_file):
    pdf_file.seek(0)
    paginas, tabelas = [], []
    with pdfplumber.open(pdf_file) as pdf:
        for numero, page in enumerate(pdf.pages, start=1):
            texto = page.extract_text(x_tolerance=2, y_tolerance=3) or ""
            paginas.append(texto)
            try:
                for tabela in page.extract_tables() or []:
                    tabelas.append((numero, tabela))
            except: pass

    texto_completo = "\n".join(paginas)
    texto_norm = normalizar(texto_completo)

    score_letra = None
    for padrao in [r"\bRISCO\s+DE\s+CREDITO\s*[:\-]?\s*([A-F])\b",
                   r"\bRISCO\s+DE\s+CREDITO\b[\s\S]{0,80}?\b([A-F])\b"]:
        m = re.search(padrao, texto_norm, flags=re.I)
        if m: score_letra = m.group(1).upper(); break
    score_faixa = mapear_score(score_letra)

    renda = None
    for _, tabela in tabelas:
        for linha in tabela:
            celulas = [normalizar(str(x)) if x is not None else "" for x in linha]
            linha_norm = " | ".join(celulas)
            if "RENDA PRESUMIDA" in linha_norm and "SPC BRASIL" in linha_norm:
                candidatos = re.findall(r"(?:R\$\s*)?(\d{1,3}(?:\.\d{3})*,\d{2})", linha_norm)
                if candidatos:
                    renda = moeda_para_float(candidatos[-1])
                    if renda and renda > 0: break
        if renda and renda > 0: break

    if not renda:
        for padrao in [
            r"RENDA\s+PRESUMIDA\s*-\s*SPC\s+BRASIL[\s\S]{0,160}?(?:R\$\s*)?(\d{1,3}(?:\.\d{3})*,\d{2})",
            r"RENDA\s+PRESUMIDA\s*:?\s*(?:_+\s*)?(?:R\$\s*)?(\d{1,3}(?:\.\d{3})*,\d{2})",
        ]:
            m = re.search(padrao, texto_norm, flags=re.I)
            if m:
                renda = moeda_para_float(m.group(1))
                if renda and renda > 0: break

    data_nascimento = None
    for padrao in [
        r"(?:DATA\s+DE\s+NASCIMENTO|DT\.?\s*NASCIMENTO|NASCIMENTO)\s*[:\-]?\s*(\d{1,2}/\d{1,2}/\d{4})",
        r"(?:DATA\s+DE\s+NASCIMENTO|DT\.?\s*NASCIMENTO|NASCIMENTO)[\s\S]{0,50}?(\d{1,2}/\d{1,2}/\d{4})",
    ]:
        m = re.search(padrao, texto_norm, flags=re.I)
        if m:
            try:
                data_nascimento = datetime.strptime(m.group(1), "%d/%m/%Y").date()
                hoje_spc = datetime.now(TIMEZONE_BRASILIA).date()
                if data_nascimento > hoje_spc or data_nascimento.year < 1900:
                    data_nascimento = None
                else: break
            except: data_nascimento = None

    cpf = None
    for padrao in [
        r"\bCPF\s*[:\-]?\s*(\d{3}[\.\-]?\d{3}[\.\-]?\d{3}[\.\-\/]?\d{2})\b",
        r"\b(\d{3}\.\d{3}\.\d{3}[-\/]\d{2})\b",
    ]:
        m = re.search(padrao, texto_norm, flags=re.I)
        if m:
            digitos = re.sub(r"\D","", m.group(1))
            if len(digitos) == 11:
                cpf = formatar_cpf(digitos); break

    return {
        "score_letra": score_letra, "score_faixa": score_faixa,
        "renda_presumida": renda, "data_nascimento": data_nascimento,
        "cpf": cpf, "texto_extraido": texto_completo,
    }

# ============================================================
# CENÁRIOS (preservado do V15.0)
# ============================================================
def montar_cenarios(score_atual, notas, renda_total, mensal, ato, valor_proposta):
    cenarios = []
    for pct_meta, faixa_meta in [(1.00,"1% A 2%"),(2.00,"2% A 3%"),(3.00,"3% A 4%"),(4.01,"ACIMA DE 4%")]:
        nova_nota = NOTAS_ATO[faixa_meta]
        ganho = (nova_nota - notas["ato"]) * PESOS["ato"]
        ato_alvo = valor_proposta * pct_meta / 100
        adicional = max(0, ato_alvo - ato)
        if ganho > 0 and adicional > 0:
            cenarios.append({"Variável":"Ato",
                "Ajuste": f"Aumentar o ato para aprox. {brl(ato_alvo)} (+{brl(adicional)}; ≈{pct_meta:.2f}% da proposta)",
                "Ganho": ganho, "NovoScore": score_atual + ganho})
    for limite, faixa_meta in [(50,"30% A 50%"),(30,"20% A 30%"),(20,"10% A 20%"),(10,"ATÉ 10%")]:
        nova_nota = NOTAS_COMPROMETIMENTO[faixa_meta]
        ganho = (nova_nota - notas["comprometimento_renda"]) * PESOS["comprometimento_renda"]
        if ganho > 0:
            renda_alvo = mensal / (limite/100) if limite > 0 else 0
            mensal_alvo = renda_total * limite / 100
            cenarios.append({"Variável":"Renda / Mensal",
                "Ajuste": f"Para comprometimento ≤{limite}%: renda total ≈{brl(renda_alvo)} OU mensal ≤{brl(mensal_alvo)}",
                "Ganho": ganho, "NovoScore": score_atual + ganho})
    for c in cenarios:
        c["NovaClassificacao"] = ("🟢 BAIXO RISCO" if c["NovoScore"]>=LIMITE_BAIXO
                                  else "🟡 RISCO MODERADO" if c["NovoScore"]>=LIMITE_MODERADO
                                  else "🔴 ALTO RISCO")
        c["AtingeModerado"] = c["NovoScore"] >= LIMITE_MODERADO
        c["AtingeBaixo"]    = c["NovoScore"] >= LIMITE_BAIXO
    return sorted(cenarios, key=lambda c: (not c["AtingeModerado"], not c["AtingeBaixo"], -c["Ganho"]))

# ============================================================
# ESTADO DA SESSÃO
# ============================================================
if "resultado" not in st.session_state:
    st.session_state.resultado = None

# ============================================================
# PÁGINA: SIMULADOR
# ============================================================
if st.session_state.pagina_atual == "Simulador":

    st.markdown("<h2 style='color:#056B3A;font-size:1.25rem;font-weight:800;margin-bottom:4px;'>Dados da Simulação</h2>", unsafe_allow_html=True)
    st.caption("Preencha as informações abaixo para calcular o score de risco da venda.")

    bloco_emp, bloco_cliente, bloco_proposta, bloco_renda = st.columns(4, gap="large")

    # ── EMPREENDIMENTO ──
    with bloco_emp:
        st.markdown("<div style='color:#079D56;font-weight:800;font-size:1rem;margin-bottom:8px;'>Empreendimento</div>", unsafe_allow_html=True)
        if cadastro.empty:
            st.error("Cadastro de empreendimentos não carregado.")
            if erro_cadastro:
                with st.expander("Detalhes técnicos"):
                    st.code(erro_cadastro)

        empreendimentos = sorted(
            cadastro["Empreendimento"].dropna().astype(str).str.strip()
            .loc[lambda x: x.ne("")].unique().tolist()
        )
        empreendimento = st.selectbox("Empreendimento *", [""]+empreendimentos, index=0, key="empreendimento_v14")

        if empreendimento:
            cad_emp = cadastro[cadastro["Empreendimento"].astype(str).str.strip()==str(empreendimento).strip()].copy()
        else:
            cad_emp = cadastro.iloc[0:0].copy()

        unidades = sorted(
            cad_emp["Unidade"].dropna().astype(str).str.strip().loc[lambda x: x.ne("")].unique().tolist(),
            key=lambda x: x.zfill(30),
        )
        def rotulo_unidade(v):
            if not v: return "Selecione a unidade"
            texto = str(v).strip()
            emp = str(empreendimento or "").strip()
            if emp and texto.upper().startswith(emp.upper()):
                curto = texto[len(emp):].lstrip(" -–—")
                if curto: return curto
            return texto

        unidade = st.selectbox("Unidade *", [""]+unidades, index=0,
                               disabled=not bool(empreendimento),
                               key="unidade_v12", format_func=rotulo_unidade)
        if unidade:
            st.caption(f"📍 {rotulo_unidade(unidade)}")

    # ── PERFIL DO CLIENTE ──
    with bloco_cliente:
        st.markdown("<div style='color:#079D56;font-weight:800;font-size:1rem;margin-bottom:8px;'>Perfil do Cliente</div>", unsafe_allow_html=True)
        st.caption("Anexe o relatório do SPC do cliente proponente.")

        pdf_prop = st.file_uploader("SPC do Proponente *", type=["pdf"], key="pdf_prop_v14")

        dados_spc_prop = None
        score_proponente = None
        renda_proponente = 0.0
        nascimento = None
        idade = None
        faixa_idade = None
        cpf_proponente = ""

        if pdf_prop:
            try:
                with st.spinner("Lendo SPC do proponente..."):
                    dados_spc_prop = extrair_dados_spc(pdf_prop)
                score_proponente = dados_spc_prop.get("score_faixa")
                renda_proponente = float(dados_spc_prop.get("renda_presumida") or 0)
                nascimento       = dados_spc_prop.get("data_nascimento")
                idade            = calcular_idade(nascimento) if nascimento else None
                faixa_idade      = faixa_etaria(idade) if idade is not None else None
                cpf_proponente   = dados_spc_prop.get("cpf") or ""

                st.markdown("<div style='font-weight:700;font-size:.85rem;color:#056B3A;margin:10px 0 6px;'>Dados identificados no SPC</div>", unsafe_allow_html=True)
                with st.container(border=True):
                    st.caption("CPF do Proponente")
                    st.markdown(f"**{cpf_proponente}**" if cpf_proponente else "*Não localizado*")
                    if nascimento:
                        st.caption("Data de Nascimento")
                        st.markdown(f"**{nascimento.strftime('%d/%m/%Y')}** — {idade} anos — {faixa_idade}")
                    else:
                        st.warning("Data de nascimento não localizada.")
                    st.caption("Score")
                    st.markdown(f"**{dados_spc_prop.get('score_letra') or '—'} → {score_proponente}**" if score_proponente else "*Não localizado*")
                    st.caption("Renda Presumida")
                    st.markdown(f"**{brl(renda_proponente)}**" if renda_proponente > 0 else "*Não localizada*")
            except Exception as e:
                st.error(f"Falha na leitura do SPC: {e}")

        if pdf_prop and not cpf_proponente:
            cpf_proponente = st.text_input("CPF — preenchimento manual", placeholder="000.000.000-00", key="cpf_prop_manual_v15").strip()
        if pdf_prop and not score_proponente:
            score_proponente = st.selectbox("Score SPC — preenchimento manual", ["","A - B","C - D","E - F"], key="score_prop_manual_v14")
        if pdf_prop and renda_proponente <= 0:
            renda_proponente = campo_moeda("Renda Presumida — manual (R$)", "renda_prop_manual_v14")

        estado_civil = st.selectbox("Estado Civil *", ["","SOLTEIRO(A)","DIVORCIADO(A)","CASADO(A)"], index=0, key="estado_civil_v14")

    # ── DADOS DA PROPOSTA ──
    with bloco_proposta:
        st.markdown("<div style='color:#079D56;font-weight:800;font-size:1rem;margin-bottom:8px;'>Dados da Proposta</div>", unsafe_allow_html=True)
        ato_urba       = campo_moeda("Ato Urba (R$) *",                    "ato_urba_v14")
        valor_proposta = campo_moeda("Valor da Proposta / Líquido CV (R$) *","valor_proposta_v14")
        primeira_mensal= campo_moeda("Valor da 1ª Mensal (R$) *",           "primeira_mensal_v14")

    # ── COMPOSIÇÃO DE RENDA ──
    with bloco_renda:
        st.markdown("<div style='color:#079D56;font-weight:800;font-size:1rem;margin-bottom:8px;'>Composição de Renda</div>", unsafe_allow_html=True)
        st.caption("Use somente quando houver cliente adicional compondo renda.")

        qtd_adicionais = st.number_input("Clientes adicionais", min_value=0, max_value=4,
                                         value=0, step=1, key="qtd_adicionais_v14")
        rendas_adicionais = []
        for i in range(int(qtd_adicionais)):
            numero = i + 2
            with st.expander(f"Cliente {numero}", expanded=True):
                # CSS extra para garantir legibilidade dentro do expander
                st.markdown("""
                <style>
                details > div * { color: #2D2D2D !important; background-color: #FFFFFF !important; }
                details > div label, details > div p, details > div span { color: #374151 !important; }
                details > div [data-baseweb="input"] > div,
                details > div [data-baseweb="base-input"] > div {
                    background-color: #FFFFFF !important;
                    border: 1.5px solid #CBD5E0 !important;
                }
                details > div input { background-color: #FFFFFF !important; color: #2D2D2D !important; }
                details > div [data-testid="stFileUploaderDropzone"] {
                    background-color: #F0FBF5 !important;
                    border: 2px dashed #079D56 !important;
                    color: #2D2D2D !important;
                }
                details > div [data-testid="stFileUploaderDropzone"] * { color: #2D2D2D !important; }
                details > div [data-testid="stFileUploaderDropzone"] button {
                    background-color: #079D56 !important; color: #FFFFFF !important;
                }
                </style>
                """, unsafe_allow_html=True)

                pdf_add  = st.file_uploader(f"SPC — Cliente {numero}", type=["pdf"], key=f"pdf_cliente_v14_{numero}")
                renda_add = 0.0
                if pdf_add:
                    try:
                        d_add = extrair_dados_spc(pdf_add)
                        renda_add = float(d_add["renda_presumida"] or 0)
                        if renda_add:
                            st.success(f"Renda identificada: {brl(renda_add)}")
                        else:
                            st.warning("Renda não localizada no SPC.")
                    except Exception as e:
                        st.error(f"Falha na leitura: {e}")
                if pdf_add and renda_add <= 0:
                    renda_add = campo_moeda(f"Renda manual — Cliente {numero} (R$)", f"renda_manual_v14_{numero}")
                rendas_adicionais.append(renda_add)

    # ── CÁLCULOS INSTANTÂNEOS ──
    score_analise = score_proponente
    renda_total   = renda_proponente + sum(rendas_adicionais)
    perc_ato      = ato_urba / valor_proposta * 100 if valor_proposta > 0 else 0
    perc_comp     = primeira_mensal / renda_total * 100 if renda_total > 0 else 0
    faixa_at      = faixa_ato(perc_ato)
    faixa_comp    = faixa_comprometimento(perc_comp)

    st.divider()
    i1, i2, i3, i4 = st.columns(4)
    i1.metric("% do Ato",       f"{perc_ato:.2f}%",  faixa_at)
    i2.metric("Comprometimento", f"{perc_comp:.2f}%", faixa_comp)
    i3.metric("Renda Total",     brl(renda_total))
    i4.metric("Faixa Etária",    faixa_idade or "—")

    # ── VALIDAÇÃO ──
    faltando = []
    if not empreendimento:    faltando.append("Empreendimento")
    if not unidade:           faltando.append("Unidade")
    if not nascimento:        faltando.append("Data de Nascimento")
    if not estado_civil:      faltando.append("Estado Civil")
    if not pdf_prop:          faltando.append("SPC do Proponente")
    if not score_analise:     faltando.append("Score SPC do Proponente")
    if renda_total <= 0:      faltando.append("Renda Presumida")
    if valor_proposta <= 0:   faltando.append("Valor da Proposta")
    if primeira_mensal <= 0:  faltando.append("1ª Mensal")

    if faltando:
        st.info(f"Preencha/valide: **{', '.join(faltando)}**")

    _, botao_calc = st.columns([3,1])
    with botao_calc:
        calcular = st.button("CALCULAR SIMULAÇÃO", type="primary",
                             use_container_width=True, disabled=bool(faltando), key="calcular_v14")

    if calcular:
        notas = {
            "score_credito":         NOTAS_SCORE[score_analise],
            "ato":                   NOTAS_ATO[faixa_at],
            "comprometimento_renda": NOTAS_COMPROMETIMENTO[faixa_comp],
            "idade":                 NOTAS_IDADE[faixa_idade],
            "estado_civil":          NOTAS_ESTADO_CIVIL[estado_civil],
        }
        score_final = calcular_score_total(notas)
        classificacao, cor = classificar(score_final)
        st.session_state.resultado = {
            "notas": notas, "score_final": score_final,
            "classificacao": classificacao, "cor": cor,
            "empreendimento": empreendimento, "unidade": unidade,
            "cpf_proponente": cpf_proponente, "idade": idade,
            "faixa_idade": faixa_idade, "estado_civil": estado_civil,
            "score_proponente": score_analise,
            "renda_proponente": renda_proponente,
            "qtd_clientes_adicionais": int(qtd_adicionais),
            "renda_adicionais": sum(rendas_adicionais),
            "renda_total": renda_total, "ato_urba": ato_urba,
            "valor_proposta": valor_proposta, "perc_ato": perc_ato,
            "faixa_at": faixa_at, "primeira_mensal": primeira_mensal,
            "perc_comp": perc_comp, "faixa_comp": faixa_comp,
        }

    # ── RESULTADO ──
    if st.session_state.resultado:
        d = st.session_state.resultado
        st.divider()
        st.markdown("<h2 style='color:#056B3A;font-size:1.2rem;font-weight:800;margin-bottom:4px;'>Resumo da Simulação</h2>", unsafe_allow_html=True)

        def resumo_card(coluna, titulo, valor):
            with coluna:
                with st.container(border=True):
                    st.caption(titulo)
                    st.markdown(f"**{valor if valor not in (None,'') else '—'}**")

        q1,q2,q3,q4 = st.columns(4)
        resumo_card(q1,"Empreendimento", d.get("empreendimento"))
        unidade_resumo = d.get("unidade","")
        emp_resumo = d.get("empreendimento","")
        if emp_resumo and unidade_resumo.upper().startswith(emp_resumo.upper()):
            unidade_resumo = unidade_resumo[len(emp_resumo):].lstrip(" -–—") or unidade_resumo
        resumo_card(q2,"Unidade", unidade_resumo)
        resumo_card(q3,"CPF do Proponente", d.get("cpf_proponente"))
        resumo_card(q4,"Renda Total", brl(d.get("renda_total",0)))

        p1,p2,p3,p4 = st.columns(4)
        resumo_card(p1,"Faixa Etária",       d.get("faixa_idade"))
        resumo_card(p2,"Estado Civil",        d.get("estado_civil"))
        resumo_card(p3,"Score do Proponente", d.get("score_proponente"))
        resumo_card(p4,"Ato Urba",            brl(d.get("ato_urba",0)))

        c1,c2,c3,c4 = st.columns(4)
        resumo_card(c1,"% do Ato",         f"{d.get('perc_ato',0):.2f}%")
        resumo_card(c2,"1ª Mensal",         brl(d.get("primeira_mensal",0)))
        resumo_card(c3,"Comprometimento",   f"{d.get('perc_comp',0):.2f}%")
        resumo_card(c4,"Valor da Proposta", brl(d.get("valor_proposta",0)))

        # ── AVALIAÇÃO DE RISCO ──
        st.markdown("<h2 style='color:#056B3A;font-size:1.2rem;font-weight:800;margin:16px 0 8px;'>Avaliação de Risco</h2>", unsafe_allow_html=True)
        r1, r2 = st.columns([1,2])
        with r1:
            score_final = d["score_final"]
            cor = d["cor"]
            classificacao = d["classificacao"]
            bg  = {"green":"#E8F5EE","orange":"#FFF4E5","red":"#FFF0F0"}[cor]
            brd = {"green":"#079D56","orange":"#FF8C23","red":"#C0392B"}[cor]
            txt = {"green":"#056B3A","orange":"#B45309","red":"#922B21"}[cor]
            icone = {"green":"✅","orange":"⚠️","red":"❌"}[cor]
            st.markdown(f"""
            <div style="background:{bg};border:2px solid {brd};border-radius:14px;
                        padding:20px 22px;text-align:center;">
                <div style="font-size:2rem;margin-bottom:6px;">{icone}</div>
                <div style="font-size:2.4rem;font-weight:900;color:{txt};">{score_final}</div>
                <div style="font-size:.82rem;color:#6B7280;margin-bottom:6px;">de {SCORE_MAX} pontos</div>
                <div style="font-size:1rem;font-weight:800;color:{txt};">{classificacao}</div>
            </div>
            """, unsafe_allow_html=True)

        with r2:
            labels = {
                "score_credito":"Score de Crédito","ato":"% do Ato",
                "comprometimento_renda":"Comprometimento de Renda",
                "idade":"Faixa Etária","estado_civil":"Estado Civil",
            }
            max_nota = {"score_credito":5,"ato":5,"comprometimento_renda":5,"idade":5,"estado_civil":3}
            detalhes = []
            for var, peso in PESOS.items():
                nota = d["notas"][var]
                detalhes.append({"Variável":labels[var],"Nota":f"{nota}/{max_nota[var]}",
                                  "Peso":peso,"Pontos":nota*peso,"Máximo":max_nota[var]*peso})
            st.dataframe(pd.DataFrame(detalhes), use_container_width=True, hide_index=True,
                column_config={
                    "Variável": st.column_config.TextColumn("Variável", width="medium"),
                    "Nota":     st.column_config.TextColumn("Nota",     width="small"),
                    "Peso":     st.column_config.NumberColumn("Peso",   width="small"),
                    "Pontos":   st.column_config.NumberColumn("Pontos", width="small"),
                    "Máximo":   st.column_config.NumberColumn("Máximo", width="small"),
                })

        # ── ESTRATÉGIAS ──
        if d["classificacao"] != "BAIXO RISCO":
            st.divider()
            st.markdown("<h2 style='color:#056B3A;font-size:1.2rem;font-weight:800;margin-bottom:8px;'>Estratégias de Estruturação da Venda</h2>", unsafe_allow_html=True)
            a1,b1 = st.columns(2)
            a1.metric("Pontos para Risco Moderado", f"+{max(0,LIMITE_MODERADO-d['score_final'])}")
            b1.metric("Pontos para Baixo Risco",    f"+{max(0,LIMITE_BAIXO-d['score_final'])}")
            cenarios = montar_cenarios(d["score_final"],d["notas"],d["renda_total"],
                                       d["primeira_mensal"],d["ato_urba"],d["valor_proposta"])
            if cenarios:
                df_c = pd.DataFrame(cenarios)
                df_c["Ganho"]     = df_c["Ganho"].map(lambda x: f"+{x}")
                df_c["NovoScore"] = df_c["NovoScore"].map(str)
                st.dataframe(
                    df_c[["Variável","Ajuste","Ganho","NovoScore","NovaClassificacao"]].head(12)
                    .rename(columns={"NovoScore":"Novo Score","NovaClassificacao":"Nova Classificação"}),
                    use_container_width=True, hide_index=True,
                    column_config={
                        "Variável":          st.column_config.TextColumn("Variável",          width="medium"),
                        "Ajuste":            st.column_config.TextColumn("Ajuste",            width="large"),
                        "Ganho":             st.column_config.TextColumn("Ganho",             width="small"),
                        "Novo Score":        st.column_config.TextColumn("Novo Score",        width="small"),
                        "Nova Classificação":st.column_config.TextColumn("Nova Classificação",width="medium"),
                    })
                st.caption("Sugestões são simulações contrafactuais. Não alteram dados cadastrais do cliente.")

        # ── SALVAR ──
        st.divider()
        st.markdown("<h2 style='color:#056B3A;font-size:1.2rem;font-weight:800;margin-bottom:4px;'>Salvar Simulação</h2>", unsafe_allow_html=True)
        st.caption("Registra esta simulação no histórico administrativo.")
        if st.button("CONFIRMAR E SALVAR NO HISTÓRICO", type="primary", key="salvar_historico_v8"):
            try:
                salvar_simulacao(d, vendedor_email)
                st.success("Simulação salva com sucesso no histórico.")
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")

# ============================================================
# PÁGINA: HISTÓRICO
# ============================================================
elif st.session_state.pagina_atual == "Histórico" and eh_admin:
    st.markdown("<h2 style='color:#056B3A;font-size:1.3rem;font-weight:800;margin-bottom:8px;'>Histórico de Simulações</h2>", unsafe_allow_html=True)

    try:
        hist = carregar_historico()
    except Exception as e:
        st.error(f"Erro ao carregar histórico: {e}")
        hist = pd.DataFrame()

    if hist.empty:
        st.info("Nenhuma simulação registrada ainda.")
    else:
        c1,c2,c3 = st.columns(3)
        with c1:
            vendedores = sorted(x for x in hist.get("vendedor_email", pd.Series()).fillna("").astype(str).unique() if x)
            filtro_v = st.selectbox("Vendedor", ["TODOS"]+vendedores, key="filtro_vendedor_v11")
        with c2:
            emps = sorted(x for x in hist.get("empreendimento", pd.Series()).fillna("").astype(str).unique() if x)
            filtro_e = st.selectbox("Empreendimento", ["TODOS"]+emps, key="filtro_emp_v11")
        with c3:
            classes = sorted(x for x in hist.get("classificacao", pd.Series()).fillna("").astype(str).unique() if x)
            filtro_c = st.selectbox("Classificação", ["TODAS"]+classes, key="filtro_class_v11")

        exib = hist.copy()
        if filtro_v != "TODOS": exib = exib[exib["vendedor_email"].astype(str)==filtro_v]
        if filtro_e != "TODOS": exib = exib[exib["empreendimento"].astype(str)==filtro_e]
        if filtro_c != "TODAS": exib = exib[exib["classificacao"].astype(str)==filtro_c]

        k1,k2,k3,k4 = st.columns(4)
        k1.metric("Simulações",  len(exib))
        k2.metric("Baixo Risco", int(exib["classificacao"].astype(str).str.contains("BAIXO",   na=False).sum()))
        k3.metric("Moderado",    int(exib["classificacao"].astype(str).str.contains("MODERADO", na=False).sum()))
        k4.metric("Alto Risco",  int(exib["classificacao"].astype(str).str.contains("ALTO",     na=False).sum()))

        st.dataframe(exib, use_container_width=True, hide_index=True)

        st.download_button(
            "BAIXAR HISTÓRICO (CSV)",
            exib.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"historico_score_{datetime.now(TIMEZONE_BRASILIA).strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv", use_container_width=True,
        )

        st.divider()
        with st.expander("Excluir histórico", expanded=False):
            st.warning("Esta ação exclui TODOS os registros do banco e não pode ser desfeita.")
            confirmar = st.checkbox("Confirmo que desejo excluir TODO o histórico", key="confirmar_exclusao_v8")
            if st.button("EXCLUIR TODO O HISTÓRICO", type="primary",
                         disabled=not confirmar, key="excluir_historico_v8"):
                try:
                    with get_conn() as conn:
                        with conn.cursor() as cur:
                            cur.execute("DELETE FROM historico_simulacoes")
                        conn.commit()
                    st.success("Histórico excluído com sucesso.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao excluir: {e}")

# ============================================================
# PÁGINA: USUÁRIOS
# ============================================================
elif st.session_state.pagina_atual == "Usuários" and eh_admin:
    st.markdown("<h2 style='color:#056B3A;font-size:1.3rem;font-weight:800;margin-bottom:8px;'>Gestão de Usuários</h2>", unsafe_allow_html=True)

    with st.expander("Adicionar novo usuário", expanded=False):
        n1,n2 = st.columns(2)
        with n1:
            novo_nome  = st.text_input("Nome completo *", key="novo_nome")
            novo_email = st.text_input("E-mail *",        key="novo_email")
        with n2:
            novo_perfil = st.selectbox("Perfil *", ["VENDEDOR","ADMINISTRADOR"], key="novo_perfil")
            nova_senha  = st.text_input("Senha *", type="password", key="nova_senha")
        if st.button("CRIAR USUÁRIO", type="primary", key="btn_criar_usuario"):
            if not all([novo_nome, novo_email, nova_senha]):
                st.error("Preencha todos os campos.")
            else:
                try:
                    criar_usuario(novo_nome, novo_email, nova_senha, novo_perfil)
                    st.success(f"Usuário {novo_email} criado com sucesso.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao criar usuário: {e}")

    st.divider()
    try:
        df_usuarios = listar_usuarios()
    except Exception as e:
        st.error(f"Erro ao listar usuários: {e}")
        df_usuarios = pd.DataFrame()

    if not df_usuarios.empty:
        for _, row in df_usuarios.iterrows():
            with st.container(border=True):
                u1,u2,u3,u4,u5 = st.columns([2,2,1,1,1])
                u1.markdown(f"**{row['nome']}**")
                u2.caption(row['email'])
                u3.markdown(f"`{row['perfil']}`")
                status = "Ativo" if row['ativo'] else "Inativo"
                u4.markdown(f"{'🟢' if row['ativo'] else '🔴'} {status}")
                with u5:
                    if row['ativo']:
                        if st.button("Desativar", key=f"desativar_{row['id']}"):
                            toggle_usuario(row['id'], False); st.rerun()
                    else:
                        if st.button("Ativar", key=f"ativar_{row['id']}"):
                            toggle_usuario(row['id'], True); st.rerun()

            with st.expander(f"Redefinir senha — {row['email']}", expanded=False):
                nova = st.text_input("Nova senha", type="password", key=f"nova_senha_{row['id']}")
                if st.button("SALVAR NOVA SENHA", key=f"salvar_senha_{row['id']}"):
                    if nova:
                        redefinir_senha(row['id'], nova)
                        st.success("Senha redefinida com sucesso.")
                    else:
                        st.error("Digite a nova senha.")

# ── RODAPÉ ──
st.markdown("""
<div style="text-align:center;padding:24px 0 8px;margin-top:32px;
            border-top:1px solid #E2E8F0;">
    <span style="color:#079D56;font-weight:800;font-size:.9rem;">Urba</span>
    <span style="color:#9CA3AF;font-size:.82rem;"> • Simulador de Score de Vendas V16.5 • Projeto Defensores do Contrato</span>
</div>
""", unsafe_allow_html=True)
