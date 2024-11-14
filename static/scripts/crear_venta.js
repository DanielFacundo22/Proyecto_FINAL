// Confirmación de la venta
function ConfirmarVenta() {
    return confirm("¿Está seguro de confirmar la venta?");
}

document.addEventListener('DOMContentLoaded', function () {
    const tablaVenta = document.querySelector('#tabla-venta tbody');
    const totalInput = document.getElementById('total');

    function actualizarTotal() {
        let total = 0;
        tablaVenta.querySelectorAll('.subtotal').forEach(subtotal => {
            total += parseFloat(subtotal.textContent) || 0;
        });
        totalInput.value = total.toFixed(2);
    }

    function actualizarSubtotal(fila) {
        const cantidad = parseInt(fila.querySelector('.cantidad').value) || 1;
        const precio = parseFloat(fila.querySelector('.precio').textContent) || 0;

        const subtotal = cantidad * precio;
        fila.querySelector('.subtotal').textContent = subtotal.toFixed(2);

        fila.querySelector('input[name="cantidades[]"]').value = cantidad;
        fila.querySelector('input[name="subtotales[]"]').value = subtotal.toFixed(2);

        actualizarTotal();
    }

    document.querySelectorAll('.agregar-producto').forEach(button => {
        button.addEventListener('click', function () {
            const id = this.dataset.id;
            const nombre = this.dataset.nombre;
            const precio = parseFloat(this.dataset.precio).toFixed(2);

            let filaExistente = Array.from(tablaVenta.querySelectorAll('input[name="productos[]"]'))
                .find(input => input.value === id);

            if (filaExistente) {
                let fila = filaExistente.closest('tr');
                let cantidadInput = fila.querySelector('.cantidad');
                cantidadInput.value = parseInt(cantidadInput.value) + 1;

                actualizarSubtotal(fila);
            } else {
                let fila = document.createElement('tr');
                fila.innerHTML = `
                    <td>${nombre}</td>
                    <td class="precio">${precio}</td>
                    <td><input type="number" class="cantidad" value="1" min="1"></td>
                    <td class="subtotal">${precio}</td>
                    <input type="hidden" name="productos[]" value="${id}">
                    <input type="hidden" name="cantidades[]" value="1">
                    <input type="hidden" name="subtotales[]" value="${precio}">
                    <td><button type="button" class="btn btn-danger eliminar-producto">Eliminar</button></td>
                `;
                tablaVenta.appendChild(fila);

                fila.querySelector('.cantidad').addEventListener('input', () => actualizarSubtotal(fila));
                fila.querySelector('.eliminar-producto').addEventListener('click', function () {
                    fila.remove();
                    actualizarTotal();
                });
            }
            actualizarTotal();
        });
    });

    let hoy = new Date().toISOString("en-CA").split('T')[0];
    document.getElementById('fecha_hs').value = hoy;
});

