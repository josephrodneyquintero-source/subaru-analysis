"""
Módulo de Análisis Exploratorio de Datos (EDA)
Proyecto: Análisis de Mercado Automotriz y Desempeño de Subaru (2018-2023)
Ruta del archivo: src/analysis.py
"""

import os
import sys
import pandas as pd
import numpy as np


# =====================================================================
# CONFIGURACIÓN DE RUTAS Y CONSTANTES
# =====================================================================
RUTA_DATASET = os.path.join("data", "processed", "dataset_maestro_vehiculos.csv")


def imprimir_encabezado(titulo: str):
    """Imprime un separador de sección estandarizado en consola."""
    print("\n" + "=" * 80)
    print(f" {titulo.upper()}")
    print("=" * 80)


def cargar_dataset(ruta_csv: str) -> pd.DataFrame:
    """Carga el dataset maestro procesado desde la ruta especificada."""
    if not os.path.exists(ruta_csv):
        print(f"[ERROR CRÍTICO] No se encontró el archivo: {ruta_csv}")
        print("Verifica que cleaning.py se haya ejecutado previamente.")
        sys.exit(1)
    
    return pd.read_csv(ruta_csv)


# =====================================================================
# 1. RESUMEN GENERAL DEL DATASET
# =====================================================================
def analizar_resumen_general(df: pd.DataFrame) -> dict:
    """Calcula y muestra métricas globales del dataset."""
    imprimir_encabezado("1. Resumen General del Dataset")
    
    total_registros = len(df)
    total_columnas = len(df.columns)
    anios_disponibles = sorted(df['Anio'].dropna().unique().astype(int).tolist())
    volumen_total = df['Valor'].sum()
    total_marcas = df['Marca'].nunique()
    total_modelos = df['Modelo'].nunique()
    total_segmentos = df['Segmento'].nunique()
    
    print(f"• Total de registros          : {total_registros:,}")
    print(f"• Total de columnas           : {total_columnas} ({', '.join(df.columns)})")
    print(f"• Período de años analizado   : {anios_disponibles[0]} - {anios_disponibles[-1]} ({len(anios_disponibles)} años)")
    print(f"• Volumen total de unidades   : {volumen_total:,.0f}")
    print(f"• Cantidad de marcas únicas   : {total_marcas}")
    print(f"• Cantidad de modelos únicos  : {total_modelos}")
    print(f"• Cantidad de segmentos únicos: {total_segmentos}")

    return {
        'total_registros': total_registros,
        'anios_disponibles': anios_disponibles,
        'volumen_total': volumen_total,
        'total_marcas': total_marcas,
        'total_modelos': total_modelos,
        'total_segmentos': total_segmentos
    }


