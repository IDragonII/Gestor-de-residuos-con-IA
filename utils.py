import csv

def buscar_departamento_numero(departamento_nombre):
    # Abre el archivo CSV que contiene los departamentos y sus números
    with open('departamento_mapeo.csv', mode='r') as file:
        reader = csv.DictReader(file)
        # Recorre cada fila del CSV
        for row in reader:
            # Compara el nombre del departamento (ignorando mayúsculas/minúsculas)
            if row['Original'].lower() == departamento_nombre.lower():
                return int(row['Reemplazo'])  # Retorna el número del departamento
    return None  # Si no se encuentra el departamento
