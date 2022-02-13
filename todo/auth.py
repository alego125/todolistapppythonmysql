# Los modulos en Flask se dividen como un blueprint, y este es una agrupacion de modulos que hacen semtido, o sea nosotros quevamos a tener un modulo de autenticacion o blueprint de autenticacion, lo que tiene mas sentido es que este tenga el inicio de sesion tambien el registro la autenticacion y funciones tipo firewall, el firewall no nos va a dejar pasar a ejecutar siertas funciones siempre y cuando el usario no tenga los permisos o ni siquiera haya iniciado sesion.
# En este archivo primero importamos functools, el cual es un set de funciones que podemos usar cuando estamos construyendo aplicaciones (son mas que nada funciones)
import functools

# Desde flask importamos blueprint que luegos podremos configurar (la gracia de los blueprint es que son configurables),
# flsh es una funcion que nos va a permitir enviar mensajes de manera generica a nuestras plantillas, por lo que si llegasemos a tener un error como puede ser el de usuario incorrecto cuando estamos iniciando sesion, en lugar de retornar los datos y tratar de interceptarlos dentro de nuestras plantillas, lo que hacemos es sensillamente es que mandamos un mensaje de flash y este sera interceptado por nuestro sistema de plantillas que vamos a construir y muestra inmediatamente ese mensaje
# g, es una variable que nos deja disponibles otras distintas variables que podemos usar como puede ser en este caso la base de datos
# render_template pora renderizar plantillas
# request, para recibir datos desde un formulario
# url_for para crear urls
# session, con esta podremos mantener una referencia del usuario que se encuentra en el contexto actual interactuando con nuestra aplicacion de flsk
# redirect para que podamos hacer uso de la funcion para redireccionar a otras paginas al realizar ciertas acciones como iniciar sesion o registrarse
from flask import (
    Blueprint, flash, g, render_template, request, url_for, session, redirect
)

# de la ibreria de werzeug y de esta el modulo de security, importamos check_password_hash (verifica si la contraseña ingresada es igual a otra) y generate_password_hash (encripta la contraseña que estoy enviando)
from werkzeug.security import check_password_hash, generate_password_hash

# Importamos la funcion de get_db que creamos dentro de db.py y con esta poder interactuar con la base de datos
from todo.db import get_db


# Luego de importar lo necesario creamos nuestro primer blueprint, el cual recibe el nombre de 'auth', el nombre que tendra sera segun el nombre del archivo __name__, que en este caso se va a llamar auth, y seguidamente debemos indicarle el url_prefix que lo que hara este ultimo es que a todas las url que se encuentran abajo, donde creamos una direccion de inicio de sesion y de registro, les va a colocar la url que le vamos a indicar aca, es decir que les va a concatenar ese string, en este caso le colocamos /auth esto hara que la ruta por ejemplo localhost:5000/auth/registro que es la procima funcion que vamos a colocar, es decir que lo que le pasemas aca sera un intermediario en la url entre la raiz y la funciones proximas que existan
bp = Blueprint('auth', __name__, url_prefix='/auth')
# Antes de continuar se debe inscribir dentro de la aplicacion este blueprint para esto hay que irse a __init__ y lo suscribimos justo debajo de donde habiamos suscripto nuestra base de datos con db.init_db(app)

# Para empezar a agregar rutas dentro de nuestro blueprint es muy similar a cuando lo hacemos en una aplicacion, que lo que haciamos era llamar a @app.route('/ruta', methods=['GET','POST]), llamabamos a route dentro de app y le definiamos la ruta, luego le indicamos cuales son los metodos que queremos manejar por ejemplo ['GET','POST'] y luego de esto se define la funcion con el nombre de la ruta y dentro de esta se realiza toda la logica, la unica diferencia que tendremos con los bluprints es que en lugar de llamar a app al comienzo del decorador llamamos a blueprint en nuestro caso bp que es el que creamos mas arriba


