document.addEventListener("DOMContentLoaded", function () {
    // Fetch para obtener los datos desde la vista de Django
    fetch("{% url 'ventas_del_mes' %}")
        .then(response => response.json())
        .then(data => {
            const ctx = document.getElementById('ventasChart').getContext('2d');
            const ventasChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Ventas',
                        data: data.data,
                        borderColor: 'rgba(54, 162, 235, 1)',
                        backgroundColor: 'rgba(54, 162, 235, 0.2)',
                        borderWidth: 8
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        })
        .catch(error => console.error('Error al cargar los datos:', error));
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


