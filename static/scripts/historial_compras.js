document.addEventListener('DOMContentLoaded', function () {
    const fechaInicioInput = document.getElementById('fecha_inicio');
    const fechaFinInput = document.getElementById('fecha_fin');
    const tablaCompras = document.querySelector('.table tbody');
    const limpiarFiltrosBtn = document.getElementById('btn_limpiar_filtros');

    document.querySelector('#filtros_compras form').addEventListener('submit', function (e) {
        e.preventDefault();

        const fechaInicio = fechaInicioInput.value ? new Date(fechaInicioInput.value) : null;
        const fechaFin = fechaFinInput.value ? new Date(fechaFinInput.value) : null;

        const filas = tablaCompras.querySelectorAll('tr');

        filas.forEach(fila => {
            const fechaCompra = new Date(fila.querySelector('td:nth-child(1)').textContent);

            let visible = true;

            if (fechaInicio && fechaCompra < fechaInicio) {
                visible = false;
            }

            if (fechaFin && fechaCompra > fechaFin) {
                visible = false;
            }

            fila.style.display = visible ? '' : 'none';
        });
    });

    // Limpiar filtros
    limpiarFiltrosBtn.addEventListener('click', function () {
        fechaInicioInput.value = '';
        fechaFinInput.value = '';

        const filas = tablaCompras.querySelectorAll('tr');
        filas.forEach(fila => {
            fila.style.display = '';
        });
    });
});
