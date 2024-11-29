from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from utils import buscar_departamento_numero
import bcrypt
import clasificacion 

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'clasificacion_db'

mysql = MySQL(app)

app.secret_key = 'supersecretkey'

@app.route('/')
def inicio():
    return render_template('inicio.html')

from flask import session

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuarios WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()

        if user:
            
            stored_password = user[2]  # Asumiendo que la contraseña está en el tercer campo
            if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                session['user_id'] = user[0]  # Almacenar el ID del usuario en la sesión
                return redirect(url_for('clasificar'))  # Redirigir a la página de clasificación
            else:
                flash('Contraseña incorrecta')
        else:
            flash('Usuario no encontrado')

    return render_template('login.html')
@app.route('/logout', methods=['GET'])
def logout():
    # Lógica para cerrar sesión (ejemplo: eliminar datos de sesión)
    session.clear()  # Borra todos los datos de la sesión
    flash('Has cerrado sesión correctamente.')
    return redirect(url_for('login'))


# Ruta de Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Validar que las contraseñas coincidan
        if password != confirm_password:
            flash('Las contraseñas no coinciden. Por favor, inténtalo de nuevo.')
            return render_template('register.html')
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Insertar nuevo usuario en la base de datos
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO usuarios (username, password) VALUES (%s, %s)", (username, password_hash))
        mysql.connection.commit()

        flash('Usuario registrado exitosamente, ahora puedes iniciar sesión')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/mis_registros', methods=['GET'])
def mis_registros():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    # Obtener los registros del usuario desde la base de datos
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM registros WHERE user_id = %s", (user_id,))
    registros = cur.fetchall()
    cur.close()

    return render_template('mis_registros.html', registros=registros)

# Ruta de clasificación (donde el usuario ingresa datos)
@app.route('/clasificar', methods=['GET', 'POST'])
def clasificar():
    user_id = session.get('user_id')
    print(user_id)
    if not user_id:
        return redirect(url_for('login'))
    if request.method == 'POST':
        departamento_input = request.form['depto'].strip().upper()  # Convierte a mayúsculas

        try:
            generacion_input = float(request.form['generacion'])
        except ValueError:
            return render_template('index.html', error="Por favor, ingresa una cantidad válida para la generación.")

        # Buscar el número del departamento usando la función buscar_departamento_numero
        departamento_numero = buscar_departamento_numero(departamento_input)
        departamento_numero = str(departamento_numero) 
        
        print(f"Departamento ingresado: {departamento_numero}")

        # Usamos la función de clasificación
        resultado = clasificacion.clasificar_departamento(departamento_numero, generacion_input)
        print(f"Departamento ingresado: {resultado}")

        if resultado:
            
            # Guardamos el registro en la base de datos
            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO registros (user_id, departamento, generacion, clasificacion)
                VALUES (%s, %s, %s, %s)
            """, (user_id, departamento_input, generacion_input, resultado))
            mysql.connection.commit()
            cur.close()

            # Mostrar el resultado en la página
            return render_template('index.html', result=resultado)
        else:
            return render_template('index.html', error="Departamento no encontrado.")
    
    # Si es un GET, se muestra el formulario
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
