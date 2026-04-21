document.addEventListener("DOMContentLoaded", function () {
  const inputActual = document.getElementById("id_glicemia_actual");
  const radiosInfusion = document.querySelectorAll('input[name="infusion_activa"]');

  const hipoHelperBox = document.getElementById("hipo_helper_box");
  const bloqueContexto = document.getElementById("bloque_contexto");

  const helperPreviaContainer = document.getElementById("helper_previa_container");
  const helperPrevia = document.getElementById("helper_previa");

  const previasBox = document.getElementById("previas_box");
  const anteriorContainer = document.getElementById("anterior_container");
  const algoritmoContainer = document.getElementById("algoritmo_container");
  const ajusteInsulinaContainer = document.getElementById("ajuste_insulina_container");
  const horasDesdeInicioContainer = document.getElementById("horas_desde_inicio_container");
  const estableContainer = document.getElementById("estable_container");

  const glicemiaPreviaInput = document.getElementById("id_glicemia_previa");
  const terceraMedicionInput = document.getElementById("id_tercera_medicion");
  const horasDesdeInicioInput = document.getElementById("id_horas_desde_inicio");

  const labelPreviaHint = document.getElementById("label_previa_hint");

  const secuenciaMediciones = document.getElementById("secuencia_mediciones");
  const stepAnterior = document.getElementById("step-anterior");
  const stepPrevia = document.getElementById("step-previa");
  const stepActual = document.getElementById("step-actual");
  const arrowAnteriorPrevia = document.getElementById("arrow-anterior-previa");
  const arrowPreviaActual = document.getElementById("arrow-previa-actual");

  const btnTablaAlgoritmos = document.getElementById("btn-tabla-algoritmos");
  const modalTabla = document.getElementById("modal-tabla");
  const cerrarModalTablaBackdrop = document.getElementById("cerrar-modal-tabla");
  const btnCerrarTabla = document.getElementById("btn-cerrar-tabla");

  const modalResultado = document.getElementById("modal-resultado");
  const cerrarModalResultado = document.getElementById("cerrar-modal-resultado");

  const ctx = {
    hipoHelperBox,
    bloqueContextoSecundario: bloqueContexto,
    helperPreviaContainer,
    helperPrevia,
    previasBox,
    anteriorContainer,
    algoritmoContainer,
    ajusteInsulinaContainer,
    horasDesdeInicioContainer,
    estableContainer,
    secuenciaMediciones,
    glicemiaPrevia: glicemiaPreviaInput,
    terceraMedicionInput,
    horasDesdeInicioInput,

    getActualValue,
    getInfusionActiva,
    mostrar,
    ocultar,
    seleccionarAlgoritmo1PorDefecto,
    resetearFlujoAvanzado,
    secuenciaDosMediciones,
    secuenciaTresMediciones,
    limpiarRadios,
    limpiarInput,
  };

  function getActualValue() {
    const valor = parseFloat(inputActual?.value);
    return Number.isFinite(valor) ? valor : null;
  }

  function getInfusionActiva() {
    const checked = document.querySelector('input[name="infusion_activa"]:checked');
    if (!checked) return null;

    const valor = String(checked.value).trim().toLowerCase();
    return valor === "true" || valor === "1" || valor === "si" || valor === "sí";
  }

  function mostrar(el) {
    if (!el) return;
    el.classList.remove("hidden");
    el.style.display = "";
  }

  function ocultar(el) {
    if (!el) return;
    el.classList.add("hidden");
    el.style.display = "none";
  }

  function limpiarInput(input) {
    if (input) input.value = "";
  }

  function limpiarRadios(name) {
    document.querySelectorAll(`input[name="${name}"]`).forEach((radio) => {
      radio.checked = false;
    });
  }

  function seleccionarAlgoritmo1PorDefecto() {
    const algoritmo1 = document.querySelector(
      'input[name="algoritmo_activo"][value="1"]'
    );
    if (algoritmo1) {
      algoritmo1.checked = true;
    }
  }

  function abrirModalTabla() {
    if (!modalTabla) return;
    modalTabla.classList.remove("hidden");
    modalTabla.setAttribute("aria-hidden", "false");
    document.body.classList.add("modal-open");
  }

  function cerrarModalTabla() {
    if (!modalTabla) return;
    modalTabla.classList.add("hidden");
    modalTabla.setAttribute("aria-hidden", "true");
    document.body.classList.remove("modal-open");
  }

  function abrirModalResultado() {
    if (!modalResultado) return;
    modalResultado.classList.remove("hidden");
    modalResultado.setAttribute("aria-hidden", "false");
    document.body.classList.add("modal-open");
  }

  function cerrarModalResultadoFn() {
    if (!modalResultado) return;
    modalResultado.classList.add("hidden");
    modalResultado.setAttribute("aria-hidden", "true");
    document.body.classList.remove("modal-open");
  }

  function resetSecuencia() {
    if (stepAnterior) {
      stepAnterior.className = "glicemia-secuencia__step glicemia-secuencia__step--muted";
      stepAnterior.textContent = "Anterior (1)";
      stepAnterior.classList.remove("hidden");
      stepAnterior.style.display = "";
    }

    if (stepPrevia) {
      stepPrevia.className = "glicemia-secuencia__step";
      stepPrevia.textContent = "Previa (2)";
      stepPrevia.classList.remove("hidden");
      stepPrevia.style.display = "";
    }

    if (stepActual) {
      stepActual.className = "glicemia-secuencia__step glicemia-secuencia__step--active";
      stepActual.textContent = "Actual (3)";
      stepActual.classList.remove("hidden");
      stepActual.style.display = "";
    }

    if (arrowAnteriorPrevia) {
      arrowAnteriorPrevia.classList.remove("hidden");
      arrowAnteriorPrevia.style.display = "";
    }

    if (arrowPreviaActual) {
      arrowPreviaActual.classList.remove("hidden");
      arrowPreviaActual.style.display = "";
    }
  }

  function secuenciaDosMediciones(obligatoria = true) {
    resetSecuencia();

    if (stepAnterior) {
      stepAnterior.classList.add("hidden");
      stepAnterior.style.display = "none";
    }

    if (arrowAnteriorPrevia) {
      arrowAnteriorPrevia.classList.add("hidden");
      arrowAnteriorPrevia.style.display = "none";
    }

    if (stepPrevia) {
      stepPrevia.className = obligatoria
        ? "glicemia-secuencia__step glicemia-secuencia__step--required"
        : "glicemia-secuencia__step";
      stepPrevia.textContent = obligatoria ? "Previa (obligatoria)" : "Previa";
      stepPrevia.style.display = "";
    }

    if (stepActual) {
      stepActual.className = "glicemia-secuencia__step glicemia-secuencia__step--active";
      stepActual.textContent = "Actual";
      stepActual.style.display = "";
    }
  }

  function secuenciaTresMediciones() {
    resetSecuencia();

    if (stepAnterior) {
      stepAnterior.className = "glicemia-secuencia__step";
      stepAnterior.textContent = "Anterior (1)";
      stepAnterior.classList.remove("hidden");
      stepAnterior.style.display = "";
    }

    if (arrowAnteriorPrevia) {
      arrowAnteriorPrevia.classList.remove("hidden");
      arrowAnteriorPrevia.style.display = "";
    }

    if (stepPrevia) {
      stepPrevia.className = "glicemia-secuencia__step glicemia-secuencia__step--required";
      stepPrevia.textContent = "Previa (2)";
      stepPrevia.style.display = "";
    }

    if (stepActual) {
      stepActual.className = "glicemia-secuencia__step glicemia-secuencia__step--active";
      stepActual.textContent = "Actual (3)";
      stepActual.style.display = "";
    }
  }

  function resetearFlujoAvanzado() {
    ocultar(previasBox);
    ocultar(anteriorContainer);
    ocultar(algoritmoContainer);
    ocultar(ajusteInsulinaContainer);
    ocultar(horasDesdeInicioContainer);
    ocultar(estableContainer);
    ocultar(secuenciaMediciones);

    limpiarInput(glicemiaPreviaInput);
    limpiarInput(terceraMedicionInput);
    limpiarInput(horasDesdeInicioInput);
    limpiarRadios("hubo_ajuste_insulina");
    limpiarRadios("estable");
    seleccionarAlgoritmo1PorDefecto();
  }

  function actualizarFormulario() {
    const actual = getActualValue();
    const infusion = getInfusionActiva();

    resetSecuencia();

    if (actual === null) {
      ocultar(hipoHelperBox);
      ocultar(bloqueContexto);
      ocultar(helperPreviaContainer);
      resetearFlujoAvanzado();
      return;
    }

    if (window.GlicemiaHipo?.esHipoglucemiaActual(ctx)) {
      mostrar(hipoHelperBox);
      ocultar(bloqueContexto);
      window.GlicemiaHipo.aplicarModoHipoglucemia(ctx);
      window.GlicemiaHipo.actualizarHelperHipoglucemia(ctx);
      return;
    }

    ocultar(hipoHelperBox);
    mostrar(bloqueContexto);

    if (infusion === null) {
      ocultar(helperPreviaContainer);
      resetearFlujoAvanzado();
      return;
    }

    mostrar(helperPreviaContainer);
    mostrar(previasBox);

    if (infusion) {
      if (helperPrevia) {
        helperPrevia.textContent =
          "Con infusión activa, la glicemia previa es obligatoria para evaluar tendencia.";
      }

      if (labelPreviaHint) {
        labelPreviaHint.textContent = "(obligatoria)";
      }

      if (window.GlicemiaHiper) {
        window.GlicemiaHiper.aplicarModoHiperglucemia(ctx);
      } else {
        // fallback mínimo
        if (actual >= 120) mostrar(algoritmoContainer);
        if (actual > 200 && actual < 360) {
          mostrar(secuenciaMediciones);
          mostrar(anteriorContainer);
          secuenciaTresMediciones();
        } else {
          ocultar(secuenciaMediciones);
          ocultar(anteriorContainer);
          secuenciaDosMediciones(true);
        }
      }

      return;
    }

    // Sin infusión
    if (helperPrevia) {
      helperPrevia.textContent = "La glicemia previa ayuda a evaluar tendencia.";
    }

    if (labelPreviaHint) {
      labelPreviaHint.textContent = "(opcional)";
    }

    ocultar(anteriorContainer);
    ocultar(algoritmoContainer);
    ocultar(ajusteInsulinaContainer);
    ocultar(horasDesdeInicioContainer);
    ocultar(estableContainer);
    ocultar(secuenciaMediciones);

    limpiarInput(terceraMedicionInput);
    limpiarInput(horasDesdeInicioInput);
    limpiarRadios("hubo_ajuste_insulina");
    limpiarRadios("estable");
    seleccionarAlgoritmo1PorDefecto();

    secuenciaDosMediciones(false);
  }

  // Modal tabla
  if (btnTablaAlgoritmos) {
    btnTablaAlgoritmos.addEventListener("click", abrirModalTabla);
  }

  if (cerrarModalTablaBackdrop) {
    cerrarModalTablaBackdrop.addEventListener("click", cerrarModalTabla);
  }

  if (btnCerrarTabla) {
    btnCerrarTabla.addEventListener("click", cerrarModalTabla);
  }

  // Modal resultado
  if (cerrarModalResultado) {
    cerrarModalResultado.addEventListener("click", cerrarModalResultadoFn);
  }

  document.querySelectorAll("[data-close-resultado]").forEach((el) => {
    el.addEventListener("click", cerrarModalResultadoFn);
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      if (modalTabla && !modalTabla.classList.contains("hidden")) {
        cerrarModalTabla();
      }

      if (modalResultado && !modalResultado.classList.contains("hidden")) {
        cerrarModalResultadoFn();
      }
    }
  });

  // Enter envía formulario
  document.getElementById("form-glicemia")?.addEventListener("keydown", function (e) {
    if (e.key === "Enter") {
      const tag = document.activeElement.tagName.toLowerCase();
      if (tag === "textarea") return;
      e.preventDefault();
      this.requestSubmit();
    }
  });

  // Eventos
  inputActual?.addEventListener("input", actualizarFormulario);
  radiosInfusion.forEach((radio) => {
    radio.addEventListener("change", actualizarFormulario);
  });

  // Abrir modal resultado si hay contenido
  const bodyResultado = modalResultado?.querySelector(".modal-resultado__body");
  if (bodyResultado && bodyResultado.textContent.trim() !== "") {
    abrirModalResultado();
  }

  actualizarFormulario();
});