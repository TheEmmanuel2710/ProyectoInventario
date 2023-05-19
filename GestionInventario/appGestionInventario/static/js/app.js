$(function(){
    $("#fileFoto").on("change",mostrarImagen);
})

function mostrarImagen(evento){
    const archivos = evento.target.files
    const archivo = archivos[0]
    const url = URL.createObjectURL(archivo)  
    $("#imagenMostrar").attr("src",url)
  }
