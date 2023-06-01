from django.shortcuts import render,redirect
from appGestionInventario.models import *
from django.contrib.auth.models import Group
from django.db import Error,transaction
import random
import string
from django.contrib.auth import authenticate
from django.contrib import auth
from django.conf import settings
import urllib
import json
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
import threading
from smtplib import SMTPException
from django.http import JsonResponse
# Create your views here.
datosSesion={"user":None,"rutaFoto":None, "rol":None}

def inicio(request):
    return render(request,"inicio.html")

def inicioAdministrador(request):
    if request.user.is_authenticated:
        datosSesion={"user": request.user}
        return render(request,"administrador/inicio.html", datosSesion)
    else:
        mensaje="Debe iniciar sesión"
        return render(request, "frmIniciarSesion.html",{"mensaje":mensaje})

def inicioAsistente(request):
    if request.user.is_authenticated:
        datosSesion={"user": request.user}
        return render(request,"asistente/inicio.html", datosSesion)
    else:
        mensaje="Debe iniciar sesión"
        return render(request, "frmIniciarSesion.html",{"mensaje":mensaje})

def inicioInstructor(request):
    if request.user.is_authenticated:
        datosSesion={"user": request.user}
        return render(request,"instructor/inicio.html", datosSesion)
    else:
        mensaje="Debe iniciar sesión"
        return render(request, "frmIniciarSesion.html",{"mensaje":mensaje})
    
def vistaRegistrarUsuario(request):
    if request.user.is_authenticated:
        roles = Group.objects.all()
        retorno = {"roles":roles,"user":request.user}
        return render(request, "administrador/frmRegistrarUsuario.html",retorno)
    else:
        mensaje="Debe iniciar sesión"
        return render(request, "frmIniciarSesion.html",{"mensaje":mensaje})

def registrarUsuario(request):
    try:
        nombres = request.POST["txtNombres"]
        apellidos = request.POST["txtApellidos"]
        correo = request.POST["txtCorreo"]
        tipo = request.POST["cbTipo"]
        foto = request.FILES.get("fileFoto",False)
        idRol = int(request.POST["cbRol"])
        with transaction.atomic():
            #crear un objeto de tipo User
            user = User(username=correo, first_name=nombres, last_name=apellidos, email=correo, userTipo=tipo, userFoto=foto)
            user.save()
            #obtener el Rol de acuerdo a id del rol 
            rol=Group.objects.get(pk=idRol)
            #agregar el usuario a ese Rol
            user.groups.add(rol)
            #si el rol es Administrador se habilita para que tenga acceso al sitio web del administrador
            if(rol.name=="Administrador"):user.is_staff=True#problemas cuando se es administrador
            #guardamos el usuario con lo que tenemos
            user.save()
            #llamamos a la funcion generarPassword 
            passwordGenerado = generarPassword()
            print (f"password {passwordGenerado}")
            #con el usuario creado llamamos a la función set_password que 
            # # encripta el password y lo agrega al campo password del user.
            user.set_password (passwordGenerado)
            #se actualiza el user
            user.save()
            mensaje="Usuario Agregado Correctamente" 
            retorno = {"mensaje":mensaje}
            #enviar correo al usuario
            asunto='Registro Sistema Inventario CIES-NEIVA'
            mensaje=f'Cordial saludo, <b>{user.first_name} {user.last_name}</b>, nos permitimos.\
                informarle que usted ha sido registrado en el Sistema de Gestión de Inventario \
                del Centro de la Industria, la Empresa y los Servicios CIES de la ciudad de Neiva.\
                Nos permitimos enviarle las credenciales de Ingreso a nuestro sistema.<br>\
                <br><b>Username: </b> {user.username}\
                <br><b>Password: </b> {passwordGenerado}\
                <br><br>Lo invitamos a ingresar a nuestro sistema en la url:\
                http://gestioninventario.sena.edu.co.'
            thread = threading.Thread(target=enviarCorreo, args=(asunto,mensaje, user.email) )
            thread.start()
            return redirect("/vistaGestionarUsuarios/", retorno)
    except Error as error:
        transaction.rollback()
        mensaje= f"{error}"
    retorno = {"mensaje":mensaje}
    return render(request,"administrador/frmRegistrarUsuario.html",retorno)