# =====================================================================
# 2. ANÁLISIS DE VENTAS POR AÑO
# =====================================================================
def analizar_por_anio(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula volumen anual, variación absoluta y variación porcentual interanual."""
    imprimir_encabezado("2. Evolución del Mercado por Año")
    
    df_anio = df.groupby('Anio', as_index=False)['Valor'].sum()
    df_anio = df_anio.rename(columns={'Valor': 'Unidades'})
    
    # Cálculo de variaciones interanuales
    df_anio['Var_Absoluta'] = df_anio['Unidades'].diff()
    df_anio['Var_Porcentual'] = np.where(
        df_anio['Unidades'].shift(1) > 0,
        (df_anio['Var_Absoluta'] / df_anio['Unidades'].shift(1)) * 100,
        np.nan
    )
    
    # Formateo visual para consola
    print(f"{'Año':<6} | {'Unidades':<12} | {'Var. Absoluta':<15} | {'Var. Porcentual':<15}")
    print("-" * 56)
    for _, row in df_anio.iterrows():
        var_abs_str = f"{row['Var_Absoluta']:+,.0f}" if pd.notna(row['Var_Absoluta']) else "N/A"
        var_pct_str = f"{row['Var_Porcentual']:+.2f}%" if pd.notna(row['Var_Porcentual']) else "N/A"
        print(f"{int(row['Anio']):<6} | {row['Unidades']:>12,.0f} | {var_abs_str:>15} | {var_pct_str:>15}")
    
    return df_anio


# =====================================================================
# 3. ANÁLISIS DE MARCAS Y POSICIONAMIENTO
# =====================================================================
def analizar_marcas(df: pd.DataFrame, volumen_total: float) -> pd.DataFrame:
    """Genera el ranking de marcas, cuotas de mercado e identifica la posición de Subaru."""
    imprimir_encabezado("3. Ranking y Concentración de Marcas")
    
    df_marcas = df.groupby('Marca', as_index=False)['Valor'].sum()
    df_marcas = df_marcas.rename(columns={'Valor': 'Unidades'})
    df_marcas = df_marcas.sort_values(by='Unidades', ascending=False).reset_index(drop=True)
    
    df_marcas['Ranking'] = df_marcas.index + 1
    df_marcas['Participacion_Pct'] = np.where(
        volumen_total > 0,
        (df_marcas['Unidades'] / volumen_total) * 100,
        0.0
    )
    
    # Top 10 marcas
    print("TOP 10 MARCAS POR VOLUMEN TOTAL (2018 - 2023):")
    print(f"{'Pos.':<5} | {'Marca':<20} | {'Unidades':<12} | {'Participación (%)':<18}")
    print("-" * 62)
    for _, row in df_marcas.head(10).iterrows():
        print(f"#{row['Ranking']:<4} | {row['Marca']:<20} | {row['Unidades']:>12,.0f} | {row['Participacion_Pct']:>17.2f}%")
    
    # Posición específica de Subaru
    subaru_fila = df_marcas[df_marcas['Marca'] == 'SUBARU']
    print("\nPOSICIÓN DE SUBARU EN EL RANKING HISTÓRICO:")
    if not subaru_fila.empty:
        r = subaru_fila.iloc[0]
        print(f"• Marca              : SUBARU")
        print(f"• Posición histórica : #{int(r['Ranking'])} de {len(df_marcas)} marcas")
        print(f"• Unidades totales   : {r['Unidades']:,.0f}")
        print(f"• Cuota de mercado   : {r['Participacion_Pct']:.2f}%")
    else:
        print("• No se encontró la marca SUBARU en los datos.")
        
    return df_marcas


# =====================================================================
# 4. ANÁLISIS ESPECÍFICO DE SUBARU
# =====================================================================
def analizar_subaru(df: pd.DataFrame, df_mercado_anio: pd.DataFrame) -> dict:
    """Analiza volumen anual, cuotas anuales, ranking y desglose por modelo de Subaru."""
    imprimir_encabezado("4. Análisis Detallado de Subaru")
    
    df_subaru = df[df['Marca'] == 'SUBARU'].copy()
    vol_subaru_total = df_subaru['Valor'].sum()
    
    # Desglose de Subaru por año
    subaru_anual = df_subaru.groupby('Anio', as_index=False)['Valor'].sum()
    subaru_anual = subaru_anual.rename(columns={'Valor': 'Unidades_Subaru'})
    
    # Cruzar con volumen total de mercado para obtener cuota anual
    subaru_evolucion = pd.merge(df_mercado_anio[['Anio', 'Unidades']], subaru_anual, on='Anio', how='left').fillna(0)
    subaru_evolucion = subaru_evolucion.rename(columns={'Unidades': 'Unidades_Mercado'})
    
    # Variaciones de Subaru
    subaru_evolucion['Var_Abs_Subaru'] = subaru_evolucion['Unidades_Subaru'].diff()
    subaru_evolucion['Var_Pct_Subaru'] = np.where(
        subaru_evolucion['Unidades_Subaru'].shift(1) > 0,
        (subaru_evolucion['Var_Abs_Subaru'] / subaru_evolucion['Unidades_Subaru'].shift(1)) * 100,
        np.nan
    )
    
    # Variaciones del mercado total
    subaru_evolucion['Var_Abs_Mercado'] = subaru_evolucion['Unidades_Mercado'].diff()
    subaru_evolucion['Var_Pct_Mercado'] = np.where(
        subaru_evolucion['Unidades_Mercado'].shift(1) > 0,
        (subaru_evolucion['Var_Abs_Mercado'] / subaru_evolucion['Unidades_Mercado'].shift(1)) * 100,
        np.nan
    )
    
    # Participación de mercado
    subaru_evolucion['Market_Share_Pct'] = np.where(
        subaru_evolucion['Unidades_Mercado'] > 0,
        (subaru_evolucion['Unidades_Subaru'] / subaru_evolucion['Unidades_Mercado']) * 100,
        0.0
    )
    
    print(f"VOLUMEN HISTÓRICO TOTAL DE SUBARU: {vol_subaru_total:,.0f} unidades\n")
    print("EVOLUCIÓN ANUAL Y PARTICIPACIÓN DE SUBARU:")
    print(f"{'Año':<6} | {'Subaru':<10} | {'Var. Abs':<12} | {'Var. %':<10} | {'Mdo Total':<12} | {'Cuota Mdo (%)':<14}")
    print("-" * 74)
    for _, row in subaru_evolucion.iterrows():
        v_abs = f"{row['Var_Abs_Subaru']:+,.0f}" if pd.notna(row['Var_Abs_Subaru']) else "N/A"
        v_pct = f"{row['Var_Pct_Subaru']:+.2f}%" if pd.notna(row['Var_Pct_Subaru']) else "N/A"
        print(f"{int(row['Anio']):<6} | {row['Unidades_Subaru']:>10,.0f} | {v_abs:>12} | {v_pct:>10} | {row['Unidades_Mercado']:>12,.0f} | {row['Market_Share_Pct']:>13.2f}%")

    # Ranking de Modelos Subaru
    subaru_modelos = df_subaru.groupby('Modelo', as_index=False)['Valor'].sum()
    subaru_modelos = subaru_modelos.rename(columns={'Valor': 'Unidades'})
    subaru_modelos = subaru_modelos.sort_values(by='Unidades', ascending=False).reset_index(drop=True)
    subaru_modelos['Ranking'] = subaru_modelos.index + 1
    subaru_modelos['Participacion_Subaru_Pct'] = np.where(
        vol_subaru_total > 0,
        (subaru_modelos['Unidades'] / vol_subaru_total) * 100,
        0.0
    )
    
    print("\nMODELOS SUBARU CON MAYOR VOLUMEN HISTÓRICO:")
    print(f"{'Pos.':<5} | {'Modelo':<30} | {'Unidades':<10} | {'% en Subaru':<12}")
    print("-" * 63)
    for _, row in subaru_modelos.iterrows():
        print(f"#{row['Ranking']:<4} | {row['Modelo']:<30} | {row['Unidades']:>10,.0f} | {row['Participacion_Subaru_Pct']:>11.2f}%")

    # Tabla Pivot de Modelos Subaru por Año
    subaru_pivot = df_subaru.pivot_table(
        index='Modelo',
        columns='Anio',
        values='Valor',
        aggfunc='sum',
        fill_value=0
    )
    subaru_pivot['Total'] = subaru_pivot.sum(axis=1)
    subaru_pivot = subaru_pivot.sort_values(by='Total', ascending=False)
    
    print("\nVOLUMEN DE MODELOS SUBARU POR AÑO (TABLA COMPLETA):")
    anios_cols = [c for c in subaru_pivot.columns if c != 'Total']
    header_anios = " | ".join([f"{col:>6}" for col in anios_cols])
    print(f"{'Modelo':<30} | {header_anios} | {'Total':>8}")
    print("-" * (42 + len(anios_cols) * 9))
    for idx_mod, row_mod in subaru_pivot.iterrows():
        valores_anios = " | ".join([f"{int(row_mod[c]):>6,}" for c in anios_cols])
        print(f"{idx_mod:<30} | {valores_anios} | {int(row_mod['Total']):>8,}")

    return {
        'evolucion': subaru_evolucion,
        'modelos_ranking': subaru_modelos,
        'volumen_total': vol_subaru_total
    }


# =====================================================================
# 5. ANÁLISIS POR SEGMENTO
# =====================================================================
def analizar_segmentos(df: pd.DataFrame, volumen_total: float) -> pd.DataFrame:
    """Evalúa volumen y ranking de segmentos de mercado junto con la presencia de Subaru."""
    imprimir_encabezado("5. Análisis por Segmento de Mercado")
    
    # Segmentos de todo el mercado
    df_seg = df.groupby('Segmento', as_index=False)['Valor'].sum()
    df_seg = df_seg.rename(columns={'Valor': 'Unidades_Mercado'})
    df_seg = df_seg.sort_values(by='Unidades_Mercado', ascending=False).reset_index(drop=True)
    df_seg['Ranking'] = df_seg.index + 1
    df_seg['Participacion_Mercado_Pct'] = np.where(
        volumen_total > 0,
        (df_seg['Unidades_Mercado'] / volumen_total) * 100,
        0.0
    )
    
    # Presencia de Subaru por segmento
    df_subaru_seg = df[df['Marca'] == 'SUBARU'].groupby('Segmento', as_index=False)['Valor'].sum()
    df_subaru_seg = df_subaru_seg.rename(columns={'Valor': 'Unidades_Subaru'})
    
    df_seg_completo = pd.merge(df_seg, df_subaru_seg, on='Segmento', how='left').fillna(0)
    df_seg_completo['Participacion_Subaru_en_Seg_Pct'] = np.where(
        df_seg_completo['Unidades_Mercado'] > 0,
        (df_seg_completo['Unidades_Subaru'] / df_seg_completo['Unidades_Mercado']) * 100,
        0.0
    )
    
    print("TOP 10 SEGMENTOS DEL MERCADO Y VOLUMEN DE SUBARU:")
    print(f"{'Pos.':<5} | {'Segmento':<24} | {'Mdo Total':<12} | {'% Mdo':<8} | {'Subaru':<10} | {'% Seg. Subaru':<14}")
    print("-" * 84)
    for _, row in df_seg_completo.head(10).iterrows():
        print(f"#{row['Ranking']:<4} | {row['Segmento']:<24} | {row['Unidades_Mercado']:>12,.0f} | {row['Participacion_Mercado_Pct']:>7.2f}% | {row['Unidades_Subaru']:>10,.0f} | {row['Participacion_Subaru_en_Seg_Pct']:>13.2f}%")
        
    return df_seg_completo


# =====================================================================
# 6. COMPARACIÓN SUBARU VS MERCADO
# =====================================================================
def comparar_subaru_vs_mercado(subaru_evolucion: pd.DataFrame):
    """Compara las tendencias de crecimiento/decrecimiento de Subaru frente al mercado global."""
    imprimir_encabezado("6. Comparativa de Tendencias: Subaru vs. Mercado")
    
    print(f"{'Año':<6} | {'Var % Mercado':<15} | {'Var % Subaru':<15} | {'Desempeño Relativo':<25}")
    print("-" * 68)
    for _, row in subaru_evolucion.iterrows():
        pct_sub = row['Var_Pct_Subaru']
        pct_mdo = row['Var_Pct_Mercado']
        
        if pd.isna(pct_sub) or pd.isna(pct_mdo):
            print(f"{int(row['Anio']):<6} | {'Base (2018)':<15} | {'Base (2018)':<15} | {'Año Base':<25}")
            continue
        
        if pct_sub > pct_mdo:
            desempeno = "Subaru Supera al Mercado"
        elif pct_sub < pct_mdo:
            desempeno = "Subaru Cae más / Crece menos"
        else:
            desempeno = "Alineado con Mercado"
            
        print(f"{int(row['Anio']):<6} | {pct_mdo:>+14.2f}% | {pct_sub:>+14.2f}% | {desempeno:<25}")


# =====================================================================
# 7. SÍNTESIS DE HALLAZGOS PRELIMINARES
# =====================================================================
def reportar_hallazgos(
    df_anio: pd.DataFrame,
    df_marcas: pd.DataFrame,
    subaru_dict: dict,
    df_seg: pd.DataFrame
):
    """Sintetiza los principales hallazgos fácticos del análisis."""
    imprimir_encabezado("7. Hallazgos Preliminares del Análisis")
    
    # Año mayor y menor volumen mercado
    anio_max_mdo = df_anio.loc[df_anio['Unidades'].idxmax()]
    anio_min_mdo = df_anio.loc[df_anio['Unidades'].idxmin()]
    
    # Marca líder
    marca_lider = df_marcas.iloc[0]
    
    # Subaru métricas
    subaru_pos = df_marcas[df_marcas['Marca'] == 'SUBARU'].iloc[0]
    subaru_evol = subaru_dict['evolucion']
    subaru_max_anio = subaru_evol.loc[subaru_evol['Unidades_Subaru'].idxmax()]
    subaru_min_anio = subaru_evol.loc[subaru_evol['Unidades_Subaru'].idxmin()]
    subaru_top_modelo = subaru_dict['modelos_ranking'].iloc[0]
    
    # Segmento líder
    seg_lider = df_seg.iloc[0]
    
    print(f"1. AÑO CON MAYOR VOLUMEN DE MERCADO: {int(anio_max_mdo['Anio'])} con {anio_max_mdo['Unidades']:,.0f} unidades.")
    print(f"2. AÑO CON MENOR VOLUMEN DE MERCADO: {int(anio_min_mdo['Anio'])} con {anio_min_mdo['Unidades']:,.0f} unidades registradas.")
    print(f"3. MARCA LÍDER DEL MERCADO         : {marca_lider['Marca']} con {marca_lider['Unidades']:,.0f} unidades ({marca_lider['Participacion_Pct']:.2f}% del mercado total).")
    print(f"4. POSICIÓN HISTÓRICA DE SUBARU    : Puesto #{int(subaru_pos['Ranking'])} del mercado con {subaru_pos['Unidades']:,.0f} unidades ({subaru_pos['Participacion_Pct']:.2f}% de cuota).")
    print(f"5. AÑO DE MAYOR VOLUMEN DE SUBARU  : {int(subaru_max_anio['Anio'])} con {subaru_max_anio['Unidades_Subaru']:,.0f} unidades registradas (cuota del {subaru_max_anio['Market_Share_Pct']:.2f}%).")
    print(f"6. AÑO DE MENOR VOLUMEN DE SUBARU  : {int(subaru_min_anio['Anio'])} con {subaru_min_anio['Unidades_Subaru']:,.0f} unidades registradas.")
    print(f"7. MODELO MÁS VENDIDO DE SUBARU    : {subaru_top_modelo['Modelo']} con {subaru_top_modelo['Unidades']:,.0f} unidades ({subaru_top_modelo['Participacion_Subaru_Pct']:.2f}% de las ventas de la marca).")
    print(f"8. SEGMENTO CON MAYOR VOLUMEN TOTAL: {seg_lider['Segmento']} con {seg_lider['Unidades_Mercado']:,.0f} unidades ({seg_lider['Participacion_Mercado_Pct']:.2f}% del mercado).")
    print("=" * 80 + "\n")


# =====================================================================
# FUNCIÓN PRINCIPAL DE EJECUCIÓN
# =====================================================================
def main():
    """Ejecuta el flujo completo de análisis exploratorio."""
    # 1. Cargar datos
    df = cargar_dataset(RUTA_DATASET)
    
    # 2. Resumen General
    resumen = analizar_resumen_general(df)
    
    # 3. Análisis por Año
    df_anio = analizar_por_anio(df)
    
    # 4. Análisis de Marcas
    df_marcas = analizar_marcas(df, resumen['volumen_total'])
    
    # 5. Análisis de Subaru
    subaru_dict = analizar_subaru(df, df_anio)
    
    # 6. Análisis por Segmento
    df_seg = analizar_segmentos(df, resumen['volumen_total'])
    
    # 7. Comparación Subaru vs Mercado
    comparar_subaru_vs_mercado(subaru_dict['evolucion'])
    
    # 8. Hallazgos Preliminares
    reportar_hallazgos(df_anio, df_marcas, subaru_dict, df_seg)


if __name__ == '__main__':
    main()