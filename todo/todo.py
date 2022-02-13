from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

# Seguido de las importaciones de flash importamos las excepciones del modulo de werkzeug, y de este importamos la funcion de abort, esto es para que si algun usuario quiera realizar la actualizacion de algun todo que no le pertenezca en ese caso le mandaremos el mesaje de abort, y tambien incluiremos algun codigo de http para indicar que no tiene permiso o autorizacion para realizar la peticion
from werkzeug.exceptions import abort

# Seguido importamos auth desde todo, y de esta importaremos una funcion que nos va a permitir proteger todos nuestros endpoints de manera de que si el usuario es que quiere ingresar a el endpoint que estamos definiendo el usuario va a tener que haber iniciado sesion necesariamente ya que si no lo ha hecho lo que haremos sera redireccionarlo, a esta funcion la vamos a llamar login_required
from todo.auth import login_required

# Desde la base de datos importamos get_db
from todo.db import get_db

# Creamos nuestro blueprint que llamaremos 'todo' y lo vamos a registrar con el nombre de __name__
bp = Blueprint('todo', __name__)

# Ahora vamos a definir la funcion de index


@bp.route('/')
# Luego de esto llamamos a la funcion que creamos en auth.py llamada login_required para proteger a la funcion de index ya que esta es la que va a listar todos nuestros todos. SEguido definimos la funcion index
@login_required
def index():
    # Ahora dentro de esta funcion lo que tenemos que hacer es ir a buscar a la base de datos y buscaremos por el id del usuario todos los todos que el mismo haya creado, para esto primero llamamos a cb y c que es la base de datos y el cursor
    db, c = get_db()
    # A continuacion le indicamos la consulta sql que vamos a ejecutar, pero debemos tener en cuenta para la misma que no queremos traer todos los todos solamente, lo que quiero traerme es el todo y algunas cosas del usuario por lo que en la consulta debemos indicarle cuales son las columnas que quiero traerme, pero para esto lo que haremos es una consulta mezclada entre la tabla de usuario con la tabla de todo, para esto debemos indicar cuales campos de la tabla de todos nos vamosa  traer y a su vez le tenemos que indicar que campos de la tabla de usuario nos vamos a traer, y eso lo vamos a hacer primero asignandole un alias a nuestras tablas, por ejemplo t para la tabla de todo y u para la tabla de usuario, o sea que la consulta dice selecciona el id del todo la descripcion del todo el nombre del usuario, si fue completado ese todo y la fecha de creacion del mismo desde donde la tabla de todo se intersecta con la de usuario y el campo created_by es igual al campo id de la tabla de usuario ademas que ordene los datos por fecha con el campo created_by y lo haga en orden descendente
    #Mediante la clausula WHERE donde le decimos que t.created_by tiene que ser igual al usuario que haya en la variable global user con el parametro id, esto quiere decir que tiene que ser el id del usuario actual para que traiga los todos de ese usuario y no los de otro usuario de esta manera mis todo por ejemplo no van a poder ser accedidos por otro ni van a poder ser modificados ni borrados ni leidos pro otra persona
    c.execute(
        'SELECT t.id, t.description, u.username, t.completed, t.created_at' 
        ' FROM todo t JOIN user u ON t.created_by = u.id' 
        ' WHERE t.created_by = %s' 
        ' ORDER BY created_at desc',(g.user['id'],)
    )
    # Seguidamente le decimos mediante el cursor y la funcion fetchall que nos traiga todo loq ue encuentre y lo asigne a la variable de todo
    todos = c.fetchall()
    # Seguidamente retornamos mediante un reder template una plantilla que se encuentra dentro de la carpeta de todo y esta plantilla se llamara index.html y lo que haremos ademas es pasarle a esta los todos a esta plantilla y dentro de esta plantilla nos encargaremos de mostrar el listado de todos que el usuario haya creado hasta ahora
    return render_template('todo/index.html', todos=todos)

# Creamos la ruta para create


