# app.py — V16.3
# Simulador de Score de Vendas — Urba
# V16.3: Identidade visual Urba (#079D56 / #FF8C23), fundo branco,
#         logo SVG no lugar de emojis, sem tira preta, inputs legíveis,
#         botões destrutivos em verde escuro, textos em cinza escuro.

import io
import os
import re
import unicodedata
from datetime import date, datetime
from zoneinfo import ZoneInfo

import pandas as pd
import psycopg2
import bcrypt
import streamlit as st
import pdfplumber

st.set_page_config(
    page_title="Simulador de Score — Urba",
    page_icon="https://i.imgur.com/placeholder.png",
    layout="wide",
)

# ============================================================
# PALETA URBA
# ============================================================
VERDE       = "#079D56"
VERDE_ESC   = "#056B3A"
VERDE_CLARO = "#E8F7EF"
LARANJA     = "#FF8C23"
LARANJA_CL  = "#FFF3E8"
CINZA_ESC   = "#2D2D2D"
CINZA_MED   = "#5A5A5A"
CINZA_CL    = "#F4F6F8"
CINZA_BORDA = "#E0E4EA"
BRANCO      = "#FFFFFF"

# Logo SVG inline (ícone das duas casinhas Urba)
LOGO_SVG = """
<svg width="38" height="38" viewBox="0 0 120 100" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect x="2" y="28" width="62" height="68" rx="10" fill="none" stroke="#079D56" stroke-width="7"/>
  <polygon points="33,2 2,32 64,32" fill="none" stroke="#079D56" stroke-width="7" stroke-linejoin="round"/>
  <rect x="38" y="38" width="58" height="58" rx="10" fill="#FF8C23"/>
  <polygon points="67,14 38,44 96,44" fill="#FF8C23"/>
</svg>
"""

LOGO_SVG_BRANCO = """
<svg width="38" height="38" viewBox="0 0 120 100" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect x="2" y="28" width="62" height="68" rx="10" fill="none" stroke="#FFFFFF" stroke-width="7"/>
  <polygon points="33,2 2,32 64,32" fill="none" stroke="#FFFFFF" stroke-width="7" stroke-linejoin="round"/>
  <rect x="38" y="38" width="58" height="58" rx="10" fill="#FF8C23"/>
  <polygon points="67,14 38,44 96,44" fill="#FF8C23"/>
</svg>
"""

# ============================================================
# CSS GLOBAL — V16.3
# ============================================================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* ── Reset geral ── */
html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif !important;
    color: {CINZA_ESC};
}}

/* ── Remove tira preta do topo ── */
#MainMenu, header, footer {{ visibility: hidden; height: 0; }}
[data-testid="stToolbar"] {{ display: none !important; }}
.stDeployButton {{ display: none !important; }}

/* ── Fundo branco ── */
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main .block-container {{
    background-color: {BRANCO} !important;
}}
.block-container {{
    max-width: 1380px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}}

/* ── Sidebar verde Urba ── */
[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, {VERDE_ESC} 0%, {VERDE} 100%) !important;
    border-right: none !important;
}}
[data-testid="stSidebar"] * {{
    color: {BRANCO} !important;
}}
[data-testid="stSidebar"] .stButton > button {{
    background: rgba(255,255,255,0.15) !important;
    color: {BRANCO} !important;
    border: 1px solid rgba(255,255,255,0.35) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: background 0.2s;
}}
[data-testid="stSidebar"] .stButton > button:hover {{
    background: rgba(255,255,255,0.28) !important;
}}
[data-testid="stSidebar"] hr {{
    border-color: rgba(255,255,255,0.25) !important;
}}
[data-testid="stSidebar"] input {{
    background: rgba(255,255,255,0.12) !important;
    color: {BRANCO} !important;
    border: 1px solid rgba(255,255,255,0.3) !important;
    border-radius: 8px !important;
}}
[data-testid="stSidebar"] input::placeholder {{
    color: rgba(255,255,255,0.55) !important;
}}

/* ── Inputs e selects ── */
[data-baseweb="input"] > div,
[data-baseweb="select"] > div,
[data-baseweb="textarea"] > div {{
    background-color: {BRANCO} !important;
    border: 1.5px solid {CINZA_BORDA} !important;
    border-radius: 8px !important;
    color: {CINZA_ESC} !important;
}}
[data-baseweb="input"] input,
[data-baseweb="select"] input,
[data-baseweb="textarea"] textarea {{
    color: {CINZA_ESC} !important;
    background: {BRANCO} !important;
}}
[data-baseweb="input"] > div:focus-within,
[data-baseweb="select"] > div:focus-within {{
    border-color: {VERDE} !important;
    box-shadow: 0 0 0 3px rgba(7,157,86,0.12) !important;
}}
[data-baseweb="select"] span {{
    color: {CINZA_ESC} !important;
}}
/* Placeholder dos selects */
[data-baseweb="select"] [data-testid="stSelectboxLabel"] {{
    color: {CINZA_MED} !important;
}}

/* ── Labels dos campos ── */
label, .stTextInput label, .stSelectbox label,
.stNumberInput label, .stFileUploader label {{
    color: {CINZA_ESC} !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
}}

