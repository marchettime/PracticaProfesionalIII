from flask_wtf import FlaskForm
from wtforms import  validators, SelectField, StringField, SubmitField, PasswordField, RadioField, TextAreaField, SelectMultipleField, FileField
from wtforms.fields.html5 import EmailField, DecimalField, IntegerField, DateField
from wtforms.validators import Required, Length, Regexp, NumberRange
from decimal import ROUND_HALF_UP
import psycopg2 
from classes import connectionString
conStr = connectionString()

def choicesRubros():
    choices = None 
    connection = None
    try:
        connection = psycopg2.connect(user = conStr.user,
                                      password = conStr.password,
                                      host = conStr.host,
                                      port = conStr.port,
                                      database = conStr.database)
    
        cursor = connection.cursor()
      
    
        # Print PostgreSQL version
        query = 'SELECT "RubroId", "Familia" || \' - \' || "RubroNombre" FROM public."Rubros" ORDER BY 2 ASC;'
        cursor.execute(query)

        #obtencion de registros
        choices = cursor.fetchall()
    
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
            if(connection):
                cursor.close()
                connection.close()
            return choices

#campos de login
class LoginForm(FlaskForm):
    rol = SelectField('Soy una: ', choices=[('P', 'Persona'), ('E', 'Empresa o Profesional')], validators=[Required()])
    usuario = StringField('Mail', validators=[Required()])#Label del campo, y las validaciones correspondientes, en este caso tiene el
    password = PasswordField('Contraseña', validators=[Required()])
    enviar = SubmitField('Ingresar')

class SaludarForm(FlaskForm):
    usuario = StringField('Nombre: ', validators.required())
    enviar = SubmitField('Saludar')

#Rol para el primer paso que es para derivar a que formulario crear
class ElegirRolForm(FlaskForm):
    rol = RadioField('Soy una: ', choices=[('P', 'Persona'), ('E', 'Empresa o Profesional')], validators=[Required()])
    submit = SubmitField('Continuar |>')

#Formulario de ALta de Persona Fisica en la web
class RegistrarPersonaForm(FlaskForm):
    nombre = StringField('Nombre',validators=[Required()])
    apellido = StringField('Apellido', validators=[Required()])
    fechaNacimiento = DateField('Fecha de Nacimiento', validators=[Required()], format='%Y-%m-%d')
    sexo = SelectField(u'Sexo', choices=[('F', 'Femenino'), ('M', 'Masculino'), ('x', 'No informar')], validators=[Required()])
    tipoDocumento = SelectField(u'Tipo de Documento', choices=[('CUIT', 'CUIT'), ('CUIL', 'CUIL'), ('DNI ', 'DNI / Documento Unico')], validators=[Required()])
    nroDocumento = IntegerField('Numero de Documento', validators=[Required(), NumberRange(min=1000000, max=55999999999, message='Ingrese un valor válido')])
    correo = EmailField('Mail', validators=[Required()])
    password = PasswordField('Contraseña', validators=[Required()])
    password_check = PasswordField('Verificar Contraseña', validators=[Required()])
    submit = SubmitField('Registrarse!')

#Formulario de ALta de Persona Juridica en la web
class RegistrarEmpresaForm(FlaskForm):
    nombre = StringField('Nombre',validators=[Required()])
    fechaNacimiento = DateField('Fecha de Constitución', validators=[Required()], format='%Y-%m-%d')
    tipoDocumento = SelectField(u'Tipo de Documento', choices=[('CUIT', 'CUIT'), ('', '')], validators=[Required()])
    nroDocumento = IntegerField('Numero de Documento', validators=[Required(), NumberRange(min=20000000001, max=55999999999,message='Minimo valor admitido: 1')])
    correo = EmailField('Mail', validators=[Required()])
    password = PasswordField('Contraseña', validators=[Required()])
    password_check = PasswordField('Verificar Contraseña', validators=[Required()])
    rubros = SelectMultipleField(u'¿A qué rubro/s te dedicas?', choices = choicesRubros(), validators=[Required() ])
    submit = SubmitField('Registrarse!')

class CrearPropuestaForm(FlaskForm):
    nombrePropuesta = StringField('PROPoné un nombre',validators=[Required()])
    rubro = SelectField(u'Tipo de PROPuesta', validators=[Required()], choices = choicesRubros())#, choices=[('1', 'Viajes'), ('2', 'Construcción'), ('3', 'Vivienda')]
    cantidadDias = IntegerField('Plazo máximo de Respuesta: ', validators=[Required(), NumberRange(min=1, max=45,message='El tiempo máximo de duracion es hasta 45 días corridos.')])
    precio = IntegerField(u'Presupuesto Máximo', validators=[Required(), NumberRange(min=1, max=99999999, message='Debe ingresar un Monto entre $1 y $99.999.999')])#, Regexp('^\s*(?=.*[1-9])\d*(?:\.\d{1,2})?\s*$'
    descripcion = TextAreaField(u'Describí que necesitas:', validators=[Required(), Length(min=15, max=3000, message='Describa lo mejor posible su necesidad a Presupuestar. Dispone de 3000 caracteres.')])
    submit = SubmitField('Continuar')
    
class EntregarPropuesta(FlaskForm):
    id = StringField(validators=[Required()])
    precio = IntegerField(u'Valor PROPuesto:', validators=[Required(), NumberRange(min=1, max=99999999, message='Debe ingresar un Monto entre $1 y $99.999.999')])#, Regexp('^\s*(?=.*[1-9])\d*(?:\.\d{1,2})?\s*$'
    comentario = TextAreaField(u'Si tenés comentarios, aprovechá este espacio:', validators=[Length(max=3000, message='Dispone de 3000 caracteres.')])
    vigencia = IntegerField('Vigencia: ', validators=[Required(), NumberRange(min=1, max=45,message='El tiempo máximo de duracion es hasta 45 días corridos.')])
    submit = SubmitField('PROP YA!')

#Formulario de busqueda....
class BuscarForm(FlaskForm):
    palabra = StringField(u'Ingrese su filtro:', validators=[Required(),Length(min=3, message='Minimo 3 caracteres de largo')])
    enviar = SubmitField('Buscar')


class AltaVentaForm(FlaskForm):
    codigo = StringField(u'Codigo de Producto:', validators=[Required(), Regexp('[a-zA-Z]+[a-zA-Z]+[a-zA-Z]+[0-9]+[0-9]+[0-9]+',message='Debe cumplir con el formato: 3 letras y 3 números'), Length(min=6, max=6, message='No cumple con el largo necesario')])
    producto = StringField(u'Nombre de Producto:', validators=[Required(), Length(min=3, message='Ingresar minimo 3 caracteres')])
    cantidad = IntegerField(u'Cantidad:', validators=[Required(), NumberRange(min=1,message='Minimo valor admitido: 1')])
    precio = StringField(u'Precio Unitario de Producto (en $): ', validators=[Required(), Regexp('^\s*(?=.*[1-9])\d*(?:\.\d{1,2})?\s*$',message='Debe ingresar un valor tipo: N.NN')])
	#precio = DecimalField(u'Precio Unitario de Producto (en $): ', places = 2,
	#use_locale=False, validators=[Required(),
	#NumberRange(min=0.01,message='$Minimo valor admitido: 0.01')])
    nombreCliente = StringField(u'Nombre de Cliente:', validators=[Required(), Length(min=3, message='Ingresar minimo 3 caracteres')])
    enviar = SubmitField('Registrar!')
    #expresion regular de precio sacado de: https://stackoverflow.com/questions/8609714/regex-greater-than-zero-with-2-decimal-places


