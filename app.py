import json
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, session, request
from flask_bootstrap import Bootstrap
from flask_script import Manager
from flask_datepicker import datepicker
import psycopg2 
import os.path
import time
from classes import LineaTabla, Propuesta, EstadoScript, connectionString, PropRespuesta
from forms import LoginForm, RegistrarEmpresaForm, RegistrarPersonaForm, ElegirRolForm, BuscarForm,  AltaVentaForm, SaludarForm, CrearPropuestaForm, EntregarPropuesta
app = Flask(__name__)
manager = Manager(app)
Bootstrap(app)
app.config['SECRET_KEY'] = 'un string que funcione como llave'#String que funciona como llave
conStr = connectionString()

#usuario_hardcodeado_empresa = '5a7ec651-6eb9-474d-b95b-a859559780b4'
#usuario_hardcodeado_persona = 'fdd4feae-0910-4af9-b9f7-56f04aabab8e'


@app.route('/', methods=['GET'])
def index():
    if 'username' not in session:
        session['rolUsuario'] = None
        session['userId'] = None
        session.clear()
    return render_template('index.html', fecha_actual=datetime.utcnow())

@app.errorhandler(404)
def no_encontrado(e):
    return render_template('404.html', errores = ""), 404

@app.errorhandler(405)
def error_interno(e):
    mensajeerror = []
    mensajeerror.append(e.description)
    mensajeerror.append("La URL a la que queire acceder, NO está permitido")
    mensajeerror.append("Por Favor, vuelva al inicio y retome sus operaciones")
    return render_template('500.html', errores = mensajeerror), 405

@app.errorhandler(500)
def error_interno(e):
    return render_template('500.html', errores = ""), 500


@app.route('/MasInfo', methods=['GET'])
def MasInfo():
    return render_template('MasInfo.html')
#region definicion de funciones
def EjecutarScript(postgres_query, record_to_insert=None, retornaResultado=False, retornaTodo=False):
    salida = EstadoScript(True,'', None)
    try:
        connection = psycopg2.connect(user = conStr.user,password = conStr.password,host = conStr.host,port = conStr.port,database = conStr.database)

        cursor = connection.cursor()
        if record_to_insert != None:
            cursor.execute(postgres_query, record_to_insert)
        else:
            cursor.execute(postgres_query)
        if retornaResultado:
            if retornaTodo:
                salida.registros = cursor.fetchall()
            else:
                salida.registros = cursor.fetchone()[0]
        salida.OK = True
        connection.commit()
    except (Exception, psycopg2.Error) as error:
        if(connection):
            connection.rollback()
        salida.OK = False
        salida.mensaje = str.format("({0}) Error en Base de datos: {1} ", error.pgcode, error.pgerror)
        
    finally:
        #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
        return salida

def AltaUsuario(mail, password, DocumentoTipo, DocumentoNumero, fechaOrigen, rol, nombre, apellido=None,sexo='X', rubros=None):
    salida = EstadoScript(True,'', None)
    if rol == None or (rol != 'P' and rol != 'E'):
       salida.OK = False
       salida.mensaje = 'Rol no contemplado en el sistema. Verifique la selección'
       return salida
    else:    
        postgres_insert_query = "INSERT INTO public.\"Usuarios\" (\"Mail\", \"Rol\", \"Password\", \"Fecha_Origen\", \"DocumentoTipo\", \"DocumentoNumero\", \"Sexo\", \"Nombre\", \"Apellido\") \
        VALUES (%s,%s,crypt(%s, gen_salt('bf')), %s, %s, %s, %s, %s, %s) RETURNING \"UsuarioId\" "
        if rol == 'P':
            record_to_insert = (mail, rol, password, fechaOrigen, DocumentoTipo, DocumentoNumero, sexo, nombre, apellido)
        else:
            if rubros == None:
                salida.OK = False
                salida.mensaje = "Debe seleccionar al menos un rubro. Vuelva a intentarlo"
                return salida
            else:
                record_to_insert = (mail, rol, password, fechaOrigen, DocumentoTipo, DocumentoNumero, 'X', nombre, apellido)

        salida = EjecutarScript(postgres_insert_query,record_to_insert,True)

        if salida.registros != None and rol == "E":
            for rubro in rubros:
                postgres_insert_query = 'INSERT INTO public."EmpresaRubros"("EmpresaId", "RubroId")	VALUES ( %s, %s);'
                record_to_insert = (salida.registros, rubro)
                salidarubro = EjecutarScript(postgres_insert_query,record_to_insert)
                if salidarubro.OK == False:
                    salida.OK = False
                    salida.mensaje + salidarubro.mensaje + "\n"
        return salida