/* ── Botão primário (verde Urba) ── */
.stButton > button[kind="primary"],
button[data-testid="baseButton-primary"] {{
    background: {VERDE} !important;
    color: {BRANCO} !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.04em !important;
    min-height: 44px !important;
    transition: background 0.2s, transform 0.1s !important;
    box-shadow: 0 2px 8px rgba(7,157,86,0.18) !important;
}}
.stButton > button[kind="primary"]:hover {{
    background: {VERDE_ESC} !important;
    transform: translateY(-1px) !important;
}}

/* ── Botão secundário ── */
.stButton > button[kind="secondary"],
button[data-testid="baseButton-secondary"] {{
    background: {BRANCO} !important;
    color: {VERDE} !important;
    border: 1.5px solid {VERDE} !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    min-height: 44px !important;
    transition: all 0.2s !important;
}}
.stButton > button[kind="secondary"]:hover {{
    background: {VERDE_CLARO} !important;
}}

/* ── Botão desabilitado ── */
.stButton > button:disabled {{
    background: {CINZA_CL} !important;
    color: #AAAAAA !important;
    border: 1.5px solid {CINZA_BORDA} !important;
    cursor: not-allowed !important;
}}

/* ── Download button (laranja) ── */
.stDownloadButton > button {{
    background: {LARANJA} !important;
    color: {BRANCO} !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    min-height: 44px !important;
    box-shadow: 0 2px 8px rgba(255,140,35,0.18) !important;
    transition: background 0.2s !important;
}}
.stDownloadButton > button:hover {{
    background: #E07010 !important;
}}

/* ── Métricas ── */
div[data-testid="stMetric"] {{
    background: {CINZA_CL} !important;
    border: 1.5px solid {CINZA_BORDA} !important;
    border-radius: 12px !important;
    padding: 16px 18px !important;
    min-height: 90px !important;
}}
div[data-testid="stMetricLabel"] p {{
    color: {CINZA_MED} !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}}
div[data-testid="stMetricValue"] {{
    color: {CINZA_ESC} !important;
    font-size: clamp(1.1rem, 1.6vw, 1.5rem) !important;
    font-weight: 700 !important;
}}
div[data-testid="stMetricDelta"] {{
    font-size: 0.78rem !important;
    font-weight: 600 !important;
}}

/* ── Cards / containers ── */
[data-testid="stVerticalBlockBorderWrapper"] {{
    background: {CINZA_CL} !important;
    border: 1.5px solid {CINZA_BORDA} !important;
    border-radius: 12px !important;
}}
[data-testid="stVerticalBlockBorderWrapper"] p,
[data-testid="stVerticalBlockBorderWrapper"] strong,
[data-testid="stVerticalBlockBorderWrapper"] span {{
    color: {CINZA_ESC} !important;
    white-space: normal !important;
    overflow-wrap: anywhere !important;
}}

/* ── Captions ── */
.stCaption, [data-testid="stCaptionContainer"] p {{
    color: {CINZA_MED} !important;
    font-size: 0.8rem !important;
}}

/* ── Alertas ── */
[data-testid="stAlert"] {{
    border-radius: 10px !important;
    border-left-width: 4px !important;
}}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {{
    border: 1.5px solid {CINZA_BORDA} !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}}

/* ── Expander ── */
[data-testid="stExpander"] {{
    border: 1.5px solid {CINZA_BORDA} !important;
    border-radius: 10px !important;
    background: {CINZA_CL} !important;
}}
[data-testid="stExpander"] summary {{
    color: {CINZA_ESC} !important;
    font-weight: 600 !important;
}}

/* ── Divider ── */
hr {{
    border-color: {CINZA_BORDA} !important;
    margin: 1.2rem 0 !important;
}}

/* ── File uploader ── */
[data-testid="stFileUploader"] {{
    background: {CINZA_CL} !important;
    border: 1.5px dashed {CINZA_BORDA} !important;
    border-radius: 10px !important;
    padding: 8px !important;
}}
[data-testid="stFileUploader"] * {{
    color: {CINZA_ESC} !important;
}}

/* ── Number input ── */
[data-testid="stNumberInput"] input {{
    background: {BRANCO} !important;
    color: {CINZA_ESC} !important;
    border: 1.5px solid {CINZA_BORDA} !important;
    border-radius: 8px !important;
}}
[data-testid="stNumberInput"] button {{
    background: {CINZA_CL} !important;
    color: {CINZA_ESC} !important;
    border: 1px solid {CINZA_BORDA} !important;
}}

/* ── Checkbox ── */
[data-testid="stCheckbox"] label span {{
    color: {CINZA_ESC} !important;
    font-weight: 500 !important;
    text-transform: none !important;
    letter-spacing: 0 !important;
    font-size: 0.9rem !important;
}}

