# ProyectoFinal-ProposUp-v1
## IFTS18 - Proyecto Final de Carrera
> *Realizado por: Maximiliano E. Marchetti*

## Pasos para componer la aplicación:
 1. Clonar el proyecto:
	```
	git clone https://github.com/marchettime/PracticaProfesionalIII.git
	```
 2. Ingresar al folder "PracticaProfesionalIII"
 3. Ingresar por comando: 
	```
	docker-compose up
	```
	*Si es la primera vez que se realiza la clonacion y acceso a este proyecto, ver apartado*
 4. Ingresar por Google Chrome al [Link de Aplicacion](http://localhost:5000).

## *Primera Vez: Creación de DB*
 1. Abrir pgAdmin ingresando con las credenciales admin@admin pass: admin
 2. Conectar el Servidor "db" al puerto 5432 (default)
 3. Abrir la base "proposup" con usuario y pass "proyecto"
 4. En el Schema public, correr el contenido del script: "Script proposupdb.sql" que se encuentra en la carpeta raiz del proyecto.