def validarUsuario(rol, usuario, clave):
    salida = EstadoScript(True,'', None)
    query = 'select "UsuarioId" from public."Usuarios" where "Rol"=\'{0}\' and "Mail" =\'{1}\' and "Password" = crypt(\'{2}\', "Password")'.format(rol, usuario, clave)
    salida = EjecutarScript(query, None, True, False)
    if salida.registros == None:
        salida.OK = False
        salida.mensaje = "Rol, Usuario y Clave no encontrados."
    else:
        session['username'] = usuario
        session['rolUsuario'] = rol
        session['userId'] = salida.registros
    return salida
#Definiciones de Funciones para Clientes

def ConsultarPropuestasUsuario():
    salida = EstadoScript(False,'', None)
    propuestas = []
    script = 'SELECT prop."PropuestaId", CONCAT(rub."Familia",\' - \',rub."RubroNombre") "Rubro", prop."NombrePROP", prop."Monto", prop."Descripcion", prop."Fecha_ALTA" + prop."Dias" as "VENCIMIENTO", prop."Fecha_BAJA" FROM public."Propuestas" prop INNER JOIN public."Rubros" rub ON prop."RubroId" = rub."RubroId"  WHERE prop."UsuarioIdCreador" = \'' + session['userId'] + '\' order by 6 asc, 3 desc'  #Aca va a tener que ir el userId como cookie
    salida = EjecutarScript(script, None, True,True)
    if salida.OK and salida.registros != None:
        for propuesta in salida.registros:
            estadoProp = True
            if propuesta[6] != None:
                estadoProp = False
            propuestas.append(Propuesta(propuesta[0], propuesta[1], propuesta[2], propuesta[3], propuesta[4], propuesta[5], estadoProp))
        salida.registros = propuestas
    return salida

#Funciones para Empresa

def ConsultarPropuestasVigentes():
    salida = EstadoScript(False,'', None)
    propuestas = []
    script = 'SELECT  prop."PropuestaId", CONCAT(rub."Familia",\' - \',rub."RubroNombre") "Rubro", prop."NombrePROP", prop."Monto", prop."Descripcion", prop."Fecha_ALTA" + prop."Dias" - CURRENT_DATE as "VENCIMIENTO"  FROM public."Propuestas" prop   inner join public."Rubros" rub on prop."RubroId" = rub."RubroId"  inner join public."EmpresaRubros" empru on prop."RubroId" = empru."RubroId"  where prop."Fecha_BAJA" is null   and prop."PropuestaId" not in (select "PropuestaId"   from public."PropuestaRespuestas"   where "EmpresaId" = \''+  session['userId']  + '\'  )  and empru."EmpresaId" = \'' +  session['userId'] + '\''
    salida = EjecutarScript(script, None, True,True)
    if salida.OK and salida.registros != None:
        for propuesta in salida.registros:
            propuestas.append(Propuesta(propuesta[0], propuesta[1], propuesta[2], propuesta[3], propuesta[4], propuesta[5]))
        salida.registros = propuestas
    return salida


#endregion

#region UNIVERSAL
##################################################
################-----UNIVERSAL-----###############
##################################################
@app.route('/Registrar', methods=['GET', 'POST'])
def registrar():
    if 'username' not in session:
    #if session['rolUsuario'] == None:
        formulario = ElegirRolForm()
        formularioCliente = RegistrarPersonaForm()
        formularioEmpresa = RegistrarEmpresaForm()
        if  request.method == 'POST':
            if formulario.rol.data == 'E':
                return redirect('/AltaEmpresa')
            elif formulario.rol.data == 'P':
                return redirect('/AltaPersona')
        return render_template('Registrar.html', form=formulario)
    else:
        flash('Debe desloguearse para poder crear un nuevo usuario','error')
        return render_template("sin_permiso.html", Logueado=True)


