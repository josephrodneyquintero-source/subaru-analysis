"""
Módulo de Visualizaciones Web e Interactivas (Plotly)
Proyecto: Análisis de Mercado Automotriz y Desempeño de Subaru en Panamá (2018-2023)
Ruta: src/visualizations.py
"""

from typing import Dict, Any
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# =====================================================================
# CONFIGURACIÓN DE TEMA CORPORATIVO (SUBARU EXECUTIVE LIGHT THEME)
# =====================================================================
PALETA = {
    "fondo_card": "#ffffff",
    "texto_principal": "#0f172a",  # Slate 900
    "texto_secundario": "#64748b", # Slate 500
    "azul_subaru": "#003399",      # Azul Oficial Subaru
    "azul_secundario": "#0148A4",  # Azul Royal
    "azul_claro": "#38bdf8",       # Sky 400
    "naranja_acento": "#f97316",   # Orange 500
    "verde_exito": "#10b981",      # Emerald 500
    "linea_guia": "#e2e8f0"        # Slate 200
}

CONFIG_PLOTLY = {
    "responsive": True,
    "displayModeBar": False,
    "showTips": False
}


def _aplicar_estilo_base(fig: go.Figure, titulo: str) -> go.Figure:
    """Aplica tipografía, colores claros, autosize y márgenes holgados a la figura Plotly."""
    fig.update_layout(
        title=dict(
            text=f"<b>{titulo}</b>",
            font=dict(size=14, color=PALETA["texto_principal"], family="system-ui, -apple-system, sans-serif"),
            x=0.01,
            y=0.98
        ),
        autosize=True,
        height=400,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=PALETA["texto_secundario"], family="system-ui, -apple-system, sans-serif", size=11),
        margin=dict(l=50, r=30, t=55, b=50),
        hoverlabel=dict(
            bgcolor="#ffffff",
            font_size=12,
            font_color=PALETA["texto_principal"],
            font_family="system-ui, sans-serif",
            bordercolor=PALETA["linea_guia"]
        )
    )
    fig.update_xaxes(
        gridcolor=PALETA["linea_guia"],
        zerolinecolor=PALETA["linea_guia"],
        tickfont=dict(color=PALETA["texto_secundario"])
    )
    fig.update_yaxes(
        gridcolor=PALETA["linea_guia"],
        zerolinecolor=PALETA["linea_guia"],
        tickfont=dict(color=PALETA["texto_secundario"])
    )
    return fig


# =====================================================================
# SECCIÓN 1: MARKET OVERVIEW
# =====================================================================
def crear_grafico_evolucion_mercado(df: pd.DataFrame) -> str:
    """Gráfico de barras con el volumen anual del mercado automotriz total."""
    df_anio = df.groupby("Anio", as_index=False)["Valor"].sum()
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df_anio["Anio"],
        y=df_anio["Valor"],
        name="Unidades Anuales",
        marker=dict(
            color=PALETA["azul_subaru"],
            line=dict(color=PALETA["azul_secundario"], width=1)
        ),
        text=[f"{val:,.0f}" for val in df_anio["Valor"]],
        textposition="outside",
        textfont=dict(color=PALETA["texto_principal"], size=11, family="system-ui, sans-serif"),
        hovertemplate="<b>Año %{x}</b><br>Volumen: %{y:,.0f} unidades<extra></extra>"
    ))

    _aplicar_estilo_base(fig, "Evolución Anual del Mercado Total (2018 - 2023)")
    fig.update_yaxes(title_text="Unidades Vendidas", range=[0, df_anio["Valor"].max() * 1.18])
    fig.update_xaxes(dtick=1)
    
    return fig.to_html(include_plotlyjs=False, full_html=False, config=CONFIG_PLOTLY)


def crear_grafico_top10_marcas(df: pd.DataFrame) -> str:
    """Gráfico de barras horizontales con las 10 marcas con mayor volumen acumulado."""
    top10 = (
        df.groupby("Marca", as_index=False)["Valor"]
        .sum()
        .sort_values(by="Valor", ascending=False)
        .head(10)
        .sort_values(by="Valor", ascending=True)
    )
    total_mdo = df["Valor"].sum()
    top10["Share"] = (top10["Valor"] / total_mdo) * 100

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=top10["Valor"],
        y=top10["Marca"],
        orientation="h",
        marker=dict(
            color=PALETA["azul_secundario"],
            line=dict(color=PALETA["azul_subaru"], width=1)
        ),
        text=[f"{v:,.0f} ({s:.1f}%)" for v, s in zip(top10["Valor"], top10["Share"])],
        textposition="outside",
        textfont=dict(color=PALETA["texto_principal"], size=10, family="system-ui, sans-serif"),
        hovertemplate="<b>%{y}</b><br>Ventas: %{x:,.0f} unidades<br>Cuota: %{customdata:.2f}%<extra></extra>",
        customdata=top10["Share"]
    ))

    _aplicar_estilo_base(fig, "Top 10 Marcas con Mayor Volumen Acumulado")
    fig.update_xaxes(title_text="Unidades Totales", range=[0, top10["Valor"].max() * 1.25])
    
    return fig.to_html(include_plotlyjs=False, full_html=False, config=CONFIG_PLOTLY)


