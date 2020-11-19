class connectionString:
    user = "proyecto"
    password = "proyecto"
    host = "127.0.0.1"
    port = "5432"
    database = "proposupdb"

class EstadoScript:
    def __init__(self, OK, mensaje, registros):
       self.OK = OK
       self.mensaje = mensaje
       self.registros = registros

class Propuesta:
     def __init__(self, id,  rubro, nombrePropuesta, monto, descripcion, vencimiento, estado = True):
         self.id = id
         self.rubro = rubro
         self.nombrePropuesta = nombrePropuesta
         self.monto = monto
         self.descripcion = descripcion
         self.vencimiento = vencimiento
         self.estado = estado
class PropRespuesta:
    def __init__(self,aceptaProp , fechaMovimiento, nombreProp, montoOriginal, montoRespuesta, vencimiento, comentario, mailRespuesta,nombreEmpresa, reproId):
        self.aceptaProp      = aceptaProp 
        self.fechaMovimiento = fechaMovimiento
        self.nombreProp      = nombreProp
        self.montoOriginal   = montoOriginal
        self.montoRespuesta  = montoRespuesta
        self.vencimiento     = vencimiento
        self.comentario      = comentario
        self.mailRespuesta   = mailRespuesta
        self.nombreEmpresa = nombreEmpresa
        self.reproId = reproId
class LineaTabla:
    def __init__(self, codigo, producto, cliente, cantidad, precioUnitario):
        self.codigo = codigo
        self.producto = producto
        self.cliente = cliente
        self.cantidad = cantidad
        self.precioUnitario = precioUnitario

