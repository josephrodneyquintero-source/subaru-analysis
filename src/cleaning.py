import os
import re
import glob
from pathlib import Path
import pandas as pd


# Lista focalizada de marcas compuestas conocidas
MARCAS_COMPUESTAS = [
    'ALFA ROMEO',
    'ASTON MARTIN',
    'GAC MOTOR',
    'GREAT WALL',
    'LAND ROVER',
    'MERCEDES BENZ',
    'MERCEDES-BENZ'
]


def extraer_anio(nombre_archivo: str) -> int:
    """Extrae el año del nombre del archivo Excel."""
    match = re.search(r'(20\d{2})', nombre_archivo)
    return int(match.group(1)) if match else None


def extraer_marca(texto_modelo: str) -> str:
    """Extrae la marca considerando marcas compuestas antes de tomar la primera palabra."""
    if pd.isna(texto_modelo) or not str(texto_modelo).strip():
        return None

    texto_limpio = " ".join(str(texto_modelo).strip().upper().split())

    # Comprobar primero marcas compuestas
    for marca in sorted(MARCAS_COMPUESTAS, key=len, reverse=True):
        if texto_limpio.startswith(marca):
            return 'MERCEDES BENZ' if marca == 'MERCEDES-BENZ' else marca

    # Si no es compuesta, tomar la primera palabra
    return texto_limpio.split()[0]


def homologar_modelo(texto_modelo: str) -> str:
    """Homologa denominaciones específicas sin modificar arbitrariamente otros modelos."""
    if pd.isna(texto_modelo):
        return None

    limpio = " ".join(str(texto_modelo).strip().upper().split())
    
    # Homologación específica de Subaru Crosstrek
    if limpio == 'SUBARU CROSSTR':
        return 'SUBARU CROSSTREK CAMIONETA'

    return " ".join(str(texto_modelo).strip().split())


def procesar_archivos_excel(
    carpeta_raw: str = os.path.join("data", "raw"),
    patron_archivos: str = "CUADROS ESTADISTICOS DE DICIEMBRE-*.xlsx",
    carpeta_processed: str = os.path.join("data", "processed"),
    nombre_salida: str = "dataset_maestro_vehiculos.csv"
):
    ruta_busqueda = os.path.join(carpeta_raw, patron_archivos)
    archivos = sorted(glob.glob(ruta_busqueda))
    
    if not archivos:
        print(f"No se encontraron archivos con el patrón: {ruta_busqueda}")
        return None

    lista_dfs = []
    total_filas_iniciales = 0
    volumen_inicial_total = 0.0

    print("Procesando archivos...")
    for ruta in archivos:
        nombre_archivo = os.path.basename(ruta)
        anio = extraer_anio(nombre_archivo)
        
        df_temp = pd.read_excel(ruta)
        total_filas_iniciales += len(df_temp)

        # Sumar volumen inicial usando la columna Valor
        if 'Valor' in df_temp.columns:
            vol_inicial = pd.to_numeric(df_temp['Valor'], errors='coerce').sum()
            volumen_inicial_total += vol_inicial
        else:
            vol_inicial = 0

        df_temp['Anio'] = anio
        df_temp['Archivo_Origen'] = nombre_archivo
        lista_dfs.append(df_temp)

        print(f"  • {nombre_archivo} | Año: {anio} | Filas: {len(df_temp):,} | Volumen: {vol_inicial:,.0f}")

    # Unificación
    df = pd.concat(lista_dfs, ignore_index=True)

    # Estandarización de nombres de columnas
    df.columns = [c.strip() for c in df.columns]

    # Limpieza de espacios en columnas de texto
    df['Segmento'] = df['Segmento'].astype(str).str.strip()
    
    # Preservar nombre original del modelo para trazabilidad
    df['Modelo_Original'] = df['Modelo'].astype(str).str.strip()

    # Homologación de modelo y extracción de marca
    df['Modelo'] = df['Modelo_Original'].apply(homologar_modelo)
    df['Marca'] = df['Modelo'].apply(extraer_marca)

    # Conversión de tipos
    df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
    
    # Detección segura y explícita de valores no convertibles en Valor
    valor_convertido = pd.to_numeric(df['Valor'], errors='coerce')
    mascara_invalidos = df['Valor'].notna() & df['Valor'].astype(str).str.strip().ne('') & valor_convertido.isna()
    valores_invalidos = mascara_invalidos.sum()
    df['Valor'] = valor_convertido

    # Revisión de duplicados y nulos
    duplicados = df.duplicated().sum()
    nulos = df.isnull().sum().to_dict()

    # Orden lógico de columnas
    columnas_finales = ['Anio', 'Fecha', 'Segmento', 'Marca', 'Modelo', 'Valor', 'Modelo_Original', 'Archivo_Origen']
    df = df[columnas_finales]

    # Crear automáticamente la carpeta de destino si no existe
    os.makedirs(carpeta_processed, exist_ok=True)
    ruta_archivo_salida = os.path.join(carpeta_processed, nombre_salida)

    # Exportación
    df.to_csv(ruta_archivo_salida, index=False, encoding='utf-8-sig')

    # Métricas finales
    total_filas_finales = len(df)
    volumen_final_total = df['Valor'].sum()

    # Resumen en consola
    print("\n" + "=" * 55)
    print("RESUMEN DE EJECUCIÓN")
    print("=" * 55)
    print(f"Archivos procesados       : {len(archivos)}")
    print(f"Filas iniciales           : {total_filas_iniciales:,}")
    print(f"Filas finales             : {total_filas_finales:,}")
    print(f"Registros duplicados      : {duplicados:,}")
    print(f"Valores no convertibles   : {valores_invalidos:,}")
    print(f"Valores nulos por columna : {nulos}")
    print(f"Volumen inicial total     : {volumen_inicial_total:,.0f}")
    print(f"Volumen final total       : {volumen_final_total:,.0f}")
    print(f"Diferencia de unidades    : {volumen_final_total - volumen_inicial_total:,.0f}")
    print(f"Archivo exportado         : {ruta_archivo_salida}")
    print("=" * 55)

    return df


if __name__ == '__main__':
    # Ejecución utilizando la estructura relativa del proyecto
    df_maestro = procesar_archivos_excel(
        carpeta_raw=os.path.join("data", "raw"),
        patron_archivos="CUADROS ESTADISTICOS DE DICIEMBRE-*.xlsx",
        carpeta_processed=os.path.join("data", "processed"),
        nombre_salida="dataset_maestro_vehiculos.csv"
    )