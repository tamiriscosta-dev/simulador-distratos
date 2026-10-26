# app.py — V16.2
# Simulador de Score de Vendas — Projeto Defensores do Contrato
# V16.2: Identidade visual Urba (verde #1E9E3E + laranja #F47920), fundo branco, design profissional

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
import streamlit as st
import pdfplumber

st.set_page_config(
    page_title="Simulador de Score — Urba",
    page_icon="🏠",
    layout="wide",
)

# ============================================================
# PALETA URBA
# ============================================================
VERDE       = "#1E9E3E"
VERDE_DARK  = "#166B2A"
VERDE_LIGHT = "#E8F5EC"
LARANJA     = "#F47920"
LARANJA_LIGHT = "#FEF0E6"
BRANCO      = "#FFFFFF"
CINZA_BG    = "#F7F8FA"
CINZA_BORDA = "#E2E6EA"
CINZA_TEXTO = "#4A5568"
PRETO       = "#1A1A1A"

# ============================================================
# CSS GLOBAL — IDENTIDADE URBA
# ============================================================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* Reset geral */
html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif !important;
    background-color: {BRANCO} !important;
    color: {PRETO} !important;
}}

.stApp {{
    background-color: {BRANCO} !important;
}}

.block-container {{
    max-width: 1380px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    background-color: {BRANCO} !important;
}}

/* ---- SIDEBAR ---- */
[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, {VERDE_DARK} 0%, {VERDE} 100%) !important;
    border-right: none !important;
}}
[data-testid="stSidebar"] * {{
    color: {BRANCO} !important;
}}
[data-testid="stSidebar"] .stButton > button {{
    background: rgba(255,255,255,0.15) !important;
    color: {BRANCO} !important;
    border: 1px solid rgba(255,255,255,0.3) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: all 0.2s !important;
}}
[data-testid="stSidebar"] .stButton > button:hover {{
    background: rgba(255,255,255,0.25) !important;
}}
[data-testid="stSidebar"] hr {{
    border-color: rgba(255,255,255,0.2) !important;
}}
[data-testid="stSidebar"] input {{
    background: rgba(255,255,255,0.12) !important;
    color: {BRANCO} !important;
    border: 1px solid rgba(255,255,255,0.3) !important;
    border-radius: 8px !important;
}}
[data-testid="stSidebar"] input::placeholder {{
    color: rgba(255,255,255,0.5) !important;
}}
[data-testid="stSidebar"] label {{
    color: rgba(255,255,255,0.85) !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
}}
[data-testid="stSidebar"] .stSuccess {{
    background: rgba(255,255,255,0.15) !important;
    border: 1px solid rgba(255,255,255,0.3) !important;
    color: {BRANCO} !important;
    border-radius: 8px !important;
}}

/* ---- HERO HEADER ---- */
.urba-hero {{
    background: linear-gradient(135deg, {VERDE} 0%, {VERDE_DARK} 100%);
    border-radius: 16px;
    padding: 28px 32px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    gap: 20px;
    box-shadow: 0 4px 20px rgba(30,158,62,0.25);
}}
.urba-hero-icon {{
    font-size: 3rem;
    line-height: 1;
}}
.urba-hero-kicker {{
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.75);
    margin-bottom: 4px;
}}
.urba-hero-title {{
    font-size: clamp(1.6rem, 2.8vw, 2.2rem);
    font-weight: 800;
    color: {BRANCO};
    line-height: 1.1;
    margin: 0;
}}
.urba-hero-sub {{
    color: rgba(255,255,255,0.8);
    font-size: 0.92rem;
    margin-top: 6px;
}}
.urba-hero-badge {{
    margin-left: auto;
    background: rgba(255,255,255,0.15);
    border: 1px solid rgba(255,255,255,0.3);
    border-radius: 50px;
    padding: 6px 16px;
    font-size: 0.78rem;
    font-weight: 700;
    color: {BRANCO};
    white-space: nowrap;
}}

/* ---- NAVEGAÇÃO ---- */
.urba-nav {{
    display: flex;
    gap: 8px;
    margin-bottom: 20px;
    border-bottom: 2px solid {CINZA_BORDA};
    padding-bottom: 0;
}}
.urba-nav-btn {{
    padding: 10px 22px;
    border-radius: 8px 8px 0 0;
    font-weight: 700;
    font-size: 0.88rem;
    cursor: pointer;
    border: none;
    transition: all 0.2s;
}}

/* ---- BOTÕES ---- */
.stButton > button {{
    border-radius: 8px !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
    min-height: 42px !important;
    transition: all 0.2s !important;
}}
.stButton > button[kind="primary"] {{
    background: {VERDE} !important;
    color: {BRANCO} !important;
    border: none !important;
    box-shadow: 0 2px 8px rgba(30,158,62,0.3) !important;
}}
.stButton > button[kind="primary"]:hover {{
    background: {VERDE_DARK} !important;
    box-shadow: 0 4px 14px rgba(30,158,62,0.4) !important;
    transform: translateY(-1px) !important;
}}
.stButton > button[kind="secondary"] {{
    background: {BRANCO} !important;
    color: {VERDE} !important;
    border: 2px solid {VERDE} !important;
}}
.stButton > button[kind="secondary"]:hover {{
    background: {VERDE_LIGHT} !important;
}}
.stDownloadButton > button {{
    background: {LARANJA} !important;
    color: {BRANCO} !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    box-shadow: 0 2px 8px rgba(244,121,32,0.3) !important;
}}
.stDownloadButton > button:hover {{
    background: #D4661A !important;
    transform: translateY(-1px) !important;
}}

/* ---- INPUTS ---- */
[data-baseweb="input"] > div,
[data-baseweb="select"] > div,
[data-baseweb="textarea"] > div {{
    border-radius: 8px !important;
    border-color: {CINZA_BORDA} !important;
    background: {BRANCO} !important;
}}
[data-baseweb="input"] > div:focus-within,
[data-baseweb="select"] > div:focus-within {{
    border-color: {VERDE} !important;
    box-shadow: 0 0 0 3px rgba(30,158,62,0.12) !important;
}}
label[data-testid="stWidgetLabel"] p {{
    font-weight: 600 !important;
    font-size: 0.83rem !important;
    color: {CINZA_TEXTO} !important;
    text-transform: uppercase !important;
    letter-spacing: 0.04em !important;
}}

