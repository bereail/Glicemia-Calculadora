document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("form-glicemia");

  const glicemiaInput = document.getElementById("id_glicemia_actual");
  const hipoBox = document.getElementById("hipo_helper_box");
  const bloqueContexto = document.getElementById("bloque_contexto");

  const helperPreviaContainer = document.getElementById("helper_previa_container");
  const helperPrevia = document.getElementById("helper_previa");

  const previasBox = document.getElementById("previas_box");
  const anteriorContainer = document.getElementById("anterior_container");
  const labelPreviaHint = document.getElementById("label_previa_hint");

  const secuencia = document.getElementById("secuencia_mediciones");
  const stepAnterior = document.getElementById("step-anterior");
  const stepPrevia = document.getElementById("step-previa");
  const stepActual = document.getElementById("step-actual");

  const infusionRadios = document.querySelectorAll('input[name="infusion_activa"]');

  const btnVerAlgoritmo = document.getElementById("btn-ver-algoritmo");
  const modalAlgoritmo = document.getElementById("modal-algoritmo");
  const cerrarModal = document.getElementById("cerrar-modal");

  function getInfusion() {
    for (const radio of infusionRadios) {
      if (radio.checked) {
        return radio.value === "True";
      }
    }
    return null;
  }

  function limpiarSeleccionInfusion() {
    infusionRadios.forEach(radio => {
      radio.checked = false;
      radio.required = false;
    });
  }

  function marcarInfusionComoObligatoria() {
    infusionRadios.forEach(radio => {
      radio.required = true;
    });
  }

  function resetSecuencia() {
    secuencia.classList.add("hidden");

    stepAnterior.classList.add("glicemia-secuencia__step--muted");
    stepAnterior.classList.remove("glicemia-secuencia__step--active");

    stepPrevia.classList.remove("glicemia-secuencia__step--active");
    stepActual.classList.add("glicemia-secuencia__step--active");
  }

  function activarSecuenciaPreviaActual() {
    secuencia.classList.remove("hidden");

    stepAnterior.classList.add("glicemia-secuencia__step--muted");
    stepAnterior.classList.remove("glicemia-secuencia__step--active");

    stepPrevia.classList.add("glicemia-secuencia__step--active");
    stepActual.classList.add("glicemia-secuencia__step--active");
  }

  function activarSecuenciaCompleta() {
    secuencia.classList.remove("hidden");

    stepAnterior.classList.remove("glicemia-secuencia__step--muted");
    stepAnterior.classList.add("glicemia-secuencia__step--active");

    stepPrevia.classList.add("glicemia-secuencia__step--active");
    stepActual.classList.add("glicemia-secuencia__step--active");
  }

  function resetUI() {
    hipoBox.classList.add("hidden");
    bloqueContexto.classList.add("hidden");
    helperPreviaContainer.classList.add("hidden");
    previasBox.classList.add("hidden");
    anteriorContainer.classList.add("hidden");

    helperPrevia.innerText = "";
    labelPreviaHint.innerText = "(opcional)";
    resetSecuencia();
  }

  function mostrarSoloPrevia(texto, obligatoria = false, mostrarSecuencia = false) {
    helperPreviaContainer.classList.remove("hidden");
    previasBox.classList.remove("hidden");
    anteriorContainer.classList.add("hidden");

    helperPrevia.innerText = texto;
    labelPreviaHint.innerText = obligatoria ? "(obligatoria)" : "(opcional)";

    if (mostrarSecuencia) {
      activarSecuenciaPreviaActual();
    }
  }

  function mostrarPreviaYAnterior(texto, previaObligatoria = true) {
    helperPreviaContainer.classList.remove("hidden");
    previasBox.classList.remove("hidden");
    anteriorContainer.classList.remove("hidden");

    helperPrevia.innerText = texto;
    labelPreviaHint.innerText = previaObligatoria ? "(obligatoria)" : "(opcional)";
    activarSecuenciaCompleta();
  }

  function updateUI() {
    resetUI();

    const actual = parseInt(glicemiaInput.value, 10);
    const infusion = getInfusion();

    if (isNaN(actual)) {
      limpiarSeleccionInfusion();
      return;
    }

    if (actual <= 70) {
      hipoBox.classList.remove("hidden");
      limpiarSeleccionInfusion();
      return;
    }

    bloqueContexto.classList.remove("hidden");
    marcarInfusionComoObligatoria();

    if (infusion === null) {
      helperPreviaContainer.classList.remove("hidden");
      helperPrevia.innerText = "Primero indicá si el paciente tiene infusión activa.";
      return;
    }

    if (infusion === true) {
      if (actual >= 140 && actual <= 200) {
        mostrarSoloPrevia(
          "Con infusión activa, una glicemia entre 140 y 200 mg/dL se considera en objetivo. La glicemia previa es obligatoria para evaluar tendencia.",
          true,
          true
        );
        return;
      }

      if (actual >= 360) {
        mostrarSoloPrevia(
          "Ingrese la glicemia previa. Si la previa también es ≥ 360 mg/dL, corresponde hiperglucemia persistente.",
          true,
          true
        );
        return;
      }

      if (actual > 200 && actual < 360) {
        mostrarPreviaYAnterior(
          "La glicemia previa es obligatoria. Si también cuenta con una glicemia anterior, y las 3 mediciones son > 200 mg/dL y < 360 mg/dL dentro del mismo escalón, corresponde hiperglucemia persistente.",
          true
        );
        return;
      }

      mostrarSoloPrevia(
        "Ingrese la glicemia previa para evaluar tendencia y riesgo de descenso con infusión activa.",
        true,
        true
      );
      return;
    }

    if (infusion === false) {
      if (actual >= 180) {
        mostrarSoloPrevia(
          "La glicemia previa es opcional. Si la previa también es ≥ 180 mg/dL, corresponde hiperglucemia sostenida e inicio de insulinización.",
          false,
          true
        );
        return;
      }

      mostrarSoloPrevia(
        "La glicemia previa es opcional y sirve para evaluar tendencia.",
        false,
        true
      );
    }
  }

  if (form) {
    form.addEventListener("submit", function (e) {
      const actual = parseInt(glicemiaInput.value, 10);
      const infusion = getInfusion();

      if (!isNaN(actual) && actual > 70 && infusion === null) {
        e.preventDefault();
        bloqueContexto.classList.remove("hidden");
        helperPreviaContainer.classList.remove("hidden");
        helperPrevia.innerText = "Debés indicar si tiene infusión activa antes de evaluar.";
      }
    });
  }

  if (glicemiaInput) {
    glicemiaInput.addEventListener("input", updateUI);
  }

  infusionRadios.forEach(radio => {
    radio.addEventListener("change", updateUI);
  });

  if (btnVerAlgoritmo && modalAlgoritmo && cerrarModal) {
    btnVerAlgoritmo.addEventListener("click", function () {
      modalAlgoritmo.classList.remove("hidden");
    });

    cerrarModal.addEventListener("click", function () {
      modalAlgoritmo.classList.add("hidden");
    });

    modalAlgoritmo.addEventListener("click", function (e) {
      if (e.target === modalAlgoritmo) {
        modalAlgoritmo.classList.add("hidden");
      }
    });
  }

  updateUI();
});


document.addEventListener("DOMContentLoaded", function () {
  const btnAbrir = document.getElementById("btn-tabla-algoritmos");
  const modal = document.getElementById("modal-tabla");
  const btnCerrar = document.getElementById("btn-cerrar-tabla");
  const backdrop = document.getElementById("cerrar-modal-tabla");

  if (!btnAbrir || !modal) return;

  // ABRIR
  btnAbrir.addEventListener("click", () => {
    modal.classList.remove("hidden");
    modal.setAttribute("aria-hidden", "false");
  });

  // CERRAR (botón X)
  if (btnCerrar) {
    btnCerrar.addEventListener("click", () => {
      modal.classList.add("hidden");
      modal.setAttribute("aria-hidden", "true");
    });
  }

  // CERRAR (click fondo)
  if (backdrop) {
    backdrop.addEventListener("click", () => {
      modal.classList.add("hidden");
      modal.setAttribute("aria-hidden", "true");
    });
  }

  // CERRAR (ESC)
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      modal.classList.add("hidden");
      modal.setAttribute("aria-hidden", "true");
    }
  });
});