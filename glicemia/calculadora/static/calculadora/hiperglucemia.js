window.GlicemiaHiper = (function () {
  function requiereAlgoritmo(ctx) {
    const actual = ctx.getActualValue();
    const infusion = ctx.getInfusionActiva();
    return infusion === true && Number.isFinite(actual) && actual >= 120;
  }

  function requiereTerceraMedicion(ctx) {
    const actual = ctx.getActualValue();
    const infusion = ctx.getInfusionActiva();
    return infusion === true && Number.isFinite(actual) && actual > 200 && actual < 360;
  }

  function requiereAjuste(ctx) {
    const actual = ctx.getActualValue();
    const infusion = ctx.getInfusionActiva();
    return infusion === true && Number.isFinite(actual) && actual > 200;
  }

  function requiereContextoControl(ctx) {
    const actual = ctx.getActualValue();
    const infusion = ctx.getInfusionActiva();
    return infusion === true && Number.isFinite(actual) && actual >= 140;
  }

  function aplicarModoHiperglucemia(ctx) {
    const actual = ctx.getActualValue();
    const infusion = ctx.getInfusionActiva();

    if (infusion !== true || !Number.isFinite(actual)) {
      return;
    }

    ctx.mostrar(ctx.helperPreviaContainer);
    ctx.mostrar(ctx.previasBox);

    if (ctx.helperPrevia) {
      ctx.helperPrevia.textContent =
        "Con infusión activa, la glicemia previa es obligatoria para evaluar tendencia.";
    }

    if (requiereAlgoritmo(ctx)) {
      ctx.mostrar(ctx.algoritmoContainer);
    } else {
      ctx.ocultar(ctx.algoritmoContainer);
      ctx.seleccionarAlgoritmo1PorDefecto();
    }

    if (requiereTerceraMedicion(ctx)) {
      ctx.mostrar(ctx.secuenciaMediciones);
      ctx.mostrar(ctx.anteriorContainer);
      ctx.secuenciaTresMediciones();
    } else {
      ctx.ocultar(ctx.secuenciaMediciones);
      ctx.ocultar(ctx.anteriorContainer);
      ctx.secuenciaDosMediciones(true);
    }

    if (requiereAjuste(ctx)) {
      ctx.mostrar(ctx.ajusteInsulinaContainer);
    } else {
      ctx.ocultar(ctx.ajusteInsulinaContainer);
      ctx.limpiarRadios("hubo_ajuste_insulina");
    }

    if (requiereContextoControl(ctx)) {
      ctx.mostrar(ctx.horasDesdeInicioContainer);
      ctx.mostrar(ctx.estableContainer);
    } else {
      ctx.ocultar(ctx.horasDesdeInicioContainer);
      ctx.ocultar(ctx.estableContainer);
      ctx.limpiarInput(ctx.horasDesdeInicioInput);
      ctx.limpiarRadios("estable");
    }
  }

  return {
    requiereAlgoritmo,
    requiereTerceraMedicion,
    requiereAjuste,
    requiereContextoControl,
    aplicarModoHiperglucemia,
  };
})();