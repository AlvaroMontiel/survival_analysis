import pandas as pd
from lifelines import KaplanMeierFitter
import matplotlib.pyplot as plt
import os

# Definir el diccionario para agrupar los tumores según los códigos CIEO (sin la letra 'C')
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

# Calcular el tiempo de sobrevida en años
df['tiempo_sobrevida_anios'] = (df['FECCON'] - df['FECDIAG']).dt.days / 365.25

# Filtrar los datos que sean válidos para el análisis
df = df.dropna(subset=['tiempo_sobrevida_anios', 'VM'])

# Convertir la columna 'VM' a un formato binario (1 = muerto, 0 = censurado)
df['evento'] = df['VM'].apply(lambda x: 1 if x == 2 else 0)

# Filtrar para las comunas específicas que quieres analizar
comunas_seleccionadas = ['2101', '2201']


def calcular_sobrevida_global(df, tumor_nombre, cieo_codigos):
    """
    Calcula la sobrevida utilizando Kaplan-Meier para un grupo de tumores específico (global).
    """
    kmf = KaplanMeierFitter()

    # Filtrar los datos para los tumores según sus códigos CIEO
    df_tumor = df[df['TOP'].astype(str).isin(cieo_codigos)]

    if df_tumor.empty:
        print(f"No hay datos para el grupo de tumores: {tumor_nombre}")
        return

    # Ajustar el modelo de Kaplan-Meier para el grupo
    kmf.fit(durations=df_tumor['tiempo_sobrevida_anios'], event_observed=df_tumor['evento'], label=f'{tumor_nombre}')

    # Graficar la curva de Kaplan-Meier global
    plt.figure(figsize=(10, 6))
    kmf.plot()
    plt.title(f'Curva de Kaplan-Meier Global - {tumor_nombre}')
    plt.xlabel('Tiempo (años)')
    plt.ylabel('Probabilidad de sobrevida')
    plt.grid(True)
    plt.xticks(range(0, 10))
    plt.savefig(f'{ruta_imagenes}kaplan_meier_global_{tumor_nombre}.png')
    # plt.show()
    print(f"Curva de Kaplan-Meier Global para {tumor_nombre} generada.")


def calcular_sobrevida_por_tumor_comuna(df, tumor_nombre, cieo_codigos, comunas_seleccionadas):
    """
    Calcula la sobrevida utilizando Kaplan-Meier para un grupo de tumores específico,
    comparando entre las comunas seleccionadas.
    """
    kmf = KaplanMeierFitter()

    plt.figure(figsize=(10, 6))

    for comuna in comunas_seleccionadas:
        # Filtrar los datos para la comuna y los tumores según sus códigos
        filtro = (df['TOP'].astype(str).isin(cieo_codigos)) & (df['REGCOM'].astype(str) == comuna)
        df_comuna = df[filtro]

        if df_comuna.empty:
            print(f"No hay datos para el tumor '{tumor_nombre}' en la comuna {comuna}")
            continue

        # Ajustar el modelo de Kaplan-Meier para la comuna
        kmf.fit(durations=df_comuna['tiempo_sobrevida_anios'],
                event_observed=df_comuna['evento'],
                label=f'Comuna {comuna}')

        # Graficar la curva de Kaplan-Meier para la comuna
        kmf.plot()

    # Personalizar el gráfico
    plt.title(f'Curva de Kaplan-Meier - {tumor_nombre} por Comuna')
    plt.xlabel('Tiempo (años)')
    plt.ylabel('Probabilidad de sobrevida')
    plt.grid(True)
    plt.xticks(range(0, 10))
    plt.legend(title='Comuna')
    plt.savefig(f'{ruta_imagenes}kaplan_meier_comunas_{tumor_nombre}.png')
    # plt.show()
    print(f"Curva de Kaplan-Meier por comuna para el tumor '{tumor_nombre}' generada.")


# Generar curvas de Kaplan-Meier globales y por comunas para cada grupo de tumores
for tumor_nombre, cieo_codigos in tumor_grupos.items():
    print(f"\nAnalizando el grupo de tumores: {tumor_nombre}")

    # Análisis de sobrevida global
    calcular_sobrevida_global(df, tumor_nombre, cieo_codigos)

    # Análisis de sobrevida por comunas
    calcular_sobrevida_por_tumor_comuna(df, tumor_nombre, cieo_codigos, comunas_seleccionadas)
    ###

