import pandas as pd
from datetime import datetime

class ConcordDataProcessor:
    def __init__(self, data: pd.DataFrame):
        """
        Inicializa la clase con un DataFrame.
        """
        self.data = data

    def seleccionar_variables(self, variables: list):
        """
        Selecciona solo las variables especificadas.
        """
        self.data = self.data[variables]
        print(f"Variables seleccionadas: {variables}")

    def filtrar_tumores_por_comportamiento(self):
        """
        Filtra los tumores por comportamiento maligno, variable COMP = 3
        """
        comportamiento = [3]
        self.data = self.data[self.data['COMP'].isin(comportamiento)]
        print(f"Tumores filtrados por comportamiento: {comportamiento}")

    def filtrar_tumores_por_cieo(self, cieo_codigos: list):
        """
        Filtra los tumores por códigos CIE-O (códigos de la Clasificación Internacional de Enfermedades para Oncología).
        """
        self.data = self.data[self.data['TOP'].isin(cieo_codigos)]
        print(f"Tumores filtrados por CIE-O: {cieo_codigos}")

    def ajustar_variables_tiempo(self):
        """
        Ajusta las variables de tiempo (convierte fechas y calcula tiempo de sobrevida).
        """
        # Convertir fechas desde el formato yyyymmdd a datetime
        self.data['FECDIAG'] = pd.to_datetime(self.data['FECDIAG'], format='%Y%m%d', errors='coerce')
        self.data['FECCON'] = pd.to_datetime(self.data['FECCON'], format='%Y%m%d', errors='coerce')
        self.data['FECNAC'] = pd.to_datetime(self.data['FECNAC'], format='%Y%m%d', errors='coerce')

        # Calcular tiempo de sobrevida en días
        self.data['tiempo_sobrevida'] = (self.data['FECCON'] - self.data['FECDIAG']).dt.days
        print("Variables de tiempo ajustadas")

    def calcular_edad_diagnostico(self):
        """
        Calcula la edad al momento del diagnóstico (FECDIAG - FECNAC).
        """
        # Asegurarse de que las fechas estén en el formato correcto
        if not pd.api.types.is_datetime64_any_dtype(self.data['FECDIAG']):
            self.data['FECDIAG'] = pd.to_datetime(self.data['FECDIAG'], format='%Y%m%d', errors='coerce')
        if not pd.api.types.is_datetime64_any_dtype(self.data['FECNAC']):
            self.data['FECNAC'] = pd.to_datetime(self.data['FECNAC'], format='%Y%m%d', errors='coerce')

        # Calcular la edad al diagnóstico
        self.data['edad_diagnostico'] = self.data.apply(
            lambda row: row['FECDIAG'].year - row['FECNAC'].year - (
                        (row['FECDIAG'].month, row['FECDIAG'].day) < (row['FECNAC'].month, row['FECNAC'].day)),
            axis=1
        )
        print("Edad al diagnóstico calculada")

    def filtrar_por_anios(self, anio_inicio: int, anio_fin: int):
        """
        Filtra los datos por rango de años de diagnóstico.
        """
        self.data = self.data[(self.data['FECDIAG'].dt.year >= anio_inicio) & (self.data['FECDIAG'].dt.year <= anio_fin)]
        print(f"Datos filtrados para los años {anio_inicio}-{anio_fin}")

    def exportar_a_excel(self, nombre_archivo: str):
        """
        Exporta el DataFrame procesado a un archivo Excel (.xlsx).
        """
        try:
            self.data.to_excel(nombre_archivo, index=False)
            print(f"Datos exportados exitosamente a {nombre_archivo}")
        except Exception as e:
            print(f"Error al exportar a Excel: {e}")

    def obtener_datos(self):
        """
        Devuelve el DataFrame procesado.
        """
        return self.data


# Ejemplo de uso:
if __name__ == "__main__":
    # Cargar los datos desde un archivo CSV (ajusta la ruta según tu archivo)
    df = pd.read_csv('data/rpcdata_13082024.csv')

    # Crear una instancia de la clase y procesar los datos
    procesador = ConcordDataProcessor(df)

    # 1. Seleccionar variables relevantes
    variables = ['REGCOM', 'FECDIAG', 'TOP', 'MORF', 'COMP',
                 'BASE', 'C10', 'CODPRI', 'PMSEC', 'PMTOT', 'GRA', 'EXT', 'LAT', 'TUMOURID', 'NOCASO',
                 'RUT', 'CODRUT', 'SEXO', 'FECNAC', 'FECCON', 'VM', 'CAUSA']
    procesador.seleccionar_variables(variables)

    # 2. Filtrar por códigos CIE-O y comportamiento (ejemplo: cáncer de mama y colon)
    procesador.filtrar_tumores_por_comportamiento()
    cieo_codigos = [339, 340, 341, 342, 343, 348, 349, 619, 160, 161, 162, 163, 164, 165, 166, 168, 169,
                    180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 209, 500, 501, 502, 503, 504, 505,
                    506, 508, 509, 239, 530, 531, 538, 539, 220, 221, 239]
    procesador.filtrar_tumores_por_cieo(cieo_codigos)


    # 3. Ajustar variables de tiempo
    procesador.ajustar_variables_tiempo()

    # 4. Calcular la edad al diagnostico
    procesador.calcular_edad_diagnostico()

    # 5. Filtrar por años de diagnóstico (2000-2019)
    procesador.filtrar_por_anios(2011, 2019)

    # 6. Exportar los datos procesados a un archivo Excel
    nombre_archivo = 'data/datos_ajustados.xlsx'
    procesador.exportar_a_excel(nombre_archivo)

    # Obtener los datos procesados
    datos_ajustados = procesador.obtener_datos()
    print(datos_ajustados.head())
