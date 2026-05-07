import sqlite3
import os

class Database:
    def __init__(self):
        # Usar %APPDATA% para guardar la base de datos
        appdata = os.environ.get('APPDATA')
        if not appdata:
            appdata = os.path.expanduser("~")
        
        db_dir = os.path.join(appdata, "Inventario TI")
        os.makedirs(db_dir, exist_ok=True)
        db_path = os.path.join(db_dir, "inventario.db")
        
        self.conexion = sqlite3.connect(db_path)
        self.cursor = self.conexion.cursor()
        self._crear_tablas()

    def _crear_tablas(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS equipos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT UNIQUE NOT NULL,
                numero_serie TEXT UNIQUE,
                nombre TEXT NOT NULL,
                categoria TEXT NOT NULL,
                tipo TEXT,
                estado TEXT NOT NULL,
                direccion_mac TEXT,
                asignado_a TEXT,
                fecha_adquisicion TEXT,
                notas TEXT
            )
        ''')
        self.conexion.commit()

    def get_equipos(self, search_query="", category_filter="Todos", status_filter="Todos"):
        query = "SELECT * FROM equipos WHERE 1=1"
        params = []

        if search_query:
            query += " AND (codigo LIKE ? OR nombre LIKE ? OR numero_serie LIKE ? OR asignado_a LIKE ?)"
            like_term = f"%{search_query}%"
            params.extend([like_term, like_term, like_term, like_term])

        if category_filter != "Todos":
            query += " AND categoria = ?"
            params.append(category_filter)

        if status_filter != "Todos":
            query += " AND estado = ?"
            params.append(status_filter)

        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def agregar_equipo(self, datos):
        try:
            self.cursor.execute('''
                INSERT INTO equipos 
                (codigo, numero_serie, nombre, categoria, tipo, estado, direccion_mac, asignado_a, fecha_adquisicion, notas)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', datos)
            self.conexion.commit()
            return True, "Equipo agregado correctamente."
        except sqlite3.IntegrityError:
            return False, "Error de integridad: Ya existe un equipo con ese código o número de serie."
        except Exception as e:
            return False, str(e)

    def actualizar_equipo(self, id_equipo, datos):
        try:
            self.cursor.execute('''
                UPDATE equipos SET
                codigo=?, numero_serie=?, nombre=?, categoria=?, tipo=?, estado=?, 
                direccion_mac=?, asignado_a=?, fecha_adquisicion=?, notas=?
                WHERE id=?
            ''', (*datos, id_equipo))
            self.conexion.commit()
            return True, "Equipo actualizado correctamente."
        except sqlite3.IntegrityError:
            return False, "Error: El código o número de serie ya está en uso."
        except Exception as e:
            return False, str(e)

    def eliminar_equipo(self, id_equipo):
        try:
            self.cursor.execute("DELETE FROM equipos WHERE id=?", (id_equipo,))
            self.conexion.commit()
            return True, "Equipo eliminado correctamente."
        except Exception as e:
            return False, str(e)

    def get_metricas(self):
        self.cursor.execute("SELECT COUNT(*) FROM equipos")
        total = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM equipos WHERE estado='Activo'")
        activos = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM equipos WHERE estado='En Reparacion'")
        reparacion = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM equipos WHERE estado='Inactivo' OR estado='De Baja'")
        inactivos = self.cursor.fetchone()[0]
        
        return {
            "total": total,
            "activos": activos,
            "reparacion": reparacion,
            "inactivos": inactivos
        }

    def get_metricas_por_categoria(self):
        self.cursor.execute("SELECT categoria, COUNT(*) FROM equipos GROUP BY categoria")
        return dict(self.cursor.fetchall())

    def get_ultimos_equipos(self, limite=5):
        self.cursor.execute("SELECT codigo, nombre, categoria, estado FROM equipos ORDER BY id DESC LIMIT ?", (limite,))
        return self.cursor.fetchall()
