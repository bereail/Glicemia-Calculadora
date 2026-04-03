document.addEventListener("DOMContentLoaded", function () {
    // ===== ELEMENTOS =====
    const glucemiaActual = document.querySelector('input[name="glicemia_actual"]');
    const glucemiaPrevia = document.querySelector('input[name="glicemia_previa"]');
    const terceraMedicion = document.querySelector('input[name="tercera_medicion"]');

    const infusionRadios = document.querySelectorAll('input[name="infusion_activa"]');
    const ajusteRadios = document.querySelectorAll('input[name="hubo_ajuste_insulina"]');

    const btnPrevia = document.getElementById("btn_previa");
    const previaContainer = document.getElementById("previa_container");
    const helperPrevia = document.getElementById("helper_previa");

    const ajusteContainer = document.getElementById("ajuste_container");
    const terceraContainer = document.getElementById("tercera_container");

    // NUEVO: botón para abrir tercera medición
    const btnTercera = document.getElementById("btn_tercera");
    const terceraBtnContainer = document.getElementById("tercera_btn_container");

    // Si faltan elementos clave, no romper el script
    if (!glucemiaActual || !btnPrevia || !previaContainer) {
        return;
    }


    // ===== FUNCIONES AUXILIARES =====
    function getInfusionActivaValue() {
        const selected = document.querySelector('input[name="infusion_activa"]:checked');
        return selected ? selected.value : "";
    }

    btnTercera.innerText = "Tercera medición activa";
    
    function getAjusteValue() {
        const selected = document.querySelector('input[name="hubo_ajuste_insulina"]:checked');
        return selected ? selected.value : "";
    }

    function getActualValue() {
        return parseInt(glucemiaActual.value, 10);
    }

    function getPreviaValue() {
        return glucemiaPrevia ? parseInt(glucemiaPrevia.value, 10) : NaN;
    }

    function getTerceraValue() {
        return terceraMedicion ? parseInt(terceraMedicion.value, 10) : NaN;
    }

    function limpiarRadios(radios) {
        if (!radios) return;
        radios.forEach((radio) => {
            radio.checked = false;
        });
    }

    function esHiperglucemiaPersistente() {
        const infusion = getInfusionActivaValue();
        const actual = getActualValue();
        const previa = getPreviaValue();

        return (
            infusion === "True" &&
            !isNaN(actual) && actual >= 180 &&
            !isNaN(previa) && previa >= 180
        );
    }

    function mostrarPrevia() {
        previaContainer.classList.remove("hidden");
        btnPrevia.classList.add("hidden");
    }

    function ocultarPreviaSiVaciaYNoNecesaria() {
        const infusion = getInfusionActivaValue();
        const actual = getActualValue();
        const previaTieneValor = glucemiaPrevia && glucemiaPrevia.value.trim() !== "";

        // Si ya hay valor cargado, no ocultar
        if (previaTieneValor) return;

        // Si hay infusión activa o glucemia alta, dejar visible
        if (infusion === "True" || (!isNaN(actual) && actual >= 180)) return;

        previaContainer.classList.add("hidden");
        btnPrevia.classList.remove("hidden");
    }

    function actualizarHelperPrevia() {
        if (!helperPrevia) return;

        const actual = getActualValue();
        const infusion = getInfusionActivaValue();

        helperPrevia.textContent = "";
        helperPrevia.classList.remove("helper-warning");

        if (isNaN(actual) || !infusion) return;

        if (infusion === "True") {
            helperPrevia.textContent = "La glucemia previa es obligatoria si hay infusión activa.";
            helperPrevia.classList.add("helper-warning");
            return;
        }

        if (actual >= 180) {
            helperPrevia.textContent = "Agregar glucemia previa ayuda a detectar hiperglucemia sostenida.";
            helperPrevia.classList.add("helper-warning");
            return;
        }

        if (actual > 70 && actual < 180 && infusion === "False") {
            helperPrevia.textContent = "La glucemia previa es opcional en este caso.";
        }
    }

    function actualizarEstadoVisualActual() {
        const valor = getActualValue();

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

    function ocultarBloqueTerceraCompleto() {
        if (terceraBtnContainer) {
            terceraBtnContainer.classList.add("hidden");
        }

        if (terceraContainer) {
            terceraContainer.classList.add("hidden");
        }

        if (terceraMedicion) {
            terceraMedicion.value = "";
        }
    }

    function ocultarAjusteCompleto() {
        if (ajusteContainer) {
            ajusteContainer.classList.add("hidden");
        }

        limpiarRadios(ajusteRadios);
    }

    function actualizarVisibilidadSegunActual() {
        const actual = getActualValue();

        if (!isNaN(actual) && actual >= 180) {
            mostrarPrevia();
        } else {
            ocultarPreviaSiVaciaYNoNecesaria();
        }
    }

    function actualizarVisibilidadSegunInfusion() {
        const infusion = getInfusionActivaValue();

        if (infusion === "True") {
            mostrarPrevia();
        } else {
            ocultarAjusteCompleto();
            ocultarBloqueTerceraCompleto();
            ocultarPreviaSiVaciaYNoNecesaria();
        }
    }

    function actualizarFlujoPersistente() {
        const persistente = esHiperglucemiaPersistente();

        // Estado base: todo oculto
        ocultarAjusteCompleto();

        if (terceraBtnContainer) {
            terceraBtnContainer.classList.add("hidden");
        }

        if (terceraContainer) {
            terceraContainer.classList.add("hidden");
        }

        // Si no cumple persistente, no mostrar nada extra
        if (!persistente) {
            if (terceraMedicion) {
                terceraMedicion.value = "";
            }
            return;
        }

        // Si cumple persistente, mostrar solo el botón
        if (terceraBtnContainer) {
            terceraBtnContainer.classList.remove("hidden");
        }

        // Si ya hay tercera cargada, mostrar el campo
        const tercera = getTerceraValue();
        if (!isNaN(tercera)) {
            if (terceraContainer) {
                terceraContainer.classList.remove("hidden");
            }

            // SOLO si la tercera es >= 200, preguntar ajuste
            if (tercera >= 200 && ajusteContainer) {
                ajusteContainer.classList.remove("hidden");
            }
        }
    }

    function inicializarVista() {
        actualizarEstadoVisualActual();
        actualizarHelperPrevia();
        actualizarVisibilidadSegunInfusion();
        actualizarVisibilidadSegunActual();
        actualizarFlujoPersistente();
    }

    // ===== EVENTOS =====
    btnPrevia.addEventListener("click", function () {
        mostrarPrevia();
    });

    if (btnTercera) {
        btnTercera.addEventListener("click", function () {
            if (terceraContainer) {
                terceraContainer.classList.remove("hidden");
            }
        });
    }

    glucemiaActual.addEventListener("input", function () {
        actualizarEstadoVisualActual();
        actualizarHelperPrevia();
        actualizarVisibilidadSegunActual();
        actualizarFlujoPersistente();
    });

    if (glucemiaPrevia) {
        glucemiaPrevia.addEventListener("input", function () {
            actualizarFlujoPersistente();
        });
    }

    if (terceraMedicion) {
        terceraMedicion.addEventListener("input", function () {
            const tercera = getTerceraValue();

            if (ajusteContainer) {
                if (!isNaN(tercera) && tercera >= 200) {
                    ajusteContainer.classList.remove("hidden");
                } else {
                    ocultarAjusteCompleto();
                }
            }
        });
    }

    infusionRadios.forEach((radio) => {
        radio.addEventListener("change", function () {
            actualizarHelperPrevia();
            actualizarVisibilidadSegunInfusion();
            actualizarFlujoPersistente();
        });
    });

    ajusteRadios.forEach((radio) => {
        radio.addEventListener("change", function () {
            // Por ahora no hace falta lógica extra acá,
            // pero lo dejamos listo por si después querés agregar validaciones.
        });
    });

    // ===== INICIO =====
    inicializarVista();
});


const btnTabla = document.getElementById("btn-tabla-algoritmos");
const modalTabla = document.getElementById("modal-tabla");
const btnCerrar = document.getElementById("btn-cerrar-tabla");
const backdrop = document.getElementById("cerrar-modal-tabla");

function abrirModal() {
    modalTabla.classList.remove("hidden");
}

function cerrarModal() {
    modalTabla.classList.add("hidden");
}

if (btnTabla) {
    btnTabla.addEventListener("click", abrirModal);
}

if (btnCerrar) {
    btnCerrar.addEventListener("click", cerrarModal);
}

if (backdrop) {
    backdrop.addEventListener("click", cerrarModal);
}

document.addEventListener("keydown", function(e) {
    if (e.key === "Escape") cerrarModal();
});