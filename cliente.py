import requests

BASE_URL = "http://127.0.0.1:5000"  # URL donde corre el servidor local de Flask
session = requests.Session()
session.headers.update({"Accept": "application/json"})


def registrar():
    username = input("Ingrese nombre de usuario: ")
    password = input("Ingrese contraseña: ")
    res = session.post(f"{BASE_URL}/registrar", json={"username": username, "password": password})
    print("Respuesta:", res.status_code, res.json())


def login():
    username = input("Ingrese nombre de usuario: ")
    password = input("Ingrese contraseña: ")
    res = session.post(f"{BASE_URL}/login", json={"username": username, "password": password})
    print("Respuesta:", res.status_code, res.json())


def listar_tareas():
    res = session.get(f"{BASE_URL}/tareas")
    print("Respuesta:", res.status_code)
    if res.ok:
        for tarea in res.json().get("tareas", []):
            estado = "✔️" if tarea["done"] else "⏳"
            print(f"  {tarea['id']}: {tarea['description']} [{estado}]")
    else:
        print(res.json())


def agregar_tarea():
    description = input("Descripción de la tarea: ")
    done = input("¿Está completada? (s/n): ").lower() == "s"
    res = session.post(f"{BASE_URL}/tareas", json={"description": description, "done": done})
    print("Respuesta:", res.status_code, res.json())


def actualizar_tarea():
    tarea_id = input("ID de la tarea a actualizar: ")
    description = input("Nueva descripción (dejar vacío para no cambiar): ")
    done_input = input("Nuevo estado (s/n/dejar vacío): ").lower()
    done = None
    if done_input == "s":
        done = True
    elif done_input == "n":
        done = False

    payload = {}
    if description:
        payload["description"] = description
    if done is not None:
        payload["done"] = done

    res = session.put(f"{BASE_URL}/tareas/{tarea_id}", json=payload)
    print("Respuesta:", res.status_code, res.json())


def eliminar_tarea():
    tarea_id = input("ID de la tarea a eliminar: ")
    res = session.delete(f"{BASE_URL}/tareas/{tarea_id}")
    print("Respuesta:", res.status_code, res.json())


def menu():
    opciones = {
        "1": ("Registrar usuario", registrar),
        "2": ("Login", login),
        "3": ("Listar tareas", listar_tareas),
        "4": ("Agregar tarea", agregar_tarea),
        "5": ("Actualizar tarea", actualizar_tarea),
        "6": ("Eliminar tarea", eliminar_tarea),
        "0": ("Salir", None),
    }

    while True:
        print("\n=== Cliente API - Menú ===")
        for k, (desc, _) in opciones.items():
            print(f"{k}. {desc}")

        opcion = input("Seleccione una opción: ").strip()
        if opcion == "0":
            print("Saliendo del cliente...")
            break
        elif opcion in opciones:
            try:
                opciones[opcion][1]() 
            except Exception as e:
                print("Error ejecutando la acción:", e)
        else:
            print("Opción inválida.")


if __name__ == "__main__":
    menu()
