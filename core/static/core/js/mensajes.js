document.addEventListener('DOMContentLoaded', function() {
    // Inicializar el modal de Bootstrap
    var messageModal = new bootstrap.Modal(document.getElementById('messageModal'));
    var mensajes = document.querySelectorAll('#modalMessages .alert');

    // Configurar los iconos y el modal
    if (mensajes.length > 0) {
        //console.log("Hay mensajes. Mostrando modal.");

        // Obtener el primer mensaje para determinar el icono
        var firstMessage = mensajes[0];
        var messageType = firstMessage.classList.contains('alert-success') ? 'success' : 'error';

        var iconContainer = document.getElementById('modalIconContainer');
        var iconSvg = '';

        // Asignar el ícono adecuado basado en el tipo de mensaje
        if (messageType === 'success') {
            iconSvg = `
                <svg version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 130.2 130.2" style="width: 60px; height: 60px;">
                    <circle class="path circle" fill="none" stroke="#198754" stroke-width="6" stroke-miterlimit="10" cx="65.1" cy="65.1" r="62.1" />
                    <polyline class="path check" fill="none" stroke="#198754" stroke-width="6" stroke-linecap="round" stroke-miterlimit="10" points="100.2,40.2 51.5,88.8 29.8,67.5 " />
                </svg>
            `;
        } else if (messageType === 'error') {
            iconSvg = `
                <svg version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 130.2 130.2" style="width: 60px; height: 60px;">
                    <circle class="path circle" fill="none" stroke="#db3646" stroke-width="6" stroke-miterlimit="10" cx="65.1" cy="65.1" r="62.1" />
                    <line class="path line" fill="none" stroke="#db3646" stroke-width="6" stroke-linecap="round" stroke-miterlimit="10" x1="34.4" y1="37.9" x2="95.8" y2="92.3" />
                    <line class="path line" fill="none" stroke="#db3646" stroke-width="6" stroke-linecap="round" stroke-miterlimit="10" x1="95.8" y1="38" x2="34.4" y2="92.2" />
                </svg>
            `;
        }

        // Inyectar el icono en el contenedor del modal
        iconContainer.innerHTML = iconSvg;

        // Mostrar el modal usando Bootstrap
        messageModal.show();

        // Ocultar el modal después de 2.8 segundos
        setTimeout(function() {
            messageModal.hide();
        }, 2800);
    } else {
        //console.log("No hay mensajes.");
    }
});