/* ---- CARDS DE SEÇÃO ---- */
.urba-section-header {{
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 16px;
    padding-bottom: 10px;
    border-bottom: 2px solid {VERDE_LIGHT};
}}
.urba-section-icon {{
    width: 36px;
    height: 36px;
    background: {VERDE_LIGHT};
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
}}
.urba-section-title {{
    font-size: 0.95rem;
    font-weight: 800;
    color: {VERDE_DARK};
    text-transform: uppercase;
    letter-spacing: 0.05em;
}}

/* ---- RESUMO CARDS ---- */
.urba-card {{
    background: {BRANCO};
    border: 1.5px solid {CINZA_BORDA};
    border-radius: 12px;
    padding: 14px 16px;
    transition: box-shadow 0.2s;
}}
.urba-card:hover {{
    box-shadow: 0 4px 16px rgba(0,0,0,0.08);
}}
.urba-card-label {{
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: {CINZA_TEXTO};
    margin-bottom: 6px;
}}
.urba-card-value {{
    font-size: 1.05rem;
    font-weight: 700;
    color: {PRETO};
    word-break: break-word;
}}

/* ---- SCORE BADGE ---- */
.urba-score-box {{
    background: linear-gradient(135deg, {VERDE} 0%, {VERDE_DARK} 100%);
    border-radius: 16px;
    padding: 28px 24px;
    text-align: center;
    box-shadow: 0 6px 24px rgba(30,158,62,0.3);
}}
.urba-score-number {{
    font-size: 4rem;
    font-weight: 800;
    color: {BRANCO};
    line-height: 1;
}}
.urba-score-label {{
    font-size: 0.82rem;
    color: rgba(255,255,255,0.8);
    font-weight: 600;
    margin-top: 6px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}}
.urba-score-class {{
    margin-top: 14px;
    padding: 8px 20px;
    border-radius: 50px;
    font-weight: 800;
    font-size: 0.95rem;
    display: inline-block;
}}
.urba-score-green  {{ background: rgba(255,255,255,0.25); color: {BRANCO}; }}
.urba-score-orange {{ background: rgba(244,121,32,0.85);  color: {BRANCO}; }}
.urba-score-red    {{ background: rgba(220,38,38,0.85);   color: {BRANCO}; }}

/* ---- MÉTRICAS ---- */
div[data-testid="stMetric"] {{
    background: {CINZA_BG};
    border: 1.5px solid {CINZA_BORDA};
    border-radius: 12px;
    padding: 14px 16px;
}}
div[data-testid="stMetricLabel"] p {{
    font-size: 0.75rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    color: {CINZA_TEXTO} !important;
}}
div[data-testid="stMetricValue"] {{
    font-size: 1.3rem !important;
    font-weight: 800 !important;
    color: {PRETO} !important;
}}
div[data-testid="stMetricDelta"] {{
    font-size: 0.78rem !important;
    font-weight: 600 !important;
}}

/* ---- ALERTAS ---- */
.stSuccess {{
    background: {VERDE_LIGHT} !important;
    border-left: 4px solid {VERDE} !important;
    border-radius: 8px !important;
    color: {VERDE_DARK} !important;
}}
.stWarning {{
    background: {LARANJA_LIGHT} !important;
    border-left: 4px solid {LARANJA} !important;
    border-radius: 8px !important;
}}
.stError {{
    background: #FEE2E2 !important;
    border-left: 4px solid #DC2626 !important;
    border-radius: 8px !important;
}}
.stInfo {{
    background: #EFF6FF !important;
    border-left: 4px solid #3B82F6 !important;
    border-radius: 8px !important;
}}

/* ---- DATAFRAME ---- */
[data-testid="stDataFrame"] {{
    border: 1.5px solid {CINZA_BORDA} !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}}

/* ---- DIVIDER ---- */
hr {{
    border-color: {CINZA_BORDA} !important;
    margin: 20px 0 !important;
}}

/* ---- FILE UPLOADER ---- */
[data-testid="stFileUploader"] {{
    border: 2px dashed {CINZA_BORDA} !important;
    border-radius: 12px !important;
    background: {CINZA_BG} !important;
    transition: border-color 0.2s !important;
}}
[data-testid="stFileUploader"]:hover {{
    border-color: {VERDE} !important;
}}

/* ---- EXPANDER ---- */
[data-testid="stExpander"] {{
    border: 1.5px solid {CINZA_BORDA} !important;
    border-radius: 12px !important;
    background: {CINZA_BG} !important;
}}

/* ---- CONTAINER BORDER ---- */
[data-testid="stVerticalBlockBorderWrapper"] {{
    border-radius: 12px !important;
    border: 1.5px solid {CINZA_BORDA} !important;
    background: {CINZA_BG} !important;
}}

/* ---- SIDEBAR LOGO ---- */
.urba-sidebar-logo {{
    text-align: center;
    padding: 20px 0 16px;
    border-bottom: 1px solid rgba(255,255,255,0.2);
    margin-bottom: 16px;
}}
.urba-sidebar-logo-text {{
    font-size: 1.8rem;
    font-weight: 800;
    color: {BRANCO};
    letter-spacing: -0.02em;
}}
.urba-sidebar-logo-sub {{
    font-size: 0.7rem;
    color: rgba(255,255,255,0.65);
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}}

/* ---- LOGIN CARD ---- */
.urba-login-wrap {{
    min-height: 80vh;
    display: flex;
    align-items: center;
    justify-content: center;
}}
.urba-login-card {{
    background: {BRANCO};
    border: 1.5px solid {CINZA_BORDA};
    border-radius: 20px;
    padding: 40px 36px 32px;
    box-shadow: 0 8px 40px rgba(0,0,0,0.10);
    max-width: 420px;
    width: 100%;
}}
.urba-login-logo {{
    text-align: center;
    margin-bottom: 28px;
}}
.urba-login-logo-icon {{
    font-size: 3rem;
    display: block;
    margin-bottom: 8px;
}}
.urba-login-logo-name {{
    font-size: 2rem;
    font-weight: 800;
    color: {VERDE};
    letter-spacing: -0.02em;
}}
.urba-login-logo-tag {{
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: {CINZA_TEXTO};
    margin-top: 2px;
}}
.urba-login-title {{
    font-size: 1.25rem;
    font-weight: 800;
    color: {PRETO};
    margin-bottom: 4px;
}}
.urba-login-sub {{
    font-size: 0.88rem;
    color: {CINZA_TEXTO};
    margin-bottom: 24px;
}}
.urba-divider-text {{
    text-align: center;
    color: {CINZA_TEXTO};
    font-size: 0.78rem;
    font-weight: 600;
    margin: 16px 0;
    position: relative;
}}

