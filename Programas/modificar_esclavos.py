import pymysql

DB_CONFIG = {
    "host": "192.168.1.14", 
    "user": "root",
    "password": "",
    "database": "dryermon",
    "port": 3306,
    "autocommit": True,
    "cursorclass": pymysql.cursors.DictCursor
}

# ---------------- DB ----------------

def get_conn():
    return pymysql.connect(**DB_CONFIG)

# ---------------- Funciones ----------------

def listar_esclavos():
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, esclavo, nombre, descripcion, version, habilitado
                    FROM esclavos
                    ORDER BY esclavo
                """)
                rows = cur.fetchall()

                print("\nID | Esclavo | Nombre | Versión | Habilitado | Descripción")
                print("-" * 70)
                for r in rows:
                    print(f"{r['id']:>2} | {r['esclavo']:>7} | {r['nombre']:<6} | "
                          f"{r['version']:>7} | {r['habilitado']:>10} | {r['descripcion']}")

    except pymysql.MySQLError as e:
        print("❌ Error al listar:", e)

def alta_o_actualiza():
    try:
        esclavo = int(input("Número de esclavo: "))
        nombre = input("Nombre (max 5): ")[:5]
        descripcion = input("Descripción: ")
        version = int(input("Versión (ej 104 significa 1.04): "))
        habilitado = int(input("Habilitado (1/0): "))

        x1 = int(input("x1: "))
        x2 = int(input("x2: "))
        y1 = int(input("y1: "))
        y2 = int(input("y2: "))
        temp1 = int(input("temp1 (1/0): "))
        temp2 = int(input("temp2 (1/0): "))

        sql = """
        INSERT INTO esclavos
        (esclavo, nombre, descripcion, version, habilitado,
         x1, x2, y1, y2, temp1, temp2)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE
            nombre=VALUES(nombre),
            descripcion=VALUES(descripcion),
            version=VALUES(version),
            habilitado=VALUES(habilitado),
            x1=VALUES(x1),
            x2=VALUES(x2),
            y1=VALUES(y1),
            y2=VALUES(y2),
            temp1=VALUES(temp1),
            temp2=VALUES(temp2)
        """

        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (
                    esclavo, nombre, descripcion, version, habilitado,
                    x1, x2, y1, y2, temp1, temp2
                ))

        print("✔ Esclavo guardado correctamente")

    except ValueError:
        print("❌ Error: dato inválido")
    except pymysql.MySQLError as e:
        print("❌ Error MySQL:", e)

def deshabilitar():
    try:
        esclavo = int(input("Número de esclavo a deshabilitar: "))
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE esclavos SET habilitado=0 WHERE esclavo=%s",
                    (esclavo,)
                )
        print("✔ Esclavo deshabilitado")

    except pymysql.MySQLError as e:
        print("❌ Error:", e)

def habilitar():
    try:
        esclavo = int(input("Número de esclavo a habilitar: "))
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE esclavos SET habilitado=1 WHERE esclavo=%s",
                    (esclavo,)
                )
        print("✔ Esclavo habilitado")

    except pymysql.MySQLError as e:
        print("❌ Error:", e)


def eliminar():
    try:
        esclavo = int(input("Número de esclavo a eliminar: "))
        confirm = input("¿Seguro? (s/N): ").lower()
        if confirm != "s":
            print("Cancelado")
            return

        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM esclavos WHERE esclavo=%s",
                    (esclavo,)
                )

        print("✔ Esclavo eliminado")

    except pymysql.MySQLError as e:
        print("❌ Error:", e)

# ---------------- Menú ----------------

def menu():
    while True:
        print("""
======== MENÚ ESCLAVOS ========
1) Listar esclavos
2) Alta / Actualizar esclavo
3) Deshabilitar esclavo
4) Habilitar esclavo              
5) Eliminar esclavo
6) Salir
""")

        op = input("Opción: ").strip()

        if op == "1":
            listar_esclavos()
        elif op == "2":
            alta_o_actualiza()
        elif op == "3":
            deshabilitar()
        elif op == "4":
            habilitar()
        elif op == "5":
            eliminar()
        elif op == "6":
            print("Saliendo...")
            break
        else:
            print("❌ Opción inválida")

if __name__ == "__main__":
    menu()