# =====================================================================
# SECCIÓN 2: SUBARU POSITION & MARKET SHARE
# =====================================================================
def crear_grafico_subaru_vs_mercado_indice(df: pd.DataFrame) -> str:
    """Compara trayectorias indexadas (Base 2018 = 100) con leyenda inferior separada."""
    df_mdo = df.groupby("Anio")["Valor"].sum().reset_index().rename(columns={"Valor": "Mercado"})
    df_sub = df[df["Marca"] == "SUBARU"].groupby("Anio")["Valor"].sum().reset_index().rename(columns={"Valor": "Subaru"})
    comp = pd.merge(df_mdo, df_sub, on="Anio", how="left").fillna(0)

    base_mdo = comp.loc[comp["Anio"] == 2018, "Mercado"].values[0]
    base_sub = comp.loc[comp["Anio"] == 2018, "Subaru"].values[0]

    comp["Indice_Mdo"] = (comp["Mercado"] / base_mdo) * 100
    comp["Indice_Sub"] = (comp["Subaru"] / base_sub) * 100

    fig = go.Figure()

    # Línea base 100
    fig.add_shape(
        type="line",
        x0=2018, y0=100, x1=2023, y1=100,
        line=dict(color=PALETA["linea_guia"], width=1.5, dash="dash")
    )

    # Mercado Total
    fig.add_trace(go.Scatter(
        x=comp["Anio"],
        y=comp["Indice_Mdo"],
        name="Mercado Total",
        mode="lines+markers+text",
        line=dict(color=PALETA["texto_secundario"], width=2.5),
        marker=dict(size=7, color=PALETA["texto_secundario"]),
        text=[f"{v:.1f}" for v in comp["Indice_Mdo"]],
        textposition="top center",
        textfont=dict(color=PALETA["texto_secundario"], size=10),
        hovertemplate="<b>Mercado</b> (Año %{x})<br>Índice: %{y:.1f}<extra></extra>"
    ))

    # Subaru
    fig.add_trace(go.Scatter(
        x=comp["Anio"],
        y=comp["Indice_Sub"],
        name="Subaru",
        mode="lines+markers+text",
        line=dict(color=PALETA["naranja_acento"], width=3),
        marker=dict(size=9, color=PALETA["naranja_acento"]),
        text=[f"{v:.1f}" for v in comp["Indice_Sub"]],
        textposition="bottom center",
        textfont=dict(color=PALETA["naranja_acento"], size=11),
        hovertemplate="<b>Subaru</b> (Año %{x})<br>Índice: %{y:.1f}<extra></extra>"
    ))

    _aplicar_estilo_base(fig, "Rendimiento Relativo Indexado (Base 2018 = 100)")
    fig.update_layout(
        margin=dict(l=50, r=30, t=55, b=65),
        legend=dict(
            orientation="h",
            y=-0.20,
            x=0.5,
            xanchor="center",
            font=dict(size=11, color=PALETA["texto_principal"])
        )
    )
    fig.update_yaxes(title_text="Índice (Base 100)")
    fig.update_xaxes(dtick=1)

    return fig.to_html(include_plotlyjs=False, full_html=False, config=CONFIG_PLOTLY)


def crear_grafico_market_share_subaru(df: pd.DataFrame) -> str:
    """Gráfico de barras de ventas absolutas con línea de Market Share anual de Subaru."""
    df_mdo = df.groupby("Anio")["Valor"].sum().reset_index().rename(columns={"Valor": "Mercado"})
    df_sub = df[df["Marca"] == "SUBARU"].groupby("Anio")["Valor"].sum().reset_index().rename(columns={"Valor": "Subaru"})
    comp = pd.merge(df_mdo, df_sub, on="Anio", how="left").fillna(0)
    comp["Market_Share"] = (comp["Subaru"] / comp["Mercado"]) * 100

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Barras de volumen Subaru
    fig.add_trace(
        go.Bar(
            x=comp["Anio"],
            y=comp["Subaru"],
            name="Unidades Subaru",
            marker=dict(color=PALETA["azul_subaru"]),
            hovertemplate="<b>Subaru %{x}</b><br>Volumen: %{y:,.0f} uds<extra></extra>"
        ),
        secondary_y=False
    )

    # Línea de Market Share %
    fig.add_trace(
        go.Scatter(
            x=comp["Anio"],
            y=comp["Market_Share"],
            name="Cuota de Mercado (%)",
            mode="lines+markers+text",
            line=dict(color=PALETA["naranja_acento"], width=3),
            marker=dict(size=8, color=PALETA["naranja_acento"]),
            text=[f"{ms:.2f}%" for ms in comp["Market_Share"]],
            textposition="top center",
            textfont=dict(color=PALETA["naranja_acento"], size=10),
            hovertemplate="<b>Cuota %{x}</b>: %{y:.2f}%<extra></extra>"
        ),
        secondary_y=True
    )

    _aplicar_estilo_base(fig, "Volumen y Participación de Mercado de Subaru")
    fig.update_layout(
        margin=dict(l=50, r=45, t=55, b=65),
        legend=dict(
            orientation="h",
            y=-0.20,
            x=0.5,
            xanchor="center",
            font=dict(size=11, color=PALETA["texto_principal"])
        )
    )
    fig.update_yaxes(title_text="Unidades Subaru", secondary_y=False, range=[0, comp["Subaru"].max() * 1.25])
    fig.update_yaxes(title_text="Market Share (%)", secondary_y=True, range=[0, comp["Market_Share"].max() * 1.3], showgrid=False)
    fig.update_xaxes(dtick=1)

    return fig.to_html(include_plotlyjs=False, full_html=False, config=CONFIG_PLOTLY)


