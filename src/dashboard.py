"""
Generador del Dashboard Ejecutivo Web (HTML + Plotly + CSS)
Proyecto: Análisis de Mercado Automotriz y Desempeño de Subaru en Panamá (2018-2023)
Ruta: src/dashboard.py
"""

import os
import sys
import pandas as pd
import numpy as np

from visualizations import (
    crear_grafico_evolucion_mercado,
    crear_grafico_top10_marcas,
    crear_grafico_subaru_vs_mercado_indice,
    crear_grafico_market_share_subaru,
    crear_grafico_modelos_subaru_pie,
    crear_grafico_evolucion_modelos_subaru
)

RUTA_DATASET = os.path.join("data", "processed", "dataset_maestro_vehiculos.csv")
CARPETA_REPORTES = "reports"
RUTA_HTML_SALIDA = os.path.join(CARPETA_REPORTES, "dashboard.html")


def cargar_datos(ruta_csv: str) -> pd.DataFrame:
    if not os.path.exists(ruta_csv):
        print(f"[ERROR CRÍTICO] Archivo no encontrado: {ruta_csv}")
        print("Ejecuta previamente cleaning.py para generar el dataset.")
        sys.exit(1)
    return pd.read_csv(ruta_csv)


def calcular_metricas_clave(df: pd.DataFrame) -> dict:
    volumen_total = df["Valor"].sum()
    volumen_2018 = df[df["Anio"] == 2018]["Valor"].sum()
    volumen_2023 = df[df["Anio"] == 2023]["Valor"].sum()
    recuperacion_mercado = ((volumen_2023 - volumen_2018) / volumen_2018) * 100

    subaru_df = df[df["Marca"] == "SUBARU"]
    volumen_subaru = subaru_df["Valor"].sum()
    share_subaru_total = (volumen_subaru / volumen_total) * 100

    sub_anual = subaru_df.groupby("Anio")["Valor"].sum()
    mdo_anual = df.groupby("Anio")["Valor"].sum()
    share_anual = (sub_anual / mdo_anual) * 100

    top_modelo_subaru = (
        subaru_df.groupby("Modelo")["Valor"].sum().sort_values(ascending=False).index[0]
    )
    top_modelo_subaru_vol = subaru_df.groupby("Modelo")["Valor"].sum().max()
    top_modelo_subaru_pct = (top_modelo_subaru_vol / volumen_subaru) * 100

    return {
        "volumen_total": volumen_total,
        "volumen_2023": volumen_2023,
        "recuperacion_mercado": recuperacion_mercado,
        "volumen_subaru": volumen_subaru,
        "share_subaru_total": share_subaru_total,
        "pico_share_subaru": share_anual.max(),
        "anio_pico_share": share_anual.idxmax(),
        "share_2023": share_anual.loc[2023],
        "top_modelo": top_modelo_subaru.replace("SUBARU ", "").replace(" CAMIONETA", ""),
        "top_modelo_vol": top_modelo_subaru_vol,
        "top_modelo_pct": top_modelo_subaru_pct
    }


