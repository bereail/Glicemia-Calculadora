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