/* ---- NOTA DE SEÇÃO ---- */
.urba-section-note {{
    color: {CINZA_TEXTO};
    font-size: 0.88rem;
    margin-top: -8px;
    margin-bottom: 16px;
}}

/* ---- TAG DE STATUS ---- */
.urba-tag {{
    display: inline-block;
    padding: 3px 10px;
    border-radius: 50px;
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}}
.urba-tag-green  {{ background: {VERDE_LIGHT};   color: {VERDE_DARK}; }}
.urba-tag-orange {{ background: {LARANJA_LIGHT}; color: #92400E; }}
.urba-tag-red    {{ background: #FEE2E2;          color: #991B1B; }}

/* ---- NÚMERO INPUT ---- */
[data-testid="stNumberInput"] input {{
    border-radius: 8px !important;
}}

/* ---- CHECKBOX ---- */
[data-testid="stCheckbox"] span {{
    color: {CINZA_TEXTO} !important;
}}
</style>
""", unsafe_allow_html=True)


# ============================================================
# BANCO DE DADOS — NEON
# ============================================================
def get_conn():
    url = st.secrets["NEON_DATABASE_URL"]
    return psycopg2.connect(url, sslmode="require")


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
                CREATE INDEX IF NOT EXISTS idx_hist_vendedor  ON historico_simulacoes(vendedor_email);
                CREATE INDEX IF NOT EXISTS idx_hist_data      ON historico_simulacoes(data_hora DESC);
                CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email);
            """)
            conn.commit()


try:
    init_db()
except Exception as e:
    st.error(f"Erro ao conectar ao banco: {e}")
    st.stop()


# ============================================================
# AUTENTICAÇÃO
# ============================================================
def verificar_login(email: str, senha: str):
    try:
        with get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM usuarios WHERE email = %s AND ativo = TRUE",
                    (email.lower().strip(),)
                )
                user = cur.fetchone()
        if not user:
            return None
        if bcrypt.checkpw(senha.encode(), user["senha_hash"].encode()):
            return dict(user)
        return None
    except Exception:
        return None


def listar_usuarios():
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT id, nome, email, perfil, ativo, criado_em FROM usuarios ORDER BY criado_em DESC")
            return [dict(r) for r in cur.fetchall()]


def criar_usuario(nome, email, senha, perfil):
    h = bcrypt.hashpw(senha.encode(), bcrypt.gensalt(12)).decode()
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO usuarios (nome, email, senha_hash, perfil) VALUES (%s, %s, %s, %s)",
                (nome, email.lower().strip(), h, perfil)
            )
            conn.commit()


def toggle_usuario(uid, ativo):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE usuarios SET ativo = %s, atualizado_em = NOW() WHERE id = %s", (ativo, uid))
            conn.commit()


def alterar_senha(uid, nova_senha):
    h = bcrypt.hashpw(nova_senha.encode(), bcrypt.gensalt(12)).decode()
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE usuarios SET senha_hash = %s, atualizado_em = NOW() WHERE id = %s", (h, uid))
            conn.commit()


def salvar_simulacao(d, vendedor_email):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO historico_simulacoes (
                    vendedor_email, empreendimento, unidade, cpf_proponente,
                    idade, faixa_etaria, estado_civil, score_proponente,
                    renda_proponente, qtd_clientes_adicionais, renda_clientes_adicionais,
                    renda_total, ato_urba, percentual_ato, faixa_ato,
                    valor_proposta, primeira_mensal, percentual_comprometimento,
                    faixa_comprometimento, score_final, classificacao
                ) VALUES (
                    %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
                )
            """, (
                vendedor_email,
                d.get("empreendimento",""), d.get("unidade",""), d.get("cpf_proponente",""),
                d.get("idade"), d.get("faixa_idade",""), d.get("estado_civil",""),
                d.get("score_proponente",""), d.get("renda_proponente",0),
                d.get("qtd_clientes_adicionais",0), d.get("renda_adicionais",0),
                d.get("renda_total",0), d.get("ato_urba",0), d.get("perc_ato",0),
                d.get("faixa_at",""), d.get("valor_proposta",0), d.get("primeira_mensal",0),
                d.get("perc_comp",0), d.get("faixa_comp",""),
                d.get("score_final",0), d.get("classificacao","")
            ))
            conn.commit()


def carregar_historico():
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM historico_simulacoes ORDER BY data_hora DESC")
            rows = cur.fetchall()
    return pd.DataFrame([dict(r) for r in rows]) if rows else pd.DataFrame()


# ============================================================
# SESSION STATE
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
    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        st.markdown(f"""
        <div class="urba-login-card">
            <div class="urba-login-logo">
                <span class="urba-login-logo-icon">🏠</span>
                <div class="urba-login-logo-name">Urba</div>
                <div class="urba-login-logo-tag">Simulador de Score de Vendas</div>
            </div>
            <div class="urba-login-title">Bem-vindo de volta</div>
            <div class="urba-login-sub">Acesse com suas credenciais para continuar.</div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("form_login"):
            email_in = st.text_input("E-mail", placeholder="nome@urba.com.br")
            senha_in = st.text_input("Senha", type="password", placeholder="••••••••")
            entrar   = st.form_submit_button("ENTRAR", use_container_width=True, type="primary")

        if entrar:
            if not email_in or not senha_in:
                st.error("Preencha e-mail e senha.")
            else:
                user = verificar_login(email_in, senha_in)
                if user:
                    st.session_state.logado  = True
                    st.session_state.usuario = user
                    st.rerun()
                else:
                    st.error("E-mail ou senha incorretos, ou usuário inativo.")
    st.stop()


# ============================================================
# SIDEBAR
# ============================================================
usuario = st.session_state.usuario
with st.sidebar:
    st.markdown(f"""
    <div class="urba-sidebar-logo">
        <div class="urba-sidebar-logo-text">🏠 Urba</div>
        <div class="urba-sidebar-logo-sub">Simulador de Score</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"**{usuario['nome']}**")
    st.caption(usuario['email'])
    perfil_tag = "🔐 Administrador" if usuario['perfil'] == 'ADMINISTRADOR' else "👤 Vendedor"
    st.caption(perfil_tag)

    st.divider()

    if st.button("🔄 Trocar usuário", use_container_width=True):
        st.session_state.logado   = False
        st.session_state.usuario  = None
        st.session_state.resultado = None
        st.session_state.pagina   = "Simulador"
        st.rerun()


# ============================================================
# HERO HEADER
# ============================================================
st.markdown(f"""
<div class="urba-hero">
    <div class="urba-hero-icon">🏠</div>
    <div>
        <div class="urba-hero-kicker">Projeto Defensores do Contrato</div>
        <div class="urba-hero-title">Simulador de Score de Vendas</div>
        <div class="urba-hero-sub">Avaliação estruturada do risco de distrato no momento da venda.</div>
    </div>
    <div class="urba-hero-badge">V16.2</div>
</div>
""", unsafe_allow_html=True)


# ============================================================
# NAVEGAÇÃO
# ============================================================
nav_cols = st.columns([1, 1, 1, 4] if usuario['perfil'] == 'ADMINISTRADOR' else [1, 4])

with nav_cols[0]:
    if st.button(
        "▣  Simulador",
        type="primary" if st.session_state.pagina == "Simulador" else "secondary",
        use_container_width=True,
        key="nav_sim",
    ):
        st.session_state.pagina = "Simulador"
        st.rerun()

if usuario['perfil'] == 'ADMINISTRADOR':
    with nav_cols[1]:
        if st.button(
            "📂  Histórico",
            type="primary" if st.session_state.pagina == "Histórico" else "secondary",
            use_container_width=True,
            key="nav_hist",
        ):
            st.session_state.pagina = "Histórico"
            st.rerun()
    with nav_cols[2]:
        if st.button(
            "👥  Usuários",
            type="primary" if st.session_state.pagina == "Usuários" else "secondary",
            use_container_width=True,
            key="nav_users",
        ):
            st.session_state.pagina = "Usuários"
            st.rerun()

st.divider()


# ============================================================
# TIMEZONE
# ============================================================
TIMEZONE_BRASILIA = ZoneInfo("America/Sao_Paulo")


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
    "ATÉ 10%":       5,
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
    "ATÉ 25 ANOS":  2,
    "25 A 35 ANOS": 1,
}

NOTAS_ESTADO_CIVIL = {
    "CASADO(A)":     3,
    "DIVORCIADO(A)": 2,
    "SOLTEIRO(A)":   1,
}

SCORE_MAX       = sum([5*5, 5*5, 5*4, 5*1, 3*1])  # 78
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
        return None
    s = str(valor).strip()
    s = re.sub(r"[^\d,.\-]", "", s)
    if not s:
        return None
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
    if idade <= 25: return "ATÉ 25 ANOS"
    if idade <= 35: return "25 A 35 ANOS"
    if idade <= 45: return "35 A 45 ANOS"
    if idade <= 60: return "45 A 60 ANOS"
    return "60+ ANOS"


def faixa_comprometimento(perc):
    if perc <= 10:  return "ATÉ 10%"
    if perc <= 20:  return "10% A 20%"
    if perc <= 30:  return "20% A 30%"
    if perc <= 50:  return "30% A 50%"
    if perc <= 100: return "50% A 100%"
    return "ACIMA DE 100%"


def faixa_ato(perc):
    if perc > 4:  return "ACIMA DE 4%"
    if perc >= 3: return "3% A 4%"
    if perc >= 2: return "2% A 3%"
    if perc >= 1: return "1% A 2%"
    return "ABAIXO DE 1%"


def classificar(score):
    if score >= LIMITE_BAIXO:    return "🟢 BAIXO RISCO",    "green"
    if score >= LIMITE_MODERADO: return "🟡 RISCO MODERADO", "orange"
    return "🔴 ALTO RISCO", "red"


def calcular_score_total(notas):
    return sum(notas[k] * PESOS[k] for k in PESOS)


def mapear_score(letra):
    letra = (letra or "").upper()
    if letra in ("A", "B"): return "A - B"
    if letra in ("C", "D"): return "C - D"
    if letra in ("E", "F"): return "E - F"
    return None


def formatar_cpf(digitos):
    return f"{digitos[:3]}.{digitos[3:6]}.{digitos[6:9]}-{digitos[9:]}"


def float_para_moeda_input(valor):
    return f"{float(valor or 0):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _normalizar_campo_moeda(chave):
    st.session_state[chave] = float_para_moeda_input(
        moeda_para_float(st.session_state.get(chave, "0,00")) or 0
    )


def campo_moeda(label, chave, valor_inicial=0.0, ajuda=None):
    if chave not in st.session_state:
        st.session_state[chave] = float_para_moeda_input(valor_inicial)
    texto = st.text_input(
        label, key=chave,
        on_change=_normalizar_campo_moeda, args=(chave,),
        help=ajuda, placeholder="0,00",
    )
    return moeda_para_float(texto) or 0.0


# ============================================================
# EXTRAÇÃO DO SPC
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
        m = re.search(padrao, texto_norm, flags=re.I)
        if m:
            try:
                data_nascimento = datetime.strptime(m.group(1), "%d/%m/%Y").date()
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
        m = re.search(padrao, texto_norm, flags=re.I)
        if m:
            digitos = re.sub(r"\D", "", m.group(1))
            if len(digitos) == 11:
                cpf = formatar_cpf(digitos)
                break

    return {
        "score_letra":    score_letra,
        "score_faixa":    score_faixa,
        "renda_presumida": renda,
        "data_nascimento": data_nascimento,
        "cpf":            cpf,
        "texto_extraido": texto_completo,
    }


# ============================================================
# CENÁRIOS
# ============================================================
def renda_minima_para_comprometimento(mensal, limite_pct):
    if mensal <= 0 or limite_pct <= 0: return 0
    return mensal / (limite_pct / 100)


def mensal_maxima_para_comprometimento(renda, limite_pct):
    return renda * limite_pct / 100


def ato_minimo_para_percentual(valor_proposta, pct):
    return valor_proposta * pct / 100


def montar_cenarios(score_atual, notas, renda_total, mensal, ato, valor_proposta):
    cenarios = []

    for pct_meta, faixa_meta in [
        (1.00, "1% A 2%"), (2.00, "2% A 3%"),
        (3.00, "3% A 4%"), (4.01, "ACIMA DE 4%"),
    ]:
        nova_nota = NOTAS_ATO[faixa_meta]
        ganho = (nova_nota - notas["ato"]) * PESOS["ato"]
        ato_alvo = ato_minimo_para_percentual(valor_proposta, pct_meta)
        adicional = max(0, ato_alvo - ato)
        if ganho > 0 and adicional > 0:
            cenarios.append({
                "Variável": "Ato",
                "Ajuste": f"Aumentar o ato para aprox. {brl(ato_alvo)} (+{brl(adicional)}; ≈ {pct_meta:.2f}% da proposta)",
                "Ganho": ganho,
                "NovoScore": score_atual + ganho,
            })

    for limite, faixa_meta in [
        (50, "30% A 50%"), (30, "20% A 30%"),
        (20, "10% A 20%"), (10, "ATÉ 10%"),
    ]:
        nova_nota = NOTAS_COMPROMETIMENTO[faixa_meta]
        ganho = (nova_nota - notas["comprometimento_renda"]) * PESOS["comprometimento_renda"]
        if ganho > 0:
            renda_alvo  = renda_minima_para_comprometimento(mensal, limite)
            mensal_alvo = mensal_maxima_para_comprometimento(renda_total, limite)
            cenarios.append({
                "Variável": "Renda / Mensal",
                "Ajuste": f"Para comprometimento ≤ {limite}%: renda total ≈ {brl(renda_alvo)} OU mensal ≤ {brl(mensal_alvo)}",
                "Ganho": ganho,
                "NovoScore": score_atual + ganho,
            })

    for c in cenarios:
        c["NovaClassificacao"] = classificar(c["NovoScore"])[0]
        c["AtingeModerado"]    = c["NovoScore"] >= LIMITE_MODERADO
        c["AtingeBaixo"]       = c["NovoScore"] >= LIMITE_BAIXO

    return sorted(cenarios, key=lambda c: (not c["AtingeModerado"], not c["AtingeBaixo"], -c["Ganho"]))


# ============================================================
# HELPER: CARD DE RESUMO
# ============================================================
def resumo_card(coluna, titulo, valor):
    with coluna:
        st.markdown(f"""
        <div class="urba-card">
            <div class="urba-card-label">{titulo}</div>
            <div class="urba-card-value">{valor if valor not in (None, '', 0) else '—'}</div>
        </div>
        """, unsafe_allow_html=True)


# ============================================================
# PÁGINA: SIMULADOR
# ============================================================
if st.session_state.pagina == "Simulador":

    st.markdown(f"""
    <div class="urba-section-header">
        <div class="urba-section-icon">📋</div>
        <div class="urba-section-title">Dados da Simulação</div>
    </div>
    <div class="urba-section-note">Preencha as informações abaixo para calcular o score de risco da venda.</div>
    """, unsafe_allow_html=True)

    bloco_emp, bloco_cliente, bloco_proposta, bloco_renda = st.columns(4, gap="large")

    # ---- EMPREENDIMENTO ----
    with bloco_emp:
        st.markdown(f"""
        <div class="urba-section-header">
            <div class="urba-section-icon">🏢</div>
            <div class="urba-section-title">Empreendimento</div>
        </div>
        """, unsafe_allow_html=True)

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
            "Empreendimento *", [""] + empreendimentos,
            index=0, key="empreendimento_v16",
        )

        cad_emp = cadastro[
            cadastro["Empreendimento"].astype(str).str.strip() == str(empreendimento).strip()
        ].copy() if empreendimento else cadastro.iloc[0:0].copy()

        unidades = sorted(
            cad_emp["Unidade"].dropna().astype(str).str.strip()
            .loc[lambda x: x.ne("")].unique().tolist(),
            key=lambda x: x.zfill(30),
        )

        def rotulo_unidade(valor):
            if not valor: return "Selecione a unidade"
            texto = str(valor).strip()
            emp   = str(empreendimento or "").strip()
            if emp and texto.upper().startswith(emp.upper()):
                curto = texto[len(emp):].lstrip(" -–—")
                if curto: return curto
            return texto

        unidade = st.selectbox(
            "Unidade *", [""] + unidades,
            index=0, disabled=not bool(empreendimento),
            key="unidade_v16", format_func=rotulo_unidade,
        )
        if unidade:
            st.caption(f"📍 **{rotulo_unidade(unidade)}**")

    # ---- PROPONENTE ----
    with bloco_cliente:
        st.markdown(f"""
        <div class="urba-section-header">
            <div class="urba-section-icon">👤</div>
            <div class="urba-section-title">Perfil do Cliente</div>
        </div>
        """, unsafe_allow_html=True)
        st.caption("Anexe o relatório SPC do cliente proponente.")

        pdf_prop = st.file_uploader("SPC do Proponente *", type=["pdf"], key="pdf_prop_v16")

        dados_spc_prop = None
        score_proponente = None
        renda_proponente = 0.0
        nascimento = None
        idade = None
        faixa_idade = None
        cpf_proponente = ""

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

                st.markdown("##### Dados identificados no SPC")
                with st.container(border=True):
                    st.caption("CPF do Proponente")
                    if cpf_proponente:
                        st.markdown(f"**{cpf_proponente}**")
                    else:
                        st.warning("CPF não localizado.")

                    if nascimento:
                        st.caption("Data de Nascimento")
                        st.markdown(f"**{nascimento.strftime('%d/%m/%Y')}**")
                        st.caption(f"Idade: **{idade} anos** • Faixa: **{faixa_idade}**")
                    else:
                        st.warning("Data de nascimento não localizada.")

                    st.caption("Score")
                    if score_proponente:
                        st.markdown(f"**{dados_spc_prop.get('score_letra') or '—'} → {score_proponente}**")
                    else:
                        st.warning("Score não localizado.")

                    st.caption("Renda Presumida")
                    if renda_proponente > 0:
                        st.markdown(f"**{brl(renda_proponente)}**")
                    else:
                        st.warning("Renda não localizada.")

            except Exception as e:
                st.error(f"Falha na leitura do SPC: {e}")

        if pdf_prop and not cpf_proponente:
            cpf_proponente = st.text_input(
                "CPF — preenchimento manual", placeholder="000.000.000-00",
                key="cpf_prop_manual_v16",
            ).strip()

        if pdf_prop and not score_proponente:
            score_proponente = st.selectbox(
                "Score SPC — manual", ["", "A - B", "C - D", "E - F"],
                key="score_prop_manual_v16",
            )

        if pdf_prop and renda_proponente <= 0:
            renda_proponente = campo_moeda(
                "Renda Presumida — manual (R$)", "renda_prop_manual_v16",
            )

        estado_civil = st.selectbox(
            "Estado Civil *",
            ["", "SOLTEIRO(A)", "DIVORCIADO(A)", "CASADO(A)"],
            index=0, key="estado_civil_v16",
        )

    # ---- PROPOSTA ----
    with bloco_proposta:
        st.markdown(f"""
        <div class="urba-section-header">
            <div class="urba-section-icon">📄</div>
            <div class="urba-section-title">Dados da Proposta</div>
        </div>
        """, unsafe_allow_html=True)

        ato_urba       = campo_moeda("Ato Urba (R$) *",                    "ato_urba_v16")
        valor_proposta = campo_moeda("Valor da Proposta / Líquido CV (R$) *", "valor_proposta_v16")
        primeira_mensal = campo_moeda("Valor da 1ª Mensal (R$) *",          "primeira_mensal_v16")

    # ---- COMPOSIÇÃO DE RENDA ----
    with bloco_renda:
        st.markdown(f"""
        <div class="urba-section-header">
            <div class="urba-section-icon">👥</div>
            <div class="urba-section-title">Composição de Renda</div>
        </div>
        """, unsafe_allow_html=True)
        st.caption("Use somente quando houver cliente adicional compondo renda.")

        qtd_adicionais = st.number_input(
            "Clientes adicionais", min_value=0, max_value=4,
            value=0, step=1, key="qtd_adicionais_v16",
        )

        rendas_adicionais = []
        for i in range(int(qtd_adicionais)):
            numero = i + 2
            with st.expander(f"Cliente {numero}", expanded=True):
                pdf_add  = st.file_uploader(f"SPC — Cliente {numero}", type=["pdf"], key=f"pdf_cli_v16_{numero}")
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
                        st.error(f"Falha: {e}")
                if pdf_add and renda_add <= 0:
                    renda_add = campo_moeda(f"Renda manual — Cliente {numero} (R$)", f"renda_manual_v16_{numero}")
                rendas_adicionais.append(renda_add)

    # ---- CÁLCULOS INSTANTÂNEOS ----
    renda_total = renda_proponente + sum(rendas_adicionais)
    perc_ato    = ato_urba / valor_proposta * 100 if valor_proposta > 0 else 0
    perc_comp   = primeira_mensal / renda_total * 100 if renda_total > 0 else 0
    faixa_at    = faixa_ato(perc_ato)
    faixa_comp  = faixa_comprometimento(perc_comp)

    st.divider()

    i1, i2, i3, i4 = st.columns(4)
    i1.metric("% do Ato",       f"{perc_ato:.2f}%",  faixa_at)
    i2.metric("Comprometimento", f"{perc_comp:.2f}%", faixa_comp)
    i3.metric("Renda Total",     brl(renda_total))
    i4.metric("Faixa Etária",    faixa_idade or "—")

    # ---- VALIDAÇÃO ----
    faltando = []
    if not empreendimento:    faltando.append("Empreendimento")
    if not unidade:           faltando.append("Unidade")
    if not nascimento:        faltando.append("Data de Nascimento")
    if not estado_civil:      faltando.append("Estado Civil")
    if not pdf_prop:          faltando.append("SPC do Proponente")
    if not score_proponente:  faltando.append("Score SPC")
    if renda_total <= 0:      faltando.append("Renda Presumida")
    if valor_proposta <= 0:   faltando.append("Valor da Proposta")
    if primeira_mensal <= 0:  faltando.append("1ª Mensal")

    if faltando:
        st.warning("Preencha/valide: **" + ", ".join(faltando) + "**")

    _, botao_calc = st.columns([3, 1])
    with botao_calc:
        calcular = st.button(
            "📊 CALCULAR SIMULAÇÃO",
            type="primary", use_container_width=True,
            disabled=bool(faltando), key="calcular_v16",
        )

    if calcular:
        notas = {
            "score_credito":         NOTAS_SCORE[score_proponente],
            "ato":                   NOTAS_ATO[faixa_at],
            "comprometimento_renda": NOTAS_COMPROMETIMENTO[faixa_comp],
            "idade":                 NOTAS_IDADE[faixa_idade],
            "estado_civil":          NOTAS_ESTADO_CIVIL[estado_civil],
        }
        score_final    = calcular_score_total(notas)
        classificacao, cor = classificar(score_final)

        st.session_state.resultado = {
            "notas": notas, "score_final": score_final,
            "classificacao": classificacao, "cor": cor,
            "empreendimento": empreendimento, "unidade": unidade,
            "cpf_proponente": cpf_proponente, "idade": idade,
            "faixa_idade": faixa_idade, "estado_civil": estado_civil,
            "score_proponente": score_proponente,
            "renda_proponente": renda_proponente,
            "qtd_clientes_adicionais": int(qtd_adicionais),
            "renda_adicionais": sum(rendas_adicionais),
            "renda_total": renda_total, "ato_urba": ato_urba,
            "valor_proposta": valor_proposta, "perc_ato": perc_ato,
            "faixa_at": faixa_at, "primeira_mensal": primeira_mensal,
            "perc_comp": perc_comp, "faixa_comp": faixa_comp,
        }

    # ---- RESULTADO ----
    if st.session_state.resultado:
        d = st.session_state.resultado

        st.divider()
        st.markdown(f"""
        <div class="urba-section-header">
            <div class="urba-section-icon">🧾</div>
            <div class="urba-section-title">Resumo da Simulação</div>
        </div>
        """, unsafe_allow_html=True)

        unidade_resumo = d.get("unidade") or ""
        emp_resumo     = d.get("empreendimento") or ""
        if emp_resumo and unidade_resumo.upper().startswith(emp_resumo.upper()):
            unidade_resumo = unidade_resumo[len(emp_resumo):].lstrip(" -–—") or unidade_resumo

        q1, q2, q3, q4 = st.columns(4)
        resumo_card(q1, "Empreendimento",   d.get("empreendimento"))
        resumo_card(q2, "Unidade",          unidade_resumo)
        resumo_card(q3, "CPF do Proponente", d.get("cpf_proponente"))
        resumo_card(q4, "Renda Total",      brl(d.get("renda_total", 0)))

        p1, p2, p3, p4 = st.columns(4)
        resumo_card(p1, "Faixa Etária",       d.get("faixa_idade"))
        resumo_card(p2, "Estado Civil",        d.get("estado_civil"))
        resumo_card(p3, "Score do Proponente", d.get("score_proponente"))
        resumo_card(p4, "Ato Urba",            brl(d.get("ato_urba", 0)))

        c1, c2, c3, c4 = st.columns(4)
        resumo_card(c1, "% do Ato",         f"{d.get('perc_ato', 0):.2f}%")
        resumo_card(c2, "1ª Mensal",         brl(d.get("primeira_mensal", 0)))
        resumo_card(c3, "Comprometimento",   f"{d.get('perc_comp', 0):.2f}%")
        resumo_card(c4, "Valor da Proposta", brl(d.get("valor_proposta", 0)))

        # ---- AVALIAÇÃO DE RISCO ----
        st.markdown(f"""
        <div class="urba-section-header" style="margin-top:24px;">
            <div class="urba-section-icon">📈</div>
            <div class="urba-section-title">Avaliação de Risco</div>
        </div>
        """, unsafe_allow_html=True)

        r1, r2 = st.columns([1, 2])
        with r1:
            css_class = {"green": "urba-score-green", "orange": "urba-score-orange", "red": "urba-score-red"}[d["cor"]]
            st.markdown(f"""
            <div class="urba-score-box">
                <div class="urba-score-number">{d['score_final']}</div>
                <div class="urba-score-label">de {SCORE_MAX} pontos</div>
                <div class="urba-score-class {css_class}">{d['classificacao']}</div>
            </div>
            """, unsafe_allow_html=True)

        with r2:
            labels  = {
                "score_credito":         "Score de Crédito",
                "ato":                   "% do Ato",
                "comprometimento_renda": "Comprometimento de Renda",
                "idade":                 "Faixa Etária",
                "estado_civil":          "Estado Civil",
            }
            max_nota = {"score_credito": 5, "ato": 5, "comprometimento_renda": 5, "idade": 5, "estado_civil": 3}
            detalhes = []
            for var, peso in PESOS.items():
                nota = d["notas"][var]
                detalhes.append({
                    "Variável": labels[var],
                    "Nota":     f"{nota}/{max_nota[var]}",
                    "Peso":     peso,
                    "Pontos":   nota * peso,
                    "Máximo":   max_nota[var] * peso,
                })
            st.dataframe(
                pd.DataFrame(detalhes),
                use_container_width=True, hide_index=True,
                column_config={
                    "Variável": st.column_config.TextColumn("Variável", width="medium"),
                    "Nota":     st.column_config.TextColumn("Nota",     width="small"),
                    "Peso":     st.column_config.NumberColumn("Peso",   width="small"),
                    "Pontos":   st.column_config.NumberColumn("Pontos", width="small"),
                    "Máximo":   st.column_config.NumberColumn("Máximo", width="small"),
                },
            )

        # ---- ESTRATÉGIAS ----
        if d["classificacao"] != "🟢 BAIXO RISCO":
            st.divider()
            st.markdown(f"""
            <div class="urba-section-header">
                <div class="urba-section-icon">💡</div>
                <div class="urba-section-title">Estratégias de Estruturação da Venda</div>
            </div>
            """, unsafe_allow_html=True)

            a1, b1 = st.columns(2)
            a1.metric("Pontos para Risco Moderado", f"+{max(0, LIMITE_MODERADO - d['score_final'])}")
            b1.metric("Pontos para Baixo Risco",    f"+{max(0, LIMITE_BAIXO    - d['score_final'])}")

            cenarios = montar_cenarios(
                score_atual=d["score_final"], notas=d["notas"],
                renda_total=d["renda_total"], mensal=d["primeira_mensal"],
                ato=d["ato_urba"], valor_proposta=d["valor_proposta"],
            )
            if cenarios:
                df_c = pd.DataFrame(cenarios)
                df_c["Ganho"]     = df_c["Ganho"].map(lambda x: f"+{x}")
                df_c["NovoScore"] = df_c["NovoScore"].map(str)
                st.dataframe(
                    df_c[["Variável","Ajuste","Ganho","NovoScore","NovaClassificacao"]].head(12)
                    .rename(columns={"NovoScore": "Novo Score", "NovaClassificacao": "Nova Classificação"}),
                    use_container_width=True, hide_index=True,
                )
                st.caption("As sugestões são simulações contrafactuais. Não são propostas alterações de idade, estado civil ou score cadastral.")

        # ---- SALVAR ----
        st.divider()
        st.markdown(f"""
        <div class="urba-section-header">
            <div class="urba-section-icon">💾</div>
            <div class="urba-section-title">Salvar no Histórico</div>
        </div>
        """, unsafe_allow_html=True)
        st.caption("Somente o administrador consulta o histórico consolidado.")

        if st.button("✅ CONFIRMAR E SALVAR NO HISTÓRICO", type="primary", key="salvar_v16"):
            try:
                salvar_simulacao(d, usuario["email"])
                st.success("✅ Simulação salva com sucesso no banco de dados!")
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")


# ============================================================
# PÁGINA: HISTÓRICO
# ============================================================
elif st.session_state.pagina == "Histórico" and usuario["perfil"] == "ADMINISTRADOR":

    st.markdown(f"""
    <div class="urba-section-header">
        <div class="urba-section-icon">📂</div>
        <div class="urba-section-title">Histórico de Simulações</div>
    </div>
    """, unsafe_allow_html=True)

    hist = carregar_historico()

    if hist.empty:
        st.info("Nenhuma simulação registrada ainda.")
    else:
        for col in ["vendedor_email", "empreendimento", "classificacao"]:
            if col not in hist.columns:
                hist[col] = ""

        c1, c2, c3 = st.columns(3)
        with c1:
            vendedores = sorted(x for x in hist["vendedor_email"].fillna("").unique() if x)
            filtro_v   = st.selectbox("Vendedor", ["TODOS"] + vendedores, key="fv")
        with c2:
            emps     = sorted(x for x in hist["empreendimento"].fillna("").unique() if x)
            filtro_e = st.selectbox("Empreendimento", ["TODOS"] + emps, key="fe")
        with c3:
            classes  = sorted(x for x in hist["classificacao"].fillna("").unique() if x)
            filtro_c = st.selectbox("Classificação", ["TODAS"] + classes, key="fc")

        exib = hist.copy()
        if filtro_v != "TODOS": exib = exib[exib["vendedor_email"] == filtro_v]
        if filtro_e != "TODOS": exib = exib[exib["empreendimento"] == filtro_e]
        if filtro_c != "TODAS": exib = exib[exib["classificacao"] == filtro_c]

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total",       len(exib))
        k2.metric("Baixo Risco", int(exib["classificacao"].astype(str).str.contains("BAIXO",    na=False).sum()))
        k3.metric("Moderado",    int(exib["classificacao"].astype(str).str.contains("MODERADO", na=False).sum()))
        k4.metric("Alto Risco",  int(exib["classificacao"].astype(str).str.contains("ALTO",     na=False).sum()))

        st.dataframe(exib, use_container_width=True, hide_index=True)

        st.download_button(
            "⬇ EXPORTAR HISTÓRICO (CSV)",
            exib.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"historico_urba_{datetime.now(TIMEZONE_BRASILIA).strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    st.divider()
    with st.expander("🗑️ Excluir histórico completo", expanded=False):
        st.warning("Esta ação remove TODOS os registros do banco e não pode ser desfeita.")
        confirmar = st.checkbox("Confirmo que desejo excluir TODO o histórico", key="conf_del")
        if st.button("🗑️ EXCLUIR TODO O HISTÓRICO", type="primary", disabled=not confirmar, key="del_hist"):
            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM historico_simulacoes")
                    conn.commit()
            st.success("Histórico excluído.")
            st.rerun()


# ============================================================
# PÁGINA: GESTÃO DE USUÁRIOS
# ============================================================
elif st.session_state.pagina == "Usuários" and usuario["perfil"] == "ADMINISTRADOR":

    st.markdown(f"""
    <div class="urba-section-header">
        <div class="urba-section-icon">👥</div>
        <div class="urba-section-title">Gestão de Usuários</div>
    </div>
    """, unsafe_allow_html=True)

    # Criar usuário
    with st.expander("➕ Novo Usuário", expanded=False):
        with st.form("form_novo_usuario"):
            col1, col2 = st.columns(2)
            with col1:
                novo_nome   = st.text_input("Nome completo *")
                novo_email  = st.text_input("E-mail *")
            with col2:
                novo_perfil = st.selectbox("Perfil *", ["VENDEDOR", "ADMINISTRADOR"])
                nova_senha  = st.text_input("Senha *", type="password")
                conf_senha  = st.text_input("Confirmar senha *", type="password")
            criar = st.form_submit_button("CRIAR USUÁRIO", type="primary", use_container_width=True)

        if criar:
            if not all([novo_nome, novo_email, nova_senha, conf_senha]):
                st.error("Preencha todos os campos.")
            elif nova_senha != conf_senha:
                st.error("As senhas não coincidem.")
            elif len(nova_senha) < 6:
                st.error("A senha deve ter pelo menos 6 caracteres.")
            else:
                try:
                    criar_usuario(novo_nome, novo_email, nova_senha, novo_perfil)
                    st.success(f"Usuário **{novo_nome}** criado com sucesso!")
                    st.rerun()
                except Exception as e:
                    if "unique" in str(e).lower():
                        st.error("E-mail já cadastrado.")
                    else:
                        st.error(f"Erro: {e}")

    st.divider()

    # Listar usuários
    usuarios_lista = listar_usuarios()
    if not usuarios_lista:
        st.info("Nenhum usuário cadastrado.")
    else:
        st.markdown(f"**{len(usuarios_lista)} usuário(s) cadastrado(s)**")
        for u in usuarios_lista:
            with st.container(border=True):
                col_info, col_status, col_acoes = st.columns([3, 1, 2])
                with col_info:
                    st.markdown(f"**{u['nome']}**")
                    st.caption(f"{u['email']} • {u['perfil']}")
                with col_status:
                    if u["ativo"]:
                        st.markdown('<span class="urba-tag urba-tag-green">✓ Ativo</span>', unsafe_allow_html=True)
                    else:
                        st.markdown('<span class="urba-tag urba-tag-red">✗ Inativo</span>', unsafe_allow_html=True)
                with col_acoes:
                    ca, cb = st.columns(2)
                    with ca:
                        label_toggle = "Desativar" if u["ativo"] else "Ativar"
                        if st.button(label_toggle, key=f"tog_{u['id']}", use_container_width=True):
                            toggle_usuario(u["id"], not u["ativo"])
                            st.rerun()
                    with cb:
                        if st.button("Senha", key=f"pwd_{u['id']}", use_container_width=True):
                            st.session_state[f"show_pwd_{u['id']}"] = not st.session_state.get(f"show_pwd_{u['id']}", False)

                if st.session_state.get(f"show_pwd_{u['id']}", False):
                    with st.form(f"form_pwd_{u['id']}"):
                        np1 = st.text_input("Nova senha", type="password", key=f"np1_{u['id']}")
                        np2 = st.text_input("Confirmar", type="password", key=f"np2_{u['id']}")
                        if st.form_submit_button("Salvar senha", type="primary"):
                            if np1 != np2:
                                st.error("Senhas não coincidem.")
                            elif len(np1) < 6:
                                st.error("Mínimo 6 caracteres.")
                            else:
                                alterar_senha(u["id"], np1)
                                st.success("Senha alterada!")
                                st.session_state[f"show_pwd_{u['id']}"] = False
                                st.rerun()

# ============================================================
# RODAPÉ
# ============================================================
st.divider()
st.markdown(f"""
<div style="text-align:center; color:{CINZA_TEXTO}; font-size:0.78rem; padding: 8px 0;">
    <strong style="color:{VERDE};">Urba</strong> • Simulador de Score de Vendas V16.2 •
    Projeto Defensores do Contrato
</div>
""", unsafe_allow_html=True)
