import mysql.connector
#Importamos clic la cual es una herramienta que a nosotros nos va a servir para a nosotros nos va a servir para poder ejecutar comandos en la terminal, eso lo vamos a necesitar para poder crear nuestras tablas y tambien crear la relacion entre ellas, pero tambien a travez de un comando en lugar de notros tener que ingresar al gestor como mysql workbench y conectarnos todo esto lo vamos a poder hacer directamente desde nuestra aplicacion 
import click

#Current app mantine la aplicacion que estamos ejecutando, e importamos g la cual es una variable que se encuetra siempre en toda nuestra aplicacion y nosotros podemos ir asignandole diferentes variables, y de esta manera nosotros despues acceder a estas variables en otras partes de nuestra aplicacion, vamos a usarla para poder almacenar el usuario dentro de g
from flask import current_app, g

#with_appcontext nos va a servir cuando estemos ejecutando el script de base de datos ya que vamos a necesitar el contexto de configuracion de nuestra aplicacion, cuando ejecutamos los scripts con appcontext podemos acceder a las variables que se encuentran en la configuracion de nuestra aplicacion, por ejemplo el host de nuestra base de datos su usuario y contraseña
from flask.cli import with_appcontext

#Importamos un archivo llamado schema este contendra todos los scripts que vamos a necesitar para poder crear nuestra base de datos y seguido de ese archivo importamos instrucciones
from .schema import instrucciones 

#Definimos una funcion que nos permita definir la base de datos y tambien el cursor dentro de nuestra aplicacion 
def get_db():
    #Mediante un condicional preguntamos, si no se encuentra el atributo 'db' dentro de g, entonces se ejecuta la operacion
    if 'db' not in g:
        ##Si la condicion se cumple entonces vamos a crear una nueva propiedad dentro de g, la cual va a contener la conexion a nuestra base de datos
        g.db = mysql.connector.connect(
            #Ahora es donde empezamos a hacer uso de la variable importada de current app
            #Definimos el host
            #Mediante current app accedemos a una propiedad de la configuracion para eso debemos usar config con corchetes para acceder a la propiedad database host, y lo mismo con cada uno de los datos requeridos para la conexion a la base de datos
            host = current_app.config['DATABASE_HOST'],
            user = current_app.config['DATABASE_USER'],
            password = current_app.config['DATABASE_PASSWORD'],
            database = current_app.config['DATABASE']
        )

        #Luego de haber asignado la base de datos a la propiedad db, ahora a continuacion accederemos al cursor, ya que con este es que vamos a ejecutar las consultas de sql
        #Para esto definimos dentro de g la propiedad de c
        #Ademas como vamos a querer acceder a las propiedades de las datos de la base de datos como un diccionario entonces debemos indicarle que active el diccionario con dictionary = True, es decir que colocamos la propiedad nombrada con el valor de true para que convierta los datos obtenidos a un diccionario y no los traiga como un arreglo que es lo que hace por defecto el cursor
        g.c = g.db.cursor(dictionary=True)

    #Por ultimo salimos del if y retornamos g.db y g.c
    return g.db, g.c
    #Entonces de esta maner cuando nosotros llamemos a get_db podremos obtener la base de datos y tambien el cursor

#Ahora lo que haremos es definir una funcion que nos permita cerrar la conexion de la base de datos cada vez que realicemos una peticion, es decir que lo que hara es ver si tenemos la conexion a la base de datos y en caso e que sea asi la vamos a cerrar para no dejar la conexion abierta, ya que si cada vez que necesitemos llamos a la base de datos podria ser que olvidemos cerrar la conexion, por lo que nos desligamos de esto y le dejamos a flask ese trabajo de cerrar la conexion por nosotros, entonces asi cada vez que realicemos una peticion, al terminar la misma sea flask el que se encargue de cerrar la conexion
#Creamos la funcion de close y le pasamos un parametro e con el valor none por defecto
def close_db(e=None):
    #Ahora medainte g.pop le saccamos la propiedad de db a g y la reasignamos a db, entonces asi de esta manera podremos luego preguntar si db no se encuentra definido es decir si no es None, y si esto es verdadero es decir que no esta definido db, significa que nunca llamamos a la funcion get_db, por lo que no seria necesario cerrar la conexion, pero por el contrario si db se encuentra definido es decir que no es None, en ese caso vamos a poder cerrar la conexion de la base de datos
    db = g.pop('db', None)
    if db is not None:
        db.close()

