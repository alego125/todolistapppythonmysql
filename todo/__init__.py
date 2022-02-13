# Lo primero que haremos es importar el modulo de os, el cual nos permite a ciertas funciones del sistema operatico,nosotros la vamos a usar para acceder a las variables de entorno
import os
from flask import Flask

# Cuando trabajamos de la forma que trabajamos aqui que es en la de modulizar es decir de separar todo en diferentes modulos, tenemos que usar una funcion que se va a llamar create_app, esta es una funcion que nos va a servir para por ejemplo hacer testing o crear varais instancias de nuestra aplciacion, en este ejercicio vamos a crear solo una pero es importante que cuando nostros estemos creando en flask una app tenemos que usar esta funcion de create_app


def create_app():
    # Detntro de esta funcion creamos la variable de app mediante la funcion de Flask, usando el cosntructor de flask
    # Todas las aplicaciones que creamos en flask son una instancia de la clase Flask, y esta mantendra un estado interno con diferentes configuraciones de entorno y tambien con variables de usario y direntes cosas que podremos hacer con nuestra aplicacion, por este motivo es muy importante el objeto de app en este caso
    app = Flask(__name__)
    # Ahora usaremos las variables de entorno para poder configurar nuestra aplicacion, lo primero llamamos a app.config y dentro de config llamamos al metodo from_mapping, este nos permitira definir variables de configuracion que despues podremos usar en nuestra aplicacion
    app.config.from_mapping(
        # La primer variable de configuracion es SECRET_KEY, esta es una llave la cual se va a usar para poder definir las sesiones en nuestra aplicacion, una sesion es cuando nostros generamos una llave que le vamos a mandar al cliente en este caso al usario que esta navegando en nuestra aplicacion para que podamos usarla como referencia con datos que se encuentran guardados en el servidor, el nombre tecnoco de esto es una cookie, es decir que le vamos a enviar una cookie al usario que tendra una llave o identificador unico y con ese identificador unico cuanod el usuario lo envie, podremos saber que tipo de datos se encuentran asociados al usario, por ejemplo el inicio de sesion, cuando un usuario inicia sesion vamos a necesitar estas sesiones para saber quien esta navegando en nuestra aplicacion. Flask usa el string que le pasamos en la siguiente linea para poder asi crear las sesiones, por ahora le mandamos uno sensillo como mikey por ejempl, pero cuando nosotros queramos pasar a produccion nuestra aplicacion, entonces en este caso lo que tendremos que hacer es cambiar esto por algun string mas complejo para que un hacker no logre identificar como estamos generando nuestras sesiones
        SECRET_KEY="mikey",
        # Seguido lo que hacemos es pasar el host de la base de datos a la cual nos queremos conectar, y estos valores los vamos a sacar de variables de entorno para esto usaremos a os, luego a environ que es el objeto que contiene a todas las variables de entorno y luego llamamos al metodo de get y dentro de este llamamos a FLASK_DATABASE_HOST, esto lo vamos a usar un par de veces por que nostros necesitamos el host, el usario la contraseña y la base de datos a la cual nos vamos a conectar, por lo cual usamos lo mismo para cada variable a recuperar
        DATABASE_HOST=os.environ.get('FLASK_DATABASE_HOST'),
        DATABASE_PASSWORD=os.environ.get('FLASK_DATABASE_PASSWORD'),
        DATABASE_USER=os.environ.get('FLASK_DATABASE_USER'),
        DATABASE=os.environ.get('FLASK_DATABASE')
        # Con esto ya tenemos la configuracion guardada dentro de app, todo esto creado arriba lo vamos a usar cuando tengamos que definir los accesos a nuestra aplicacion
    )

    # Llamamos a nuestro archivo de base de datos que acabamos de crear, para esto importamos todo desde el punto donde estamos es decir desde la carpeta que estamos mediante . el punto de el archivo db,
    from . import db
    # Ahora ejecutamos el init_app y le pasamos la app esta que hemos creado como parametro a la funcion
    db.init_app(app)
    # Entonces lo que aca estamos haciendo es llamar a la funcion init app de el archivo db.py en donde se usa la funcion teardown_appcontext la cual se encarga de ejecutar la funcion que le pasamos por parametro cuando estemos terminando la ejecucion de algun metodo que hayamos llamado o de algun endpoint que hayamos creado. En resumen, llamamos anuestro servidor se ejecuta el end point devolvemos los daots al usuario y finalmente se ejecuta la funcion de close db para segurarnos que cerramos la conexion a la base de datos

    # Importamos todo lo de auth desde el punto donde nos encontramos
    from . import auth
    # Importamos a todo.py
    from . import todo

    # Ahora suscribimos el bluprint a nuestra aplicacion
    # Mediante app con el metodo register y dentro de este el de blueprint le decimos que queremos registrar auth, pero el blueprint que creamos dentro de este que le dimos el nombre de bp
    app.register_blueprint(auth.bp)

    # Registramos el blueprint de todo, con esto sabemos que nuestra app va a funcionar cuando nosotros comencemos a agregar nuestros endpoints, si no registramos estos blueprint en este archivo entonces no funcionaran nuestras rutas creadas medainte blueprint cuando llamemos al archivo init desde neustro servidor
    app.register_blueprint(todo.bp)

    # Ahora lo que haremos es crear una ruta de prueba

    @app.route('/hola')
    def hola():
        return "Chanchito Feliz"

    # Por ultimo en la funcion de create app debemos retornar nuestra aplicacion
    return app
