"""
URL configuration for GestionInventario project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from appGestionInventario import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.inicio),
    path('inicioAdministrador/',views.inicioAdministrador),
    path('inicioAsistente/',views.inicioAsistente),
    path('inicioInstructor/',views.inicioInstructor),
    path('vistaRegistrarUsuario/',views.vistaRegistrarUsuario),
    path('registrarUsuario/',views.registrarUsuario),
    path('vistaGestionarUsuarios/',views.vistaGestionarUsuarios),
    path('vistaLogin/',views.vistaLogin),
    path('login/',views.login),
    path('salir/',views.salir),
    path('solicitudesInstructor/',views.GestionarSolicitudesI),
    path('vistaRegistrarSolicitud/',views.vistaRegistrarSolicitud),
    path('vistaGestionarElementos/',views.vistaGestionarElementosDevolutivos),
    path('vistaRegistrarElementos/',views.vistaRegistrarElementosDevolutivos),
    path('registrarElemento/',views.registrarElementosDevolutivos),
    path('vistaRegistrarMateriales/',views.vistaRegistrarMaterial),
    path('registrarMaterial/',views.registrarMaterial),
    path('vistaEntradaMaterial/',views.vistaEntradaMaterial),
    path('registrarEntradaMaterial/',views.registrarEntradaMaterial),
    
]

if settings.DEBUG:
    urlpatterns += static (settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
