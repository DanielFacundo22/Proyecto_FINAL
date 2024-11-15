     
     
    //buscador por fecha
     document.addEventListener('DOMContentLoaded', function () {
        const fechaInput = document.getElementById('fecha_apertura');
        
        fechaInput.addEventListener('change', function () {
            const queryParams = new URLSearchParams(window.location.search);
            queryParams.set('fecha_apertura', fechaInput.value);
            window.location.search = queryParams.toString();
        });
    });

        // Script para manejar la ventana modal
        var modal = document.getElementById("modal");
        var span = document.getElementsByClassName("close")[0];
    
        // Mostrar la ventana modal
        if (modal) {
            modal.style.display = "block";
        }
    
        // Cerrar la ventana modal cuando el usuario hace clic en <span> (x)
        if (span) {
            span.onclick = function () {
                modal.style.display = "none";
            }
        }
    
        // Cerrar la ventana modal cuando el usuario hace clic fuera de la ventana modal
        window.onclick = function (event) {
            if (event.target == modal) {
                modal.style.display = "none";
            }
        }
    
        function actualizarMontos(id_caja) {
            fetch(`/obtener_monto_final/${id_caja}/`)
                .then(response => response.json())
                .then(data => {
                    document.getElementById(`monto-final-${id_caja}`).innerText = `$${data.monto_final}`;
                });
        }
        // Actualiza los montos cada 10 segundos
        setInterval(() => {
            document.querySelectorAll('[id^="monto-final-"]').forEach(element => {
                const id_caja = element.id.split('-')[2];
                actualizarMontos(id_caja);
            });
        }, 10000);