@bp.route('/register', methods=['GET', 'POST'])
def register():
    # Lo primero que haremos es validar dentro del request que nosotros estamos validando a nuestro servidor si el metodo que estamos enviando es de tipo POST
    if request.method == 'POST':
        # En caso de que lo sea sacaremos entonces la variable de username de nuestro formulario que en este caso le daremos el nombre de username y tambien sacaremos una contraseña con el nombre de password
        username = request.form['username']
        password = request.form['password']
        # Una vez que tenemos el usuario y la contraseña ahora podemos ir a la base de datos a preguntar si es que existe un usuario que tenga el username pasado
        # Para hacer todo esto sacamos nuevamente la base de datos y el cursor de la misma desde la funcion de db que importamos mas arriba desde el archivo db.py
        db, c = get_db()
        # lo primero qu eharemos sera crear una varible de error que no tendra nada dentro o sea no tendra ningun valor, y denpendiendo de por ejemplo si el usuario no envia un username o un password vamos a reemplazar el None de la variable error y vamos a devolver un mensaje flsh al usuario
        error = None
        # Ejecutamos la consulta a la basde de datos mediante el curso
        # le decimos que seleccione el id del usuario donde el nombre de usuario coincida con el que le pasamos desde el formulario, y seleccionamos el id ya que ahora solo nos interesa si el usuario existe es decir que si no existe no va a tener id ya que este es un campo obligatorio es decir que tiene que estar en todos los registros
        # Ejecutamos la consulta de select y le pasamos el valor de ususario para que filtre
        c.execute(
            'SELECT id FROM user WHERE username = %s', (username,)
        )
        # Validamos los mensajes de error si es que no tenemos username ni password
        if not username:
            # En este caso le pasamos como mensaje de erro el texto de que es requerido el username
            error = 'Username es requerido'
        # Lo mismo hacemos en caso de que no tengamos un password
        if not password:
            error = 'Password es requerido'
        # Una vez que tenemos validados estos dos casos y enviados los mensajes flash en caso de error entonces buscamos mediate fetchone al usuario y en caso de que este no sea none o sea que exista efectivamente le mandamos otro mensaje diciendo que el usuario tal se encuentra registrado en la base de datos
        elif c.fetchone() is not None:
            # Le pasamos mediante un format el username dentro del string, es decir que el username se colocara dentro del string donde se coloquen las llaves {}
            error = 'Usuario {} se encuentra registrado'.format(username)
        # Ahora validamos que el error sea None o sea si no tenemos ningun error, ya que si el usuario se encuentra registrado no vamos a querer registrar el usuario si no que vmaos a querer directamente saltar al mensaje de flash

        if error is None:
            # Aca dentro colocamos la logica para registrar el usuario
            # Ejecutamos el query mediante excecute y seguido le pasamos los values username y la contraseña pero aca no queremos pasar la contraseña en texto plano es decir sin encriptar, ya que si nos llegan a robar la base de datos queremos que ese hacker vea solamente hashes y no pueda ver la contraseña real en texto plano, para esto llamamos despues de username la funcion generate_password_hash y le pasamos nuestro password para que lo encripte
            c.execute(
                'INSERT INTO user (username, password) values (%s, %s)', (
                    username, generate_password_hash(password))
            )
            print(generate_password_hash(password))
            # Luego de todo esto hacemos un commit de la base de datos para que se inserte con exito nuestra peticion de insercion de usuario en este caso
            db.commit()
            # Seguidamente retornamos un redirect donde vmaos a enviar al usuario a auth.login la plantilla de la pagina de inicio de sesion
            return redirect(url_for('auth.login'))
        # Ahora ya fuera del if de la logica de registro de usuario mandamos el mensaje flash de error al cliente mediante la funcion flash
        flash(error)
    # Por ultimo retornamos el render_template de register.html, este render se va a devolver en caso de que el usuario no este realizando una peticion POST si no que este realizando una peticion de GET
    return render_template('auth/register.html')
# A continuacion de la funcion de registro definimos la funcion de inicio de sesion la cual llamamos login pero antes de la funcion indicamos la ruto mediate bp.route la cual es login y los metodos que va a manejar son los de GET y POST


