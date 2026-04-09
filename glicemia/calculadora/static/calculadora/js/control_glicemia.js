document.addEventListener("DOMContentLoaded", function () {
  const inputActual = document.getElementById("id_glicemia_actual");
  const radiosInfusion = document.querySelectorAll('input[name="infusion_activa"]');

  const hipoHelperBox = document.getElementById("hipo_helper_box");
  const bloqueContexto = document.getElementById("bloque_contexto");
  const helperPreviaContainer = document.getElementById("helper_previa_container");
  const helperPrevia = document.getElementById("helper_previa");

  const previasBox = document.getElementById("previas_box");
  const anteriorContainer = document.getElementById("anterior_container");

  const labelPreviaHint = document.getElementById("label_previa_hint");

  const secuenciaMediciones = document.getElementById("secuencia_mediciones");
  const stepAnterior = document.getElementById("step-anterior");
  const stepPrevia = document.getElementById("step-previa");
  const stepActual = document.getElementById("step-actual");

  const arrowAnteriorPrevia = document.getElementById("arrow-anterior-previa");
  const arrowPreviaActual = document.getElementById("arrow-previa-actual");

  // TABLA DE ALGORITMOS
  const btnTablaAlgoritmos = document.getElementById("btn-tabla-algoritmos");
  const modalTablaAlgoritmos = document.getElementById("modal-tabla-algoritmos");
  const cerrarTablaAlgoritmos = document.getElementById("cerrar-tabla-algoritmos");

  function obtenerActual() {
    const valor = parseFloat(inputActual?.value);
    return Number.isFinite(valor) ? valor : null;
  }

  function infusionActiva() {
    const checked = document.querySelector('input[name="infusion_activa"]:checked');
    if (!checked) return null;

    const valor = checked.value.toLowerCase();
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

  function actualizarFormulario() {
    const actual = obtenerActual();
    const infusion = infusionActiva();

    resetSecuencia();

    if (actual === null) {
      ocultar(hipoHelperBox);
      ocultar(bloqueContexto);
      ocultar(helperPreviaContainer);
      ocultar(previasBox);
      ocultar(anteriorContainer);
      ocultar(secuenciaMediciones);
      return;
    }

    if (actual <= 70) {
      mostrar(hipoHelperBox);
      ocultar(bloqueContexto);
      ocultar(helperPreviaContainer);
      ocultar(previasBox);
      ocultar(anteriorContainer);
      ocultar(secuenciaMediciones);
      return;
    }

    ocultar(hipoHelperBox);
    mostrar(bloqueContexto);

    if (infusion === null) {
      ocultar(helperPreviaContainer);
      ocultar(previasBox);
      ocultar(anteriorContainer);
      ocultar(secuenciaMediciones);
      return;
    }

    mostrar(helperPreviaContainer);
    mostrar(previasBox);

    if (infusion) {
      if (helperPrevia) {
        helperPrevia.textContent = "La glicemia previa es obligatoria para evaluar tendencia.";
      }
      if (labelPreviaHint) {
        labelPreviaHint.textContent = "(obligatoria)";
      }

      if (actual > 200 && actual < 360) {
        mostrar(secuenciaMediciones);
        mostrar(anteriorContainer);
        secuenciaTresMediciones();
      } else {
        ocultar(secuenciaMediciones);
        ocultar(anteriorContainer);
        secuenciaDosMediciones(true);
      }
    } else {
      if (helperPrevia) {
        helperPrevia.textContent = "La glicemia previa ayuda a evaluar tendencia.";
      }
      if (labelPreviaHint) {
        labelPreviaHint.textContent = "(opcional)";
      }

      ocultar(anteriorContainer);
      ocultar(secuenciaMediciones);
      secuenciaDosMediciones(false);
    }
  }

  // EVENTOS TABLA DE ALGORITMOS
  if (btnTablaAlgoritmos && modalTablaAlgoritmos) {
    btnTablaAlgoritmos.addEventListener("click", function () {
      modalTablaAlgoritmos.classList.remove("hidden");
      modalTablaAlgoritmos.style.display = "flex";
    });
  }

  if (cerrarTablaAlgoritmos && modalTablaAlgoritmos) {
    cerrarTablaAlgoritmos.addEventListener("click", function () {
      modalTablaAlgoritmos.classList.add("hidden");
      modalTablaAlgoritmos.style.display = "none";
    });
  }

  if (modalTablaAlgoritmos) {
    modalTablaAlgoritmos.addEventListener("click", function (e) {
      if (e.target === modalTablaAlgoritmos) {
        modalTablaAlgoritmos.classList.add("hidden");
        modalTablaAlgoritmos.style.display = "none";
      }
    });
  }

  inputActual?.addEventListener("input", actualizarFormulario);
  radiosInfusion.forEach((r) => r.addEventListener("change", actualizarFormulario));

  actualizarFormulario();
});