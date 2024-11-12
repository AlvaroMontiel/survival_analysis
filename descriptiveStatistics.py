import pandas as pd
import os


class DescriptiveStatistics:
    def __init__(self, ruta_datos):
        """
        Inicializa la clase y carga los datos.
        """
        self.ruta_datos = ruta_datos
        self.df = self.cargar_datos()

    def cargar_datos(self):
        """
        Cargar los datos desde un archivo Excel y filtrar por edad (mayores de 14 años).
        """
        try:
            df = pd.read_excel(self.ruta_datos, dtype={'RUT': str})

            # Convertir fechas a formato datetime
            df['FECDIAG'] = pd.to_datetime(df['FECDIAG'], errors='coerce')
            df['FECCON'] = pd.to_datetime(df['FECCON'], errors='coerce')
            df['FECNAC'] = pd.to_datetime(df['FECNAC'], errors='coerce')

            # Calcular la edad al momento del diagnóstico
            df['edad_diagnostico'] = (df['FECDIAG'] - df['FECNAC']).dt.days // 365.25

            # Filtrar solo los casos de 15 años o más
            df = df[df['edad_diagnostico'] >= 15]

            return df
        except FileNotFoundError:
            print(f"Error: No se encontró el archivo {self.ruta_datos}.")
            return None

    def obtener_tabla_consolidada(self, tumor_grupos):
        """
        Obtiene una tabla consolidada con el total de casos por comuna, sexo y tipo de tumor.
        """
        # Crear una columna para el nombre del tumor basado en el grupo
        self.df['TUMOR_GRUPO'] = self.df['TOP'].apply(lambda x: self.obtener_nombre_tumor(x, tumor_grupos))

        # Crear la tabla consolidada
        tabla_consolidada = self.df.groupby(['REGCOM', 'SEXO', 'TUMOR_GRUPO']).size().reset_index(name='Total Casos')

        # Mapear los códigos de sexo a etiquetas
        sexos = {1: "Masculino", 2: "Femenino"}
        tabla_consolidada['SEXO'] = tabla_consolidada['SEXO'].map(sexos)

        print("\nTabla consolidada de casos por Comuna, Sexo y Tipo de Tumor:")
        print(tabla_consolidada)
        return tabla_consolidada

    def obtener_nombre_tumor(self, codigo_top, tumor_grupos):
        """
        Obtiene el nombre del grupo de tumor basado en el código CIEO.
        """
        for tumor_nombre, cieo_codigos in tumor_grupos.items():
            if str(codigo_top) in cieo_codigos:
                return tumor_nombre
        return "Otro"

    def exportar_a_excel(self, ruta_salida, tumor_grupos):
        """
        Exporta todas las estadísticas a un archivo Excel, incluyendo la tabla consolidada.
        """
        with pd.ExcelWriter(ruta_salida, engine='xlsxwriter') as writer:
            # Estadísticas generales
            n_total = len(self.df)
            df_total = pd.DataFrame({'Total de casos': [n_total]})
            df_total.to_excel(writer, sheet_name='Total', index=False)

            # Tabla consolidada por Comuna, Sexo y Tipo de Tumor
            tabla_consolidada = self.obtener_tabla_consolidada(tumor_grupos)
            tabla_consolidada.to_excel(writer, sheet_name='Consolidado', index=False)

        print(f"\nEstadísticas exportadas a {ruta_salida}")


# ========================
# Ejecución del Análisis
# ========================

if __name__ == "__main__":
    ruta_datos = 'data/datos_ajustados.xlsx'
    ruta_salida = 'data/estadisticas_descriptivas.xlsx'

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

    stats = DescriptiveStatistics(ruta_datos)
    stats.exportar_a_excel(ruta_salida, tumor_grupos)
