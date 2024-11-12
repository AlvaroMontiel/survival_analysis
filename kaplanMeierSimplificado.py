import pandas as pd
from lifelines import KaplanMeierFitter
import matplotlib.pyplot as plt
import os

# Diccionario que agrupa los tumores según los códigos CIEO (sin la letra 'C')
tumor_grupos = {
    "Tráquea, bronquio pulmón": ['33.9', '340', '341', '342', '343', '348', '349'],
    "Próstata": ['619'],
    "Estómago": ['160', '161', '162', '163', '164', '165', '166', '168', '169'],
    "Colon": ['180', '181', '182', '183', '184', '185', '186', '187', '188', '189'],
    "Recto": ['209'],
    "Mama": ['500', '501', '502', '503', '504', '505', '506', '508', '509'],
    "Vesícula biliar": ['239'],
    "Cuello uterino": ['530', '531', '538', '539'],
    "Hígado": ['220', '221', '222', '223', '224', '227', '229']
}

# Ruta para cargar los datos y guardar las imágenes
ruta_datos = 'data/datos_ajustados.xlsx'
ruta_imagenes = 'data/images/'

# Crear el directorio para guardar las imágenes si no existe
os.makedirs(ruta_imagenes, exist_ok=True)

# Cargar el archivo de datos ajustados
df = pd.read_excel(ruta_datos, dtype={'RUT': str})

# Convertir las fechas a formato datetime
df['FECDIAG'] = pd.to_datetime(df['FECDIAG'], errors='coerce')
df['FECCON'] = pd.to_datetime(df['FECCON'], errors='coerce')
df['FECNAC'] = pd.to_datetime(df['FECNAC'], errors='coerce')

# Calcular la edad al momento del diagnóstico
df['edad_diagnostico'] = (df['FECDIAG'] - df['FECNAC']).dt.days // 365.25

# Filtrar los datos para pacientes mayores de 14 años
df = df[df['edad_diagnostico'] >= 15]

# Calcular el tiempo de sobrevida en años
df['tiempo_sobrevida_anios'] = (df['FECCON'] - df['FECDIAG']).dt.days / 365.25

# Filtrar los datos que sean válidos para el análisis (sin valores NaN)
df = df.dropna(subset=['tiempo_sobrevida_anios'])

# Crear la columna 'evento' basado en el estado vital
df['evento'] = df['VM'].apply(lambda x: 1 if x == 2 else 0)

# Filtrar para las comunas específicas que quieres analizar
comunas_seleccionadas = ['2201']


# ============================
# Funciones de Análisis
# ============================

def calcular_sobrevida_global(df, tumor_nombre, cieo_codigos):
    """
    Calcula la sobrevida global sin estratificación.
    """
    kmf = KaplanMeierFitter()

    df_tumor = df[df['TOP'].astype(str).isin(cieo_codigos)]
    if df_tumor.empty:
        return

    kmf.fit(durations=df_tumor['tiempo_sobrevida_anios'], event_observed=df_tumor['evento'], label=f'{tumor_nombre}')
    plt.figure(figsize=(10, 6))
    kmf.plot()
    plt.title(f'Sobrevida Global - {tumor_nombre}')
    plt.xlabel('Tiempo (años)')
    plt.ylabel('Probabilidad de sobrevida')
    plt.grid(True)
    plt.savefig(f'{ruta_imagenes}global_{tumor_nombre}.png')
    plt.close()


def calcular_sobrevida_por_comuna(df, tumor_nombre, cieo_codigos, comunas_seleccionadas):
    """
    Calcula la sobrevida por comunas sin estratificación.
    """
    kmf = KaplanMeierFitter()

    plt.figure(figsize=(10, 6))
    for comuna in comunas_seleccionadas:
        df_comuna = df[(df['TOP'].astype(str).isin(cieo_codigos)) & (df['REGCOM'].astype(str) == comuna)]
        if df_comuna.empty:
            continue

        kmf.fit(durations=df_comuna['tiempo_sobrevida_anios'], event_observed=df_comuna['evento'],
                label=f'Comuna {comuna}')
        kmf.plot()

    plt.title(f'Sobrevida por Comuna - {tumor_nombre}')
    plt.xlabel('Tiempo (años)')
    plt.ylabel('Probabilidad de sobrevida')
    plt.grid(True)
    plt.legend(title='Comuna')
    plt.savefig(f'{ruta_imagenes}comuna_{tumor_nombre}.png')
    plt.close()


def calcular_sobrevida_por_sexo(df, tumor_nombre, cieo_codigos):
    """
    Calcula la sobrevida global estratificada por sexo.
    """
    kmf = KaplanMeierFitter()
    sexos = {1: "Masculino", 2: "Femenino"}

    plt.figure(figsize=(10, 6))
    for sexo, label in sexos.items():
        df_sexo = df[(df['TOP'].astype(str).isin(cieo_codigos)) & (df['SEXO'] == sexo)]
        if df_sexo.empty:
            continue

        kmf.fit(durations=df_sexo['tiempo_sobrevida_anios'], event_observed=df_sexo['evento'], label=label)
        kmf.plot()

    plt.title(f'Sobrevida Global por Sexo - {tumor_nombre}')
    plt.xlabel('Tiempo (años)')
    plt.ylabel('Probabilidad de sobrevida')
    plt.grid(True)
    plt.legend(title='Sexo')
    plt.savefig(f'{ruta_imagenes}sexo_global_{tumor_nombre}.png')
    plt.close()


def calcular_sobrevida_por_comuna_y_sexo(df, tumor_nombre, cieo_codigos, comunas_seleccionadas):
    """
    Calcula la sobrevida por comuna y sexo.
    """
    kmf = KaplanMeierFitter()
    sexos = {1: "Masculino", 2: "Femenino"}

    plt.figure(figsize=(10, 6))
    for comuna in comunas_seleccionadas:
        for sexo, label in sexos.items():
            df_comuna_sexo = df[(df['TOP'].astype(str).isin(cieo_codigos)) &
                                (df['REGCOM'].astype(str) == comuna) &
                                (df['SEXO'] == sexo)]
            if df_comuna_sexo.empty:
                continue

            kmf.fit(durations=df_comuna_sexo['tiempo_sobrevida_anios'], event_observed=df_comuna_sexo['evento'],
                    label=f'Comuna {comuna} - {label}')
            kmf.plot()

    plt.title(f'Sobrevida por Comuna y Sexo - {tumor_nombre}')
    plt.xlabel('Tiempo (años)')
    plt.ylabel('Probabilidad de sobrevida')
    plt.grid(True)
    plt.legend(title='Comuna y Sexo')
    plt.savefig(f'{ruta_imagenes}comuna_sexo_{tumor_nombre}.png')
    plt.close()


# ============================
# Ejecución de Análisis
# ============================

for tumor_nombre, cieo_codigos in tumor_grupos.items():
    calcular_sobrevida_global(df, tumor_nombre, cieo_codigos)
    calcular_sobrevida_por_comuna(df, tumor_nombre, cieo_codigos, comunas_seleccionadas)
    calcular_sobrevida_por_sexo(df, tumor_nombre, cieo_codigos)
    calcular_sobrevida_por_comuna_y_sexo(df, tumor_nombre, cieo_codigos, comunas_seleccionadas)