/* ── Scrollbar ── */
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: {CINZA_CL}; }}
::-webkit-scrollbar-thumb {{ background: #C0C8D0; border-radius: 3px; }}
::-webkit-scrollbar-thumb:hover {{ background: {VERDE}; }}
</style>
""", unsafe_allow_html=True)


# ============================================================
# BANCO DE DADOS — NEON
# ============================================================
def get_conn():
    url = st.secrets["NEON_DATABASE_URL"]
    return psycopg2.connect(url)


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
                    "SELECT nome, senha_hash, perfil, ativo FROM usuarios WHERE email = %s",
                    (email.lower().strip(),)
                )
                row = cur.fetchone()
                if not row:
                    return None
                nome, senha_hash, perfil, ativo = row
                if not ativo:
                    return None
                if bcrypt.checkpw(senha.encode(), senha_hash.encode()):
                    return {"nome": nome, "email": email.lower().strip(), "perfil": perfil}
                return None
    except Exception:
        return None


def listar_usuarios():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, nome, email, perfil, ativo, criado_em FROM usuarios ORDER BY criado_em DESC")
            cols = ["id", "nome", "email", "perfil", "ativo", "criado_em"]
            return [dict(zip(cols, row)) for row in cur.fetchall()]


def criar_usuario(nome, email, senha, perfil):
    senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt(12)).decode()
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO usuarios (nome, email, senha_hash, perfil) VALUES (%s, %s, %s, %s)",
                (nome, email.lower().strip(), senha_hash, perfil)
            )
            conn.commit()


def toggle_usuario(user_id, ativo):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE usuarios SET ativo = %s, atualizado_em = NOW() WHERE id = %s", (ativo, user_id))
            conn.commit()


def deletar_usuario(user_id):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM usuarios WHERE id = %s", (user_id,))
            conn.commit()


def salvar_simulacao(dados, vendedor_email):
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
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                vendedor_email,
                dados.get("empreendimento",""),
                dados.get("unidade",""),
                dados.get("cpf_proponente",""),
                dados.get("idade"),
                dados.get("faixa_idade",""),
                dados.get("estado_civil",""),
                dados.get("score_proponente",""),
                dados.get("renda_proponente",0),
                dados.get("qtd_clientes_adicionais",0),
                dados.get("renda_adicionais",0),
                dados.get("renda_total",0),
                dados.get("ato_urba",0),
                dados.get("perc_ato",0),
                dados.get("faixa_at",""),
                dados.get("valor_proposta",0),
                dados.get("primeira_mensal",0),
                dados.get("perc_comp",0),
                dados.get("faixa_comp",""),
                dados.get("score_final",0),
                dados.get("classificacao",""),
            ))
            conn.commit()


def carregar_historico():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT data_hora, vendedor_email, empreendimento, unidade, cpf_proponente,
                       idade, faixa_etaria, estado_civil, score_proponente,
                       renda_proponente, qtd_clientes_adicionais, renda_clientes_adicionais,
                       renda_total, ato_urba, percentual_ato, faixa_ato,
                       valor_proposta, primeira_mensal, percentual_comprometimento,
                       faixa_comprometimento, score_final, classificacao
                FROM historico_simulacoes ORDER BY data_hora DESC
            """)
            cols = [
                "Data/Hora","Vendedor","Empreendimento","Unidade","CPF",
                "Idade","Faixa Etária","Estado Civil","Score SPC",
                "Renda Proponente","Qtd Adicionais","Renda Adicionais",
                "Renda Total","Ato Urba","% Ato","Faixa Ato",
                "Valor Proposta","1ª Mensal","% Comprometimento",
                "Faixa Comprometimento","Score Final","Classificação"
            ]
            rows = cur.fetchall()
            return pd.DataFrame(rows, columns=cols) if rows else pd.DataFrame(columns=cols)


def limpar_historico():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM historico_simulacoes")
            conn.commit()


# ============================================================
# AUTENTICAÇÃO — TELA DE LOGIN
# ============================================================
if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None
if "pagina" not in st.session_state:
    st.session_state.pagina = "Simulador"

if not st.session_state.usuario_logado:
    st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background: {CINZA_CL} !important;
    }}
    .login-wrapper {{
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 80vh;
    }}
    .login-card {{
        background: {BRANCO};
        border: 1.5px solid {CINZA_BORDA};
        border-radius: 20px;
        padding: 40px 44px 36px;
        max-width: 420px;
        width: 100%;
        box-shadow: 0 8px 32px rgba(0,0,0,0.08);
        text-align: center;
    }}
    .login-logo {{
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        margin-bottom: 6px;
    }}
    .login-brand {{
        font-size: 2rem;
        font-weight: 800;
        color: {VERDE};
        letter-spacing: -0.03em;
    }}
    .login-sub {{
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: {CINZA_MED};
        margin-bottom: 28px;
    }}
    .login-title {{
        font-size: 1.25rem;
        font-weight: 700;
        color: {CINZA_ESC};
        margin-bottom: 4px;
    }}
    .login-desc {{
        font-size: 0.88rem;
        color: {CINZA_MED};
        margin-bottom: 24px;
    }}
    </style>
    """, unsafe_allow_html=True)

    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        st.markdown(f"""
        <div class="login-card">
          <div class="login-logo">
            {LOGO_SVG}
            <span class="login-brand">Urba</span>
          </div>
          <div class="login-sub">Simulador de Score de Vendas</div>
          <div class="login-title">Bem-vindo de volta</div>
          <div class="login-desc">Acesse com suas credenciais para continuar.</div>
        </div>
        """, unsafe_allow_html=True)

        email_in = st.text_input("E-mail", placeholder="nome@urba.com.br", key="login_email")
        senha_in = st.text_input("Senha", type="password", placeholder="••••••••", key="login_senha")

        if st.button("ENTRAR", type="primary", use_container_width=True, key="btn_entrar"):
            if not email_in or not senha_in:
                st.error("Preencha e-mail e senha.")
            else:
                usuario = autenticar_usuario(email_in, senha_in)
                if usuario:
                    st.session_state.usuario_logado = usuario
                    st.session_state.pagina = "Simulador"
                    st.rerun()
                else:
                    st.error("E-mail ou senha incorretos, ou usuário inativo.")
    st.stop()

# ============================================================
# USUÁRIO LOGADO
# ============================================================
usuario = st.session_state.usuario_logado
eh_admin = usuario["perfil"] == "ADMINISTRADOR"

# ── SIDEBAR ──
with st.sidebar:
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px;">
      {LOGO_SVG_BRANCO}
      <span style="font-size:1.5rem;font-weight:800;color:#fff;letter-spacing:-0.02em;">Urba</span>
    </div>
    <div style="font-size:0.68rem;font-weight:700;letter-spacing:0.14em;
                text-transform:uppercase;color:rgba(255,255,255,0.65);
                margin-bottom:18px;">Simulador de Score</div>
    <hr style="border-color:rgba(255,255,255,0.2);margin:0 0 16px 0;">
    <div style="font-size:0.95rem;font-weight:700;color:#fff;">{usuario['nome']}</div>
    <div style="font-size:0.78rem;color:rgba(255,255,255,0.75);margin-bottom:4px;">{usuario['email']}</div>
    <div style="display:inline-block;background:rgba(255,255,255,0.18);
                border-radius:20px;padding:2px 10px;font-size:0.72rem;
                font-weight:700;color:#fff;margin-bottom:16px;">
      {'Administrador' if eh_admin else 'Vendedor'}
    </div>
    """, unsafe_allow_html=True)

    if st.button("Sair", use_container_width=True, key="btn_sair"):
        st.session_state.usuario_logado = None
        st.session_state.pagina = "Simulador"
        st.session_state.pop("resultado", None)
        st.rerun()

    st.divider()
    st.caption("Versão 16.3 • Urba")