@app.route('/Ingresar', methods=['GET', 'POST'])
def Ingresar():
    if 'username' not in session:
        formulario = LoginForm()
        login = EstadoScript(True, '', None)
        if formulario.validate_on_submit() or request.method == 'POST':
            rol = formulario.rol.data
            mail = formulario.usuario.data
            clave = formulario.password.data
            login = validarUsuario(rol, mail, clave)
            if login.OK == True:
                flash('Bienvenido') #flash es cola de mensaje
                if session['rolUsuario'] == 'E':
                    return redirect('/HomeEmpresa')
                elif session['rolUsuario'] == 'P':
                    return redirect('/HomeCliente')
            else:

                flash(str(login.mensaje), 'error')
                return render_template('login.html', form=formulario)
        else:
            return render_template('login.html', form=formulario)

    else:
        formulario = LoginForm()
        session['rolUsuario'] = None
        session['userId'] = None
        return render_template('login.html', form=formulario)

##@app.route('/EditarUsuario', methods=['GET', 'POST'])
##def EditarUsuario():
 #   if 'username' in session:
 #       formularioCliente = RegistrarPersonaForm()
 #       formularioEmpresa = RegistrarEmpresaForm()
 #
 #       if request.method == 'GET':
 #           salida = EstadoScript(False,'',None)
 #           query = 'SELECT "UsuarioId", "Mail", "Password", "Fecha_Origen", "Sexo", "DocumentoNumero", "Nombre", "Apellido", "DocumentoTipo" FROM public."Usuarios" where "UsuarioId" = \'' + session['userId'] +'\''
 #           salida = EjecutarScript(query, None, True, False)
 #           if salida.OK:
 #               if session['rolUsuario'] == 'P':
 #                   formularioCliente.nombre.data    = salida.registros[6]
 #                   formularioCliente.apellido.data  = salida.registros[7]
 #                   formularioCliente.fechaNacimiento= salida.registros[3]
 #                   formularioCliente.sexo           = salida.registros[4]
 #                   formularioCliente.tipoDocumento  = salida.registros[8]
 #                   formularioCliente.nroDocumento   = salida.registros[5]
 #                   formularioCliente.correo         = salida.registros[1]
 #                   return render_template('/Cliente/AltaPersona.html', form=formularioCliente)
 #               
 #               else:
 #                   formularioCliente.nombre.data    = salida.registros[6]
 #                   formularioCliente.fechaNacimiento.data = salida.registros[3]
 #                   formularioCliente.tipoDocumento.data = salida.registros[8]
 #                   formularioCliente.nroDocumento.data = salida.registros[5]
 #                   formularioCliente.correo.data = salida.registros[1]
 #                   return render_template('/Empresa/AltaEmpresa.html', form=formularioEmpresa)
 #           else:
 #               return redirect(url_for('index.html'),200)
 #       else:
 #           #updates
 #           return 1
 #   else:
 #       return render_template('sin_permiso.html')
##
@app.route('/secret', methods=['GET'])
def secreto():
    if 'username' in session:
        return render_template('private.html', username=session['username'])
    else:
        return render_template('sin_permiso.html')

@app.route('/logout', methods=['GET'])
def logout():
    if 'username' in session:
        session.pop('username')
        session['rolUsuario'] = None
        session['userId'] = None
        return render_template('logged_out.html')
    else:
        session['rolUsuario'] = None
        session['userId'] = None
        return render_template('sin_permiso.html')   

    
@app.route('/Contactos', methods=['GET'])
def CargarContactos():
    return render_template('Contactos.html')

#endregion UNIVERSAL