def generarPassword():
    """
    Genera un password de longitud de 10 que incluye letras mayusculas
    y minusculas,digitos y cararcteres especiales
    Returns:
        _str_: retorna un password
    """
    longitud = 10
    
    caracteres = string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation
    password = ''
    
    for i in range(longitud):
        password +=''.join(random.choice(caracteres))
    return password

def vistaGestionarUsuarios(request):
    if request.user.is_authenticated:
        usuarios=User.objects.all()
        retorno = {"usuarios":usuarios,"user":request.user}
        return render(request,"administrador/vistaGestionarUsuarios.html",retorno)
    else:
        mensaje="Debe iniciar sesión"
        return render(request, "frmIniciarSesion.html",{"mensaje":mensaje})
    
def vistaRegistrarMaterial(request):
    unidadesMedida = UnidadMedida.objects.all()
    retorno = {"unidadesMedida":unidadesMedida,"estados":estadosElementos}
    return render(request,"asistente/frmRegistrarMaterial.html",retorno)

def vistaEntradaMaterial(request):
    proveedores=Proveedor.objects.all()
    usuarios=User.objects.all()
    materiales = Material.objects.all()
    unidadesMedida = UnidadMedida.objects.all()
    retorno = {"unidadesMedida":unidadesMedida,"proveedores":proveedores, "usuarios":usuarios,"materiales":materiales}
    return render(request,"asistente/frmRegistrarEntradaMaterial.html",retorno)

def registrarEntradaMaterial(request):
    if request.method=='POST':
        try:
            with transaction.atomic():
                estado=False
                codigoFactura=request.POST['codigoFactura']
                entregadoPor=request.POST['entregadoPor']
                idProveedor= int(request.POST['proveedor'])
                recibidoPor= int(request.POST['recibidoPor'])
                fechaHora=request.POST.get('fechaHora',None)
                observaciones=request.POST['observaciones']
                userRecibe=User.objects.get(pk=recibidoPor)
                proveedor=Proveedor.objects.get(pk=idProveedor)
                entradaMaterial=EntradaMaterial(entNumeroFactura=codigoFactura,entFechaHora=fechaHora,
                                                entUsuarioRecibe=userRecibe,entEntregadoPor=entregadoPor,
                                                entProveedor=proveedor,entObservaciones=observaciones)
                entradaMaterial.save()
                detalleMateriales=json.loads(request.POST['detalle'])
                for detalle in detalleMateriales:
                    material=Material.objects.get(id=int(detalle['idMaterial']))
                    cantidad=int(detalle['cantidad'])
                    precio=int(detalle['precio'])
                    estado=detalle['estado']
                    unidadaMedida=UnidadMedida.objects.get(pk=int(detalle['idUnidadMedida']))
                    detalleEntrada=DetalleEntradaMaterial(detEntradaMaterial=entradaMaterial,
                                                          detMaterial=material,matUnidadMedida=unidadaMedida,
                                                          detCantidad=cantidad,detPrecioUnitario=precio,detEstado=estado)
                    detalleEntrada.save()
                estado=True
                mensaje="Se ha registrado la entrada de Materiales correctamente"
        except Error as error:
            transaction.rollback()
            mensaje=f"{error}"
        retorno={"estado":estado,"mensaje":mensaje}
        return JsonResponse(retorno)
    
    
