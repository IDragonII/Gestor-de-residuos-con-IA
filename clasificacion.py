import pandas as pd
import numpy as np
import joblib
import pkg_resources

csv_file = pkg_resources.resource_stream(__name__, 'datos_preprocesados.csv')
data = pd.read_csv(csv_file)

joblib_file = pkg_resources.resource_stream(__name__, 'random.joblib')
model = joblib.load(joblib_file)


generacion_per_capita_percentiles = data['GENERACION_PER_CAPITA_DOM'].quantile([0.25, 0.5, 0.75]) 

limite_bajo = generacion_per_capita_percentiles[0.25]
limite_moderado = generacion_per_capita_percentiles[0.75]
limite_alto = generacion_per_capita_percentiles[0.75] + (generacion_per_capita_percentiles[0.75] - generacion_per_capita_percentiles[0.25])  # Un rango superior

def clasificar_residuos_per_capita(generacion_per_capita):
    if generacion_per_capita <= limite_bajo:
        return "Bajo"
    elif generacion_per_capita <= limite_moderado:
        return "Moderado"
    else:
        return "Alto"

def clasificar_departamento(departamento, generacion_per_capita):
    if departamento in data['DEPARTAMENTO'].astype(str).values:
        rango = clasificar_residuos_per_capita(generacion_per_capita)
        return rango 
    else:
        return None 
