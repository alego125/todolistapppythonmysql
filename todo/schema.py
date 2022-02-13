#En este archivo crearemos todas las instrucciones sql necesarias para hacer las consultas a la base de datos
#Primero creamos la variable de instrucciones y le asignamos en forma de lista le escribirmos el script. 
#Debemos aclarar algo importante sobre esto, si por alguna razon tenemos que eliminar las tablas y lo queremos hacer dentro de este mismo script,por que por ejemplo queremos cambiar algo para volver a crearlas, no nos va adejar si es que estas tienen referencias de llaves foraneas es decir si estan relacionadas entre si, entonces para poder eliminarlas de todos modos debemos desactivar esta validacion y luego volver a activarla una vez se haya eliminado la tabla
instrucciones = [
    #Cada instruccion que queremos que ejecute nuestro script tiene que cumplir con ser un elmento de esta lista, es decir que cada instruccion sql es un elemento diferente de la lista
    #Desactivamos la llave foranea para que se puedan eliminar las tablas
    'SET FOREIGN_KEY_CHECKS=0;',
    #Con las siguientes instrucciones lo que hacemos es que si la tabla llegase a existir la eliminaremos y despues la vamos a recrear
    'DROP TABLE IF EXISTS todo;',
    'DROP TABLE IF EXISTS user;',
    #Ahora volvemos a activar la valodacion de llaves foraneas pasandole el valor de 1
    'SET FOREIGN_KEY_CHECKS=1;',
    #Hasta ahora hemos creado string de una sola linea pero a continuacion crearemos string de multiples lineas, para esto usaremos las triples comillas dobles, de esta manera lo que se coloque entre medio de estas se considerara un string pero en este caso de multiples lineas y aqui es donde crearemos la tabla de usuarios
    #Creamos a continuacion la tabla de usuario
    #En este ejercicio encriptaremos las contraseñas por lo que tendran una longitud cercana a los 91 por lo que ponemos 100 pasword VARCHAR(100) para tener un margen por las dudas
    """
        CREATE TABLE user (
            id INT PRIMARY KEY AUTO_INCREMENT,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(100) NOT NULL         
        )
    """,
    #A continuacion creamos la tabla de todos
    #El created_by es una referencia o clave foranea para relacionarla con un usuario en concreto, por lo que si por ejemplo si el que lo creo fue el usuario 1 lo que tendra sera el calor de 1, luego created_at tendra la fecha de crecion del todo, dentro de esto le indicamos que el tipo de dato sera timestamp y como valor por default le colocamos current_timestamp, esto lo que hara es que sin necesidad de que le indiquemos la fecha manualmente simplemente mysql automaticamente le asignara un valor por defecto en este caso la fecha actual que tiene el servidor de mysql, otro atributo es completed el cual tendra dentro si el todo se encuentra completado o no para esto usaremos true o false, y por ultimo indicamos la llave foranea diciendo que sera el atributo created_by y hara referencia a la tabla de user al atributo id de la misma, esto es para enlazar cada registro con un usuario en especifico
    """
        CREATE TABLE todo(
            id INT PRIMARY KEY AUTO_INCREMENT,
            created_by INT NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            description TEXT NOT NULL,
            completed BOOLEAN NOT NULL,
            FOREIGN KEY (created_by) REFERENCES user (id)
        )
    """
]

#Si queremos probar las instrucciones de arriba debemos definir las variables de enorno desde nuestra cosola de comandos del so de la sigueinte manera cada linea va apor separado, siempre para ejecutar los comandos debemos estar ubicados en la carpeta principal del proyecto

# set FLASK_DATABASE_HOST=localhost
# set FLASK_DATABASE_PASSWORD= Si la base de datos no tiene password entonces este comando lo saltamos y no lo ponemos
# set FLASK_DATABASE_USER=root
# set FLASK_DATABASE=test

#Luego de esto nos vamos a el archivo db.py y suscribimos la funcion init_db_command a la aplicacion dentro de la funcion init_app
#Luego con el entorno virtual activado en la carpeta del proyecto y habiendo pasado el comando

#set FLASK_APP=carpetadelarchivoprincipal
#set FLASK_ENV=development

#Ejecutamos dentro de la carpeta del proyecto el comando 

#flask init-db

#Este comando ejecuta la funcion que inicializa la base de datos con la logica programada dentro del archivo db.py
#Debemos verificar que todo el query sql del archivo schema este correcto si no nos saltara un error al ejecutar el comando