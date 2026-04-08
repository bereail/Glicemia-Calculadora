window.GlicemiaHipo = (function () {
    function esHipoglucemiaActual(ctx) {
        const actual = ctx.getActualValue();
        return !isNaN(actual) && actual <= 70;
    }

    function aplicarModoHipoglucemia(ctx) {
        // Ocultar flujo de hiperglucemia persistente
        ctx.resetearFlujoHiperglucemiaPersistente();

        // La previa queda opcional; si está vacía, se oculta para no cargar pantalla
        const previaTieneValor = ctx.glucemiaPrevia && ctx.glucemiaPrevia.value.trim() !== "";
        if (!previaTieneValor) {
            ctx.ocultarPrevia();
        }
    }

    function actualizarHelperHipoglucemia(ctx) {
        if (!ctx.helperPrevia) return;

        const actual = ctx.getActualValue();

        if (isNaN(actual)) return;

        if (actual <= 70) {
            ctx.helperPrevia.textContent =
                "Hipoglucemia: la glucemia previa e infusión quedan opcionales para este flujo.";
            ctx.helperPrevia.classList.remove("helper-warning");
        }
    }

    return {
        esHipoglucemiaActual,
        aplicarModoHipoglucemia,
        actualizarHelperHipoglucemia
    };
})();

document.addEventListener("DOMContentLoaded", function () {
  const btnAbrirTabla = document.getElementById("btn-tabla-algoritmos");
  const modalTabla = document.getElementById("modal-tabla");
  const btnCerrarTabla = document.getElementById("btn-cerrar-tabla");
  const backdropTabla = document.getElementById("cerrar-modal-tabla");

  if (btnAbrirTabla && modalTabla) {
    btnAbrirTabla.addEventListener("click", function () {
      modalTabla.classList.remove("hidden");
      modalTabla.setAttribute("aria-hidden", "false");
    });
  }

  function cerrarModalTabla() {
    if (modalTabla) {
      modalTabla.classList.add("hidden");
      modalTabla.setAttribute("aria-hidden", "true");
    }
  }

  if (btnCerrarTabla) {
    btnCerrarTabla.addEventListener("click", cerrarModalTabla);
  }

  if (backdropTabla) {
    backdropTabla.addEventListener("click", cerrarModalTabla);
  }

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      cerrarModalTabla();
    }
  });
});