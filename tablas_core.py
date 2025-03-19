import sqlite3

def create_tables():
    connection = sqlite3.connect("db.sqlite3")
    cursor = connection.cursor()

    # Tabla Pais
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS core_pais (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT UNIQUE NOT NULL
    );
    ''')

    # Tabla Provincia
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS core_provincia (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT UNIQUE NOT NULL,
        pais_id INTEGER NOT NULL,
        FOREIGN KEY (pais_id) REFERENCES Pais (id) ON DELETE CASCADE
    );
    ''')

    # Tabla Localidad
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS core_localidad (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        provincia_id INTEGER NOT NULL,
        FOREIGN KEY (provincia_id) REFERENCES Provincia (id) ON DELETE CASCADE,
        UNIQUE (nombre, provincia_id)
    );
    ''')

    # Tabla Servicio
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS core_servicio (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT UNIQUE NOT NULL,
        descripcion TEXT
    );
    ''')

    # Tabla Categoria
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS core_categoria (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        estrellas INTEGER NOT NULL,
        nombre TEXT UNIQUE NOT NULL
    );
    ''')

    # Tabla intermedia Categoria-Servicio
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS core_categoria_servicios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        categoria_id INTEGER NOT NULL,
        servicio_id INTEGER NOT NULL,
        FOREIGN KEY (categoria_id) REFERENCES Categoria (id) ON DELETE CASCADE,
        FOREIGN KEY (servicio_id) REFERENCES Servicio (id) ON DELETE CASCADE
    );
    ''')

    # Tabla TipoHabitacion
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS core_tipohabitacion (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT UNIQUE NOT NULL,
        descripcion TEXT,
        pasajeros INTEGER NOT NULL,
        cuartos INTEGER DEFAULT 0
    );
    ''')

    # Tabla Persona
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS core_persona (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo_documento INTEGER NOT NULL,
        documento TEXT NOT NULL,
        nombre TEXT NOT NULL,
        apellido TEXT NOT NULL,
        usuario_id INTEGER,
        FOREIGN KEY (usuario_id) REFERENCES auth_user (id) ON DELETE SET NULL
    );
    ''')

    # Tabla Rol
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS core_rol (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        persona_id INTEGER NOT NULL,
        tipo INTEGER NOT NULL,
        FOREIGN KEY (persona_id) REFERENCES Persona (id) ON DELETE CASCADE
    );
    ''')

    # Tabla Encargado
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS core_encargado (
        rol_ptr_id INTEGER PRIMARY KEY,
        bajaEncargado BOOLEAN DEFAULT 0,
        clave TEXT DEFAULT "",
        FOREIGN KEY (rol_ptr_id) REFERENCES Rol (id) ON DELETE CASCADE
    );
    ''')

    # Tabla Vendedor
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS core_vendedor (
        rol_ptr_id INTEGER PRIMARY KEY,
        estoyHabilitado BOOLEAN DEFAULT 1,
        coeficiente DECIMAL(3, 2) DEFAULT 0,
        FOREIGN KEY (rol_ptr_id) REFERENCES Rol (id) ON DELETE CASCADE
    );
    ''')

    # Tabla Cliente
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS core_cliente (
        rol_ptr_id INTEGER PRIMARY KEY,
        bajaCliente BOOLEAN DEFAULT 0,
        puntos INTEGER DEFAULT 0,
        FOREIGN KEY (rol_ptr_id) REFERENCES Rol (id) ON DELETE CASCADE
    );
    ''')

    connection.commit()
    connection.close()

if __name__ == "__main__":
    create_tables()
    print("Tablas creadas exitosamente en la base de datos SQLite.")