def registrarMaterial(request):
    estado = False
    try:
        nombre = request.POST["txtNombre"]
        marca = request.POST.get("txtMarca",None)
        descripcion = request.POST.get("txtDescripcion",None)
        estado = request.POST["cbEstado"]
        deposito = request.POST["cbDeposito"]
        estante = request.POST.get("txtEstante",False)
        entrepano = request.POST.get("txtEntrepano",False)
        locker = request.POST.get("txtLocker",False)
        with transaction.atomic():
            cantidad = Elemento.objects.all().filter(eleTipo='MAT').count()
            codigoElemento = 'MAT' + str(cantidad+1).rjust(6,'0')
            #crear Elemento
            elemento = Elemento(eleCodigo = codigoElemento, eleNombre = nombre, eleTipo = "MAT", eleEstado = estado)
            #salvar el elemento en al base de datos
            elemento.save()
            #crear Material
            material = Material(matReferencia = descripcion,matMarca = marca,matElemento=elemento)
            material.save()
            #crear objeto de ubicacion fisica del elemento
            ubicacion = UbicacionFisica(ubiDeposito = deposito,ubiEstante = estante, ubiEntrepano = entrepano, ubiLocker = locker,ubiElemento =elemento)
            # registrar en la base de datos la ubicacion fisica del elemento
            ubicacion.save()
            estado=True
            mensaje =f"Material registrado exitosamente con el codigo {codigoElemento}"
    except Error as error:
        transaction.rollback()
        mensaje =f"error"
    retorno = {"mensaje":mensaje,"material":material,"estado":estado}
    return render(request,"asistente/frmRegistrarMaterial.html",retorno)

    
def vistaLogin(request):
    return render(request,"frmIniciarSesion.html")

def login(request):
    #validar el recapthcha
    """Begin reCAPTCHA validation"""
    recaptcha_response = request.POST.get('g-recaptcha-response')
    url = 'https://www.google.com/recaptcha/api/siteverify'
    values = {
        'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY, 
        'response': recaptcha_response
    }
    data = urllib.parse.urlencode(values).encode()
    req = urllib.request.Request(url, data=data)
    response = urllib.request.urlopen(req)
    result = json.loads(response.read().decode()) 
    print (result)
    """ End reCAPTCHA validation """
    if result['success']:
        username= request.POST["txtUsername"] 
        password = request.POST["txtPassword"]
        user = authenticate(username=username, password=password)
        print (user)
        if user is not None:
            #registrar la variable de sesión
            auth.login(request, user)
            if user.groups.filter(name='Administrador').exists():
                return redirect('/inicioAdministrador')
            elif user.groups.filter(name='Asistente').exists():
                return redirect('/inicioAsistente')
            else:
                return redirect('/inicioInstructor')
        else:
            mensaje = "Usuario o Contraseña Incorrectas"
            return render(request, "frmIniciarSesion.html",{"mensaje":mensaje})
    else:
        mensaje="Debe validar primero el recaptcha"
        return render(request, "frmIniciarSesion.html",{"mensaje" :mensaje})
    
def salir(request):
    auth.logout(request)
    return render(request, "frmIniciarSesion.html",
                  {"mensaje":"Ha cerrado la sesión"})

def GestionarSolicitudesI(request):
    if request.user.is_authenticated:
        usuarios=User.objects.all()
        retorno = {"usuarios":usuarios,"user":request.user}
        return render(request,"instructor/vistaGestionarSolicitudes.html",retorno)
    else:
        mensaje="Debe iniciar sesión"
        return render(request, "frmIniciarSesion.html",{"mensaje":mensaje})

def vistaRegistrarSolicitud(request):
     if request.user.is_authenticated:
         unidadesMedida = UnidadMedida.objects.all()
         fichas=Ficha.objects.all()
         elementos=Elemento.objects.all()
         retorno = {"unidadesMedida":unidadesMedida,"fichas":fichas,"elementos":elementos,"user":request.user}
         return render(request,"instructor/frmRegistrarSolicitud.html",retorno)
     else:
         mensaje="Debe iniciar sesión"
         return render(request, "frmIniciarSesion.html",{"mensaje":mensaje})


