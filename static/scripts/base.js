let tiempoInactividadPermitido = 50000
let temporizador;

function resetearTemporizador() {
    clearTimeout(temporizador);
    temporizador = setTimeout(cerrarSesionPorInactividad, tiempoInactividadPermitido);
}

function cerrarSesionPorInactividad() {

    document.getElementById('logoutForm').submit();
}


window.onload = resetearTemporizador;
document.onmousemove = resetearTemporizador;
document.onkeypress = resetearTemporizador;
document.onclick = resetearTemporizador;
document.onscroll = resetearTemporizador;


