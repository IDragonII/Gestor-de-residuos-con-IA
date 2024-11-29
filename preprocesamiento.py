import pandas as pd
import chardet

csv_path = "datos.csv"
with open(csv_path, 'rb') as f:
    result = chardet.detect(f.read())
detected_encoding = result['encoding']
print(f"Codificación detectada: {detected_encoding}")

try:
    data = pd.read_csv(csv_path, delimiter=';', encoding=detected_encoding, on_bad_lines='skip')
    print("Archivo leído correctamente.")
except Exception as e:
    print(f"Error al leer el archivo: {e}")
    exit()

data.columns = data.columns.str.replace(' ', '_')

print("Nombres de las columnas:", data.columns)

departamento_map = {dep: idx+1 for idx, dep in enumerate(data['DEPARTAMENTO'].unique())}
provincia_map = {prov: idx+1 for idx, prov in enumerate(data['PROVINCIA'].unique())}
distrito_map = {dist: idx+1 for idx, dist in enumerate(data['DISTRITO'].unique())}
region_natural_map = {"SELVA": 1, "SIERRA": 2, "COSTA": 3}
tipo_municipalidad_map = {"DISTRITAL": 0, "PROVINCIAL": 1}

clasificacion_map = {
    "A": 1,
    "B": 2,
    "C": 3,
    "D": 4,
    "E": 5,
    "F": 6,
    "G": 7
}

data['DEPARTAMENTO'] = data['DEPARTAMENTO'].map(departamento_map)
data['PROVINCIA'] = data['PROVINCIA'].map(provincia_map)
data['DISTRITO'] = data['DISTRITO'].map(distrito_map)
data['REGION_NATURAL'] = data['REGION_NATURAL'].map(region_natural_map)
data['TIPO_MUNICIPALIDAD'] = data['TIPO_MUNICIPALIDAD'].map(tipo_municipalidad_map)
data['CLASIFICACION_MUNICIPAL_MEF'] = data['CLASIFICACION_MUNICIPAL_MEF'].map(clasificacion_map)

# Limpiar comas
columns_to_clean = ['GENERACION_PER_CAPITA_DOM', 'GENERACION_DOM_URBANA_TDIA', 'GENERACION_DOM_URBANA_TANIO', 'GENERACION_MUN_TANIO', 'GENERACION_MUN_TDIA', 'GENERACION_PER_CAPITA_MUNICIPAL']
for column in columns_to_clean:
    if column in data.columns:
        data[column] = data[column].replace({',': ''}, regex=True)
        data[column] = pd.to_numeric(data[column], errors='coerce') 

print("Valores nulos en los datos después de la limpieza:")
print(data.isnull().sum())

data = data.dropna()

output_path = "datos_preprocesados.csv"
data.to_csv(output_path, index=False)

def save_mapping_to_csv(mapping, filename):
    mapping_df = pd.DataFrame(list(mapping.items()), columns=["Original", "Reemplazo"])
    mapping_df.to_csv(filename, index=False)
    print(f"Archivo de mapeo guardado en {filename}")

save_mapping_to_csv(departamento_map, "departamento_mapeo.csv")
save_mapping_to_csv(provincia_map, "provincia_mapeo.csv")
save_mapping_to_csv(distrito_map, "distrito_mapeo.csv")
save_mapping_to_csv(region_natural_map, "region_natural_mapeo.csv")
save_mapping_to_csv(tipo_municipalidad_map, "tipo_municipalidad_mapeo.csv")
save_mapping_to_csv(clasificacion_map, "clasificacion_municipal_mapeo.csv")

print(f"Datos preprocesados guardados en {output_path}.")
