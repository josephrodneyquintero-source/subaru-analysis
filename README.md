# Análisis de Mercado Automotriz y Desempeño de Subaru en Panamá (2018–2023)

Pipeline integral de ingeniería, validación, análisis exploratorio de datos (EDA) y generación de tablero interactivo para la evaluación del mercado automotriz en Panamá y el posicionamiento comercial de Subaru.

---

## Descripción

El proyecto consolida y analiza las cifras oficiales de ventas automotrices correspondientes al período **2018–2023** en Panamá (totalizando **251,742 unidades** registradas). Su propósito es estructurar los registros históricos, auditar la consistencia de los datos y evaluar el rendimiento estratégico de **Subaru** frente a la industria general, examinando su cuota de mercado, evolución ante fluctuaciones macroeconómicas y la transición generacional de sus modelos clave (Forester, XV y Crosstrek).

---

## Características

* **Pipeline ETL automatizado**: Ingesta, limpieza, homologación de modelos y extracción algorítmica de marcas a partir de cuadros estadísticos anuales en formato Excel.
* **Suite de validación de calidad de datos**: Comprobación de volumetría, completitud temporal (2018–2023), control de duplicados e integridad de métricas numéricas.
* **Módulo de Análisis Exploratorio (EDA)**: Resúmenes en consola sobre variaciones interanuales, ranking de marcas, concentración de mercado y cruces por segmento.
* **Tablero Ejecutivo Interactivo**: Dashboard en HTML y Plotly responsivo, con métricas clave (KPIs), comparativas indexadas de rendimiento y gráficos de distribución.

---

## Tecnologías Utilizadas

* **Lenguaje**: Python 3.9+
* **Procesamiento y Análisis de Datos**: `pandas`, `numpy`
* **Lectura de Hojas de Cálculo**: `openpyxl`
* **Visualización Interactiva**: `plotly`
* **Presentación Web**: HTML5, CSS3 moderno (Light Theme) y JavaScript nativo

---

## Estructura del Proyecto

```text
subaru-analysis/
├── assets/
│   └── Subaru_logo.svg                  # Recursos gráficos del dashboard
├── data/
│   ├── processed/
│   │   └── dataset_maestro_vehiculos.csv # Dataset consolidado y limpio
│   └── raw/
│       ├── CUADROS ESTADISTICOS DE DICIEMBRE-2018.xlsx
│       ├── CUADROS ESTADISTICOS DE DICIEMBRE-2019.xlsx
│       ├── CUADROS ESTADISTICOS DE DICIEMBRE-2020.xlsx
│       ├── CUADROS ESTADISTICOS DE DICIEMBRE-2021.xlsx
│       ├── CUADROS ESTADISTICOS DE DICIEMBRE-2022.xlsx
│       └── CUADROS ESTADISTICOS DE DICIEMBRE-2023.xlsx
├── reports/
│   └── dashboard.html                   # Reporte ejecutivo interactivo
├── src/
│   ├── analysis.py                      # Módulo de análisis estadístico en consola
│   ├── cleaning.py                      # Pipeline de limpieza y unificación ETL
│   ├── dashboard.py                     # Ensamblador del dashboard web
│   ├── validation.py                    # Pruebas de calidad y validación de datos
│   └── visualizations.py                # Definición de figuras interactivas Plotly
├── .gitignore
├── README.md
└── requirements.txt
```

---

## Requisitos

* **Python**: Versión 3.9 o superior recomendada.
* **Navegador Web**: Cualquier navegador moderno para visualizar `reports/dashboard.html` (Chrome, Firefox, Safari, Edge).

---

## Instalación

1. **Clonar el repositorio**:
   ```bash
   git clone https://github.com/tu-usuario/subaru-analysis.git
   cd subaru-analysis
   ```

2. **Crear y activar un entorno virtual**:
   * En **Windows**:
     ```bash
     python -m venv .venv
     .venv\Scripts\activate
     ```
   * En **macOS / Linux**:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

---

## Ejecución

Ejecuta los scripts secuencialmente desde la **carpeta raíz** del proyecto:

1. **Paso 1 — Procesar y limpiar datos crudos**:
   ```bash
   python src/cleaning.py
   ```
   *Lee los archivos en `data/raw/` y genera `data/processed/dataset_maestro_vehiculos.csv`.*

2. **Paso 2 — Validar calidad del dataset**:
   ```bash
   python src/validation.py
   ```
   *Verifica volumetría, consistencia de marcas y formatos.*

3. **Paso 3 — Ejecutar el análisis exploratorio**:
   ```bash
   python src/analysis.py
   ```
   *Muestra tablas de resumen, rankings y comparativas de mercado en consola.*

4. **Paso 4 — Generar el dashboard interactivo**:
   ```bash
   python src/dashboard.py
   ```
   *Crea el archivo `reports/dashboard.html`.*

---

## Visualización del Dashboard

Abre el archivo generado en tu navegador web:
* En **Windows**:
  ```bash
  start reports/dashboard.html
  ```
* En **macOS**:
  ```bash
  open reports/dashboard.html
  ```
* En **Linux**:
  ```bash
  xdg-open reports/dashboard.html
  ```

El dashboard incluye:
* **KPIs Principales**: Volumen de la industria, ventas de Subaru, pico de cuota de mercado y modelo pilar.
* **Panorama General**: Evolución anual de ventas y Top 10 marcas con mayor volumen.
* **Dinámica de Subaru**: Comparativa de rendimiento indexado (Base 2018=100) y evolución del market share.
* **Portafolio de Productos**: Distribución del mix de ventas y transición comercial de Subaru XV hacia Crosstrek.

---

## Notas sobre los Datos

* Los datos crudos provienen de los cuadros estadísticos anuales oficiales de la industria automotriz panameña.
* No se incluyen credenciales, claves de API ni datos de carácter confidencial en el repositorio.