# ============================================================
# HERO HEADER
# ============================================================
st.markdown(f"""
<div style="background:linear-gradient(135deg,{VERDE_ESC} 0%,{VERDE} 100%);
            border-radius:16px;padding:24px 28px 20px;margin-bottom:20px;
            box-shadow:0 4px 20px rgba(7,157,86,0.18);">
  <div style="display:flex;align-items:center;gap:14px;">
    <div>{LOGO_SVG_BRANCO}</div>
    <div>
      <div style="font-size:0.72rem;font-weight:700;letter-spacing:0.14em;
                  text-transform:uppercase;color:rgba(255,255,255,0.75);margin-bottom:3px;">
        Projeto Defensores do Contrato
      </div>
      <div style="font-size:clamp(1.5rem,2.5vw,2rem);font-weight:800;
                  color:#fff;line-height:1.1;letter-spacing:-0.02em;">
        Simulador de Score de Vendas
      </div>
      <div style="font-size:0.88rem;color:rgba(255,255,255,0.8);margin-top:4px;">
        Avaliação estruturada do risco de distrato no momento da venda.
      </div>
    </div>
    <div style="margin-left:auto;">
      <span style="background:rgba(255,255,255,0.18);border-radius:20px;
                   padding:4px 12px;font-size:0.75rem;font-weight:700;color:#fff;">
        V16.3
      </span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── NAVEGAÇÃO ──
nav_cols = st.columns([1, 1, 1, 3])
with nav_cols[0]:
    if st.button("Simulador",
                 type="primary" if st.session_state.pagina == "Simulador" else "secondary",
                 use_container_width=True, key="nav_sim"):
        st.session_state.pagina = "Simulador"
        st.rerun()
with nav_cols[1]:
    if eh_admin:
        if st.button("Histórico",
                     type="primary" if st.session_state.pagina == "Histórico" else "secondary",
                     use_container_width=True, key="nav_hist"):
            st.session_state.pagina = "Histórico"
            st.rerun()
    else:
        st.button("Histórico", disabled=True, use_container_width=True, key="nav_hist_off")
with nav_cols[2]:
    if eh_admin:
        if st.button("Usuários",
                     type="primary" if st.session_state.pagina == "Usuários" else "secondary",
                     use_container_width=True, key="nav_usr"):
            st.session_state.pagina = "Usuários"
            st.rerun()
    else:
        st.button("Usuários", disabled=True, use_container_width=True, key="nav_usr_off")

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
    "60+ ANOS":      5,
    "45 A 60 ANOS":  4,
    "35 A 45 ANOS":  3,
    "ATÉ 25 ANOS":   2,
    "25 A 35 ANOS":  1,
}

NOTAS_ESTADO_CIVIL = {
    "CASADO(A)":     3,
    "DIVORCIADO(A)": 2,
    "SOLTEIRO(A)":   1,
}

SCORE_MAX       = sum([5*5, 5*5, 5*4, 5*1, 3*1])  # = 78
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
    texto = str(valor or "").strip().replace("R$", "").replace(" ", "")
    if not texto:
        return 0.0
    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    else:
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
    if chave not in st.session_state:
        st.session_state[chave] = float_para_moeda_input(valor_inicial)
    texto = st.text_input(
        label, key=chave,
        on_change=_normalizar_campo_moeda, args=(chave,),
        help=ajuda, placeholder="0,00",
    )
    return moeda_para_float(texto)


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
    if score >= LIMITE_BAIXO:    return "BAIXO RISCO",    "green"
    if score >= LIMITE_MODERADO: return "RISCO MODERADO", "orange"
    return "ALTO RISCO", "red"


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
        "score_letra":    score_letra,
        "score_faixa":    score_faixa,
        "renda_presumida": renda,
        "data_nascimento": data_nascimento,
        "cpf":            cpf,
        "texto_extraido": texto_completo,
    }


# ============================================================
# CENÁRIOS (preservado do V15.0)
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
            renda_alvo = renda_minima_para_comprometimento(mensal, limite)
            mensal_alvo = mensal_maxima_para_comprometimento(renda_total, limite)
            cenarios.append({
                "Variável": "Renda / Mensal",
                "Ajuste": f"Para comprometimento ≤ {limite}%: renda total ≈ {brl(renda_alvo)} OU mensal ≤ {brl(mensal_alvo)}",
                "Ganho": ganho,
                "NovoScore": score_atual + ganho,
            })

    for c in cenarios:
        c["NovaClassificacao"] = classificar(c["NovoScore"])[0]
        c["AtingeModerado"] = c["NovoScore"] >= LIMITE_MODERADO
        c["AtingeBaixo"]    = c["NovoScore"] >= LIMITE_BAIXO

    return sorted(cenarios, key=lambda c: (not c["AtingeModerado"], not c["AtingeBaixo"], -c["Ganho"]))


# ============================================================
# ESTADO DA SESSÃO
# ============================================================
if "resultado" not in st.session_state:
    st.session_state.resultado = None


# ============================================================
# HELPER: CARD DE RESUMO
# ============================================================
def resumo_card(coluna, titulo, valor):
    with coluna:
        with st.container(border=True):
            st.caption(titulo)
            st.markdown(f"**{valor if valor not in (None, '') else '—'}**")


# ============================================================
# PÁGINA: SIMULADOR
# ============================================================
if st.session_state.pagina == "Simulador":

    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">
      <span style="font-size:1.15rem;font-weight:700;color:{VERDE_ESC};">Dados da Simulação</span>
    </div>
    <p style="color:{CINZA_MED};font-size:0.88rem;margin-bottom:18px;">
      Preencha as informações abaixo para calcular o score de risco da venda.
    </p>
    """, unsafe_allow_html=True)

    bloco_emp, bloco_cliente, bloco_proposta, bloco_renda = st.columns(4, gap="large")

    # ── EMPREENDIMENTO ──
    with bloco_emp:
        st.markdown(f"<div style='font-weight:700;color:{VERDE_ESC};margin-bottom:10px;'>Empreendimento</div>", unsafe_allow_html=True)

        if cadastro.empty:
            st.error("Cadastro de empreendimentos não carregado.")
            if erro_cadastro:
                with st.expander("Detalhes técnicos"):
                    st.code(erro_cadastro)

        empreendimentos = sorted(
            cadastro["Empreendimento"].dropna().astype(str).str.strip()
            .loc[lambda x: x.ne("")].unique().tolist()
        )
        empreendimento = st.selectbox("Empreendimento *", [""] + empreendimentos, index=0, key="empreendimento_v16")

        if empreendimento:
            cad_emp = cadastro[cadastro["Empreendimento"].astype(str).str.strip() == str(empreendimento).strip()].copy()
        else:
            cad_emp = cadastro.iloc[0:0].copy()

        unidades = sorted(
            cad_emp["Unidade"].dropna().astype(str).str.strip()
            .loc[lambda x: x.ne("")].unique().tolist(),
            key=lambda x: x.zfill(30),
        )

        def rotulo_unidade(valor):
            if not valor: return "Selecione a unidade"
            texto = str(valor).strip()
            emp = str(empreendimento or "").strip()
            if emp and texto.upper().startswith(emp.upper()):
                curto = texto[len(emp):].lstrip(" -–—")
                if curto: return curto
            return texto

        unidade = st.selectbox(
            "Unidade *", [""] + unidades, index=0,
            disabled=not bool(empreendimento),
            key="unidade_v16", format_func=rotulo_unidade,
        )
        if unidade:
            st.caption(f"Unidade selecionada: **{rotulo_unidade(unidade)}**")

    # ── PERFIL DO CLIENTE ──
    with bloco_cliente:
        st.markdown(f"<div style='font-weight:700;color:{VERDE_ESC};margin-bottom:10px;'>Perfil do Cliente</div>", unsafe_allow_html=True)
        st.caption("Anexe o relatório SPC do proponente.")

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
                with st.spinner("Lendo SPC do proponente..."):
                    dados_spc_prop = extrair_dados_spc(pdf_prop)

                score_proponente = dados_spc_prop.get("score_faixa")
                renda_proponente = float(dados_spc_prop.get("renda_presumida") or 0)
                nascimento       = dados_spc_prop.get("data_nascimento")
                idade            = calcular_idade(nascimento) if nascimento else None
                faixa_idade      = faixa_etaria(idade) if idade is not None else None
                cpf_proponente   = dados_spc_prop.get("cpf") or ""

                st.markdown("**Dados identificados no SPC**")
                with st.container(border=True):
                    st.caption("CPF do Proponente")
                    st.markdown(f"**{cpf_proponente if cpf_proponente else '—'}**")
                    if not cpf_proponente:
                        st.warning("CPF não localizado no SPC.")

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
                        st.warning("Score não localizado no SPC.")

                    st.caption("Renda Presumida")
                    if renda_proponente > 0:
                        st.markdown(f"**{brl(renda_proponente)}**")
                    else:
                        st.warning("Renda não localizada no SPC.")

            except Exception as e:
                st.error(f"Falha na leitura do SPC: {e}")

        if pdf_prop and not cpf_proponente:
            cpf_proponente = st.text_input("CPF — preenchimento manual", placeholder="000.000.000-00", key="cpf_manual_v16").strip()

        if pdf_prop and not score_proponente:
            score_proponente = st.selectbox("Score SPC — preenchimento manual", ["", "A - B", "C - D", "E - F"], key="score_manual_v16")

        if pdf_prop and renda_proponente <= 0:
            renda_proponente = campo_moeda("Renda Presumida — manual (R$)", "renda_manual_v16")

        estado_civil = st.selectbox(
            "Estado Civil *",
            ["", "SOLTEIRO(A)", "DIVORCIADO(A)", "CASADO(A)"],
            index=0, key="estado_civil_v16",
        )

    # ── DADOS DA PROPOSTA ──
    with bloco_proposta:
        st.markdown(f"<div style='font-weight:700;color:{VERDE_ESC};margin-bottom:10px;'>Dados da Proposta</div>", unsafe_allow_html=True)
        ato_urba        = campo_moeda("Ato Urba (R$) *",                    "ato_urba_v16")
        valor_proposta  = campo_moeda("Valor da Proposta / Líquido CV (R$) *", "valor_proposta_v16")
        primeira_mensal = campo_moeda("Valor da 1ª Mensal (R$) *",          "primeira_mensal_v16")

    # ── COMPOSIÇÃO DE RENDA ──
    with bloco_renda:
        st.markdown(f"<div style='font-weight:700;color:{VERDE_ESC};margin-bottom:10px;'>Composição de Renda</div>", unsafe_allow_html=True)
        st.caption("Use somente quando houver cliente adicional compondo renda.")

        qtd_adicionais = st.number_input("Clientes adicionais", min_value=0, max_value=4, value=0, step=1, key="qtd_adicionais_v16")

        rendas_adicionais = []
        for i in range(int(qtd_adicionais)):
            numero = i + 2
            with st.expander(f"Cliente {numero}", expanded=True):
                pdf_add = st.file_uploader(f"SPC — Cliente {numero}", type=["pdf"], key=f"pdf_add_v16_{numero}")
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
                    renda_add = campo_moeda(f"Renda manual — Cliente {numero} (R$)", f"renda_add_v16_{numero}")
                rendas_adicionais.append(renda_add)

    # ── CÁLCULOS INSTANTÂNEOS ──
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

    # ── VALIDAÇÃO ──
    faltando = []
    if not empreendimento:   faltando.append("Empreendimento")
    if not unidade:          faltando.append("Unidade")
    if not nascimento:       faltando.append("Data de Nascimento")
    if not estado_civil:     faltando.append("Estado Civil")
    if not pdf_prop:         faltando.append("SPC do Proponente")
    if not score_proponente: faltando.append("Score SPC")
    if renda_total <= 0:     faltando.append("Renda Presumida")
    if valor_proposta <= 0:  faltando.append("Valor da Proposta")
    if primeira_mensal <= 0: faltando.append("1ª Mensal")

    if faltando:
        st.warning("Preencha/valide: **" + ", ".join(faltando) + "**")

    _, botao_calc = st.columns([3, 1])
    with botao_calc:
        calcular = st.button(
            "CALCULAR SIMULAÇÃO", type="primary",
            use_container_width=True, disabled=bool(faltando), key="calcular_v16",
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

    # ── RESULTADO ──
    if st.session_state.resultado:
        d = st.session_state.resultado

        st.divider()
        st.markdown(f"<div style='font-size:1.1rem;font-weight:700;color:{VERDE_ESC};margin-bottom:12px;'>Resumo da Simulação</div>", unsafe_allow_html=True)

        q1, q2, q3, q4 = st.columns(4)
        resumo_card(q1, "Empreendimento", d.get("empreendimento"))
        unidade_resumo = d.get("unidade") or ""
        emp_resumo = d.get("empreendimento") or ""
        if emp_resumo and unidade_resumo.upper().startswith(emp_resumo.upper()):
            unidade_resumo = unidade_resumo[len(emp_resumo):].lstrip(" -–—") or unidade_resumo
        resumo_card(q2, "Unidade", unidade_resumo)
        resumo_card(q3, "CPF do Proponente", d.get("cpf_proponente"))
        resumo_card(q4, "Renda Total", brl(d.get("renda_total", 0)))

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

        # ── AVALIAÇÃO DE RISCO ──
        st.markdown(f"<div style='font-size:1.1rem;font-weight:700;color:{VERDE_ESC};margin:18px 0 12px;'>Avaliação de Risco</div>", unsafe_allow_html=True)

        cor_map = {
            "green":  (VERDE,   VERDE_CLARO,  "BAIXO RISCO"),
            "orange": (LARANJA, LARANJA_CL,   "RISCO MODERADO"),
            "red":    ("#C0392B","#FDECEA",   "ALTO RISCO"),
        }
        cor_hex, cor_bg, _ = cor_map[d["cor"]]

        r1, r2 = st.columns([1, 2])
        with r1:
            st.markdown(f"""
            <div style="background:{cor_bg};border:2px solid {cor_hex};border-radius:14px;
                        padding:22px 20px;text-align:center;">
              <div style="font-size:0.75rem;font-weight:700;letter-spacing:0.1em;
                          text-transform:uppercase;color:{cor_hex};margin-bottom:6px;">
                Score Final
              </div>
              <div style="font-size:3rem;font-weight:800;color:{cor_hex};line-height:1;">
                {d['score_final']}
              </div>
              <div style="font-size:0.8rem;color:{CINZA_MED};margin:4px 0 10px;">
                de {SCORE_MAX} pontos
              </div>
              <div style="background:{cor_hex};color:#fff;border-radius:8px;
                          padding:6px 12px;font-weight:700;font-size:0.88rem;">
                {d['classificacao']}
              </div>
            </div>
            """, unsafe_allow_html=True)

        with r2:
            labels = {
                "score_credito":         "Score de Crédito",
                "ato":                   "% do Ato",
                "comprometimento_renda": "Comprometimento de Renda",
                "idade":                 "Faixa Etária",
                "estado_civil":          "Estado Civil",
            }
            max_nota = {"score_credito":5,"ato":5,"comprometimento_renda":5,"idade":5,"estado_civil":3}
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
                pd.DataFrame(detalhes), use_container_width=True, hide_index=True,
                column_config={
                    "Variável": st.column_config.TextColumn("Variável", width="medium"),
                    "Nota":     st.column_config.TextColumn("Nota",     width="small"),
                    "Peso":     st.column_config.NumberColumn("Peso",   width="small"),
                    "Pontos":   st.column_config.NumberColumn("Pontos", width="small"),
                    "Máximo":   st.column_config.NumberColumn("Máximo", width="small"),
                },
            )

        # ── ESTRATÉGIAS ──
        if d["classificacao"] != "BAIXO RISCO":
            st.divider()
            st.markdown(f"<div style='font-size:1.1rem;font-weight:700;color:{VERDE_ESC};margin-bottom:12px;'>Estratégias de Estruturação da Venda</div>", unsafe_allow_html=True)

            falta_mod   = max(0, LIMITE_MODERADO - d["score_final"])
            falta_baixo = max(0, LIMITE_BAIXO    - d["score_final"])
            a1, b1 = st.columns(2)
            a1.metric("Pontos para Risco Moderado", f"+{falta_mod}")
            b1.metric("Pontos para Baixo Risco",    f"+{falta_baixo}")

            cenarios = montar_cenarios(
                score_atual=d["score_final"], notas=d["notas"],
                renda_total=d["renda_total"], mensal=d["primeira_mensal"],
                ato=d["ato_urba"], valor_proposta=d["valor_proposta"],
            )
            if cenarios:
                df_c = pd.DataFrame(cenarios)
                df_c["Ganho"]     = df_c["Ganho"].map(lambda x: f"+{x}")
                df_c["NovoScore"] = df_c["NovoScore"].map(str)
                df_exib = df_c[["Variável","Ajuste","Ganho","NovoScore","NovaClassificacao"]].head(12).rename(columns={
                    "NovoScore": "Novo Score", "NovaClassificacao": "Nova Classificação"
                })
                st.dataframe(df_exib, use_container_width=True, hide_index=True)
                st.caption("As sugestões são simulações contrafactuais. Não são propostas alterações de idade, estado civil ou score cadastral.")

        # ── SALVAR ──
        st.divider()
        st.markdown(f"<div style='font-size:1.1rem;font-weight:700;color:{VERDE_ESC};margin-bottom:6px;'>Salvar Simulação</div>", unsafe_allow_html=True)
        st.caption("Confirme para registrar esta simulação no histórico.")

        if st.button("CONFIRMAR E SALVAR NO HISTÓRICO", type="primary", key="salvar_v16"):
            try:
                salvar_simulacao(d, usuario["email"])
                st.success("Simulação salva com sucesso no histórico.")
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")