@bp.route('/create', methods=['GET', 'POST'])
# Le decimos que el usuario debe haber iniciado sesion para poder crear medainte le siguiente decorador que es la funcion que creamos login_required
@login_required
# indicamos el nombre de la funcion
def create():
    #Primero vemos si en el request estamos usando el metodo de post mediante un condicional if
    if request.method == 'POST':
        #En caso de que el condicional se cumpla sacamos la descripcion desde el formulario con el metodo form de request
        description = request.form['description']
        #Creamos un mensaje de error y lo igualamos a none para iniciarlo
        error = None

        if not description:
            #Ahora preguntamos si existe una descripcion y si no existe entonces indicamos un error que diga la descripcion es requerida
            error = 'La descripcion es requerida'
        if error is not None:
            #si nuestro mensaje de error no es None entonces quiere decir que tenemos un error y mandamos el mensaje flash entonces con el error anterior declarado
            flash(error)
        else:
            #En el caso contrario si error sigue siendo None eso significa que no hay error por lo que procedemos con la creacion del todo
            #Primero sacamos la base de datos y el cursor usando la funcion de get_db
            db, c = get_db()
            #Ejecutamos la consulta para insertar los datos que nos interesan, a la misma le decirmos que insertaremos la descricion, si esta o no completado y por quien fue creado
            #Para separar los query en dos lineas simplemente presionamos enter volvemos a abrir comillas y dejamos un espacio al comienzo para separar los dos estring con los query nada mas
            #Los valores de %s se los asignamos mediante una tupla al final, primero le pasamos la variable description, luego le decimos en completado False para decir que no esta completado, y tercero le pasamos el valor de id de la variable user almacenada en g global
            c.execute(
                'INSERT INTO todo (description, completed, created_by)'
                ' values (%s, %s, %s)',
                (description, False, g.user['id'])
            )

            #Seguidamente realizamos un commit de los cambios realizados
            db.commit()
            #Finalmente retornamos al usuario a la ruta donde listamos los tudos es decir a index
            return redirect(url_for('todo.index'))

    #Renderizamos la plantilla
    return render_template('todo/create.html')

#Definimos la funcion de get_todo que encuentra el todo en la base de datos para traernoslo 
def get_todo(id):
    #Primero sacamos la base de datos y el cursor
    db, c = get_db()
    #Seguido ejecutamos la consulta para traer el todo de la base de datos
    c.execute(
        'SELECT t.id, t.description, t.completed, t.created_by, t.created_at, u.username' 
        ' FROM todo t JOIN user u ON t.created_by = u.id WHERE t.id = %s', 
        (id,)
    )

    #Llamamos a fetchone para obtener el registro encontrado 
    todo = c.fetchone()

    #Preguntamos si todo es none entonces aca usamo la funcion de abort
    if todo is None:
        #le indicamos medaitne la funcion de abort el numero del error primero y segundo el mensaje que tendra el cual mediante formateo de string le pasamos el texto y entre medio le colocamos el codigo 0 para indicar que vamos a colocar el primer valor que tenga format en ese lugar que es el id
        abort(404, 'El todo de id {0} no existe'.format(id))
    return todo
    #Por ultimo retornamos neustro todo

