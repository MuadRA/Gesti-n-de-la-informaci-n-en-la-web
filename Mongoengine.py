
"""
GIW 2021-22
Práctica 8
Grupo 7
Autores: MATEO GONZALEZ DE MIGUEL, MUAD ROHAIBANI ALKADRI , MARIANA DE LA CARIDAD VILLAR ROJAS, LUIS SÁNCHEZ CAMACHO

(MATEO GONZALEZ DE MIGUEL, MUAD ROHAIBANI ALKADRI , MARIANA DE LA CARIDAD VILLAR ROJAS, LUIS SÁNCHEZ CAMACHO) 
declaramos que esta solución es fruto exclusivamente de nuestro trabajo personal. No hemos sido ayudados por 
ninguna otra persona ni hemos obtenido la solución de fuentes externas, y tampoco hemos compartido nuestra solución
con nadie. Declaramos además que no hemos realizado de manera deshonesta ninguna otra
actividad que pueda mejorar nuestros resultados ni perjudicar los resultados de los demás.
"""

from mongoengine import connect, StringField, IntField, ListField, ValidationError, FloatField, Document, EmbeddedDocument, EmbeddedDocumentListField, DateTimeField, ComplexDateTimeField, ReferenceField, PULL
import string
connect('giw_mongoengine')

class Tarjeta(EmbeddedDocument):
  nombre = StringField(required = True, min_length = 2)
  numero = StringField(required = True, min_length = 16, max_length = 16, regex = "[0-9]{16}")
  mes = StringField(required = True, min_length = 2, max_length = 2, regex = "[0-9]{2}")
  año = StringField(required = True, min_length = 2, max_length = 2, regex = "[0-9]{2}")
  ccv = StringField(required = True, min_length = 3, max_length = 3, regex = "[0-9]{3}")

class Producto(Document):
  codigo_barras = StringField(required = True, unique = True) #que cumpla el formato del pdf
  nombre = StringField(required = True, min_length = 2)
  categoria_principal = IntField(required = True, min_value = 0)
  categorias_secundarias = ListField(IntField(min_value = 0))

  def clean(self):
    self.validate(clean = False)
    if len(self.categorias_secundarias):
      if self.categorias_secundarias[0] is not self.categoria_principal:
        raise ValidationError("La primera categoria secundaria no es igual a la principal.")
    
    #calcular el codigo de barras
    aux = list(self.codigo_barras)
    aux.reverse()
    checkDigit = int(aux.pop(0))
    suma = 0

    for i in range(1, len(aux) + 1):
      k = 3
      if i % 2 == 0:
        k = 1
      suma += int(aux[i-1]) * k
    modulo = suma % 10
    if 10 - modulo != checkDigit:
      raise ValidationError("El checkDigit es incorrecto.")
    
class Linea(EmbeddedDocument):
  num_items = IntField(required = True, min_value = 0)
  precio_item = FloatField(required = True, min_value = 0)
  nombre_item = StringField(required = True, min_length = 2)
  total = FloatField(required = True, min_value = 0)
  ref = ReferenceField(Producto, required = True)

  def clean(self):
    self.validate(clean = False)
    if (self.num_items * self.precio_item) != self.total:
      raise ValidationError("El total es diferente a la multiplicacion de numero de productos por su precio.")
    if self.nombre_item != self.ref.nombre:
      raise ValidationError("El nombre del producto es diferente al de su referencia.")


class Pedido(Document):
  total = FloatField(required = True, min_value = 0)
  fecha = ComplexDateTimeField(required = True)
  lineas = EmbeddedDocumentListField(Linea, required = True)

  def clean(self):
    self.validate(clean = False)
    suma = 0
    listaRef = list()
    for i in self.lineas:
      suma += i.total
      if i.ref in listaRef:
        raise ValidationError("El total es diferente al total de las lineas.")
      listaRef.append(i.ref)

    if suma != self.total:
      raise ValidationError("El total es diferente al total de las lineas.")

class Usuario(Document):
    dni = StringField(primary_key = True, min_length = 9, max_length = 9, regex = "[0-9]+[A-Z]")
    nombre = StringField(required = True, min_length = 2)
    apellido1 = StringField(required = True, min_length = 2)
    apellido2 = StringField()
    f_nac = StringField(required = True) #mirar como hacer que se adapte al formato
    tarjetas = EmbeddedDocumentListField(Tarjeta)
    pedidos = ListField(ReferenceField(Pedido, reverse_delete_rule = PULL))

    def clean(self):
      self.validate(clean = False)

      #Comprobar que el DNI es válido
      letra = self.dni[8]
      numero = int(self.dni[0:8])
      letrasResto = "TRWAGMYFPDXBNJZSQVHLCKE"
      resto = numero % 23

      if letra not in string.ascii_uppercase: # Compruebo que hay una letra al final
          raise ValidationError("El DNI debe contener 1 letra al final")

      if letrasResto[resto] != letra:# Compruebo que el DNI es válido realizando el cálculo de dígito
          raise ValidationError("El DNI no pasa el cálculo de dígito de control español")
      
      #comprobar fecha
      aux = self.f_nac
      aux = aux.split("-")

      if len(aux) != 3 or len(aux[0]) != 4 or len(aux[1]) != 2 or len(aux[2]) != 2:
        raise ValidationError("La fecha debe seguir el siguiente formato: 'AAAA-MM-DD'")

       



