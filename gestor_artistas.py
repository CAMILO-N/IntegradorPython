import pyodbc
import json

# Aca lo que hicimos fue crear la clase principal que va a contener todo el sistema CRUD
class GestorArtistas:

    # Este es el constructor, lo que hicimos aca fue inicializar la conexion al arrancar el objeto
    def __init__(self):
        try:
            # Aca abrimos el archivo config.json para leer los datos de conexion sin hardcodearlos
            with open('config.json', 'r') as archivo_config:
                config = json.load(archivo_config)

            # Lo que hicimos fue extraer cada dato del JSON en su propia variable para tenerlo limpio
            name_server      = config['name_server']
            database         = config['database']
            controlador_odbc = config['controlador_odbc']
            usuario          = config['usuario']
            clave            = config['clave']

            # Aca armamos la cadena de conexion juntando todos los datos que sacamos del JSON
            self.connection_string = (
                f"DRIVER={controlador_odbc};"
                f"SERVER={name_server};"
                f"DATABASE={database};"
                f"UID={usuario};"
                f"PWD={clave};"
            )
            # Aqui establecemos la conexion y la guardamos en self para usarla en todos los metodos
            self.conexion = pyodbc.connect(self.connection_string)
            print("Conexion establecida correctamente con SonoraInc.")

        except FileNotFoundError:
            # Si no encuentra el config.json avisamos con un mensaje claro
            print("Error: no se encontro el archivo config.json.")
            raise
        except Exception as e:
            # Aca capturamos cualquier otro error que pueda ocurrir al conectar
            print(f"Error al conectar con la base de datos: {e}")
            raise

    # Este metodo es el CREATE, aca lo que hicimos fue pedir los datos al usuario e invocar el SP de insercion
    def insertar_artista(self):
        try:
            print("\n--- REGISTRAR ARTISTA ---")
            # Pedimos cada dato por teclado y usamos strip() para limpiar espacios
            nombre        = input("Nombre del artista: ").strip()
            pais          = input("Pais de origen: ").strip()
            # Aca pusimos or None para que si el usuario no escribe nada se guarde como NULL en la BD
            descripcion   = input("Descripcion (Enter para omitir): ").strip() or None
            id_productora = int(input("ID de la productora: "))

            # Creamos el cursor, que es el objeto que nos permite mandar comandos a la base
            cursor = self.conexion.cursor()
            # Aca lo que hicimos fue llamar al stored procedure con los parametros usando ? para evitar SQL injection
            cursor.execute(
                "EXEC Procesos.sp_InsertarArtista "
                "@nombreArtista=?, @paisOrigenArtista=?, "
                "@descripcionArtista=?, @Productora_idProductora=?",
                nombre, pais, descripcion, id_productora
            )
            # Leemos la respuesta que nos devuelve el SP, en este caso el mensaje y el ID generado
            row = cursor.fetchone()
            if row:
                print(f"\n{row[0]} - ID asignado: {row[1]}")
            # Aca confirmamos los cambios, sin esto el INSERT no queda guardado
            self.conexion.commit()

        except Exception as e:
            print(f"Error al insertar artista: {e}")

    # Este es el READ, aca lo que hicimos fue dar la opcion de ver todos los artistas o filtrar por ID
    def consultar_artistas(self):
        try:
            print("\n--- CONSULTAR ARTISTAS ---")
            # Le preguntamos al usuario si quiere buscar uno especifico o ver todos
            opcion = input("Consultar por ID? (s/n): ").strip().lower()
            id_artista = None
            if opcion == 's':
                id_artista = int(input("ID del artista: "))

            cursor = self.conexion.cursor()
            # Aca llamamos al SP de consulta, si id_artista queda en None el SP devuelve todos
            cursor.execute(
                "EXEC Procesos.sp_ConsultarArtistas @idArtista=?",
                id_artista
            )
            # Traemos todos los registros que devolvio el SP de una vez
            rows = cursor.fetchall()

            if not rows:
                print("No se encontraron artistas.")
                return

            # Lo que hicimos aca fue imprimir los resultados en forma de tabla con columnas alineadas
            encabezado = f"\n{'ID':<6}{'Nombre':<26}{'Pais':<22}{'Descripcion':<26}{'Productora':<20}"
            print(encabezado)
            print("-" * len(encabezado))
            for row in rows:
                print(
                    f"{row[0]:<6}{row[1]:<26}{row[2]:<22}"
                    f"{row[3]:<26}{row[5]:<20}"
                )

        except Exception as e:
            print(f"Error al consultar artistas: {e}")

    # Este es el UPDATE, aca pedimos el ID del artista a modificar y los nuevos valores
    def actualizar_artista(self):
        try:
            print("\n--- ACTUALIZAR ARTISTA ---")
            # Primero pedimos el ID para saber cual artista vamos a modificar
            id_artista    = int(input("ID del artista a actualizar: "))
            nombre        = input("Nuevo nombre: ").strip()
            pais          = input("Nuevo pais de origen: ").strip()
            descripcion   = input("Nueva descripcion (Enter para omitir): ").strip() or None
            id_productora = int(input("Nuevo ID de productora: "))

            cursor = self.conexion.cursor()
            # Ac llamamos al SP de actualizacion pasandole el ID y todos los datos nuevos
            cursor.execute(
                "EXEC Procesos.sp_ActualizarArtista "
                "@idArtista=?, @nombreArtista=?, @paisOrigenArtista=?, "
                "@descripcionArtista=?, @Productora_idProductora=?",
                id_artista, nombre, pais, descripcion, id_productora
            )
            row = cursor.fetchone()
            if row:
                print(f"\n{row[0]}")
            # Guardamos los cambios para que queden en la base
            self.conexion.commit()

        except Exception as e:
            print(f"Error al actualizar artista: {e}")

    # Este es el DELETE, aca lo que hicimos fue pedir confirmacion antes de borrar para evitar errores
    def eliminar_artista(self):
        try:
            print("\n--- ELIMINAR ARTISTA ---")
            id_artista = int(input("ID del artista a eliminar: "))
            # Pedimos confirmacion, si no escribe s cancelamos la operacion
            confirmar  = input(f"Confirmar eliminacion del artista {id_artista}? (s/n): ").strip().lower()

            if confirmar != 's':
                print("Operacion cancelada.")
                return

            cursor = self.conexion.cursor()
            # El SP se encarga de validar si el artista tiene canciones o seguidores antes de borrarlo
            cursor.execute(
                "EXEC Procesos.sp_EliminarArtista @idArtista=?",
                id_artista
            )
            row = cursor.fetchone()
            if row:
                print(f"\n{row[0]}")
            self.conexion.commit()

        except Exception as e:
            print(f"Error al eliminar artista: {e}")

    # Este metodo es el menu, aca lo que hicimos fue usar un while True para que siga corriendo hasta que el usuario salga
    def ejecutar_menu(self):
        while True:
            # Mostramos las opciones del sistema
            print("\n\t** SISTEMA CRUD - SONORA INC | ARTISTAS **")
            print("\t1. Registrar artista")
            print("\t2. Consultar artistas")
            print("\t3. Actualizar artista")
            print("\t4. Eliminar artista")
            print("\t0. Salir")

            opcion = input("\n\tSeleccione una opcion: ").strip()

            # Aca evaluamos la opcion y llamamos al metodo que le corresponde
            if opcion == '1':
                self.insertar_artista()
            elif opcion == '2':
                self.consultar_artistas()
            elif opcion == '3':
                self.actualizar_artista()
            elif opcion == '4':
                self.eliminar_artista()
            elif opcion == '0':
                # Antes de salir cerramos la conexion con la base de datos
                self.conexion.close()
                break
            else:
                print("Opcion no valida. Intente de nuevo.")


# Aca lo que hicimos fue crear el objeto y llamar al menu para arrancar el programa
if __name__ == "__main__":
    gestor = GestorArtistas()
    gestor.ejecutar_menu()
