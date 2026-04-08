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
    if (el) el.classList.remove("hidden");
  }

  function ocultar(el) {
    if (el) el.classList.add("hidden");
  }

  function resetSecuencia() {
    stepAnterior.className = "glicemia-secuencia__step glicemia-secuencia__step--muted";
    stepPrevia.className = "glicemia-secuencia__step";
    stepActual.className = "glicemia-secuencia__step glicemia-secuencia__step--active";

    stepAnterior.textContent = "Anterior (1)";
    stepPrevia.textContent = "Previa (2)";
    stepActual.textContent = "Actual (3)";

    arrowAnteriorPrevia?.classList.remove("hidden");
    arrowPreviaActual?.classList.remove("hidden");
  }

  function secuenciaDosMediciones() {
    resetSecuencia();

    stepAnterior.classList.add("hidden");
    arrowAnteriorPrevia?.classList.add("hidden");

    stepPrevia.className = "glicemia-secuencia__step glicemia-secuencia__step--required";
    stepActual.className = "glicemia-secuencia__step glicemia-secuencia__step--active";

    stepPrevia.textContent = "Previa (obligatoria)";
    stepActual.textContent = "Actual";
  }

  function secuenciaTresMediciones() {
    resetSecuencia();

    stepAnterior.classList.remove("hidden");
    arrowAnteriorPrevia?.classList.remove("hidden");

    stepAnterior.className = "glicemia-secuencia__step";
    stepPrevia.className = "glicemia-secuencia__step glicemia-secuencia__step--required";
    stepActual.className = "glicemia-secuencia__step glicemia-secuencia__step--active";
  }


 function actualizarFormulario() {
  const actual = obtenerActual();
  const infusion = infusionActiva();

  resetSecuencia();

  if (actual === null) {
    ocultar(hipoHelperBox);
    ocultar(bloqueContexto);
    ocultar(previasBox);
    ocultar(anteriorContainer);
    ocultar(secuenciaMediciones);
    return;
  }

  if (actual <= 70) {
    mostrar(hipoHelperBox);
    ocultar(bloqueContexto);
    ocultar(previasBox);
    ocultar(anteriorContainer);
    ocultar(secuenciaMediciones);
    return;
  }

  ocultar(hipoHelperBox);
  mostrar(bloqueContexto);

  if (infusion === null) {
    ocultar(previasBox);
    ocultar(anteriorContainer);
    ocultar(secuenciaMediciones);
    return;
  }

  mostrar(previasBox);

  if (infusion) {
    helperPrevia.textContent = "La glicemia previa es obligatoria para evaluar tendencia.";
    labelPreviaHint.textContent = "(obligatoria)";

    if (actual > 200) {
      mostrar(secuenciaMediciones);
    } else {
      ocultar(secuenciaMediciones);
    }

    if (actual > 200 && actual < 360) {
      mostrar(anteriorContainer);
      secuenciaTresMediciones();
    } else {
      ocultar(anteriorContainer);
      secuenciaDosMediciones();
    }

  } else {
    helperPrevia.textContent = "La glicemia previa ayuda a evaluar tendencia.";
    labelPreviaHint.textContent = "(opcional)";

    ocultar(anteriorContainer);

    if (actual > 200) {
      mostrar(secuenciaMediciones);
    } else {
      ocultar(secuenciaMediciones);
    }

    secuenciaDosMediciones();
  }
}

inputActual?.addEventListener("input", actualizarFormulario);
radiosInfusion.forEach(r => r.addEventListener("change", actualizarFormulario));

actualizarFormulario();
});