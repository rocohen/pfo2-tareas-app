import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

# =====================================
# Clase Override para métodos HTTP 
# que no son soportados por HTML forms
# =====================================
class MethodOverrideMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        if environ.get('REQUEST_METHOD') == 'POST':
            from io import BytesIO
            from urllib.parse import parse_qs

            try:
                request_body_size = int(environ.get('CONTENT_LENGTH', 0))
            except (ValueError, TypeError):
                request_body_size = 0

            if request_body_size > 0:
                try:
                    # Leer el body sin romper si está vacío
                    request_body = environ['wsgi.input'].read(request_body_size)
                    # Resetear el stream para que Flask pueda volver a leerlo
                    environ['wsgi.input'] = BytesIO(request_body)

                    # Parsear formulario
                    form_data = parse_qs(request_body.decode(errors="ignore"))
                    method_override = form_data.get('_method', [None])[0]

                    if method_override and method_override.upper() in ['PUT', 'DELETE', 'PATCH']:
                        environ['REQUEST_METHOD'] = method_override.upper()
                except Exception:
                    # Si falla el parseo, no romper el flujo
                    pass

        return self.app(environ, start_response)

app = Flask(__name__)
app.secret_key ="supersecretkey"
app.wsgi_app = MethodOverrideMiddleware(app.wsgi_app)



# ======================
# Configuración del ORM
# ======================
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///tareas.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Inicialización de la base de datos
db = SQLAlchemy(app)

def inicializar_bd():
    try:
        with app.app_context():
            # Verificar si la base de datos ya existe
            db_exists = os.path.exists('tareas.db')
            db.create_all()
            
            if not db_exists:
                print("Base de datos inicializada correctamente")
            else:
                print("Base de datos verificada")
                
    except Exception as e:
        print(f"Error al inicializar la base de datos: {e}")

# ======================
# Modelos de la base de datos
# ======================
class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Tarea(db.Model):
    __tablename__ = 'tareas'

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    done = db.Column(db.Boolean, default=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())  

    usuario = db.relationship('Usuario', backref=db.backref('tareas', lazy=True))

# =================================
# Función utilitaria para responder 
# tanto HTML como JSON
# =================================
def responder(template_name=None, context=None, json_data=None, status_code=200):
    """
    Devuelve HTML o JSON según el cliente lo requiera.
    Maneja tanto respuestas normales como errores.
    """
    context = context or {}
    json_data = json_data or context

    if request.accept_mimetypes['application/json'] >= request.accept_mimetypes['text/html']:
        return jsonify(json_data), status_code
    return render_template(template_name, **context), status_code

# ===============================================
# Decorador para restringir el acceso a rutas
# de la aplicación si el usuario no está logueado
# ===============================================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            session.pop('username', None)
            return responder(
                template_name="index.html",
                context={"error": "Debes iniciar sesión."},
                json_data={"error": "No autorizado"},
                status_code=401
            )
        # Verificar si el usuario existe en la base de datos
        usuario = Usuario.query.filter_by(username=session['username']).first()
        if not usuario:
            session.pop('username', None)
            return responder(
                template_name="index.html",
                context={"error": "Usuario no encontrado."},
                json_data={"error": "Usuario no encontrado."},
                status_code=404
            )
        return f(*args, **kwargs)
    return decorated_function


# ======================
# Rutas de la aplicación
# ======================

@app.route('/')
def home():
    return render_template('index.html')


# ======================
# Rutas de usuarios
# ======================

# Login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True)
    if data:
        username = data.get('username')
        password = data.get('password')
    # Si no es JSON, obtiene los datos del formulario
    else:
        username = request.form.get('username')
        password = request.form.get('password')

    # Caso: faltan credenciales
    if not username or not password:
        return responder(
            template_name="index.html",
            context={"error": "Faltan credenciales."},
            json_data={"error": "Faltan credenciales."},
            status_code=400
        )

    usuario = Usuario.query.filter_by(username=username).first()
    # Si Usuario no existe
    if not usuario:
        return responder(
            template_name="index.html",
            context={"error": "Usuario no encontrado."},
            json_data={"error": "Usuario no encontrado."},
            status_code=404
        )

    if usuario and usuario.check_password(password):
        session['username'] = username
        # Trae sólo las tareas del usuario logueado
        tareas = Tarea.query.filter_by(usuario_id=usuario.id).order_by(Tarea.created_at.desc()).all()
        tareas_list = [{"id": tarea.id, "description": tarea.description, "done": tarea.done} for tarea in tareas]
        # Si el cliente pide JSON devuelve info de sesión
        # Si pide HTML redirige al dashboard de tareas
        return responder(
            template_name="tareas.html",
            context={"usuario": username, "tareas": tareas_list},
            json_data={"mensaje": "Login exitoso", "usuario": username}
        )

    # Credenciales inválidas
    return responder(
        template_name="index.html",
        context={"error": "Credenciales inválidas."},
        json_data={"error": "Credenciales inválidas."},
        status_code=401
    )

