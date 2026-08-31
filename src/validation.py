import os
import sys
import pandas as pd
import numpy as np


# ==========================================
# PARÁMETROS Y CONSTANTES DE VALIDACIÓN
# ==========================================

VOLUMEN_ESPERADO = 251742
ANIO_MIN_ESPERADO = 2018
ANIO_MAX_ESPERADO = 2023
FECHA_MIN_ESPERADA = "2018-01-01"
FECHA_MAX_ESPERADA = "2023-12-01"
RUTA_CSV = os.path.join("data", "processed", "dataset_maestro_vehiculos.csv")


def imprimir_seccion(titulo: str):
    """Imprime un separador de sección en consola."""
    print("\n" + "=" * 65)
    print(f" {titulo.upper()}")
    print("=" * 65)


def validar_dataset(ruta_archivo: str = RUTA_CSV):
    """Ejecuta un conjunto integral de pruebas de calidad sobre el dataset maestro."""
    
    if not os.path.exists(ruta_archivo):
        print(f"[ERROR CRÍTICO] No se encontró el archivo: {ruta_archivo}")
        print("Asegúrate de ejecutar primero cleaning.py.")
        sys.exit(1)

    print(f"Cargando dataset desde: {ruta_archivo}")
    df = pd.read_csv(ruta_archivo)
    
    alertas = []
    
    # -------------------------------------------------------------
    # 1. VOLUMETRÍA GENERAL Y COMPLETITUD
    # -------------------------------------------------------------
    imprimir_seccion("1. Volumetría y Estructura")
    total_filas = len(df)
    total_columnas = len(df.columns)
    print(f"• Total de registros : {total_filas:,}")
    print(f"• Total de columnas  : {total_columnas} -> {df.columns.tolist()}")
    
    if total_filas == 0:
        alertas.append("El dataset está completamente vacío.")

    # -------------------------------------------------------------
    # 2. VALORES NULOS Y DUPLICADOS
    # -------------------------------------------------------------
    imprimir_seccion("2. Nulos y Duplicados")
    nulos = df.isnull().sum()
    total_nulos = nulos.sum()
    
    print("• Conteo de valores nulos por columna:")
    for col, cant in nulos.items():
        estado = "✓ [0 nulos]" if cant == 0 else f"⚠ [{cant:,} nulos]"
        print(f"   - {col:18}: {estado}")
    
    if total_nulos > 0:
        alertas.append(f"Se encontraron {total_nulos:,} valores nulos en total.")

    duplicados_completos = df.duplicated().sum()
    print(f"\n• Filas idénticas duplicadas: {duplicados_completos}")
    if duplicados_completos > 0:
        alertas.append(f"Existen {duplicados_completos} filas duplicadas en el dataset.")

    # -------------------------------------------------------------
    # 3. RANGO TEMPORAL Y FECHAS
    # -------------------------------------------------------------
    imprimir_seccion("3. Rango Temporal y Fechas")
    df_fechas = pd.to_datetime(df['Fecha'], errors='coerce')
    fechas_invalidas = df_fechas.isna().sum()
    
    fecha_min = df_fechas.min().strftime('%Y-%m-%d') if fechas_invalidas < len(df) else "N/A"
    fecha_max = df_fechas.max().strftime('%Y-%m-%d') if fechas_invalidas < len(df) else "N/A"
    anios_presentes = sorted(df['Anio'].dropna().unique().tolist())
    
    print(f"• Fechas no convertibles : {fechas_invalidas}")
    print(f"• Rango de fechas        : {fecha_min} a {fecha_max}")
    print(f"• Años encontrados       : {anios_presentes}")

    if fechas_invalidas > 0:
        alertas.append(f"Existen {fechas_invalidas} fechas con formato inválido.")
    if fecha_min != FECHA_MIN_ESPERADA or fecha_max != FECHA_MAX_ESPERADA:
        alertas.append(f"El rango de fechas ({fecha_min} a {fecha_max}) no coincide con el esperado ({FECHA_MIN_ESPERADA} a {FECHA_MAX_ESPERADA}).")
    if anios_presentes != list(range(ANIO_MIN_ESPERADO, ANIO_MAX_ESPERADO + 1)):
        alertas.append("Faltan años en la serie esperada 2018-2023.")

    # -------------------------------------------------------------
    # 4. COLUMNA VALOR (UNIDADES Y VOLUMEN TOTAL)
    # -------------------------------------------------------------
    imprimir_seccion("4. Validación de Métrica 'Valor'")
    valor_num = pd.to_numeric(df['Valor'], errors='coerce')
    valores_no_num = valor_num.isna().sum()
    valores_negativos = (valor_num < 0).sum()
    volumen_total = valor_num.sum()
    diferencia_volumen = volumen_total - VOLUMEN_ESPERADO

    print(f"• Valores no numéricos   : {valores_no_num}")
    print(f"• Valores negativos      : {valores_negativos}")
    print(f"• Mínimo valor registrado: {valor_num.min()}")
    print(f"• Máximo valor registrado: {valor_num.max()}")
    print(f"• Volumen total calculado: {volumen_total:,.0f} unidades")
    print(f"• Volumen total esperado : {VOLUMEN_ESPERADO:,.0f} unidades")
    print(f"• Diferencia de volumen  : {diferencia_volumen:,.0f} unidades")

    if valores_no_num > 0:
        alertas.append(f"Existen {valores_no_num} valores no convertibles en 'Valor'.")
    if valores_negativos > 0:
        alertas.append(f"Se detectaron {valores_negativos} registros con valores negativos en 'Valor'.")
    if diferencia_volumen != 0:
        alertas.append(f"Discrepancia en volumen total: {diferencia_volumen:+,.0f} unidades vs objetivo.")

    # -------------------------------------------------------------
    # 5. SEGMENTOS
    # -------------------------------------------------------------
    imprimir_seccion("5. Consistencia de Segmentos")
    segmentos = sorted(df['Segmento'].dropna().unique().tolist())
    print(f"• Total segmentos únicos: {len(segmentos)}")
    
    # Detección de posibles inconsistencias por espacios o diferencias de mayúsculas
    segmentos_lower = [str(s).strip().lower() for s in segmentos]
    duplicados_segmento = len(segmentos_lower) - len(set(segmentos_lower))
    
    if duplicados_segmento > 0:
        alertas.append("Existen segmentos que difieren únicamente por mayúsculas/minúsculas o espacios.")
        print(f"  ⚠ Segmentos duplicados por formato: {duplicados_segmento}")
    else:
        print("  ✓ No hay segmentos duplicados por inconsistencias de formato.")

    # -------------------------------------------------------------
    # 6. EXTRACCIÓN Y CONSISTENCIA DE MARCAS
    # -------------------------------------------------------------
    imprimir_seccion("6. Extracción y Consistencia de Marcas")
    marcas = sorted(df['Marca'].dropna().unique().tolist())
    print(f"• Total marcas únicas detectadas: {len(marcas)}")

    # Validar coherencia entre Marca, Modelo y Modelo_Original
    df_temp = df[['Marca', 'Modelo', 'Modelo_Original']].drop_duplicates().copy()

    def es_consistente_marca_modelo(row):
        # 1. Validar que ninguno de los tres campos sea nulo o vacío
        for col in ['Marca', 'Modelo', 'Modelo_Original']:
            val = row[col]
            if pd.isna(val) or not str(val).strip():
                return False

        marca = str(row['Marca']).strip().upper()
        modelo_orig = str(row['Modelo_Original']).strip().upper()
        modelo = str(row['Modelo']).strip().upper()

        # 2. Descartar cadenas literales no válidas
        if marca in ['NAN', 'NONE'] or modelo in ['NAN', 'NONE'] or modelo_orig in ['NAN', 'NONE']:
            return False

        # 3. Comprobar que el texto original o el modelo limpio comiencen con la marca
        coincide_origen = modelo_orig.startswith(marca) or modelo.startswith(marca)
        return coincide_origen

    inconsistencias_marca = df_temp[~df_temp.apply(es_consistente_marca_modelo, axis=1)]

    if len(inconsistencias_marca) > 0:
        print(
            f"  ⚠ Inconsistencias detectadas en Marca / Modelo / Modelo_Original ({len(inconsistencias_marca)} casos):"
        )
        print(inconsistencias_marca.head())
        alertas.append(
            f"{len(inconsistencias_marca)} combinaciones presentan inconsistencia entre Marca, Modelo y Modelo_Original."
        )
    else:
        print(
            "  ✓ La extracción de Marca es coherente con Modelo_Original y la columna Modelo."
        )

    # Marcas compuestas clave
    marcas_compuestas_check = [
        'MERCEDES BENZ',
        'LAND ROVER',
        'GREAT WALL',
        'GAC MOTOR',
        'ALFA ROMEO',
        'ASTON MARTIN',
    ]
    print("\n• Muestreo de marcas compuestas detectadas:")
    for mc in marcas_compuestas_check:
        cant_modelos = df[df['Marca'] == mc]['Modelo'].nunique()
        print(f"   - {mc:16}: {cant_modelos} modelos asociados")

    # -------------------------------------------------------------
    # 7. HOMOLOGACIÓN ESPECÍFICA (SUBARU CROSSTR)
    # -------------------------------------------------------------
    imprimir_seccion("7. Verificación de Homologación Subaru Crosstrek")
    casos_crosstr = df[df['Modelo_Original'].astype(str).str.upper().str.contains('CROSSTR', na=False)]
    
    if len(casos_crosstr) == 0:
        print("  ⚠ No se encontraron registros de Subaru Crosstr/Crosstrek en los datos.")
        alertas.append("No se registraron modelos Crosstr/Crosstrek.")
    else:
        resumen_homologacion = casos_crosstr.groupby(['Modelo_Original', 'Modelo', 'Marca'])['Valor'].agg(['count', 'sum']).reset_index()
        print(resumen_homologacion.to_string(index=False))
        
        # Validar que ningún modelo destino haya quedado como 'SUBARU CROSSTR'
        pendientes = df[df['Modelo'] == 'SUBARU CROSSTR']
        if len(pendientes) > 0:
            print(f"  ⚠ Existen {len(pendientes)} registros que aún conservan 'SUBARU CROSSTR' sin homologar.")
            alertas.append("Quedaron registros con 'SUBARU CROSSTR' sin homologar en la columna Modelo.")
        else:
            print("  ✓ Todos los registros de 'SUBARU CROSSTR' fueron homologados a 'SUBARU CROSSTREK CAMIONETA'.")

    # -------------------------------------------------------------
    # 8. DIAGNÓSTICO FINAL
    # -------------------------------------------------------------
    imprimir_seccion("8. Resumen Final de Calidad")
    if not alertas:
        print("✓ TODAS LAS VALIDACIONES PASARON EXITOSAMENTE.")
        print(f"El dataset está listo para análisis posterior ({total_filas:,} filas, {volumen_total:,.0f} unidades).")
    else:
        print(f"⚠ SE ENCONTRARON {len(alertas)} POSIBLE(S) PROBLEMA(S) / ADVERTENCIA(S):")
        for idx, alerta in enumerate(alertas, 1):
            print(f"  {idx}. {alerta}")
    print("=" * 65 + "\n")


if __name__ == '__main__':
    validar_dataset()