def enviarCorreo (asunto=None, mensaje=None, destinatario=None): 
    remitente = settings.EMAIL_HOST_USER 
    template = get_template('enviarCorreo.html')
    contenido = template.render({
        'destinatario': destinatario,
        'mensaje': mensaje,
        'asunto': asunto,
        'remitente': remitente,
    })
    try:
        correo = EmailMultiAlternatives (asunto, mensaje, remitente, [destinatario]) 
        correo.attach_alternative (contenido, 'text/html') 
        correo.send(fail_silently=True)
    except SMTPException as error: 
        print(error)

def vistaGestionarElementosDevolutivos(request):
    if request.user.is_authenticated:
        retorno = {"devolutivos":Devolutivo.objects.all(),"user":request.user}
        return render(request,"asistente/vistaGestionarElementosDevolutivos.html",retorno)
    else:
        mensaje="Debe iniciar sesión"
        return render(request, "frmIniciarSesion.html",{"mensaje":mensaje})

    
def vistaRegistrarElementosDevolutivos(request):
    if request.user.is_authenticated:
        retorno = {"tipoElemento": tipoElemento,"estadoElemento":estadosElementos,"user":request.user}
        return render(request,"asistente/frmRegistrarElementosDevolutivos.html",retorno)
    else:
        mensaje="Debe iniciar sesión"
        return render(request, "frmIniciarSesion.html",{"mensaje":mensaje})
    
def registrarElementosDevolutivos(request):
    estado = False
    try:
        #datos del elemento en general
        nombreEle = request.POST['txtNombre']
        tipoEle = request.POST['cbTipo']
        estadoEle = request.POST['cbEstado']
        #datos del devolitivo
        placaSena = request.POST['txtPlacaSena']
        serial = request.POST['txtSerial']
        marca = request.POST['txtMarca'] 
        descripcion = request.POST['txtDescripcion']    
        fechaIngreso = request.POST['txtFecha']
        valor = float(request.POST['txtValor'])   
        foto= request.FILES.get('fileFoto',False)
        #datos de la ubucacion fisica
        deposito = request.POST['txtDesposito']
        estante = request.POST.get('txtEstante',False)
        entrepaño = request.POST.get('txtEntrepaño',False)
        loker = request.POST.get('txtLoker',False)
        with transaction.atomic():
            #obtener cuantos elementos se han registrado    
            cantidad = Elemento.objects.all().count()
            #crear un codigo a partir de la cantidad, ajustando 0 al inicio
            codigoElemento = tipoEle.upper() + str(cantidad+1).rjust(5, '0')
            #crear el elemento
            elemento = Elemento(eleCodigo = codigoElemento,eleNombre=nombreEle,eleTipo=tipoEle,eleEstado=estadoEle)
            #salvar el elemento en la base de datos
            elemento.save()
            #crear objeto ubicación física del elemento
            ubicacion = UbicacionFisica(ubiElemento = elemento,ubiDeposito =deposito,ubiEstante=estante,ubiEntrepano=entrepaño,
                                        ubiLocker=loker)
            #registrar en la base de datos la ubicación física del elemento
            ubicacion.save()
            #crear el devolutivo
            devolutivo = Devolutivo(devPlacaSena=placaSena,devSerial=serial,devDescripcion=descripcion,
                                    devMarca=marca,devFechaIngresoSENA=fechaIngreso,devValor=valor,
                                    devFoto=foto,devElemento=elemento) 
            #registrar el elemento en la base de datos
            devolutivo.save()
            estado=True
            mensaje=f"Elemento Devolutivo registrado Satisfactoriamente con el codigo {codigoElemento}"
    except Error as error:
        transaction.rollback()
        mensaje=f"{error}"
    retorno = {"mensaje":mensaje,"devolutivo": devolutivo,"estado":estado,"tipoElemento": tipoElemento,"estadoElemento":estadosElementos}
    return render(request,"asistente/frmRegistrarElementosDevolutivos.html",retorno)



