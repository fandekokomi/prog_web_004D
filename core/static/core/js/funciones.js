// Esperar a que el DOM esté completamente cargado
document.addEventListener("DOMContentLoaded", function() {
    // Función para obtener una cookie
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Función para establecer una cookie
    function setCookie(name, value, days) {
        var expires = "";
        if (days) {
            var date = new Date();
            date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
            expires = "; expires=" + date.toUTCString();
        }
        var secure = location.protocol === 'https:' ? "; Secure" : "";
        document.cookie = name + "=" + (value || "") + expires + "; path=/; SameSite=None" + secure;
    }

    // Función para habilitar/deshabilitar artista, producto o miembro
    function toggleHabilitado(tipo, id) {
        var baseUrl = window.location.origin;
        var url = `${baseUrl}/administradores/enable_or_disable_${tipo}/${id}/`;

        var csrfToken = getCookie('csrftoken');

        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            //console.log(data.message);
            var boton = document.querySelector(`button[data-id="${id}"][class*="toggle-${tipo}"]`);
            boton.classList.toggle('btn-success');
            boton.classList.toggle('btn-danger');
            boton.textContent = data.habilitado ? 'Habilitado' : 'Deshabilitado';
        })
        .catch(error => {
            //console.error('Error:', error);
        });
    }

    // Seleccionar todos los botones de eliminar con la clase eliminar-artista
    var botonesEliminarArtista = document.querySelectorAll('.eliminar-artista');
    botonesEliminarArtista.forEach(function(boton) {
        boton.addEventListener('click', function() {
            var url = boton.getAttribute('data-url');
            if (confirm("¿Estás seguro de que quieres eliminar este artista?")) {
                window.location.href = url;
            }
        });
    });

    // Seleccionar todos los botones de eliminar con la clase eliminar-producto
    var botonesEliminarProducto = document.querySelectorAll('.eliminar-producto');
    botonesEliminarProducto.forEach(function(boton) {
        boton.addEventListener('click', function() {
            var url = boton.getAttribute('data-url');
            if (confirm("¿Estás seguro de que quieres eliminar este producto?")) {
                window.location.href = url;
            }
        });
    });

    // Seleccionar todos los botones de eliminar con la clase carrito
    var botonesCarrito = document.querySelectorAll('.carrito');
    botonesCarrito.forEach(function(boton) {
        boton.addEventListener('click', function() {
            var url = boton.getAttribute('data-url');
            if (confirm("¿Estás seguro de que quieres eliminar este producto de tu carrito?")) {
                window.location.href = url;
            }
        });
    });

    // Seleccionar todos los botones de eliminar con la clase eliminar-miembro
    var botonesCarrito = document.querySelectorAll('.eliminar-miembro');
    botonesCarrito.forEach(function(boton) {
        boton.addEventListener('click', function() {
            var url = boton.getAttribute('data-url');
            if (confirm("¿Estás seguro de que quieres eliminar a este miembro?")) {
                window.location.href = url;
            }
        });
    });

    // Seleccionar todos los botones de habilitar/deshabilitar artistas con la clase toggle-artista
    var botonesToggleArtista = document.querySelectorAll('.toggle-artista');
    botonesToggleArtista.forEach(function(boton) {
        boton.addEventListener('click', function() {
            var artistaId = boton.getAttribute('data-id');
            toggleHabilitado('artista', artistaId);
        });
    });

    // Seleccionar todos los botones de habilitar/deshabilitar productos con la clase toggle-producto
    var botonesToggleProducto = document.querySelectorAll('.toggle-producto');
    botonesToggleProducto.forEach(function(boton) {
        boton.addEventListener('click', function() {
            var productoId = boton.getAttribute('data-id');
            toggleHabilitado('producto', productoId);
        });
    });

    // Seleccionar todos los botones de habilitar/deshabilitar productos con la clase toggle-miembro
    var botonesToggleProducto = document.querySelectorAll('.toggle-miembro');
    botonesToggleProducto.forEach(function(boton) {
        boton.addEventListener('click', function() {
            var miembroId = boton.getAttribute('data-id');
            toggleHabilitado('miembro', miembroId);
        });
    });

    // Seleccionar el botón de eliminar imagen de artista
    var botonesEliminarImagenArtista = document.querySelectorAll('.eliminar_imagen_artista');
    botonesEliminarImagenArtista.forEach(function(boton) {
        boton.addEventListener('click', function() {
            var artistaId = boton.getAttribute('data-id');
            var url = `/administradores/quitarimg-a/${artistaId}/`;
            if (confirm("¿Estás seguro de que quieres eliminar la imagen del artista?")) {
                window.location.href = url;
            }
        });
    });

    // Obtén el botón y el elemento HTML
    var themeButton = document.getElementById('themeButton');
    //console.log("themeButton:", themeButton); // Log para depuración
    var htmlTag = document.getElementsByTagName('html')[0];

    // Comprueba si ya hay un tema guardado en las cookies
    var theme = getCookie('theme');
    //console.log("Tema actual desde cookie:", theme); // Log para depuración
    if (theme) {
        htmlTag.setAttribute('data-bs-theme', theme);
    } else {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            htmlTag.setAttribute('data-bs-theme', 'dark');
        } else {
            htmlTag.setAttribute('data-bs-theme', 'light');
        }
    }

    // Cambia el tema cuando se hace clic en el botón
    themeButton.onclick = function() {
        //console.log("Botón de cambio de tema clicado"); // Log para depuración
        var currentTheme = htmlTag.getAttribute('data-bs-theme');
        var newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        htmlTag.setAttribute('data-bs-theme', newTheme);
        setCookie('theme', newTheme, 365);
        //console.log("Nuevo tema establecido:", newTheme); // Log para depuración
    }
});