##################################################
#################-----Cliente-----################
##################################################
#region Clientes
@app.route('/AltaPersona', methods=['GET', 'POST'])
def AltaPersona():
    if 'username' not in session: 
        formulario = RegistrarPersonaForm()
        if formulario.validate_on_submit():
            if request.method == 'POST' and (((formulario.tipoDocumento.data == 'CUIT' or formulario.tipoDocumento.data == 'CUIL') and len(str(formulario.nroDocumento.data)) != 11) or (formulario.tipoDocumento.data == 'DNI ' and len(str(formulario.nroDocumento.data)) != 8)):
                observaciones = list(formulario.nroDocumento.errors)
                observaciones.append("Para CUIT/CUIL debe ingresar 11 dígitos, para Numero de Documento 8 dígitos")
                formulario.nroDocumento.errors = tuple(observaciones)
                return render_template('/Cliente/AltaPersona.html', form=formulario)

            if formulario.password.data == formulario.password_check.data:
                insertar = AltaUsuario(formulario.correo.data, formulario.password.data, \
                     formulario.tipoDocumento.data, formulario.nroDocumento.data, formulario.fechaNacimiento.data, 'P', \
                      formulario.nombre.data,formulario.apellido.data, formulario.sexo.data) 
                if(insertar):
                    flash('Usuario creado correctamente', 'sucess')
                    flash('Valide su correo electronico para comenzar!', 'warning')
                    return redirect(url_for('Ingresar'))
                else:
                    flash('Ha ocurrido un error al crear el usuario. Reintente nuevamente mas tarde.', 'error')
            else:
                 flash('Las contraseñas no son iguales', 'error')

        return render_template('/Cliente/AltaPersona.html', form=formulario)
    else:
        flash('Debe desloguearse para poder crear un nuevo usuario','error')
        return render_template("sin_permiso.html", Logueado=True)

@app.route('/HomeCliente', methods=['GET'])
def ClientePrincipal():
    if 'username' in session and session['rolUsuario'] == 'P':
        return render_template('/Cliente/Principal.html')
    else: 
        return render_template('sin_permiso.html', Logueado = False)


@app.route('/VerPropuestas', methods=['GET'])
def VerPropuestas():
    if 'username' in session and session['rolUsuario'] == 'P':
        salida = EstadoScript(False,'', None)
        salida = ConsultarPropuestasUsuario()
        return render_template('/Cliente/VerPropuestas.html', propuestas = salida.registros)
    else:
        return render_template('sin_permiso.html', Logueado = False)

@app.route('/EliminarPropuesta/<id>', methods=['GET'])
def EliminarPropuesta(id):
    if 'username' in session and session['rolUsuario'] == 'P':
        if id != None:
            salida = EstadoScript(False,'',None)
            postgres_query = 'UPDATE public."Propuestas" set "Fecha_BAJA" = CURRENT_DATE WHERE "PropuestaId" = \'' + id + '\''
            salida = EjecutarScript(postgres_query, None, False, False)
            if salida.OK:
                flash('PROPUESTA ELIMINADA')
            else: 
                flash('Ha ocurrido un error al intentar Descartar la propuesta: \n' + salida.mensaje, 'error')

        return redirect(url_for('VerPropuestas'))
    else:
        return render_template('sin_permiso.html', Logueado = False)

@app.route('/VerREPROPuesta/<id>', methods=['GET'])
def VerREPROPuesta(id):
    if 'username' in session and session['rolUsuario'] == 'P':
    
        if id != None:
            salida = EstadoScript(False,'',None)
            PROPRes = []
            postgres_query = 'select propres."AceptaProp", propres."Fecha_MOVIMIENTO", prop."NombrePROP", prop."Monto", propres."MontoRespuesta", prop."Fecha_ALTA" + propres."Vigencia" as "Vencimiento", propres."Comentario", usu."Mail", usu."Nombre", propres."PropuestaRtaId" from public."PropuestaRespuestas" propres inner join public."Propuestas" prop on propres."PropuestaId" = prop."PropuestaId" inner join public."Usuarios" usu on propres."EmpresaId" = usu."UsuarioId" where prop."PropuestaId" =  \'' + id + '\''
            salida = EjecutarScript(postgres_query, None, True, True)
            if salida.OK:
                if len(salida.registros) != 0: 
                    for propuesta in salida.registros:
                        if propuesta[0] == False:
                            PROPRes.append(PropRespuesta(propuesta[0],propuesta[1],propuesta[2],propuesta[3],0,propuesta[5],propuesta[6],propuesta[7], propuesta[8], propuesta[9]))
                        else:
                            PROPRes.append(PropRespuesta(propuesta[0],propuesta[1],propuesta[2],propuesta[3],propuesta[4],propuesta[5],propuesta[6],propuesta[7], propuesta[8], propuesta[9]))
                    salida.registros = PROPRes
                else:
                    salida.registros = 0
                return render_template('/Cliente/PROPRespuestas.html', respuestas = salida.registros)
            else: 
                flash('Ha ocurrido un error al intentar Descartar la propuesta: \n' + salida.mensaje, 'error')
        return redirect(url_for('VerREPROPuesta'))
    else:
        return render_template('sin_permiso.html', Logueado = False)

