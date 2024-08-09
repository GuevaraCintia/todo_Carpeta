from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)

# Configuración de la base de datos
app.config['SECRET_KEY'] = 'mysecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar la base de datos
db = SQLAlchemy(app)

# Modelo de la base de datos
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)

# Ruta para la página principal
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para el registro
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = data['password']
    email = data['email']

    # Validar que los campos no estén vacíos
    if not username or not password or not email:
        return jsonify({'success': False, 'message': 'Todos los campos son obligatorios'}), 400

    # Verificar si el usuario ya existe
    user = User.query.filter_by(username=username).first()
    if user:
        return jsonify({'success': False, 'message': 'El usuario ya existe'}), 400

    # Crear nuevo usuario
    hashed_password = generate_password_hash(password, method='sha256')
    new_user = User(username=username, password=hashed_password, email=email)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'success': True}), 200

# Ruta para el login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    # Validar que los campos no estén vacíos
    if not username or not password:
        return jsonify({'success': False, 'message': 'Usuario y contraseña son obligatorios'}), 400

    # Buscar usuario en la base de datos
    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({'success': False, 'message': 'Usuario o contraseña incorrectos'}), 401

    # Iniciar sesión
    session['user_id'] = user.id
    return jsonify({'success': True}), 200

# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Crear base de datos si no existe
    if not os.path.exists('users.db'):
        db.create_all()
    app.run(host='0.0.0.0', port=5000)