def generar_plantilla_html(kpis: dict, plots: dict) -> str:
    """Genera la estructura HTML moderna en Light Mode con layout de 2 columnas y control de responsive."""
    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Subaru Panamá | Dashboard Ejecutivo (2018-2023)</title>
    <!-- Plotly CDN -->
    <script src="https://cdn.plot.ly/plotly-2.30.0.min.js"></script>
    <style>
        :root {{
            --bg-app: #f8fafc;
            --bg-sidebar: #ffffff;
            --bg-card: #ffffff;
            --border-ui: #e2e8f0;
            --border-hover: #cbd5e1;
            
            --subaru-blue: #003399;
            --subaru-blue-light: #0148a4;
            --subaru-blue-soft: #eff6ff;
            --accent-orange: #f97316;
            --accent-emerald: #10b981;
            
            --text-title: #0f172a;
            --text-body: #334155;
            --text-muted: #64748b;
            
            --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
            --shadow-card: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
            --shadow-hover: 0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -2px rgba(0, 0, 0, 0.04);
            
            --radius-xl: 16px;
            --radius-lg: 12px;
            --radius-md: 8px;
        }}

        html, body {{
            scroll-behavior: smooth;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Inter, Helvetica, Arial, sans-serif;
        }}

        body {{
            background-color: var(--bg-app);
            color: var(--text-body);
            height: 100vh;
            overflow: hidden;
            display: flex;
        }}

        /* =========================================================
           1. SIDEBAR FIJO (IZQUIERDA)
           ========================================================= */
        aside.sidebar {{
            width: 270px;
            background-color: var(--bg-sidebar);
            border-right: 1px solid var(--border-ui);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            padding: 30px 20px;
            flex-shrink: 0;
            height: 100vh;
        }}

        .brand-logo-box {{
            display: flex;
            justify-content: center;
            align-items: center;
            width: 100%;
            padding-bottom: 24px;
            border-bottom: 1px solid var(--border-ui);
        }}

        .brand-logo-box img {{
            max-height: 46px;
            max-width: 170px;
            width: auto;
            height: auto;
            object-fit: contain;
            display: block;
            margin: 0 auto;
        }}

        .nav-group-title {{
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: var(--text-muted);
            margin: 28px 0 12px 6px;
        }}

        .nav-menu {{
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 6px;
        }}

        .nav-item a {{
            display: flex;
            align-items: center;
            padding: 12px 14px;
            border-radius: var(--radius-md);
            text-decoration: none;
            color: var(--text-body);
            font-size: 0.88rem;
            font-weight: 600;
            transition: all 0.2s ease;
        }}

        .nav-item a:hover {{
            background-color: var(--subaru-blue-soft);
            color: var(--subaru-blue);
        }}

        .sidebar-footer-card {{
            background: linear-gradient(135deg, var(--subaru-blue) 0%, var(--subaru-blue-light) 100%);
            border-radius: var(--radius-lg);
            padding: 16px;
            color: #ffffff;
        }}

        .sidebar-footer-card h4 {{
            font-size: 0.85rem;
            font-weight: 600;
            margin-bottom: 4px;
        }}

        .sidebar-footer-card p {{
            font-size: 0.75rem;
            color: rgba(255, 255, 255, 0.85);
            line-height: 1.4;
        }}

        /* =========================================================
           2. PANEL PRINCIPAL (DERECHA CON SCROLL INDEPENDIENTE)
           ========================================================= */
        main.main-content {{
            flex: 1;
            height: 100vh;
            overflow-y: auto;
            scroll-behavior: smooth;
            padding: 36px 40px 80px 40px;
        }}

        /* Header Superior */
        .top-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 32px;
            flex-wrap: wrap;
            gap: 16px;
        }}

        .header-title-block h1 {{
            font-size: 1.85rem;
            font-weight: 800;
            color: var(--text-title);
            letter-spacing: -0.02em;
        }}

        .header-title-block p {{
            color: var(--text-muted);
            font-size: 0.95rem;
            margin-top: 4px;
        }}

        .badge-pill {{
            background-color: var(--subaru-blue-soft);
            color: var(--subaru-blue);
            border: 1px solid rgba(0, 51, 153, 0.15);
            padding: 6px 14px;
            border-radius: 9999px;
            font-size: 0.82rem;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }}

        /* =========================================================
           3. KPI METRIC CARDS
           ========================================================= */
        .kpi-container {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}

        .kpi-card {{
            background-color: var(--bg-card);
            border: 1px solid var(--border-ui);
            border-radius: var(--radius-xl);
            padding: 22px;
            box-shadow: var(--shadow-card);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}

        .kpi-card:hover {{
            transform: translateY(-2px);
            box-shadow: var(--shadow-hover);
            border-color: var(--border-hover);
        }}

        .kpi-tag {{
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-muted);
            margin-bottom: 6px;
        }}

        .kpi-num {{
            font-size: 1.9rem;
            font-weight: 800;
            color: var(--text-title);
            line-height: 1.1;
        }}

        .kpi-foot {{
            font-size: 0.82rem;
            color: var(--subaru-blue);
            font-weight: 600;
            margin-top: 6px;
        }}

        /* =========================================================
           4. SECCIONES Y CONTENEDORES DE GRÁFICOS
           ========================================================= */
        .section-wrapper {{
            margin-bottom: 48px;
            scroll-margin-top: 24px;
        }}

        .section-heading {{
            margin-bottom: 18px;
        }}

        .section-badge {{
            font-size: 0.72rem;
            color: var(--accent-orange);
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }}

        .section-heading h2 {{
            font-size: 1.35rem;
            font-weight: 700;
            color: var(--text-title);
            margin: 2px 0 6px 0;
        }}

        .section-heading p {{
            font-size: 0.92rem;
            color: var(--text-muted);
            max-width: 950px;
            line-height: 1.5;
        }}

        .charts-row {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(460px, 1fr));
            gap: 22px;
            width: 100%;
        }}

        @media (max-width: 1024px) {{
            .charts-row {{
                grid-template-columns: 1fr;
            }}
        }}

        .chart-card {{
            background-color: var(--bg-card);
            border: 1px solid var(--border-ui);
            border-radius: var(--radius-xl);
            padding: 20px;
            box-shadow: var(--shadow-card);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            min-width: 0;
            min-height: 460px;
            width: 100%;
            overflow: hidden;
            box-sizing: border-box;
        }}

        .chart-wrapper {{
            width: 100% !important;
            flex: 1;
            min-height: 400px;
            overflow: hidden;
            position: relative;
        }}

        .chart-wrapper .plotly-graph-div {{
            width: 100% !important;
            height: 100% !important;
            min-height: 400px;
        }}

        .chart-footer-insight {{
            margin-top: 14px;
            padding-top: 12px;
            border-top: 1px solid var(--border-ui);
            font-size: 0.82rem;
            color: var(--text-muted);
            line-height: 1.45;
        }}

        .chart-footer-insight strong {{
            color: var(--text-title);
        }}

        /* Footer */
        footer.app-footer {{
            margin-top: 48px;
            border-top: 1px solid var(--border-ui);
            padding-top: 20px;
            font-size: 0.8rem;
            color: var(--text-muted);
            text-align: center;
        }}
    </style>
