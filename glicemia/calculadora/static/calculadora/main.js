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

    function esHipoglucemiaActual() {
        const actual = getActualValue();
        return !isNaN(actual) && actual <= 70;
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

    function limpiarRadios(radios) {
        if (!radios) return;
        radios.forEach((radio) => {
            radio.checked = false;
        });
    }

    function mostrarPrevia() {
        previaContainer.classList.remove("hidden");
        btnPrevia.classList.add("hidden");
    }

    function ocultarPrevia() {
        previaContainer.classList.add("hidden");
        btnPrevia.classList.remove("hidden");
    }

    function limpiarPrevia() {
        if (glucemiaPrevia) {
            glucemiaPrevia.value = "";
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

    function resetearFlujoHiperglucemiaPersistente() {
        ocultarAjusteCompleto();
        ocultarBloqueTerceraCompleto();
    }

    function aplicarModoHipoglucemia() {
        // En hipoglucemia no molestamos con flujo de hiper persistente
        resetearFlujoHiperglucemiaPersistente();

        // La previa queda opcional; si está vacía, mejor ocultarla para no cargar la pantalla
        const previaTieneValor = glucemiaPrevia && glucemiaPrevia.value.trim() !== "";
        if (!previaTieneValor) {
            ocultarPrevia();
        }
    }

    function ocultarPreviaSiVaciaYNoNecesaria() {
        const infusion = getInfusionActivaValue();
        const actual = getActualValue();
        const previaTieneValor = glucemiaPrevia && glucemiaPrevia.value.trim() !== "";

        // Si es hipoglucemia, previa opcional y sin molestar
        if (!isNaN(actual) && actual <= 70) {
            if (!previaTieneValor) {
                ocultarPrevia();
            }
            return;
        }

        // Si ya hay valor cargado, no ocultar
        if (previaTieneValor) return;

        // Si hay infusión activa o glucemia alta, dejar visible
        if (infusion === "True" || (!isNaN(actual) && actual >= 180)) return;

        ocultarPrevia();
    }

    function actualizarHelperPrevia() {
        if (!helperPrevia) return;

        const actual = getActualValue();
        const infusion = getInfusionActivaValue();

        helperPrevia.textContent = "";
        helperPrevia.classList.remove("helper-warning");

        if (isNaN(actual)) return;

        if (actual <= 70) {
            helperPrevia.textContent = "Hipoglucemia: la glucemia previa e infusión quedan opcionales para este flujo.";
            return;
        }

        if (!infusion) return;

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

    function actualizarVisibilidadSegunActual() {
        const actual = getActualValue();

        if (isNaN(actual)) {
            ocultarPreviaSiVaciaYNoNecesaria();
            return;
        }

        // HIPOglicemia: no pedir nada extra
        if (actual <= 70) {
            aplicarModoHipoglucemia();
            return;
        }

        // HIPERglicemia: sugerir/mostrar previa
        if (actual >= 180) {
            mostrarPrevia();
            return;
        }

        // Rango intermedio
        ocultarPreviaSiVaciaYNoNecesaria();
    }

    function actualizarVisibilidadSegunInfusion() {
        const infusion = getInfusionActivaValue();
        const actual = getActualValue();

        // Si es hipoglucemia, ignorar infusión a nivel UX
        if (!isNaN(actual) && actual <= 70) {
            aplicarModoHipoglucemia();
            return;
        }

        if (infusion === "True") {
            mostrarPrevia();
        } else {
            ocultarAjusteCompleto();
            ocultarBloqueTerceraCompleto();
            ocultarPreviaSiVaciaYNoNecesaria();
        }
    }

    function actualizarFlujoPersistente() {
        const actual = getActualValue();

        // Si es hipoglucemia, jamás mostrar flujo de persistente
        if (!isNaN(actual) && actual <= 70) {
            resetearFlujoHiperglucemiaPersistente();
            return;
        }

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

            // Solo si la tercera es >= 200, preguntar ajuste
            if (tercera >= 200 && ajusteContainer) {
                ajusteContainer.classList.remove("hidden");
            }
        }
    }

    function inicializarTextos() {
        if (btnTercera) {
            btnTercera.innerText = "Tercera medición activa";
        }
    }

    function inicializarVista() {
        inicializarTextos();
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
        actualizarVisibilidadSegunInfusion();
        actualizarFlujoPersistente();
    });

    if (glucemiaPrevia) {
        glucemiaPrevia.addEventListener("input", function () {
            actualizarFlujoPersistente();
            actualizarHelperPrevia();
        });
    }

    if (terceraMedicion) {
        terceraMedicion.addEventListener("input", function () {
            const actual = getActualValue();

            // En hipoglucemia esto no debería intervenir
            if (!isNaN(actual) && actual <= 70) {
                ocultarAjusteCompleto();
                return;
            }

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
            actualizarVisibilidadSegunActual();
            actualizarFlujoPersistente();
        });
    });

    ajusteRadios.forEach((radio) => {
        radio.addEventListener("change", function () {
            // Reservado para lógica futura
            getAjusteValue();
        });
    });

    // ===== INICIO =====
    inicializarVista();
});


// ===== MODAL TABLA =====
const btnTabla = document.getElementById("btn-tabla-algoritmos");
const modalTabla = document.getElementById("modal-tabla");
const btnCerrar = document.getElementById("btn-cerrar-tabla");
const backdrop = document.getElementById("cerrar-modal-tabla");

function abrirModal() {
    if (modalTabla) {
        modalTabla.classList.remove("hidden");
    }
}

function cerrarModal() {
    if (modalTabla) {
        modalTabla.classList.add("hidden");
    }
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

document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
        cerrarModal();
    }
});