@app.route('/CrearPropuesta', methods=['GET', 'POST'])
def CrearPropuesta_STP1():
    if 'username' in session and session['rolUsuario'] == 'P':
        formulario = CrearPropuestaForm()
        
        if request.method == 'GET':
            return render_template('/Cliente/CrearPropuesta.html', form = formulario)
        else:
            if formulario.validate_on_submit():
                
                return redirect(url_for('ConfirmarPropuesta', form = formulario), code = 307)
            else:
                return render_template('/Cliente/CrearPropuesta.html', form = formulario)
    
    else:
        return render_template('sin_permiso.html', Logueado = False)

@app.route('/ConfirmarPropuesta', methods=['POST'])
def ConfirmarPropuesta():
    if 'username' in session and session['rolUsuario'] == 'P':
        form = CrearPropuestaForm(request.form)
        if form.validate_on_submit():
            global PROPGrabar
            PROPGrabar = CrearPropuestaForm(request.form)
            return render_template('/Cliente/ConfirmarPropuesta.html', form = form) 
        else:
            return render_template("sin_permiso.html", Logueado = True)
    else:
            return render_template("sin_permiso.html", Logueado = False)

@app.route('/GrabarPropuesta', methods=['get','POST'])
def GrabarPropuesta():
    if 'username' in session and session['rolUsuario'] == 'P':
        PropuestaIdGenerada = None
        if PROPGrabar == None:
            return render_template("sin_permiso.html", Logueado = True)
        else:
            salida = EstadoScript(True,'', None)
            postgres_insert_query = "INSERT INTO public.\"Propuestas\"(\"UsuarioIdCreador\", \"NombrePROP\", \"RubroId\", \"Dias\", \"Monto\", \"Descripcion\")	VALUES (%s, %s, %s, %s, %s, %s)  RETURNING \"PropuestaId\";"
            #fdd4feae-0910-4af9-b9f7-56f04aabab8e es el id de un usuario persona de
            #prueba.  Por ahora irá harcodeado
            record_to_insert = (session['userId'], 
                                PROPGrabar.nombrePropuesta.data,
                                PROPGrabar.rubro.data,
                                PROPGrabar.cantidadDias.data,
                                PROPGrabar.precio.data,
                                PROPGrabar.descripcion.data)
          
            salida = EjecutarScript(postgres_insert_query, record_to_insert, True,False)
            if salida.OK:
                return render_template("/Cliente/PropuestaResponse.html", rta = salida)
            else:
               return render_template('500.html')
    else:
        return render_template('sin_permiso.html', Logueado = False)
#endregion


