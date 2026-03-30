document.addEventListener("DOMContentLoaded", function () {
    // ===== ELEMENTOS =====
    const glucemiaActual = document.querySelector('input[name="glicemia_actual"]');
    const glucemiaPrevia = document.querySelector('input[name="glicemia_previa"]');

    const infusionRadios = document.querySelectorAll('input[name="infusion_activa"]');
    const ajusteRadios = document.querySelectorAll('input[name="hubo_ajuste_insulina"]');

    const btnPrevia = document.getElementById("btn_previa");
    const previaContainer = document.getElementById("previa_container");
    const helperPrevia = document.getElementById("helper_previa");

    const ajusteContainer = document.getElementById("ajuste_container");
    const terceraContainer = document.getElementById("tercera_container");

    // Si falta algo clave, no romper el script
    if (!glucemiaActual || !btnPrevia || !previaContainer) {
        return;
    }

    // ===== FUNCIONES =====
    function getInfusionActivaValue() {
        const selected = document.querySelector('input[name="infusion_activa"]:checked');
        return selected ? selected.value : "";
    }

    function getAjusteValue() {
        const selected = document.querySelector('input[name="hubo_ajuste_insulina"]:checked');
        return selected ? selected.value : "";
    }

    function mostrarPrevia() {
        previaContainer.classList.remove("hidden");
        btnPrevia.classList.add("hidden");
    }

    function ocultarPreviaSiVaciaYNoNecesaria() {
        const infusion = getInfusionActivaValue();
        const actual = parseInt(glucemiaActual.value, 10);
        const previaTieneValor = glucemiaPrevia && glucemiaPrevia.value.trim() !== "";

        // Si ya hay valor cargado, no ocultar
        if (previaTieneValor) return;

        // Si hay infusión activa o glucemia alta, conviene dejarla visible
        if (infusion === "si" || (!isNaN(actual) && actual >= 180)) return;

        previaContainer.classList.add("hidden");
        btnPrevia.classList.remove("hidden");
    }

    function actualizarHelperPrevia() {
        if (!helperPrevia) return;

        const actual = parseInt(glucemiaActual.value, 10);
        const infusion = getInfusionActivaValue();

        helperPrevia.textContent = "";
        helperPrevia.classList.remove("helper-warning");

        if (isNaN(actual) || !infusion) return;

        if (infusion === "si") {
            helperPrevia.textContent = "Se recomienda ingresar glucemia previa para evaluar tendencia y ajuste.";
            helperPrevia.classList.add("helper-warning");
            return;
        }

        if (actual >= 180) {
            helperPrevia.textContent = "Agregar glucemia previa ayuda a detectar hiperglucemia sostenida.";
            helperPrevia.classList.add("helper-warning");
            return;
        }

        if (actual > 70 && actual < 180 && infusion === "no") {
            helperPrevia.textContent = "La glucemia previa es opcional en este caso.";
        }
    }

    function actualizarEstadoVisualActual() {
        const valor = parseInt(glucemiaActual.value, 10);

        glucemiaActual.classList.remove("input-ok", "input-alert", "input-danger");

        if (isNaN(valor)) return;

        if (valor <= 70) {
            glucemiaActual.classList.add("input-danger");
        } else if (valor >= 180) {
            glucemiaActual.classList.add("input-alert");
        } else {
            glucemiaActual.classList.add("input-ok");
        }
    }

    function actualizarVisibilidadSegunInfusion() {
        const infusion = getInfusionActivaValue();

        if (infusion === "si") {
            mostrarPrevia();

            if (ajusteContainer) {
                ajusteContainer.classList.remove("hidden");
            }
        } else {
            if (ajusteContainer) {
                ajusteContainer.classList.add("hidden");
            }

            if (terceraContainer) {
                terceraContainer.classList.add("hidden");
            }

            ocultarPreviaSiVaciaYNoNecesaria();
        }
    }

    function actualizarVisibilidadSegunActual() {
        const actual = parseInt(glucemiaActual.value, 10);

        if (!isNaN(actual) && actual >= 180) {
            mostrarPrevia();
        } else {
            ocultarPreviaSiVaciaYNoNecesaria();
        }
    }

    function actualizarTerceraMedicion() {
        if (!terceraContainer) return;

        const infusion = getInfusionActivaValue();
        const ajuste = getAjusteValue();

        if (infusion === "si" && ajuste === "no") {
            terceraContainer.classList.remove("hidden");
        } else {
            terceraContainer.classList.add("hidden");
        }
    }

    function inicializarVista() {
        actualizarEstadoVisualActual();
        actualizarHelperPrevia();
        actualizarVisibilidadSegunInfusion();
        actualizarVisibilidadSegunActual();
        actualizarTerceraMedicion();
    }

    // ===== EVENTOS =====
    btnPrevia.addEventListener("click", function () {
        mostrarPrevia();
    });

    glucemiaActual.addEventListener("input", function () {
        actualizarEstadoVisualActual();
        actualizarHelperPrevia();
        actualizarVisibilidadSegunActual();
    });

    infusionRadios.forEach((radio) => {
        radio.addEventListener("change", function () {
            actualizarHelperPrevia();
            actualizarVisibilidadSegunInfusion();
            actualizarTerceraMedicion();
        });
    });

    ajusteRadios.forEach((radio) => {
        radio.addEventListener("change", function () {
            actualizarTerceraMedicion();
        });
    });

    // ===== INICIO =====
    inicializarVista();
});