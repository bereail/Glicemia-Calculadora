document.addEventListener("DOMContentLoaded", () => {
  const glicemiaActualInput = document.getElementById("id_glicemia_actual");
  const bloqueContexto = document.getElementById("bloque_contexto");

  const btnPrevia = document.getElementById("btn_previa");
  const btnPreviaContainer = document.getElementById("btn_previa_container");
  const btnPreviaText = document.getElementById("btn_previa_text");
  const btnPreviaIcon = document.getElementById("btn_previa_icon");

  const previaContainer = document.getElementById("previa_container");
  const helperPrevia = document.getElementById("helper_previa");
  const labelPreviaHint = document.getElementById("label_previa_hint");
  const glicemiaPreviaInput = document.getElementById("id_glicemia_previa");

  const infusionRadios = document.querySelectorAll('input[name="infusion_activa"]');

  function mostrar(el) {
    if (el) el.classList.remove("hidden");
  }

  function ocultar(el) {
    if (el) el.classList.add("hidden");
  }

  function getGlicemiaActual() {
    if (!glicemiaActualInput) return null;
    const raw = glicemiaActualInput.value.trim();
    if (raw === "") return null;

    const value = parseFloat(raw);
    return Number.isNaN(value) ? null : value;
  }

  function getInfusionValue() {
    const checked = document.querySelector('input[name="infusion_activa"]:checked');
    return checked ? checked.value : null;
  }

  function infusionActiva() {
    return getInfusionValue() === "True";
  }

  function mostrarPrevia() {
    if (!previaContainer) return;
    mostrar(previaContainer);

    if (btnPrevia) btnPrevia.setAttribute("aria-expanded", "true");
    if (btnPreviaText) btnPreviaText.textContent = "Quitar glicemia previa";
    if (btnPreviaIcon) btnPreviaIcon.textContent = "−";
  }

  function ocultarPrevia(limpiar = true) {
    if (!previaContainer) return;
    ocultar(previaContainer);

    if (btnPrevia) btnPrevia.setAttribute("aria-expanded", "false");
    if (btnPreviaText) btnPreviaText.textContent = "Agregar glicemia previa";
    if (btnPreviaIcon) btnPreviaIcon.textContent = "+";

    if (limpiar && glicemiaPreviaInput) {
      glicemiaPreviaInput.value = "";
    }
  }

  function actualizarTextoPrevia() {
    if (!helperPrevia || !labelPreviaHint) return;

    if (infusionActiva()) {
      helperPrevia.textContent = "Con infusión activa, la glicemia previa es obligatoria para evaluar tendencia.";
      labelPreviaHint.textContent = "(obligatoria)";
      labelPreviaHint.classList.add("required-mark");
      labelPreviaHint.classList.remove("muted");
    } else {
      helperPrevia.textContent = "Podés agregar una glicemia previa para evaluar tendencia.";
      labelPreviaHint.textContent = "(opcional)";
      labelPreviaHint.classList.remove("required-mark");
      labelPreviaHint.classList.add("muted");
    }
  }

  function limpiarInfusion() {
    infusionRadios.forEach((radio) => {
      radio.checked = false;
    });
  }

  function actualizarFlujo() {
    const actual = getGlicemiaActual();

    if (actual === null) {
      ocultar(bloqueContexto);
      ocultar(btnPreviaContainer);
      ocultarPrevia(true);
      limpiarInfusion();
      return;
    }

    if (actual < 70) {
      ocultar(bloqueContexto);
      ocultar(btnPreviaContainer);
      ocultarPrevia(true);
      limpiarInfusion();
      return;
    }

    mostrar(bloqueContexto);

    const infusionValue = getInfusionValue();
    actualizarTextoPrevia();

    if (!infusionValue) {
      ocultar(btnPreviaContainer);
      ocultarPrevia(true);
      return;
    }

    if (infusionActiva()) {
      ocultar(btnPreviaContainer);
      mostrarPrevia();
      return;
    }

    mostrar(btnPreviaContainer);
    ocultarPrevia(true);
  }

  if (glicemiaActualInput) {
    glicemiaActualInput.addEventListener("input", actualizarFlujo);
  }

  infusionRadios.forEach((radio) => {
    radio.addEventListener("change", actualizarFlujo);
  });

  if (btnPrevia) {
    btnPrevia.addEventListener("click", () => {
      if (infusionActiva()) return;

      const estaOculto = previaContainer.classList.contains("hidden");
      if (estaOculto) {
        mostrarPrevia();
      } else {
        ocultarPrevia(true);
      }
    });
  }

  actualizarFlujo();
});