@bp.route('/login', methods=['GET', 'POST'])
def login():
    # Primero validamos que l estemos enviando a nuestra aplicacion de flash un metodo de POST
    if request.method == 'POST':
        # Si es que nos estan enviando el metodo de POST es por que el usaurio esta intentando iniciar sesion  por lo cual entramos al if y sacamos del formulario el username y el password
        username = request.form['username']
        password = request.form['password']
        # Seguido sacamos nuestra base de datos y el cursor
        db, c = get_db()
        # Nuevamente colocamos una variable de error con un none
        error = None
        # LA logica en este caso sera similar a la de registro pero en este caso en lugar de crear el usuari lo buscaremos y lo devolveremos en caso de que lo encuentre
        # Lo primero que haremos es buscar un usuario que tenga este username y luego verificar si la contraseña que se encuentra registrada es la misma constraseña que el usuario esta enviando el usuario al intentar iniciar sesion, para buscarlo ejecutamos por media del cursor el siguiente query
        # Al valor de username se lo indicamos mediante username, y una coma al final por que las tuplas por mas que sea un solo elemento para que las lea tiene que tener al final una coma
        c.execute(
            'SELECT * FROM user WHERE username = %s', (username,)
        )
        # Seguidamente sacamos el usuario de la base de datos y lo guardamos en una variable usando fetchone
        user = c.fetchone()

        # Una vez sacado el usuario ahora validamos que el usuario exista, ya que si no existe entonces dedbemos mandar mensaje de error indicando usuario contraseña o usuario invalido
        # Nosotros le decimos el siguiente mensaje en vez de el usuario tanto es icorrecto para que asi de esta manera el hacker no pueda sacar el nombre de usuario a la fuerza, por que lo que podria hacer es empezar a realizar consultas al formulario de login y si nosotros le indicamos el valor de usuario incorrecto el hacker inmediatamente por descarte sabra que el usuario ya no existe, entonces no debemos darle alhacker ningun indicio que un usuario exioste o no existe por eso le mandamos usuario y/o contraseña invalida
        if user is None:
            error = 'Usuario y/o Contraseña invalida'
        # Ahora mediante check_password_hash chequeamos que la contraseña que le estamos pasando sean iguales si no son iguales entonces entra al if y coloca el mensaje de error en la variable error
        elif not check_password_hash(user['password'], str(password)):
            # Aca usamos la misma logica que para el error del usuario incorrecto, no debemos dar indicio de contraseña o usuario incorrecto si no que le ponemos un mensaje general como en usuario
            error = 'Usuario y/o Contraseña invalida'

        # Ahora si no tenemos ningun erro y todo es valido, entonces lo que haremos es limpiar la sesion, asignaremos dentro de la sesion el id del usuario para que podamos ir a buscarlo y ademas de eso vamos a redirigir al usuario a la pagina de inicio, la cual le diremos index
        if error is None:
            # Limpiamos la session medainte le metodo clear de al sesion
            session.clear()
            # Creamos una variable dentro de la sesion llamada user_id y le asignamos el id del usuario que buscamos en nuestra base de datos, es decir que el id traido de la base de dtos se lo pasamos a la sesion y luego mas adelante esta sesion la podemos referenciar
            session['user_id'] = user['id']
            # Luego de esto ya podemos redirigir a neustro usuario a nuestra pagina de incio que en este caso es la pagina de index
            return redirect(url_for('todo.index'))
        # Para el caso de que el usuario si haya tenido errores entonces le enviamos el mesaje de error mediante le metodo flash
        flash(error)
    # En el caso de que el usuario no este realizando una peticion de POST si no que este realizando una peticion GET entonces lo que haremos sera retornar un render_template de la plantilla de login.html para mostrarla al usuario
    return render_template('auth/login.html')