# =====================================================================
# SECCIÓN 3: SUBARU PRODUCT PERFORMANCE
# =====================================================================
def crear_grafico_modelos_subaru_pie(df: pd.DataFrame) -> str:
    """Gráfico de dona de la distribución acumulada del portafolio Subaru."""
    sub_df = df[df["Marca"] == "SUBARU"]
    modelos = sub_df.groupby("Modelo", as_index=False)["Valor"].sum().sort_values(by="Valor", ascending=False)
    
    colores_donut = ["#003399", "#0148A4", "#0284c7", "#f97316", "#a855f7", "#64748b", "#cbd5e1"]

    fig = go.Figure(data=[go.Pie(
        labels=modelos["Modelo"],
        values=modelos["Valor"],
        hole=0.55,
        marker=dict(colors=colores_donut[:len(modelos)], line=dict(color="#ffffff", width=2)),
        textinfo="label+percent",
        textposition="outside",
        insidetextorientation="radial",
        textfont=dict(color=PALETA["texto_principal"], size=10, family="system-ui, sans-serif"),
        hovertemplate="<b>%{label}</b><br>Unidades: %{value:,.0f}<br>Porcentaje: %{percent}<extra></extra>"
    )])

    _aplicar_estilo_base(fig, "Mix de Ventas Acumulado por Modelo (2018 - 2023)")
    fig.update_layout(
        showlegend=False,
        margin=dict(l=40, r=40, t=55, b=40)
    )

    return fig.to_html(include_plotlyjs=False, full_html=False, config=CONFIG_PLOTLY)


def crear_grafico_evolucion_modelos_subaru(df: pd.DataFrame) -> str:
    """Gráfico de evolución temporal de los modelos Subaru con leyenda inferior ordenada."""
    sub_df = df[df["Marca"] == "SUBARU"]
    pivot_sub = sub_df.pivot_table(index="Anio", columns="Modelo", values="Valor", aggfunc="sum", fill_value=0)

    # Ordenar por volumen total
    orden = pivot_sub.sum(axis=0).sort_values(ascending=False).index
    pivot_sub = pivot_sub[orden]

    colores_map = {
        "SUBARU FORESTER CAMIONETA": PALETA["azul_subaru"],
        "SUBARU XV CAMIONETA": PALETA["texto_secundario"],
        "SUBARU CROSSTREK CAMIONETA": PALETA["naranja_acento"],
        "SUBARU OUTBACK CAMIONETA": "#a855f7",
        "SUBARU WRX SEDAN": "#eab308",
        "SUBARU EVOLTIS CAMIONETA": "#ec4899",
        "SUBARU IMPREZA SEDAN": "#94a3b8"
    }

    fig = go.Figure()
    for modelo in pivot_sub.columns:
        nombre_limpio = modelo.replace("SUBARU ", "").replace(" CAMIONETA", "").replace(" SEDAN", "")
        fig.add_trace(go.Scatter(
            x=pivot_sub.index,
            y=pivot_sub[modelo],
            name=nombre_limpio,
            mode="lines+markers",
            line=dict(color=colores_map.get(modelo, PALETA["azul_subaru"]), width=2.5),
            marker=dict(size=6),
            hovertemplate=f"<b>{modelo}</b> (%{{x}})<br>Ventas: %{{y:,.0f}} uds<extra></extra>"
        ))

    _aplicar_estilo_base(fig, "Trayectoria Anual por Modelo (Transición XV a Crosstrek)")
    fig.update_layout(
        margin=dict(l=50, r=30, t=55, b=75),
        legend=dict(
            orientation="h",
            y=-0.24,
            x=0.5,
            xanchor="center",
            font=dict(size=10, color=PALETA["texto_principal"])
        )
    )
    fig.update_yaxes(title_text="Unidades Registradas")
    fig.update_xaxes(dtick=1)

    return fig.to_html(include_plotlyjs=False, full_html=False, config=CONFIG_PLOTLY)