
function validarMontos() {
    var montoSistema = parseFloat(document.getElementById('monto_final_sistema').innerText.replace('$', '').replace(',', '').trim());
    var montoUsuario = parseFloat(document.getElementById('monto_final_usuario').value.trim());

    alert("Monto Sistema: " + montoSistema + "\nMonto Usuario: " + montoUsuario); // Línea de depuración

    if (isNaN(montoSistema) || isNaN(montoUsuario)) {
        alert('Por favor, ingrese valores válidos.');
        return false;
    }

    if (Math.abs(montoSistema - montoUsuario) > 0.01) {
        alert('El monto final según el sistema no coincide con el monto final según el usuario. Por favor, verifica los valores.');
        return false;
    }

    return true;
}