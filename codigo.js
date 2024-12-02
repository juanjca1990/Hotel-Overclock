function validate() {
    var num1 = document.getElementById("usuario");
    var num2 = document.getElementById("clave");
    if (num1.value != "" && num2.value != "") {
        if (num1.value == num2.value) {
            return true;
        }
    }
    alert("Los campos cara de pija deben ser iguales y no deben estar vacios")
    return false;
}