# La siguiente funcion esta definida antes de la peticion por lo que primero se va a ejecutar primero esta funcion y luego la que estamos definiendo en nuestra vista, por ejemplo cuando vallamos a buscar nuestros todos, primero se va a ejecutar la funcion siguiente y despues se va a ejecutar la funcion index para poder traernos nuestros todos
# Ahora vamos a crear una funcion que se encargue de colocar el usuario dentro de de la variable global g, para esto lo que vamos a hacer es volver a crear una funcion decoradora que lo que se va a encargar es de verificar antes de cada peticion que estemos realizando a nuestro servidor si es que el usuario se encuentra si no se encuentra y es que el usuario ha iniciado sesion entonces en este caso tomaremos la sesion del usuario (ya que en ese momento solamente estamos guardando el id del usuario) buscaremos el id del usuario y se lo vamos a asignar a la variable global g
# creamos el decorador llamando a blueprint y a before_app_request


@bp.before_app_request
# Y ahora definimos la funcion que se encargara de asignar al usuario
def load_logged_in_user():
    # Sacamos primero el user id de nuestro objeto de session que ya previamente se habia pasado este a la session, especificamente mas arriba en la funcion de inicio de sesion
    user_id = session.get('user_id')

    # Ahora preguntaremos si nuestro user_id es none si esto es verdad entonces significa que tenemos que asignar none al mismo usuario es decir al user de la variable global g ya que no tenemos un usuario que haya iniciado sesion
    if user_id is None:
        g.user = None
    # Por otro lado en caso de que si haya iniciado sesion un usuario lo que tendremos que hacer es ir a buscar este usuario por su id a la base de datos y luego de esto asignarlo a g.user
    else:
        # Traemos mediante la funcion get_db al cursor y la base de datos
        db, c = get_db()
        # Luego llamamos con el cursor a execute y aqui dentro de execute ejecutamos el query de select para traer el id del usuario, en la clausa en el where el id tiene qu eser el id que nosotros estamos sacando es decir el user_id
        c.execute(
            'SELECT * FROM user WHERE id = %s', (user_id,)
        )
        # Luego de ejecutar el query mediante el cursor, esta nos retorna una lista de diccionario por lo que llamamos a fetchone es para que de esta lista de diccionarios solo nos devuelva el primer elemento que se encuentre y lo asignamos a la user de la variable global g
        g.user = c.fetchone()

# Ahroa a continuacion crearemos la funcion que va a proteger nuestras rutas y a esta le vamos a pasar el argumento de view
# La funcion esta que estamos definiendo es una funcion decoradora, y una funcion decoradora lo que hace es que recibe como argumento la misma funcion que nosotros estamos decorando, por esto cuando estamos definiendo una funcion decoradora le tenemos que indicar que esta va a estar recibiendo una funcion en este caso de la vista o view, se le llama asi pero para nosotros es la funcion que define nuestros endpoints


def login_required(view):
    # Ahora llamaremos a functools y de esta la funcion wraps y con esta lo que haremos sera envolver usando esta funcion de wraps
    @functools.wraps(view)
    # Seguido a haber envuelto a view definimos la funcion
    def wrapped_view(**kwargs):
        # A continuacio preguntamos si g.user es none, ya que si es none significa que el usuario todavia no ha iniciado sesion por lo que lo vamos a redirigir a nuestra pagina de login
        if g.user is None:
            # Si el usuario se no encuentra definido dentro de la variable global g
            return redirect(url_for('auth.login'))

        # Y entonces en el caso de que el usuario si se encuentre definido vamos a retornar nuestra vista que vendria siendo la funcion que estamos envolviendo o la que estamos decorando y le vamosa  pasar todos los argumentos con **kwargs
        return view(**kwargs)

    # Por ultimo lo que debemos hacer es devolver la funcion que acabamos de crear llamada wrapped_view
    return wrapped_view

# Crearemos a continaucion una nueva vista que es la vista de logout


@bp.route('/logout')
def logout():
    # Para esta funcion de cierre de sesion lo que haremos es limpiar la sesion del usuario con la funcion clear de session y seguido a eso lo vamos a redirigir al login
    session.clear()
    return redirect(url_for('auth.login'))