# Registro
@app.route('/registro', methods=['POST'])
def registrar():
    data = request.get_json(silent=True)
    if data:
        username = data.get('username')
        password = data.get('password')
    # Si no es JSON, obtiene los datos del formulario
    else:
        username = request.form.get('username')
        password = request.form.get('password')

    usuario = Usuario.query.filter_by(username=username).first()

    # Caso: faltan credenciales
    if not username or not password:
        return responder(
            template_name="index.html",
            context={"error": "Faltan credenciales."},
            json_data={"error": "Faltan credenciales."},
            status_code=400
        )
        
    # Caso: usuario ya existe
    if usuario:
        return responder(
            template_name="index.html",
            context={"error": "El usuario ya existe."},
            json_data={"error": "El usuario ya existe."},
            status_code=409
        )

    nuevo_usuario = Usuario(username=username)
    nuevo_usuario.set_password(password)
    db.session.add(nuevo_usuario)
    db.session.commit()

    session['username'] = username

    return responder(
        template_name="tareas.html",
        context={"usuario": username},
        json_data={"mensaje": "Registro exitoso", "usuario": username}
    )

# Logout
@app.route('/logout', methods=['GET'])
@login_required
def logout():
   session.pop('username', None)
   return redirect(url_for('home'))
   
# ======================
# Rutas de tareas
# ======================
# Dashboard de tareas - Listar tareas
@app.route('/tareas', methods=['GET'])
@login_required
def get_tareas():
    # Trae sólo las tareas del usuario logueado
    usuario = Usuario.query.filter_by(username=session['username']).first()
    tareas = Tarea.query.filter_by(usuario_id=usuario.id).order_by(Tarea.created_at.desc()).all()
    tareas_list = [{"id": tarea.id, "description": tarea.description, "done": tarea.done} for tarea in tareas]

    return responder(
        template_name="tareas.html",
        context={"tareas": tareas_list, "usuario": session['username']},
        json_data={"tareas": tareas_list}
    )

# Crear una tarea nueva
@app.route('/tareas', methods=['POST'])
@login_required
def add_tarea():
    data = request.get_json(silent=True)
    if data:
        description = data.get('description')
        done = data.get('done', False)
    # Si no es JSON, obtiene los datos del formulario
    else:
        description = request.form.get('description')
        done = request.form.get('done')

    # Obtener el usuario actual
    usuario = Usuario.query.filter_by(username=session['username']).first()
    tareas = Tarea.query.filter_by(usuario_id=usuario.id).order_by(Tarea.created_at.desc()).all()
    tareas_list = [{"id": tarea.id, "description": tarea.description, "done": tarea.done} for tarea in tareas]

    if not description:
        usuario = Usuario.query.filter_by(username=session['username']).first()
        tareas = Tarea.query.filter_by(usuario_id=usuario.id).all()
        return responder(
            template_name="tareas.html",
            context={"error": "La tarea no puede estar vacía.", "usuario": session.get('username'), "tareas": tareas_list},
            json_data={"error": "La tarea no puede estar vacía."},
            status_code=400
        )

    
    done_bool = True if done == "true" or done is True else False

    # Crear y guardar la nueva tarea asociada al usuario
    nueva_tarea = Tarea(description=description, done=done_bool, usuario_id=usuario.id)
    db.session.add(nueva_tarea)
    db.session.commit()

    if request.accept_mimetypes['application/json'] >= request.accept_mimetypes['text/html']:
        return responder(
            json_data={"mensaje": "Tarea creada exitosamente", "tarea": {
                "id": nueva_tarea.id, 
                "description": nueva_tarea.description, 
                "done": nueva_tarea.done
            }},
            status_code=201
        )
    
    # Si es petición normal, redirigir a GET /tareas
    return redirect(url_for('get_tareas'))


