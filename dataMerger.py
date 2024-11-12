import pandas as pd
from datetime import datetime


class DataMerger:
    def __init__(self, archivo_cancer: str, archivo_defunciones: str):
        # Cargar datos de los archivos Excel
        self.cancer_data = pd.read_excel(archivo_cancer, dtype={'RUT': str})
        self.defunciones_data = pd.read_csv(archivo_defunciones, dtype={'RUN': str})

    def cruzar_datos(self):
        """
        Realiza el cruce de datos entre el archivo de cáncer y el archivo de defunciones.
        """
        # Unir las columnas DIA_DEF, MES_DEF, ANO_DEF en un solo campo de fecha en defunciones
        self.defunciones_data['FECHA_DEF'] = pd.to_datetime(
            self.defunciones_data['ANO_DEF'].astype(str) + '-' +
            self.defunciones_data['MES_DEF'].astype(str).str.zfill(2) + '-' +
            self.defunciones_data['DIA_DEF'].astype(str).str.zfill(2),
            errors='coerce'
        )
        print("Fechas de defunción unida correctamente")

        # Realizar un merge entre los datos de cáncer y defunciones usando RUT y RUN
        merged_data = pd.merge(
            self.cancer_data,
            self.defunciones_data[['RUN', 'FECHA_DEF', 'DIAG1']],
            left_on='RUT',
            right_on='RUN',
            how='left'
        )
        print("Merge finalizado")

        # Actualizar el estado vital (VM) y la fecha de contacto (FECCON)
        merged_data['VM'] = merged_data['FECHA_DEF'].apply(lambda x: 2 if pd.notnull(x) else 1)
        merged_data['FECCON'] = merged_data['FECHA_DEF'].dt.strftime('%Y-%m-%d')
        merged_data['FECCON'] = merged_data['FECCON'].fillna('2019-12-31')
        print("Estado vital y fecha contacto actualizada")

        # Actualizar la causa de muerte (CAUSA)
        def determinar_causa(diag1, vm):
            if vm == 1:  # Vivo
                return None
            elif isinstance(diag1, str) and diag1.startswith('C'):
                return 1  # Cáncer
            else:
                return 2  # Otra causa

        merged_data['CAUSA'] = merged_data.apply(lambda row: determinar_causa(row['DIAG1'], row['VM']), axis=1)
        print("Causa de muerte actualizada")

        # Guardar el resultado en self.cancer_data actualizado
        self.cancer_data = merged_data

    def exportar_resultado(self, nombre_archivo: str):
        """
        Exporta el DataFrame actualizado a un archivo Excel (.xlsx).
        """
        try:
            self.cancer_data.to_excel(nombre_archivo, index=False)
            print(f"Datos exportados exitosamente a {nombre_archivo}")
        except Exception as e:
            print(f"Error al exportar a Excel: {e}")

    def obtener_datos(self):
        """
        Devuelve el DataFrame combinado.
        """
        return self.cancer_data


# Ejemplo de uso
if __name__ == "__main__":
    # Archivos de entrada
    archivo_cancer = 'data/datos_ajustados.xlsx'
    archivo_defunciones = 'data/defunciones_combinadas.csv'

    # Crear una instancia de la clase y procesar los datos
    procesador = DataMerger(archivo_cancer, archivo_defunciones)

    # Realizar el cruce de datos y actualizar los campos
    procesador.cruzar_datos()

    # Exportar el resultado a un nuevo archivo Excel
    procesador.exportar_resultado('data/datos_ajustados_actualizados.xlsx')

    # Mostrar algunos registros del DataFrame actualizado
    print(procesador.obtener_datos().head())
