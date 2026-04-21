window.GlicemiaHipo = (function () {
  function esHipoglucemiaActual(ctx) {
    const actual = ctx.getActualValue();
    return Number.isFinite(actual) && actual < 70;
  }

  function aplicarModoHipoglucemia(ctx) {
    ctx.resetearFlujoAvanzado();

    ctx.ocultar(ctx.bloqueContextoSecundario);
    ctx.ocultar(ctx.helperPreviaContainer);
    ctx.ocultar(ctx.previasBox);
    ctx.ocultar(ctx.anteriorContainer);
    ctx.ocultar(ctx.algoritmoContainer);
    ctx.ocultar(ctx.ajusteInsulinaContainer);
    ctx.ocultar(ctx.horasDesdeInicioContainer);
    ctx.ocultar(ctx.estableContainer);
    ctx.ocultar(ctx.secuenciaMediciones);

    ctx.seleccionarAlgoritmo1PorDefecto();

    if (ctx.helperPrevia) {
      ctx.helperPrevia.textContent =
        "Hipoglucemia: la glicemia previa y la infusión quedan opcionales para este flujo.";
      ctx.helperPrevia.classList.remove("helper-warning");
    }
  }

  function actualizarHelperHipoglucemia(ctx) {
    if (!ctx.helperPrevia) return;

    const actual = ctx.getActualValue();
    if (!Number.isFinite(actual)) return;

    if (actual < 70) {
      ctx.helperPrevia.textContent =
        "Hipoglucemia: la glicemia previa y la infusión quedan opcionales para este flujo.";
      ctx.helperPrevia.classList.remove("helper-warning");
    }
  }

  return {
    esHipoglucemiaActual,
    aplicarModoHipoglucemia,
    actualizarHelperHipoglucemia,
  };
})();