# ============================================================
# PÁGINA: HISTÓRICO
# ============================================================
elif st.session_state.pagina == "Histórico" and eh_admin:

    st.markdown(f"<div style='font-size:1.1rem;font-weight:700;color:{VERDE_ESC};margin-bottom:16px;'>Histórico de Simulações</div>", unsafe_allow_html=True)

    try:
        hist = carregar_historico()
    except Exception as e:
        st.error(f"Erro ao carregar histórico: {e}")
        hist = pd.DataFrame()

    if hist.empty:
        st.info("Nenhuma simulação registrada ainda.")
    else:
        c1, c2, c3 = st.columns(3)
        with c1:
            vendedores = ["TODOS"] + sorted(hist["Vendedor"].dropna().unique().tolist())
            filtro_v = st.selectbox("Vendedor", vendedores, key="filt_vend_v16")
        with c2:
            emps = ["TODOS"] + sorted(hist["Empreendimento"].dropna().unique().tolist())
            filtro_e = st.selectbox("Empreendimento", emps, key="filt_emp_v16")
        with c3:
            classes = ["TODAS"] + sorted(hist["Classificação"].dropna().unique().tolist())
            filtro_c = st.selectbox("Classificação", classes, key="filt_class_v16")

        exib = hist.copy()
        if filtro_v != "TODOS":  exib = exib[exib["Vendedor"] == filtro_v]
        if filtro_e != "TODOS":  exib = exib[exib["Empreendimento"] == filtro_e]
        if filtro_c != "TODAS":  exib = exib[exib["Classificação"] == filtro_c]

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total",       len(exib))
        k2.metric("Baixo Risco", int(exib["Classificação"].astype(str).str.contains("BAIXO",    na=False).sum()))
        k3.metric("Moderado",    int(exib["Classificação"].astype(str).str.contains("MODERADO", na=False).sum()))
        k4.metric("Alto Risco",  int(exib["Classificação"].astype(str).str.contains("ALTO",     na=False).sum()))

        st.dataframe(exib, use_container_width=True, hide_index=True)

        st.download_button(
            "BAIXAR HISTÓRICO (CSV)",
            exib.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"historico_urba_{datetime.now(TIMEZONE_BRASILIA).strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv", use_container_width=True,
        )

    st.divider()
    with st.expander("Excluir todo o histórico", expanded=False):
        st.warning("Esta ação remove permanentemente todos os registros do banco de dados.")
        confirmar = st.checkbox("Confirmo que desejo excluir TODO o histórico", key="conf_del_v16")
        if st.button("EXCLUIR TODO O HISTÓRICO", type="primary", disabled=not confirmar, key="del_hist_v16"):
            try:
                limpar_historico()
                st.success("Histórico excluído com sucesso.")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao excluir: {e}")