#Ahora vamos a hacer un script para poder ejecutar un set de instrucciones que vamos a escribir en sql, este set de instrucciones nos va a permitr crear las tablas que almacenaran los datos de la aplicacion y esto lo haremos desde la linea de comandos. Para esto crearemos la funcion init_db_command

#Definimos la funcion init_db
def init_db():
    #Aca vamos a importar o traer la base de datos usando la funcion get_db definida arriba
    #Como podemos ver aca abajo en una sola linea importamos la base de datos y el cursor 
    db,c = get_db()
    #Las instrucciones que vamos a importar dentro de el archivo de schema se van a encontrar todas escritas dentro de una lista por lo que debemos preocuparnos primero de escribir las instrucciones en el orden que queremos que se ejecuten y segundo definirlas todas dentro de una lista, haciendo que cada uno de estos strings va a ser una linea, esto es debido a que la libreria que estamos usando de mysql connector para poder conectarnos a mysql solamente nos permite ejecutar una instruccion a la vez y no podemos pasarle un script completo para que cree todas las tablas. Pero esto anterior lo solucionamos de manera sencilla simplemente iterando todas las instrucciones con un for y dentro de este medainte el cursor c ejecutamos cada una de las instrucciones dentro de instrucciones
    for i in instrucciones:
        c.execute(i)
    #Luego de esto hacemos commit de las instrucciones ejecutadas para que se realicen los cambios
    db.commit()

#Debemos decorar la funcion siguiente, ya que si solo la dejamos simplemente definida no la podremos ejecutar desde nuestra terminal, para esto la decoramos con click.command y entre parentesis le indicamos el nombre que queremos que tenga, este nombre nos va a servir cuando queramos llamarlo en la terminal es decir si le colocamos init-db, desde la terminal tendre que escribir flask init-db y esto lo que hara es ejecutar esta funcion que acabamos de definir. Otra cosa importante es que para que nuestro script se ejecute con exito, tenemos que indicar que utilice el contexto de la aplicacion para que el pueda acceder a las variables de configuracion que tenemos como DATABASE_HOST, DATABASE_USER, ETC, para esto usamos el decorador de with_appcontext y con esto ya podremos acceder a las variables
@click.command('init-db')
@with_appcontext
def init_db_command():
    #Aca dentro lo que haremos es llamar a una funcion llamada init_db, la cual se va a encargar de ejecutar toda la logica para poder correr los scripts que definamos, ahora es donde haremos uso de la libreria de click que importamos arriba, con esta mediante el comando echo imprimimos en la consola un mensaje, para asi indicarnos que el script ha terminado de correr con exito
    init_db()
    click.echo("Base de datos inicializada")



#Ahora le indicaremos a flask que tiene que cerrar la conexio al terminar una peticion, y para esto tendremos que configurar la aplicacion, para esto crearemos una funcion donde le pasamos como argumento app el que creamos en el archivo de __init__.py, y ahi vamos a agregar la funcion que tiene que ejecutar cuando este terminando de realizar la peticion a la base de datos
def init_app(app):
    #Le decimos a app que ejecute la funcion que lepasamos por parametro la cual es la de close para que cierre la conexion 
    app.teardown_appcontext(close_db)
    #De esta manera cada vez que realicemos una peticion  a nuestro servidor de flask que estamos construyendo, cuando termine de ejecutar la peticion es decir una vez que nos devolvio el resultado de la misma, lo que hara es llamar a la funcion llamada close_db y se va a cerrar la conexion a la base de datos segun la logica programada en la funcion 
#Despues en el archivo __init__.py configuramos todo esto
    #Suscribimos el comando de la linea de comando con todas las variables de entorno ya agregadas con la funcion init_db_command para eso usamos app, cli y con add comand le pasamos el comando mediante la funcion init_db_command
    app.cli.add_command(init_db_command)