</head>
<body>

    <!-- 1. SIDEBAR FIJO -->
    <aside class="sidebar">
        <div>
            <div class="brand-logo-box">
                <img src="../assets/Subaru_logo.svg" alt="Subaru Logo" onerror="this.style.display='none'; document.getElementById('subaru-fallback').style.display='block';">
                <h3 id="subaru-fallback" style="display:none; font-weight:800; color:var(--subaru-blue); letter-spacing:-0.03em;">SUBARU</h3>
            </div>

            <div class="nav-group-title">Navegación Ejecutiva</div>
            <ul class="nav-menu">
                <li class="nav-item">
                    <a href="#seccion-1" class="nav-link">01. Panorama General</a>
                </li>
                <li class="nav-item">
                    <a href="#seccion-2" class="nav-link">02. Posicionamiento Subaru</a>
                </li>
                <li class="nav-item">
                    <a href="#seccion-3" class="nav-link">03. Rendimiento de Modelos</a>
                </li>
            </ul>
        </div>

        <div class="sidebar-footer-card">
            <h4>Informe de Mercado</h4>
            <p>Datos oficiales consolidados de la industria automotriz en Panamá (2018 - 2023).</p>
        </div>
    </aside>

    <!-- 2. PANEL PRINCIPAL DE CONTENIDOS -->
    <main class="main-content" id="main-container">
        
        <!-- Header -->
        <header class="top-header">
            <div class="header-title-block">
                <h1>Tablero de Inteligencia Comercial</h1>
                <p>Monitoreo Estratégico de Industria, Participación de Mercado y Portafolio Subaru</p>
            </div>
            <div>
                <span class="badge-pill">Período 2018 - 2023</span>
            </div>
        </header>

        <!-- KPI Cards -->
        <section class="kpi-container">
            <div class="kpi-card">
                <div class="kpi-tag">Volumen Total Industria</div>
                <div class="kpi-num">{kpis['volumen_total']:,.0f}</div>
                <div class="kpi-foot">2018 - 2023 (6 Años)</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-tag">Ventas Totales Subaru</div>
                <div class="kpi-num">{kpis['volumen_subaru']:,.0f}</div>
                <div class="kpi-foot">{kpis['share_subaru_total']:.2f}% de Cuota Acumulada</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-tag">Pico de Cuota Anual</div>
                <div class="kpi-num">{kpis['pico_share_subaru']:.2f}%</div>
                <div class="kpi-foot">Alcanzado en el Año {kpis['anio_pico_share']}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-tag">Modelo Pilar (Top 1)</div>
                <div class="kpi-num">{kpis['top_modelo']}</div>
                <div class="kpi-foot">{kpis['top_modelo_vol']:,.0f} uds ({kpis['top_modelo_pct']:.1f}% del Mix)</div>
            </div>
        </section>

        <!-- SECCIÓN 1: MARKET OVERVIEW -->
        <section class="section-wrapper" id="seccion-1">
            <div class="section-heading">
                <span class="section-badge">Sección 01</span>
                <h2>Panorama General del Mercado Automotriz</h2>
                <p>
                    El mercado panameño totalizó 251,742 unidades en el período analizado. Tras la contracción de 2020 (24,091 unidades), la industria mostró una recuperación sostenida hasta situarse en 48,918 unidades en 2023. Las tres primeras marcas acumulan más del 49% de concentración del mercado.
                </p>
            </div>
            <div class="charts-row">
                <div class="chart-card">
                    <div class="chart-wrapper">
                        {plots['evolucion_mercado']}
                    </div>
                    <div class="chart-footer-insight">
                        <strong>Evolución:</strong> Crecimiento continuo en ventas durante el trienio 2021-2023.
                    </div>
                </div>
                <div class="chart-card">
                    <div class="chart-wrapper">
                        {plots['top10_marcas']}
                    </div>
                    <div class="chart-footer-insight">
                        <strong>Concentración:</strong> Toyota lidera el mercado con 53,454 unidades (21.2%), seguida de Hyundai (15.6%) y Kia (12.8%).
                    </div>
                </div>
            </div>
        </section>

        <!-- SECCIÓN 2: SUBARU POSITION -->
        <section class="section-wrapper" id="seccion-2">
            <div class="section-heading">
                <span class="section-badge">Sección 02</span>
                <h2>Posicionamiento y Dinámica de Subaru</h2>
                <p>
                    Subaru acumuló 1,350 unidades (#22 histórico). En 2020 registró su máxima cuota de mercado relativa (0.71%). En 2022 tocó su punto mínimo de participación (0.37%), repuntando en 2023 con un incremento del +47.4% (230 unidades y 0.47% de cuota de mercado).
                </p>
            </div>
            <div class="charts-row">
                <div class="chart-card">
                    <div class="chart-wrapper">
                        {plots['subaru_vs_mercado']}
                    </div>
                    <div class="chart-footer-insight">
                        <strong>Lectura Indexada (Base 2018=100):</strong> En 2019 (+15.0%) y 2023 (+47.4%) el ritmo de avance de Subaru superó la media del mercado.
                    </div>
                </div>
                <div class="chart-card">
                    <div class="chart-wrapper">
                        {plots['market_share_subaru']}
                    </div>
                    <div class="chart-footer-insight">
                        <strong>Recuperación:</strong> El rebote de 2023 recuperó 10 puntos básicos de cuota frente al cierre de 2022.
                    </div>
                </div>
            </div>
        </section>

        <!-- SECCIÓN 3: SUBARU PRODUCT PERFORMANCE -->
        <section class="section-wrapper" id="seccion-3">
            <div class="section-heading">
                <span class="section-badge">Sección 03</span>
                <h2>Rendimiento de Portafolio y Transición de Modelos</h2>
                <p>
                    La estructura de ventas de Subaru se sustenta en su gama SUV. <strong>Forester</strong> es el pilar central con 735 unidades (54.4% del volumen histórico). En 2023 destaca la transición comercial de <strong>XV</strong> (10 unidades) hacia el nuevo <strong>Crosstrek</strong> (60 unidades).
                </p>
            </div>
            <div class="charts-row">
                <div class="chart-card">
                    <div class="chart-wrapper">
                        {plots['modelos_pie']}
                    </div>
                    <div class="chart-footer-insight">
                        <strong>Concentración de Gama:</strong> Forester y la familia XV/Crosstrek representan más del 90% de las ventas de la marca.
                    </div>
                </div>
                <div class="chart-card">
                    <div class="chart-wrapper">
                        {plots['evolucion_modelos']}
                    </div>
                    <div class="chart-footer-insight">
                        <strong>Relevo Generacional:</strong> En 2023 Crosstrek asume con éxito la demanda del segmento ante la salida del Subaru XV.
                    </div>
                </div>
            </div>
        </section>

        <footer class="app-footer">
            <p>Dashboard Generado Automáticamente por Pipeline de Datos | Subaru Analysis Project (2018-2023)</p>
        </footer>

    </main>

    <!-- SCRIPT DE RESIZE Y SMOOTH SCROLL PARA CONTENEDOR INDEPENDIENTE -->
    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            // 1. Smooth scroll interno en el contenedor principal
            const links = document.querySelectorAll('.nav-link');
            const container = document.getElementById('main-container');

            links.forEach(function(link) {{
                link.addEventListener('click', function(e) {{
                    e.preventDefault();
                    const targetId = this.getAttribute('href').substring(1);
                    const targetElement = document.getElementById(targetId);
                    if (targetElement) {{
                        targetElement.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                    }}
                }});
            }});

            // 2. Resize dinámico de Plotly
            function resizeAllCharts() {{
                const chartDivs = document.querySelectorAll('.plotly-graph-div');
                chartDivs.forEach(function(el) {{
                    if (window.Plotly && el) {{
                        Plotly.Plots.resize(el);
                    }}
                }});
            }}

            setTimeout(resizeAllCharts, 250);
            window.addEventListener('resize', resizeAllCharts);
        }});
    </script>
