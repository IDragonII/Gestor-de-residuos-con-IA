import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.metrics import confusion_matrix
import joblib
import numpy as np 
import subprocess
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

subprocess.run(["python", "preprocesamiento.py"])

input_path = "datos_preprocesados.csv"
data = pd.read_csv(input_path)

print("Primeras filas de los datos preprocesados:")
print(data.head())


X = data.drop(['DEPARTAMENTO', 'CLASIFICACION_MUNICIPAL_MEF'], axis=1)
y = data['DEPARTAMENTO']

#Dividir los datos en conjuntos de entrenamiento y prueba (80% entrenamiento, 20% prueba)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

#Random Forest
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

print("Precisión del modelo en los datos de prueba:", accuracy_score(y_test, y_pred))
print("Reporte de clasificación:\n", classification_report(y_test, y_pred))

model_filename = "random.joblib"
joblib.dump(model, model_filename)
print(f"Modelo guardado como {model_filename}")

departamento_map_df = pd.read_csv("departamento_mapeo.csv")
provincia_map_df = pd.read_csv("provincia_mapeo.csv")
distrito_map_df = pd.read_csv("distrito_mapeo.csv")
region_natural_map_df = pd.read_csv("region_natural_mapeo.csv")
tipo_municipalidad_map_df = pd.read_csv("tipo_municipalidad_mapeo.csv")
clasificacion_map_df = pd.read_csv("clasificacion_municipal_mapeo.csv")

departamento_map_reverse = dict(zip(departamento_map_df['Reemplazo'], departamento_map_df['Original']))
provincia_map_reverse = dict(zip(provincia_map_df['Reemplazo'], provincia_map_df['Original']))
distrito_map_reverse = dict(zip(distrito_map_df['Reemplazo'], distrito_map_df['Original']))
region_natural_map_reverse = dict(zip(region_natural_map_df['Reemplazo'], region_natural_map_df['Original']))
tipo_municipalidad_map_reverse = dict(zip(tipo_municipalidad_map_df['Reemplazo'], tipo_municipalidad_map_df['Original']))
clasificacion_map_reverse = dict(zip(clasificacion_map_df['Reemplazo'], clasificacion_map_df['Original']))


loaded_model = joblib.load(model_filename)

sample_data = X_test.iloc[0].values.reshape(1, -1)  #ejemplo del conjunto de prueba
predicted_depto_numeric = loaded_model.predict(sample_data)

predicted_depto = departamento_map_reverse.get(predicted_depto_numeric[0], "Desconocido")

print(f"Predicción para el primer ejemplo de prueba: {predicted_depto}")

data['GENERACION_TOTAL'] = data['GENERACION_DOM_URBANA_TDIA'] * data['POB_TOTAL_INEI']

departamento_residuos = data.groupby('DEPARTAMENTO')['GENERACION_TOTAL'].sum()

max_generacion_depto_numeric = departamento_residuos.idxmax()

max_generacion_depto = departamento_map_reverse.get(max_generacion_depto_numeric, "Desconocido")

print(f"El departamento con la mayor generación de residuos es: {max_generacion_depto}")

cm = confusion_matrix(y_test, y_pred)

root = tk.Tk()
root.title("Matriz de Confusión")

fig, ax = plt.subplots(figsize=(8, 6))
cax = ax.matshow(cm, cmap="Blues")

ticks = np.arange(len(set(y)))
ax.set_xticks(ticks)
ax.set_yticks(ticks)

for (i, j), val in np.ndenumerate(cm):
    ax.text(j, i, f'{val}', ha='center', va='center', color='white')

fig.colorbar(cax)

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(row=1, column=0, padx=10, pady=10)
canvas.draw()

root.mainloop()