# Creamos la ruta de updete para actualizar un registro con su respectiva funcion
#Para esta en la ruta debemos realizar algo en particular y es indicarle el todo que queremos actualizar, para esto usaremos <tipodedato:dato>
@bp.route('/<int:id>/update', methods=['GET', 'POST'])
# Le decimos que el usuario debe haber iniciado sesion para poder crear medainte le siguiente decorador que es la funcion que creamos login_required
@login_required
# indicamos el nombre de la funcion y le pasamos el id del registro a actualizar como parametro de la funcino 
def update(id):
    #Primero que nada obtenemos el todo de la base de datos, pero como la logica para obtenerlo es larga entonces lo que hacemos es pasarsela a una funcion que vamos a llamar get_todo la caul recibe como parametro el id del todo a encontrar
    todo = get_todo(id)
    print(todo)
    #Luego de obtener el todo preguntamos si el metodo que estamos utilizando es el de POST, los metodos siempre debemos colocarlos en mayusculas para no tener problemas de comparacion y que salten errores al realizar las consultas
    if request.method == 'POST':
        #si es asi entonces obtenemos la descripcion desde request form es decir desde el input del formulario con el nombre de description
        description = request.form['description']
        print(description) 
        #Ahora la sigueinte parte sera diferente a las demas obtenciones del formulario, ya que por lo general llamabamos al objeto de request despues llamabamos a form y luego con el corchete sacabamos los valores que nos interesaban, pero en este caso para los campos de tipo checkbox no vamosa poder usar esa forma ya que no nos va a devolver nada usaremos la sigueinte 
        #Mediante un operador ternario le diremos que asigne true a completed en caso de que mediante request.form.get y dentro de get le pasamos le decimos que nos obtenga el valor del checkbox con el nombre de completed (esta manera es solo para los checkbox) si esto es on en caso contrario entonces le asignara un False a la variable
        completed = True if request.form.get('completed') == 'on' else False
        print(completed)
        #Seguido creamos la variable de error que la iniciamos en None
        error = None

        #Ahora a continuacion realizamos las validaciones
        #preguntamos primero si description se encuentra vacio si es asi mandamos el primer error
        if not description:
            error = 'La descripcion es requerida'
        #A continaucion preguntamos sin error no es none es decir si tenemos algun error entonces mandamos o mostramos ese error mediante la funcion de flash
        if error is not None:
            flash(error)
        #por ultimo si error es none quiere decir que no hay ningun error entonces alli procedemos a actualizar el todo
        else:
            #Traemos la bae de datos y el cursor
            db, c = get_db()
            #Y ahora ejecutamos la consulta, la cual dice que actualice del todo la descripcion y si esta completado siempre y cuando el id sea el que nosotros le pasemos es decir el que venga del parametro id de la funcion
            #Le agregamos a la clusula where el t.created_by tiene que ser igual al usuario que haya en la variable global user con el parametro id, esto quiere decir que tiene que ser el id del usuario actual para que traiga los todos de ese usuario y no los de otro usuario de esta manera mis todo por ejemplo no van a poder ser accedidos por otro ni van a poder ser modificados ni borrados ni leidos pro otra persona
            c.execute(
                'UPDATE todo SET description = %s, completed = %s'
                ' WHERE id = %s AND created_by = %s',
                (description, completed, id, g.user['id'])
            )
            #Seguido hacemos commit de la query de arriba para que se registren los cambios en la base de datos
            db.commit()
            print(db)
            #Por ultimos retornamos un redirect a todo.index
            return redirect(url_for('todo.index'))

    #Renderizamos la plantilla de update y le pasamos como parametro el todo a actualizar
    return render_template('todo/update.html', todo=todo)

#Creamos la funcion de borrar o delete en la cual le colcoamos solo el metodo post ya que los demas no nos interesan en este caso para eliminar un registro
@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
#definimos la funcion y le pasamos el id del usuario a eliminar como parametro
def delete(id):
    #Lo primero que hacemos es trae la base de datos y el curso
    db, c = get_db()
    #Le agregamos ademas del id a la clusula where el t.created_by tiene que ser igual al usuario que haya en la variable global user con el parametro id, esto quiere decir que tiene que ser el id del usuario actual para que traiga los todos de ese usuario y no los de otro usuario de esta manera mis todo por ejemplo no van a poder ser accedidos por otro ni van a poder ser modificados ni borrados ni leidos pro otra persona
    c.execute(
        'DELETE FROM todo WHERE id = %s AND created_by = %s',(id, g.user['id'])
    )
    db.commit()
    #Luego de haber hecho commit de la instruccion e eliminar o sea de haber eliminado el todo retornamos una redireccion a index.html para ver nuevamente los todo disponibles
    return redirect(url_for('todo.index'))
