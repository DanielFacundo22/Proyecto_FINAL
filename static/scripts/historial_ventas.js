document.addEventListener('DOMContentLoaded', function () {
    const buscarClienteInput = document.querySelector('input[name="buscar_cliente"]');
    const fechaInicioInput = document.querySelector('input[name="fecha_inicio"]');
    const fechaFinInput = document.querySelector('input[name="fecha_fin"]');
    const tablaVentas = document.querySelector('#pa_tabla_historial_ventas tbody');
    const limpiarFiltrosBtn = document.getElementById('btn_limpiar_filtros');

    document.querySelector('#pa_filtros_ventas form').addEventListener('submit', function (e) {
        e.preventDefault();

        const buscarTexto = buscarClienteInput.value.toLowerCase();
        const fechaInicio = fechaInicioInput.value ? new Date(fechaInicioInput.value) : null;
        const fechaFin = fechaFinInput.value ? new Date(fechaFinInput.value) : null;

        const filas = tablaVentas.querySelectorAll('tr');

        filas.forEach(fila => {
            const cliente = fila.querySelector('td:nth-child(2)').textContent.toLowerCase();
            const fechaVenta = new Date(fila.querySelector('td:nth-child(1)').textContent);

            let visible = true;

            if (buscarTexto && !cliente.includes(buscarTexto)) {
                visible = false;
            }

            if (fechaInicio && fechaVenta < fechaInicio) {
                visible = false;
            }

            if (fechaFin && fechaVenta > fechaFin) {
                visible = false;
            }

            fila.style.display = visible ? '' : 'none';
        });
    });

    // Limpiar filtros
    limpiarFiltrosBtn.addEventListener('click', function () {
        buscarClienteInput.value = '';
        fechaInicioInput.value = '';
        fechaFinInput.value = '';

        const filas = tablaVentas.querySelectorAll('tr');
        filas.forEach(fila => {
            fila.style.display = '';
        });
    });
});