</body>
</html>
"""
    return html_content


def main():
    print("=" * 65)
    print("ENSAMBLANDO DASHBOARD EJECUTIVO WEB (LIGHT THEME)")
    print("=" * 65)

    os.makedirs(CARPETA_REPORTES, exist_ok=True)
    df = cargar_datos(RUTA_DATASET)
    kpis = calcular_metricas_clave(df)
    print("  ✓ Métricas e indicadores clave calculados.")

    plots = {
        "evolucion_mercado": crear_grafico_evolucion_mercado(df),
        "top10_marcas": crear_grafico_top10_marcas(df),
        "subaru_vs_mercado": crear_grafico_subaru_vs_mercado_indice(df),
        "market_share_subaru": crear_grafico_market_share_subaru(df),
        "modelos_pie": crear_grafico_modelos_subaru_pie(df),
        "evolucion_modelos": crear_grafico_evolucion_modelos_subaru(df)
    }
    print("  ✓ Componentes interactivos Plotly generados.")

    html_final = generar_plantilla_html(kpis, plots)
    with open(RUTA_HTML_SALIDA, "w", encoding="utf-8") as f:
        f.write(html_final)

    print(f"  ✓ Dashboard HTML generado exitosamente en: {RUTA_HTML_SALIDA}")
    print("=" * 65)


if __name__ == "__main__":
    main()