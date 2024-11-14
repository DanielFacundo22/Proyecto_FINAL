document.addEventListener('DOMContentLoaded', function () {
    function setCurrentDate() {
        const today = new Date();
        const dateString = today.toISOString().split('T')[0];
        document.getElementById('fecha_hs').value = dateString;
    }
    setCurrentDate();

    const actualizarTotal = () => {
        let total = 0;
        document.querySelectorAll('#tabla_compras .subtotal').forEach(subtotal => {
            total += parseFloat(subtotal.innerText);
        });
        document.getElementById('total').value = total.toFixed(2);
    };

    document.querySelectorAll('.agregar-producto').forEach(button => {
        button.addEventListener('click', function () {
            const idProducto = this.dataset.id;
            const nombreProducto = this.dataset.nombre;
            const precioCosto = parseFloat(this.dataset.precio).toFixed(2);
            const tbody = document.querySelector('#tabla_compras tbody');

            // Verificar si el producto ya está en la tabla
            let filaExistente = Array.from(tbody.querySelectorAll('input[name="producto_ids[]"]')).find(input => input.value === idProducto);
            if (filaExistente) {
                const fila = filaExistente.closest('tr');
                const cantidadInput = fila.querySelector('.cantidad');
                cantidadInput.value = parseInt(cantidadInput.value) + 1;
                fila.querySelector('.subtotal').innerText = (cantidadInput.value * precioCosto).toFixed(2);
                actualizarTotal();
                return;
            }

            // Crear una nueva fila de producto
            const fila = document.createElement('tr');
            fila.innerHTML = `
                <td>${nombreProducto} <input type="hidden" name="producto_ids[]" value="${idProducto}"></td>
                <td><input type="number" name="precios_costos[]" value="${precioCosto}" step="0.01" class="precio-costo"></td>
                <td><input type="number" name="cantidades[]" value="1" min="1" class="cantidad"></td>
                <td class="subtotal">${precioCosto}</td>
                <td><button type="button" class="btn btn-danger eliminar-producto">Eliminar</button></td>
            `;
            tbody.appendChild(fila);

            // Eventos para actualizar subtotal y total
            fila.querySelector('.cantidad').addEventListener('change', () => actualizarSubtotal(fila));
            fila.querySelector('.precio-costo').addEventListener('change', () => actualizarSubtotal(fila));
            fila.querySelector('.eliminar-producto').addEventListener('click', () => { fila.remove(); actualizarTotal(); });

            actualizarTotal();
        });
    });

    const actualizarSubtotal = fila => {
        const cantidad = parseInt(fila.querySelector('.cantidad').value);
        const precioCosto = parseFloat(fila.querySelector('.precio-costo').value);
        const subtotal = cantidad * precioCosto;
        fila.querySelector('.subtotal').innerText = subtotal.toFixed(2);
        actualizarTotal();
    };
});

document.addEventListener('DOMContentLoaded', function () {
    const buscarProducto = document.getElementById('buscarProducto');
    const listaProductos = document.getElementById('lista-productos');

    buscarProducto.addEventListener('keyup', function () {
        const texto = buscarProducto.value.toLowerCase();
        const filas = listaProductos.querySelectorAll('tr');

        filas.forEach(fila => {
            const descripcionProducto = fila.querySelector('td:nth-child(2)').textContent.toLowerCase();
            if (descripcionProducto.includes(texto)) {
                fila.style.display = '';
            } else {
                fila.style.display = 'none';
            }
        });
    });
});

