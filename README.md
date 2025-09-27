# PFO2 - Programación sobre Redes

REST API desarrollada con **Flask**, utilizando **SQLAlchemy** como ORM y **SQLite** como base de datos para la gestión de tareas de usuarios.

## 📋 Descripción

Esta aplicación web permite a los usuarios gestionar sus tareas personales a través de una interfaz REST API completa. La aplicación maneja autenticación de usuarios y operaciones CRUD (Crear, Leer, Actualizar, Eliminar) para las tareas.

Ver descripción completa en githubpages [Link](https://rocohen.github.io/pfo2-tareas-app/)

## ✨ Funcionalidades

La aplicación permite realizar las siguientes operaciones:

1. **👤 Registrar usuarios** con nombre de usuario y contraseña
2. **🔐 Iniciar sesión** con nombre de usuario y contraseña
3. **➕ Crear tareas** mediante una descripción y la opción de establecer un estado (completada o pendiente). Por defecto es pendiente
4. **📋 Listar todas las tareas** del usuario logueado
5. **✏️ Actualizar o modificar una tarea** (tanto la descripción como su estado pueden actualizarse)
6. **🗑️ Eliminar una tarea**
7. **👋 Cerrar sesión** (logout)

## 🛠️ Tecnologías Utilizadas

- **Backend**: Flask (Python)
- **ORM**: SQLAlchemy
- **Base de Datos**: SQLite
- **Templating**: Jinja2
- **Frontend**: HTML + Tailwind CSS
- **Cliente**: Requests (Python)

## 📦 Instalación y Configuración

### Requisitos Previos
- Python 3.7 o superior
- pip (gestor de paquetes de Python)

### Instalación

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/rocohen/pfo2-tareas-app
   cd pfo2-tareas-app
   ```

2. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Inicializar el servidor**
   ```bash
   python servidor.py
   ```
   
   El servidor se ejecutará en `http://127.0.0.1:5000`

## 🎯 Usuarios de Prueba

La aplicación incluye los siguientes usuarios de prueba:

| Usuario | Contraseña |
|---------|------------|
| Juan    | 1234       |
| Ana     | 1234       |
| Fran    | 1234       |
| María   | 1234       |

## 🌐 API Endpoints

### Autenticación
- `POST /login` - Iniciar sesión
- `POST /registrar` - Registrar nuevo usuario
- `GET /logout` - Cerrar sesión

### Gestión de Tareas
- `GET /tareas` - Listar todas las tareas del usuario
- `POST /tareas` - Crear una nueva tarea
- `PUT /tareas/<id>` - Actualizar una tarea específica
- `DELETE /tareas/<id>` - Eliminar una tarea específica

## 📱 Tipos de Respuesta

La aplicación soporta **respuestas duales**:

- **🌐 HTML**: Renderizado con Jinja2 desde el servidor para navegadores web
- **📡 JSON**: Para clientes API y aplicaciones que consumen la API

El tipo de respuesta se determina automáticamente según las cabeceras HTTP de la petición (`Accept`).

## 🖥️ Cliente de Consola

El proyecto incluye un **cliente de consola** (`cliente.py`) que despliega un menú interactivo para probar todas las funcionalidades de la aplicación.

### Uso del Cliente

1. **Asegurarse de que el servidor esté ejecutándose**
   ```bash
   python servidor.py
   ```

2. **En otra terminal, ejecutar el cliente**
   ```bash
   python cliente.py
   ```

3. **Seguir el menú interactivo**
   ```
   📋 CLIENTE API - MENÚ
   ===============================
   1. Registrar usuario
   2. Login
   3. Listar tareas
   4. Agregar tarea
   5. Actualizar tarea
   6. Eliminar tarea
   0. Salir
   ```

## 📁 Estructura del Proyecto

```
pfo2-tareas-app/
├── intance/
|   ├── tarea.db 
├── servidor.py             # Aplicación principal Flask
├── cliente.py              # Cliente de consola
├── requirements.txt        # Dependencias del proyecto
├── README.md               # Este archivo
├── templates/              # Templates HTML
│   ├── base.html           # Template base
│   ├── index.html          # Página de inicio/login
│   ├── tareas.html         # Dashboard de tareas
|   ├── header.html         # Template header
│   └── Error/              # Templates de error
│       ├── 404.html        # Página no encontrada
│       └── 500.html        # Error interno del servidor
└── tareas.db               # Base de datos SQLite (generada automáticamente)
```

## 🔧 Ejemplos de Uso

### Crear una nueva tarea (JSON)
```bash
curl -X POST http://127.0.0.1:5000/tareas \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"description": "Completar el proyecto", "done": false}' \
  -b cookies.txt
```

### Listar tareas (JSON)
```bash
curl -X GET http://127.0.0.1:5000/tareas \
  -H "Accept: application/json" \
  -b cookies.txt
```

### Actualizar una tarea (JSON)
```bash
curl -X PUT http://127.0.0.1:5000/tareas/1 \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"description": "Tarea actualizada", "done": true}' \
  -b cookies.txt
```

## 🚀 Características Técnicas

- **Autenticación basada en sesiones** con Flask-Session
- **Validación de entrada** en todos los endpoints
- **Manejo de errores** personalizado (404, 500)
- **Middleware para métodos HTTP** (PUT, DELETE) en formularios HTML
- **Seguridad**: Hash de contraseñas con Werkzeug
- **Base de datos relacional** con SQLAlchemy ORM
- **Responsive design** con Tailwind CSS

## 📝 Notas Importantes

- **⚠️ IMPORTANTE**: Instalar los paquetes necesarios con `pip install -r requirements.txt` e inicializar primero `servidor.py` antes de ejecutar el cliente
- La base de datos SQLite se crea automáticamente la primera vez que se ejecuta la aplicación
- Las sesiones se mantienen mediante cookies HTTP
- El cliente de consola maneja automáticamente las cookies de sesión

## 👥 Contribución

Este proyecto fue desarrollado como PFO2 de la materia Programación sobre Redes.

## 📄 Licencia

Este proyecto es de uso académico para la materia Programación sobre Redes.
