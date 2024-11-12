import pandas as pd
import os
from glob import glob


class DefuncionesProcessor:
    def __init__(self, directorio: str):
        """
        Inicializa la clase con el directorio donde están los archivos Excel.
        """
        self.directorio = directorio
        self.data_combined = pd.DataFrame()

    def cargar_y_combinar_archivos(self):
        """
        Carga todos los archivos Excel (.xlsx) del directorio y combina las columnas relevantes en un solo DataFrame.
        """
        # Obtener todos los archivos Excel en el directorio
        archivos = glob(os.path.join(self.directorio, '*.xlsx'))

        # Verificar si hay archivos disponibles
        if not archivos:
            print("No se encontraron archivos Excel en el directorio especificado.")
            return

        lista_dataframes = []

        # Cargar cada archivo y seleccionar las columnas necesarias
        for archivo in archivos:
            print(f"Cargando archivo: {archivo}")
            try:
                # Leer el archivo Excel y seleccionar las columnas necesarias
                df = pd.read_excel(archivo, usecols=['RUN', 'DIA_DEF', 'MES_DEF', 'ANO_DEF', 'DIAG1'], dtype=str)
                lista_dataframes.append(df)
            except Exception as e:
                print(f"Error al cargar {archivo}: {e}")

        # Unir todos los DataFrames en uno solo
        self.data_combined = pd.concat(lista_dataframes, ignore_index=True)
        print("Archivos combinados exitosamente.")

    def exportar_a_excel(self, nombre_archivo: str):
        """
        Exporta el DataFrame combinado a un archivo Excel (.xlsx).
        """
        try:
            self.data_combined.to_excel(nombre_archivo, index=False)
            print(f"Datos exportados exitosamente a {nombre_archivo}")
        except Exception as e:
            print(f"Error al exportar a Excel: {e}")

    def exportar_a_csv(self, nombre_archivo: str):
        """
        Exporta el DataFrame combinado a un archivo CSV (.csv).
        """
        try:
            self.data_combined.to_csv(nombre_archivo, index=False)
            print(f"Datos exportados exitosamente a {nombre_archivo}")
        except Exception as e:
            print(f"Error al exportar a CSV: {e}")

    def obtener_datos(self):
        """
        Devuelve el DataFrame combinado.
        """
        return self.data_combined


# Ejemplo de uso
if __name__ == "__main__":
    # Especificar el directorio donde se encuentran los archivos Excel
    directorio = 'data'

    # Crear una instancia de la clase y procesar los archivos
    procesador = DefuncionesProcessor(directorio)

    # 1. Cargar y combinar los archivos
    procesador.cargar_y_combinar_archivos()

    # 2. Exportar a CSV
    procesador.exportar_a_csv('data/defunciones_combinadas.csv')

    # Mostrar algunos registros del DataFrame combinado
    print(procesador.obtener_datos().head())