##################################################
#################-----Empresa-----################
##################################################
#region EMPRESA
@app.route('/AltaEmpresa', methods=['GET', 'POST'])
def AltaEmpresa():
    if 'username' not in session:
        formulario = RegistrarEmpresaForm()
        formulario.tipoDocumento.data = 'CUIT'
        if len(str(formulario.nroDocumento.data)) != 11 :
            observaciones = list(formulario.nroDocumento.errors)
            observaciones.append("Para CUIT/CUIL debe ingresar 11 dígitos, para Numero de Documento 8 dígitos")
            formulario.nroDocumento.errors = tuple(observaciones)
            return render_template('/Empresa/AltaEmpresa.html', form=formulario)

        if formulario.validate_on_submit():
            if request.method == 'POST' and (((formulario.tipoDocumento.data == 'CUIT' or formulario.tipoDocumento.data == 'CUIL') and len(str(formulario.nroDocumento.data)) != 11) or (formulario.tipoDocumento.data == 'DNI ' and len(srt(formulario.nroDocumento.data)) != 8)):
                    observaciones = list(formulario.nroDocumento.errors)
                    observaciones.append("Para CUIT/CUIL debe ingresar 11 dígitos, para Numero de Documento 8 dígitos")
                    formulario.nroDocumento.errors = tuple(observaciones)
                    return render_template('/Empresa/AltaEmpresa.html', form=formulario)

            if formulario.password.data == formulario.password_check.data:
                 crearUsuario = AltaUsuario(formulario.correo.data, formulario.password.data, \
                 formulario.tipoDocumento.data, formulario.nroDocumento.data, formulario.fechaNacimiento.data, 'E', \
                 formulario.nombre.data, None , None , formulario.rubros.data)
                 if crearUsuario.OK == True:
                    flash('Usuario creado correctamente', 'success')
                    
                    return redirect(url_for('Ingresar'))
                 else:
                    flash('Se ha producido un error: ' + crearUsuario.mensaje, 'error')
                    return render_template('/Empresa/AltaEmpresa.html', form=formulario)

            else:
                 flash('Las contraseñas no son iguales', 'error')
        return render_template('/Empresa/AltaEmpresa.html', form=formulario)
    else:
        return render_template('sin_permiso.html', Logueado = False)


@app.route('/ListaPropuestas', methods=['GET','POST'])
def ListarPropuestas():
    if 'username' in session and session['rolUsuario'] == 'E':
        formulario = EntregarPropuesta()
        listaPropuestas = ConsultarPropuestasVigentes()

        if request.method == 'POST':
            if formulario.validate_on_submit():
                salida = EstadoScript(False,'',None)
                postgres_insert_query = 'INSERT INTO public."PropuestaRespuestas"("PropuestaId", "EmpresaId", "AceptaProp", "MontoRespuesta", "Comentario", "Vigencia") VALUES (%s, %s, %s, %s, %s, %s)'
                record_to_insert = (formulario.id.data, session['userId'], True, formulario.precio.data, formulario.comentario.data, formulario.vigencia.data)
                salida = EjecutarScript(postgres_insert_query, record_to_insert, False, False)
                if salida.OK:
                    flash('PROPUESTA ACEPTADA! Esperemos que PROPongamos más juntos!', 'success')
                    return redirect(url_for('ListarPropuestas'))
                else: 
                    flash('Ha ocurrido un error al intentar enviar su PROPuesta: \n' + salida.mensaje, 'error')

                time.sleep(2)
                return render_template('/Empresa/ListaPropuestas.html',formModal = formulario, propuestas = listaPropuestas.registros)
        return render_template('/Empresa/ListaPropuestas.html',formModal = formulario, propuestas = listaPropuestas.registros)
    else:
        return render_template('sin_permiso.html', Logueado = False)

@app.route('/CancelarPropuesta/<id>', methods=['GET'])
def CancelarPropuesta(id):
    if 'username' in session and session['rolUsuario'] == 'E':
        if id != None:
            salida = EstadoScript(False,'',None)
            postgres_insert_query = 'INSERT INTO public."PropuestaRespuestas"("PropuestaId", "EmpresaId", "AceptaProp") VALUES (%s, %s, %s)'
            record_to_insert = (id, session['userId'] , False)
            salida = EjecutarScript(postgres_insert_query, record_to_insert, False, False)
            if salida.OK:
                flash('PROPUESTA DESCARTADA')
            else: 
                flash('Ha ocurrido un error al intentar Descartar la propuesta: \n' + salida.mensaje, 'error')

        return redirect(url_for('ListarPropuestas'))
    else:
        return render_template('sin_permiso.html', Logueado = False)


@app.route('/HomeEmpresa', methods=['GET'])
def EmpresaPrincipal():
    if session['rolUsuario'] == 'E':
        return render_template('/Empresa/Principal.html')
    else: 
        return render_template('sin_permiso.html')

#endregion
##################################################
##################################################
##################################################


#Programa Principal: Levantamiento de Servidor, esto NO SE TOCA, por NADA del
#mundo
if __name__ == "__main__":
  
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')

    
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5000'))
    except ValueError:
        PORT = 5000
    app.run(HOST, PORT)


