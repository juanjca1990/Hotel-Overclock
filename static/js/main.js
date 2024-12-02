/*script para abrir modales recibe por parametros la url y el id*/

function abrir_modal(url, id) { /// al llamar a la funcion para apertura de modales le damos url del modal y id del mismo

    $(id).load(url, function() {});
    console.log("estoy en abrir modal");
}


/*script para colocar fecha actual en input de fechas*/
function fecha_actual() {
    var today = new Date().toISOString().split('T')[0];
    document.getElementById('fecha1').setAttribute('min', today);

}

/*script para evitar ingreso fin mayor a inicio*/
function fecha_minima() {

    var fecha1 = document.getElementById('fecha1');
    var fecha2 = document.getElementById('fecha2');
    if (fecha1.value == "") {
        document.getElementById('fecha2').value = "";
        Swal.fire({
            icon: 'error',
            title: 'No puede seleccionar Segunda Fecha',
            text: 'Primero debe cargar Fecha Inicio',
        });
        document.getElementById('fecha2').value = "";
    } else {

        fecha2.min = fecha1.value;
    }
}

function abrir_carrito(){
    console.log("carrito")
    location.href="/venta/vistaCarrito";
}