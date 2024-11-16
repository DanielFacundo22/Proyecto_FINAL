     
     
    //buscador por fecha
     document.addEventListener('DOMContentLoaded', function () {
        const fechaInput = document.getElementById('fecha_apertura');
        
        fechaInput.addEventListener('change', function () {
            const queryParams = new URLSearchParams(window.location.search);
            queryParams.set('fecha_apertura', fechaInput.value);
            window.location.search = queryParams.toString();
        });
    });

// modal cartel

document.addEventListener('DOMContentLoaded', function () {
    var modal = document.getElementById('modal');
    var closeBtn = document.querySelector('.close');

    // Verificar si el modal y el botón de cerrar existen
    if (modal && closeBtn) {
        // Mostrar modal si contiene mensajes
        if (modal.querySelector('p')) {
            modal.style.display = 'flex';
        }

        // Cerrar modal al hacer clic en la "x"
        closeBtn.addEventListener('click', function () {
            modal.style.display = 'none';
        });

        // Cerrar modal al hacer clic fuera del contenido
        window.addEventListener('click', function (event) {
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        });
    }
});
        // Actualiza los montos cada 10 segundos
        setInterval(() => {
            document.querySelectorAll('[id^="monto-final-"]').forEach(element => {
                const id_caja = element.id.split('-')[2];
                actualizarMontos(id_caja);
            });
        }, 10000);