# ============================================================
# PÁGINA: USUÁRIOS
# ============================================================
elif st.session_state.pagina == "Usuários" and eh_admin:

    st.markdown(f"<div style='font-size:1.1rem;font-weight:700;color:{VERDE_ESC};margin-bottom:16px;'>Gestão de Usuários</div>", unsafe_allow_html=True)

    with st.expander("Adicionar novo usuário", expanded=False):
        u1, u2 = st.columns(2)
        with u1:
            novo_nome  = st.text_input("Nome completo", key="novo_nome_v16")
            novo_email = st.text_input("E-mail",        key="novo_email_v16")
        with u2:
            novo_perfil = st.selectbox("Perfil", ["VENDEDOR", "ADMINISTRADOR"], key="novo_perfil_v16")
            nova_senha  = st.text_input("Senha",  type="password", key="nova_senha_v16")

        if st.button("CRIAR USUÁRIO", type="primary", key="criar_usr_v16"):
            if not all([novo_nome, novo_email, nova_senha]):
                st.error("Preencha todos os campos.")
            else:
                try:
                    criar_usuario(novo_nome, novo_email, nova_senha, novo_perfil)
                    st.success(f"Usuário {novo_nome} criado com sucesso.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao criar usuário: {e}")

    st.divider()
    try:
        usuarios_lista = listar_usuarios()
    except Exception as e:
        st.error(f"Erro ao listar usuários: {e}")
        usuarios_lista = []

    if not usuarios_lista:
        st.info("Nenhum usuário cadastrado.")
    else:
        for u in usuarios_lista:
            with st.container(border=True):
                col_info, col_status, col_acao = st.columns([3, 1, 1])
                with col_info:
                    st.markdown(f"**{u['nome']}**")
                    st.caption(f"{u['email']} • {u['perfil']}")
                with col_status:
                    status_cor  = VERDE   if u["ativo"] else "#999"
                    status_txt  = "Ativo" if u["ativo"] else "Inativo"
                    st.markdown(f"<span style='color:{status_cor};font-weight:700;'>{status_txt}</span>", unsafe_allow_html=True)
                with col_acao:
                    if u["email"] != usuario["email"]:
                        label_toggle = "Desativar" if u["ativo"] else "Ativar"
                        if st.button(label_toggle, key=f"toggle_{u['id']}", use_container_width=True):
                            toggle_usuario(u["id"], not u["ativo"])
                            st.rerun()
                    else:
                        st.caption("(você)")

# ── RODAPÉ ──
st.markdown(f"""
<div style="text-align:center;padding:24px 0 8px;
            color:{CINZA_MED};font-size:0.78rem;border-top:1px solid {CINZA_BORDA};
            margin-top:32px;">
  <strong style="color:{VERDE};">Urba</strong> • Simulador de Score de Vendas V16.3 •
  Projeto Defensores do Contrato
</div>
""", unsafe_allow_html=True)