# Actualizar una tarea existente
@app.route('/tareas/<int:id>', methods=['PUT'])
@login_required
def put_tarea(id):
    # La variable 'id' viene de la URL.
    tarea_id = id
    
    # Intenta obtener datos de JSON (prioritario)
    data = request.get_json(silent=True)

    if data:
        # Si hay datos JSON, se usan esos.
        description = data.get('description')
        done = data.get('done', None) # Se usa None para manejar el caso de no estar presente
    else:
        # Si no hay JSON, se usan los datos del formulario.
        description = request.form.get('description')
        done = request.form.get('done')
    
    try:
        tarea_id = int(tarea_id)
    except (ValueError, TypeError):
        return responder(
            template_name="tareas.html",
            context={"error": "ID de tarea inválido."},
            json_data={"error": "ID de tarea inválido."},
            status_code=400
        )
        
    # Obtener el usuario actual
    usuario = Usuario.query.filter_by(username=session['username']).first()
    
    # Buscar la tarea y verificar que pertenece al usuario
    tarea = Tarea.query.filter_by(id=tarea_id, usuario_id=usuario.id).first()
    
    if not tarea:
        return responder(
            template_name="tareas.html",
            context={"error": "Tarea no encontrada."},
            json_data={"error": "Tarea no encontrada."},
            status_code=404
        )

    if description:
        tarea.description = description
    
    # Se actualiza el estado 'done' si se proporciona
    if done is not None:
        tarea.done = done.lower() == 'true' if isinstance(done, str) else done

    # Se guardan los cambios en la base de datos
    db.session.commit()
    # Se traen las tareas
    tareas = Tarea.query.filter_by(usuario_id=usuario.id).order_by(Tarea.created_at.desc()).all()
    tareas_list = [{"id": tarea.id, "description": tarea.description, "done": tarea.done} for tarea in tareas]
    
    return responder(
        template_name="tareas.html",
        context={"mensaje": "Tarea actualizada exitosamente.", "usuario": session['username'], "tareas": tareas_list},
        json_data={"mensaje": "Tarea actualizada exitosamente", "tarea": {"id": tarea.id, "description": tarea.description, "done": tarea.done}},
        status_code=200
    )


# Eliminar una tarea
@app.route('/tareas/<int:id>', methods=['DELETE'])
@login_required
def delete_tarea(id):
    tarea_id = id
    
    # Comprobamos si la solicitud es de tipo JSON.
    data = request.get_json(silent=True)
    if data:
        # Si el JSON contiene un 'id', lo usamos.
        tarea_id = data.get('id', id) 
    
    try:
        tarea_id = int(tarea_id)
    except (ValueError, TypeError):
        return responder(
            template_name="tareas.html",
            context={"error": "ID de tarea inválido."},
            json_data={"error": "ID de tarea inválido."},
            status_code=400
        )
    
    # Obtiene el usuario actual
    usuario = Usuario.query.filter_by(username=session['username']).first()
    
    # Busca la tarea y verificar que pertenece al usuario
    tarea = Tarea.query.filter_by(id=tarea_id, usuario_id=usuario.id).first()
    
    if not tarea:
        return responder(
            template_name="tareas.html",
            context={"error": "Tarea no encontrada."},
            json_data={"error": "Tarea no encontrada."},
            status_code=404
        )
        
    db.session.delete(tarea)
    db.session.commit()
    # Trae sólo las tareas del usuario logueado
    tareas = Tarea.query.filter_by(usuario_id=usuario.id).order_by(Tarea.created_at.desc()).all()
    tareas_list = [{"id": tarea.id, "description": tarea.description, "done": tarea.done} for tarea in tareas]
    
    return responder(
            template_name="tareas.html",
            context={"mensaje": "Tarea eliminada exitosamente.", "usuario": session['username'], "tareas": tareas_list},
            json_data={"mensaje": "Tarea eliminada exitosamente."},
            status_code=200
    )


#=================================
#Captura todas las rutas que no 
# están definidas explícitamente
#================================
@app.route('/<path:path>')
def catch_all(path):
    return responder(
        template_name="Error/404.html",
        context={"mensaje": f"La ruta '/{path}' no existe.", "ruta": path},
        json_data={"error": f"La ruta '/{path}' no existe.", "ruta": path},
        status_code=404
    )

# Manejo de errores
@app.errorhandler(404)
def pagina_no_encontrada(e):
    return responder(
        template_name="Error/404.html" if request.accept_mimetypes['text/html'] else None,
        context={"mensaje": "La página que buscás no existe."},
        json_data={"error": "La página que buscás no existe."},
        status_code=404
    )

@app.errorhandler(500)
def error_interno(e):
    return responder(
        template_name="Error/500.html" if request.accept_mimetypes['text/html'] else None,
        context={"mensaje": "Error interno en el servidor."},
        json_data={"error": "Error interno en el servidor."},
        status_code=500
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)