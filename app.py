"""
Observatório Ligue 180 · Pernambuco
Violências contra a mulher — 2021–2025
Fonte: Ministério da Mulher
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG  (deve ser o primeiro comando Streamlit)
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Observatório Ligue 180 · PE",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────────────────────────────────────
DATA_PATH = Path(r"C:\Users\arthu\OneDrive\Programas - Copia\IC-Feminicidio\EDA\basegeral_2021-2025.csv")

PALETTE = [
    "#5E1675", "#8B2FC9", "#A855F7", "#C77DFF",
    "#E0AAFF", "#FF6B9D", "#FFB3C6", "#9CA3AF",
]

MESES_PT = {
    1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr",
    5: "Mai", 6: "Jun", 7: "Jul", 8: "Ago",
    9: "Set", 10: "Out", 11: "Nov", 12: "Dez",
}

# Ordenação cronológica das faixas etárias presentes no dataset
FAIXA_ORDER = [
    "0 A 1 Anos", "0 A 4 Anos", "2 A 5 Anos", "5 A 11 Anos", "6 A 9 Anos",
    "10 A 12 Anos", "12 A 14 Anos", "13 A 15 Anos", "15 A 17 Anos", "16 A 17 Anos",
    "18 A 19 Anos", "20 A 24 Anos", "25 A 29 Anos", "30 A 34 Anos", "35 A 39 Anos",
    "40 A 44 Anos", "45 A 49 Anos", "50 A 54 Anos", "55 A 59 Anos", "60 A 64 Anos",
    "65 A 69 Anos", "70 A 74 Anos", "75 A 79 Anos", "80 A 84 Anos",
    "85 A 89 Anos", "90+", "Não Informado",
]

INSTRUCAO_ORDER = [
    "Analfabeto/Sem Instrucao", "Ensino Fundamental Incompleto",
    "Ensino Fundamental Completo", "Ensino Medio Incompleto",
    "Ensino Medio Completo", "Superior Incompleto", "Superior Completo",
    "Pos-Graduacao", "Mestrado", "Doutorado", "Pos-Doutorado", "Não Informado",
]

# ─────────────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

.dash-header {
    background: linear-gradient(135deg, #3b0764 0%, #6d28d9 55%, #a855f7 100%);
    padding: 1.6rem 2rem;
    border-radius: 14px;
    margin-bottom: 1.4rem;
    color: white;
}
.dash-header h1 { font-size: 1.65rem; font-weight: 700; margin: 0 0 .25rem; }
.dash-header p  { opacity: .75; margin: 0; font-size: .9rem; }

.kpi-card {
    background: white;
    border-left: 5px solid #7e22ce;
    border-radius: 12px;
    padding: 1rem 1.3rem;
    box-shadow: 0 2px 10px rgba(94,22,117,.1);
    height: 100%;
}
.kpi-value { font-size: 1.8rem; font-weight: 700; color: #5e1675; line-height: 1.15; }
.kpi-label { font-size: .78rem; color: #6b7280; text-transform: uppercase;
             letter-spacing: .05em; margin-top: .25rem; }

.section-title {
    font-size: 1rem; font-weight: 700; color: #5e1675;
    margin: 1.2rem 0 .6rem;
    padding-bottom: .3rem;
    border-bottom: 2px solid #e0aaff;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 4px; background: white;
    padding: 5px; border-radius: 12px;
    box-shadow: 0 2px 8px rgba(94,22,117,.1);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    padding: 6px 20px !important;
    font-weight: 600; color: #7e22ce !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg,#6d28d9,#a855f7) !important;
    color: white !important;
}

.sim-result {
    background: linear-gradient(135deg, #3b0764, #6d28d9);
    color: white; border-radius: 14px;
    padding: 1.5rem 2rem; margin-top: 1rem;
}
.sim-result .grupo-title { font-size: 1.4rem; font-weight: 700; margin-bottom: .4rem; }

.sim-placeholder {
    background: #fefce8; border: 2px dashed #ca8a04;
    border-radius: 10px; padding: 1rem 1.5rem; margin-top: 1rem;
    color: #78350f; font-size: .9rem;
}

.note-box {
    background: #f0fdf4; border-left: 4px solid #22c55e;
    border-radius: 8px; padding: .75rem 1rem;
    font-size: .85rem; color: #166534;
}

#MainMenu, footer { visibility: hidden; }
div[data-testid="stToolbar"] { display: none; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# CARREGAMENTO DOS DADOS
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Carregando dados...")
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, index_col=0)
    df["data_de_cadastro"] = pd.to_datetime(df["data_de_cadastro"], errors="coerce")

    text_cols = [
        "grupo", "violacao", "municipio", "cenario_da_violacao",
        "genero_da_vitima", "genero_do_suspeito", "raca_cor_da_vitima",
        "relacao_vitima_suspeito", "faixa_etaria_da_vitima",
        "faixa_etaria_do_suspeito", "motivacao", "grau_de_instrucao_da_vitima",
    ]
    for col in text_cols:
        df[col] = df[col].fillna("Não Informado").str.strip().str.title()

    df["mes_nome"] = df["mes"].map(MESES_PT)
    return df


df = load_data()


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def chart_layout(fig, height=370):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#374151", size=12),
        height=height,
        margin=dict(l=8, r=8, t=36, b=8),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_xaxes(showgrid=False, linecolor="#e5e7eb", linewidth=1)
    fig.update_yaxes(gridcolor="#f3e8ff", linecolor="#e5e7eb", linewidth=1)
    return fig


def kpi_card(col, value, label):
    col.markdown(
        f'<div class="kpi-card">'
        f'<div class="kpi-value">{value}</div>'
        f'<div class="kpi-label">{label}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def ordered_categorical(series: pd.Series, order: list) -> pd.Categorical:
    present = [v for v in order if v in series.values]
    extra   = [v for v in series.values if v not in present]
    return pd.Categorical(series, categories=present + extra, ordered=True)


# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="dash-header">
  <h1>🔴 Observatório Ligue 180 · Pernambuco</h1>
  <p>Violências contra a mulher &nbsp;·&nbsp; 2021–2025 &nbsp;·&nbsp;
     Fonte: Ministério da Mulher / Serviço Ligue 180</p>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────────────────────
t_geral, t_temporal, t_perfil, t_geo, t_sim = st.tabs([
    "📊  Visão Geral",
    "📈  Série Temporal",
    "👤  Perfil da Vítima",
    "🗺️  Distribuição Geográfica",
    "🤖  Simulador de Risco",
])


# ═══════════════════════════════════════════════════════════════════════════
# TAB 1 — VISÃO GERAL
# ═══════════════════════════════════════════════════════════════════════════
with t_geral:
    with st.expander("🔎 Filtros", expanded=False):
        fc1, fc2 = st.columns(2)
        anos_g = fc1.multiselect(
            "Ano", sorted(df["ano"].unique()), default=sorted(df["ano"].unique()), key="g_anos"
        )
        grupos_g = fc2.multiselect(
            "Macrogrupo", sorted(df["grupo"].unique()),
            default=sorted(df["grupo"].unique()), key="g_grupos"
        )

    dg = df[df["ano"].isin(anos_g) & df["grupo"].isin(grupos_g)]

    # KPIs ──────────────────────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    kpi_card(k1, f"{len(dg):,}".replace(",", "."), "Ocorrências registradas")
    kpi_card(k2, dg["violacao"].value_counts().idxmax(), "Violação mais frequente")
    kpi_card(k3, dg["municipio"].value_counts().idxmax().title(), "Município com mais casos")
    kpi_card(k4, str(int(dg["ano"].value_counts().idxmax())), "Ano com mais registros")

    st.markdown('<div class="section-title">Distribuição por Macrogrupo e Tipo de Violação</div>', unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1.8])

    with c1:
        gdata = dg["grupo"].value_counts().reset_index()
        gdata.columns = ["Macrogrupo", "Casos"]
        fig = px.pie(gdata, values="Casos", names="Macrogrupo",
                     hole=0.52, color_discrete_sequence=PALETTE)
        fig.update_traces(textinfo="percent+label", textfont_size=12)
        fig.update_layout(showlegend=False)
        st.plotly_chart(chart_layout(fig, 360), use_container_width=True)

    with c2:
        vdata = dg["violacao"].value_counts().head(12).reset_index()
        vdata.columns = ["Violação", "Casos"]
        fig = px.bar(
            vdata.sort_values("Casos"), x="Casos", y="Violação",
            orientation="h", color="Casos",
            color_continuous_scale="Purples",
        )
        fig.update_layout(
            coloraxis_showscale=False,
            yaxis_title=None, xaxis_title="Nº de casos",
        )
        st.plotly_chart(chart_layout(fig, 400), use_container_width=True)

    st.markdown('<div class="section-title">Contexto das Violações</div>', unsafe_allow_html=True)
    c3, c4 = st.columns(2)

    with c3:
        rel = dg["relacao_vitima_suspeito"].value_counts().head(12).reset_index()
        rel.columns = ["Relação", "Casos"]
        fig = px.bar(
            rel.sort_values("Casos"), x="Casos", y="Relação",
            orientation="h", color_discrete_sequence=[PALETTE[0]],
            title="Relação Vítima–Suspeito",
        )
        fig.update_layout(yaxis_title=None, title_font_size=13)
        st.plotly_chart(chart_layout(fig, 380), use_container_width=True)

    with c4:
        loc = dg["cenario_da_violacao"].value_counts().reset_index()
        loc.columns = ["Local", "Casos"]
        fig = px.bar(
            loc.sort_values("Casos"), x="Casos", y="Local",
            orientation="h", color_discrete_sequence=[PALETTE[2]],
            title="Local da Violação",
        )
        fig.update_layout(yaxis_title=None, title_font_size=13)
        st.plotly_chart(chart_layout(fig, 380), use_container_width=True)

    st.markdown('<div class="section-title">Motivação do Crime</div>', unsafe_allow_html=True)
    mot = dg["motivacao"].value_counts().reset_index()
    mot.columns = ["Motivação", "Casos"]
    fig = px.bar(
        mot.sort_values("Casos"), x="Casos", y="Motivação",
        orientation="h", color="Casos", color_continuous_scale="Purples",
    )
    fig.update_layout(coloraxis_showscale=False, yaxis_title=None)
    st.plotly_chart(chart_layout(fig, 350), use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════
# TAB 2 — SÉRIE TEMPORAL
# ═══════════════════════════════════════════════════════════════════════════
with t_temporal:
    st.markdown('<div class="section-title">Ocorrências mensais — comparação por ano</div>', unsafe_allow_html=True)

    tc1, tc2, tc3 = st.columns([2, 1.5, 1])
    anos_t = tc1.multiselect(
        "Anos para comparar",
        sorted(df["ano"].unique()),
        default=sorted(df["ano"].unique()),
        key="t_anos",
    )
    grupo_t = tc2.selectbox(
        "Filtrar por macrogrupo",
        ["Todos"] + sorted(df["grupo"].unique()),
        key="t_grupo",
    )
    violacao_t = tc3.selectbox(
        "Filtrar por violação",
        ["Todas"] + sorted(df["violacao"].unique()),
        key="t_violacao",
    )

    dt = df[df["ano"].isin(anos_t)]
    if grupo_t != "Todos":
        dt = dt[dt["grupo"] == grupo_t]
    if violacao_t != "Todas":
        dt = dt[dt["violacao"] == violacao_t]

    monthly = (
        dt.groupby(["ano", "mes"])
        .size()
        .reset_index(name="casos")
    )
    monthly["ano"] = monthly["ano"].astype(str)

    fig = px.line(
        monthly, x="mes", y="casos", color="ano",
        markers=True,
        labels={"mes": "Mês", "casos": "Nº de casos", "ano": "Ano"},
        color_discrete_sequence=PALETTE,
    )
    fig.update_xaxes(
        tickvals=list(range(1, 13)),
        ticktext=list(MESES_PT.values()),
    )
    fig.update_traces(line_width=2.5, marker_size=7)
    st.plotly_chart(chart_layout(fig, 430), use_container_width=True)

    # Totais anuais
    st.markdown('<div class="section-title">Total anual de ocorrências</div>', unsafe_allow_html=True)
    anual = dt.groupby("ano").size().reset_index(name="casos")
    anual["ano"] = anual["ano"].astype(str)

    fig = px.bar(
        anual, x="ano", y="casos", color="ano",
        color_discrete_sequence=PALETTE,
        text="casos",
    )
    fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
    fig.update_layout(showlegend=False, xaxis_title="Ano", yaxis_title="Total de casos")
    st.plotly_chart(chart_layout(fig, 310), use_container_width=True)

    # Evolução por macrogrupo ao longo dos anos
    st.markdown('<div class="section-title">Evolução por macrogrupo</div>', unsafe_allow_html=True)
    grupo_anual = (
        dt.groupby(["ano", "grupo"])
        .size()
        .reset_index(name="casos")
    )
    grupo_anual["ano"] = grupo_anual["ano"].astype(str)
    fig = px.bar(
        grupo_anual, x="ano", y="casos", color="grupo",
        color_discrete_sequence=PALETTE,
        barmode="stack",
        labels={"ano": "Ano", "casos": "Casos", "grupo": "Macrogrupo"},
    )
    fig.update_layout(xaxis_title="Ano", yaxis_title="Casos")
    st.plotly_chart(chart_layout(fig, 350), use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════
# TAB 3 — PERFIL DA VÍTIMA
# ═══════════════════════════════════════════════════════════════════════════
with t_perfil:
    with st.expander("🔎 Filtros", expanded=False):
        pc1, pc2, pc3 = st.columns(3)
        anos_p = pc1.multiselect(
            "Ano", sorted(df["ano"].unique()), default=sorted(df["ano"].unique()), key="p_anos"
        )
        grupo_p = pc2.selectbox("Macrogrupo", ["Todos"] + sorted(df["grupo"].unique()), key="p_grupo")
        violacao_p = pc3.selectbox("Violação", ["Todas"] + sorted(df["violacao"].unique()), key="p_violacao")

    dp = df[df["ano"].isin(anos_p)]
    if grupo_p != "Todos":
        dp = dp[dp["grupo"] == grupo_p]
    if violacao_p != "Todas":
        dp = dp[dp["violacao"] == violacao_p]

    # Linha 1: Raça/Cor e Gênero
    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<div class="section-title">Raça / Cor da Vítima</div>', unsafe_allow_html=True)
        rc = dp["raca_cor_da_vitima"].value_counts().reset_index()
        rc.columns = ["Raça/Cor", "Casos"]
        fig = px.bar(rc, x="Raça/Cor", y="Casos", color="Raça/Cor",
                     color_discrete_sequence=PALETTE, text="Casos")
        fig.update_traces(texttemplate="%{text:,}", textposition="outside")
        fig.update_layout(showlegend=False, xaxis_title=None)
        st.plotly_chart(chart_layout(fig, 330), use_container_width=True)

    with c2:
        st.markdown('<div class="section-title">Gênero da Vítima</div>', unsafe_allow_html=True)
        gen = dp["genero_da_vitima"].value_counts().reset_index()
        gen.columns = ["Gênero", "Casos"]
        fig = px.pie(gen, values="Casos", names="Gênero",
                     hole=0.48, color_discrete_sequence=PALETTE)
        fig.update_traces(textinfo="percent+label")
        fig.update_layout(showlegend=False)
        st.plotly_chart(chart_layout(fig, 330), use_container_width=True)

    # Linha 2: Faixa Etária e Grau de Instrução
    c3, c4 = st.columns(2)

    with c3:
        st.markdown('<div class="section-title">Faixa Etária da Vítima</div>', unsafe_allow_html=True)
        fe = dp["faixa_etaria_da_vitima"].value_counts().reset_index()
        fe.columns = ["Faixa", "Casos"]
        fe["Faixa"] = ordered_categorical(fe["Faixa"], FAIXA_ORDER)
        fe = fe.sort_values("Faixa")
        fig = px.bar(fe, x="Faixa", y="Casos", color_discrete_sequence=[PALETTE[1]])
        fig.update_layout(xaxis_tickangle=-40, xaxis_title=None)
        st.plotly_chart(chart_layout(fig, 360), use_container_width=True)

    with c4:
        st.markdown('<div class="section-title">Grau de Instrução da Vítima</div>', unsafe_allow_html=True)
        gi = dp["grau_de_instrucao_da_vitima"].value_counts().reset_index()
        gi.columns = ["Instrução", "Casos"]
        gi["Instrução"] = ordered_categorical(gi["Instrução"], INSTRUCAO_ORDER)
        gi = gi.sort_values("Instrução")
        fig = px.bar(
            gi, x="Casos", y="Instrução",
            orientation="h", color_discrete_sequence=[PALETTE[3]],
        )
        fig.update_layout(yaxis_title=None)
        st.plotly_chart(chart_layout(fig, 360), use_container_width=True)

    # Heatmap: raça x macrogrupo
    st.markdown('<div class="section-title">Tipo de Violação por Raça/Cor (heatmap)</div>', unsafe_allow_html=True)
    heat_data = dp.groupby(["raca_cor_da_vitima", "grupo"]).size().unstack(fill_value=0)
    fig = px.imshow(
        heat_data,
        color_continuous_scale="Purples",
        labels=dict(x="Macrogrupo", y="Raça/Cor", color="Casos"),
        aspect="auto",
        text_auto=True,
    )
    fig.update_layout(coloraxis_showscale=True)
    st.plotly_chart(chart_layout(fig, 300), use_container_width=True)

    # Linha 3: perfil do suspeito
    st.markdown('<div class="section-title">Perfil do Suspeito</div>', unsafe_allow_html=True)
    s1, s2 = st.columns(2)

    with s1:
        gs = dp["genero_do_suspeito"].value_counts().reset_index()
        gs.columns = ["Gênero", "Casos"]
        fig = px.pie(gs, values="Casos", names="Gênero",
                     hole=0.48, color_discrete_sequence=PALETTE,
                     title="Gênero do Suspeito")
        fig.update_traces(textinfo="percent+label")
        fig.update_layout(showlegend=False, title_font_size=13)
        st.plotly_chart(chart_layout(fig, 300), use_container_width=True)

    with s2:
        fes = dp["faixa_etaria_do_suspeito"].value_counts().reset_index()
        fes.columns = ["Faixa", "Casos"]
        fes["Faixa"] = ordered_categorical(fes["Faixa"], FAIXA_ORDER)
        fes = fes.sort_values("Faixa")
        fig = px.bar(fes, x="Faixa", y="Casos",
                     color_discrete_sequence=[PALETTE[0]],
                     title="Faixa Etária do Suspeito")
        fig.update_layout(xaxis_tickangle=-40, xaxis_title=None, title_font_size=13)
        st.plotly_chart(chart_layout(fig, 300), use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════
# TAB 4 — DISTRIBUIÇÃO GEOGRÁFICA
# ═══════════════════════════════════════════════════════════════════════════
with t_geo:
    with st.expander("🔎 Filtros", expanded=False):
        gc1, gc2, gc3 = st.columns(3)
        anos_geo = gc1.multiselect(
            "Ano", sorted(df["ano"].unique()), default=sorted(df["ano"].unique()), key="geo_anos"
        )
        grupo_geo = gc2.selectbox("Macrogrupo", ["Todos"] + sorted(df["grupo"].unique()), key="geo_grupo")
        top_n = gc3.slider("Top N municípios", min_value=5, max_value=50, value=20, step=5)

    dg2 = df[df["ano"].isin(anos_geo)]
    if grupo_geo != "Todos":
        dg2 = dg2[dg2["grupo"] == grupo_geo]

    # Top municípios
    st.markdown(f'<div class="section-title">Top {top_n} municípios por número de ocorrências</div>', unsafe_allow_html=True)
    mun = dg2["municipio"].value_counts().head(top_n).reset_index()
    mun.columns = ["Município", "Casos"]
    fig = px.bar(
        mun.sort_values("Casos"), x="Casos", y="Município",
        orientation="h", color="Casos",
        color_continuous_scale="Purples",
    )
    fig.update_layout(coloraxis_showscale=False, yaxis_title=None)
    st.plotly_chart(chart_layout(fig, max(380, top_n * 22)), use_container_width=True)

    # Treemap município x macrogrupo
    st.markdown('<div class="section-title">Distribuição proporcional por município e macrogrupo</div>', unsafe_allow_html=True)

    top_muns = dg2["municipio"].value_counts().head(30).index.tolist()
    tree_data = (
        dg2[dg2["municipio"].isin(top_muns)]
        .groupby(["municipio", "grupo"])
        .size()
        .reset_index(name="casos")
    )
    fig = px.treemap(
        tree_data,
        path=["municipio", "grupo"],
        values="casos",
        color="casos",
        color_continuous_scale="Purples",
    )
    fig.update_layout(margin=dict(t=30, l=0, r=0, b=0), height=480)
    st.plotly_chart(fig, use_container_width=True)

    # Tabela resumo
    st.markdown('<div class="section-title">Tabela de ocorrências por município</div>', unsafe_allow_html=True)
    tabela_mun = (
        dg2.groupby(["municipio", "grupo"])
        .size()
        .unstack(fill_value=0)
        .assign(Total=lambda x: x.sum(axis=1))
        .sort_values("Total", ascending=False)
    )
    tabela_mun.index.name = "Município"
    st.dataframe(
        tabela_mun.style.background_gradient(cmap="Purples", subset=["Total"]),
        use_container_width=True,
        height=320,
    )

    st.markdown(
        '<div class="note-box">🗺️ Mapa geográfico interativo (choropleth) será implementado '
        'na versão final com dados de geocodificação dos municípios de Pernambuco.</div>',
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════
# TAB 5 — SIMULADOR
# ═══════════════════════════════════════════════════════════════════════════
with t_sim:
    st.markdown("""
    <div class="section-title">Simulador de Classificação de Risco</div>
    <p style="color:#6b7280; font-size:.9rem; margin-bottom:1.2rem;">
      Preencha o perfil da vítima e o contexto da violação para obter a classificação
      de risco pelo modelo de Machine Learning treinado nos dados do Ligue 180.
      <br><br>
      <strong>Público-alvo:</strong> pesquisadores/as, gestores/as públicos/as e profissionais
      do atendimento. Os resultados são probabilísticos e não substituem avaliação especializada.
    </p>
    """, unsafe_allow_html=True)

    # Opções disponíveis no dataset (já normalizadas via str.title)
    faixas_vitima  = [f for f in FAIXA_ORDER if f in df["faixa_etaria_da_vitima"].unique()]
    faixas_suspeito = [f for f in FAIXA_ORDER if f in df["faixa_etaria_do_suspeito"].unique()]

    with st.form("sim_form"):
        col_v, col_s, col_ctx = st.columns(3)

        with col_v:
            st.subheader("👩 Perfil da Vítima")
            s_genero_v = st.selectbox(
                "Gênero", sorted(df["genero_da_vitima"].unique()), key="sv_gen"
            )
            s_faixa_v = st.selectbox(
                "Faixa etária", faixas_vitima, key="sv_faixa"
            )
            s_raca = st.selectbox(
                "Raça / Cor",
                [v for v in df["raca_cor_da_vitima"].unique() if v != "Não Informado"]
                + ["Não Informado"],
                key="sv_raca",
            )
            s_instrucao = st.selectbox(
                "Grau de instrução",
                [v for v in INSTRUCAO_ORDER if v in df["grau_de_instrucao_da_vitima"].unique()],
                key="sv_inst",
            )

        with col_s:
            st.subheader("🕵️ Perfil do Suspeito")
            s_genero_s = st.selectbox(
                "Gênero", sorted(df["genero_do_suspeito"].unique()), key="ss_gen"
            )
            s_faixa_s = st.selectbox(
                "Faixa etária", faixas_suspeito, key="ss_faixa"
            )
            s_relacao = st.selectbox(
                "Relação com a vítima",
                sorted(df["relacao_vitima_suspeito"].unique()),
                key="ss_rel",
            )

        with col_ctx:
            st.subheader("📍 Contexto")
            s_municipio = st.selectbox(
                "Município",
                sorted(df["municipio"].unique()),
                key="ctx_mun",
            )
            s_local = st.selectbox(
                "Local da violação",
                sorted(df["cenario_da_violacao"].unique()),
                key="ctx_local",
            )
            s_motivacao = st.selectbox(
                "Motivação",
                ["Não Informado"] + sorted(
                    [v for v in df["motivacao"].unique() if v != "Não Informado"]
                ),
                key="ctx_mot",
            )

        submitted = st.form_submit_button(
            "🔍  Classificar risco", use_container_width=True
        )

    if submitted:
        input_dict = {
            "genero_da_vitima":            s_genero_v,
            "faixa_etaria_da_vitima":      s_faixa_v,
            "raca_cor_da_vitima":          s_raca,
            "grau_de_instrucao_da_vitima": s_instrucao,
            "genero_do_suspeito":          s_genero_s,
            "faixa_etaria_do_suspeito":    s_faixa_s,
            "relacao_vitima_suspeito":     s_relacao,
            "municipio":                   s_municipio,
            "cenario_da_violacao":         s_local,
            "motivacao":                   s_motivacao,
        }

        # ── Placeholder: substituir pela chamada ao modelo real ──────────────
        st.markdown("""
        <div class="sim-result">
          <div style="font-size:.72rem; opacity:.65; text-transform:uppercase;
                      letter-spacing:.12em; margin-bottom:.4rem;">
            Resultado da Classificação
          </div>
          <div class="grupo-title">⚠️ Modelo não integrado</div>
          <div style="opacity:.85; font-size:.93rem; line-height:1.6; margin-top:.5rem;">
            O modelo de Machine Learning será integrado nesta etapa.<br>
            Quando disponível, este painel exibirá:
            <ul style="margin:.5rem 0 0 1rem;">
              <li>O <strong>grupo de cluster</strong> identificado (ex.: Grupo 2)</li>
              <li>As <strong>violações associadas</strong> ao cluster</li>
              <li>O <strong>nível de confiança</strong> da predição</li>
            </ul>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="sim-placeholder" style="margin-top:1rem;">
          <strong>⚙️ Para integrar o modelo:</strong> substitua o bloco de placeholder
          no código por <code>modelo.predict(input_dict)</code> e mapeie o cluster
          retornado para o nome do grupo e suas violações correspondentes.
        </div>
        """, unsafe_allow_html=True)

        st.markdown("**Dados capturados para predição:**")
        st.json(input_dict)

        # Distribuição histórica para o perfil similar (análise descritiva)
        st.markdown('<div class="section-title">Distribuição histórica para perfil similar</div>', unsafe_allow_html=True)
        st.caption("Casos registrados com o mesmo local e relação vítima–suspeito selecionados.")
        filtro_similar = df[
            (df["cenario_da_violacao"] == s_local) &
            (df["relacao_vitima_suspeito"] == s_relacao)
        ]
        if len(filtro_similar) > 0:
            hist_viol = filtro_similar["violacao"].value_counts().head(8).reset_index()
            hist_viol.columns = ["Violação", "Casos"]
            fig = px.bar(
                hist_viol.sort_values("Casos"), x="Casos", y="Violação",
                orientation="h", color="Casos", color_continuous_scale="Purples",
            )
            fig.update_layout(coloraxis_showscale=False, yaxis_title=None)
            st.plotly_chart(chart_layout(fig, 320), use_container_width=True)
        else:
            st.info("Nenhum caso histórico encontrado para este perfil.")
