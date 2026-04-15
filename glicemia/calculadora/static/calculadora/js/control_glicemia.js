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
  const modalTabla = document.getElementById("modal-tabla");
  const cerrarModalTabla = document.getElementById("cerrar-modal-tabla");
  const btnCerrarTabla = document.getElementById("btn-cerrar-tabla");

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

  function abrirModalTabla() {
    if (!modalTabla) return;
    modalTabla.classList.remove("hidden");
    modalTabla.setAttribute("aria-hidden", "false");
    document.body.classList.add("modal-open");
  }

  function cerrarModal() {
    if (!modalTabla) return;
    modalTabla.classList.add("hidden");
    modalTabla.setAttribute("aria-hidden", "true");
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

  if (btnTablaAlgoritmos) {
    btnTablaAlgoritmos.addEventListener("click", abrirModalTabla);
  }

  if (cerrarModalTabla) {
    cerrarModalTabla.addEventListener("click", cerrarModal);
  }

  if (btnCerrarTabla) {
    btnCerrarTabla.addEventListener("click", cerrarModal);
  }

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      cerrarModal();
    }
  });

  inputActual?.addEventListener("input", actualizarFormulario);
  radiosInfusion.forEach((r) => r.addEventListener("change", actualizarFormulario));

  actualizarFormulario();
});

document.addEventListener("click", function (e) {
  const link = e.target.closest(".link-algoritmo");
  if (!link) return;

  const algoritmo = link.dataset.algoritmo;
  const modal = document.getElementById("modal-algoritmo");
  const img = document.getElementById("img-algoritmo");

  if (!modal || !img) return;

  img.src = `/static/calculadora/img/algoritmo_${algoritmo}.png`;
  img.alt = `Algoritmo ${algoritmo}`;
  modal.classList.add("active");
});

document.addEventListener("click", function (e) {
  if (e.target.matches("#modal-algoritmo, #cerrar-modal-algoritmo")) {
    const modal = document.getElementById("modal-algoritmo");
    if (modal) {
      modal.classList.remove("active");
    }
  }
});

document.getElementById("form-glicemia")?.addEventListener("keydown", function (e) {
  if (e.key === "Enter") {
    const tag = document.activeElement.tagName.toLowerCase();
    if (tag === "textarea") return;

    e.preventDefault();
    this.requestSubmit();
  }
});

document.addEventListener("DOMContentLoaded", function () {
  const body = document.body;

  const modalResultado = document.getElementById("modal-resultado");
  const cerrarModalResultado = document.getElementById("cerrar-modal-resultado");

  function abrirModalResultado() {
    if (!modalResultado) return;
    modalResultado.classList.remove("hidden");
    modalResultado.setAttribute("aria-hidden", "false");
    body.classList.add("modal-open");
  }

  function cerrarModalResultadoFn() {
    if (!modalResultado) return;
    modalResultado.classList.add("hidden");
    modalResultado.setAttribute("aria-hidden", "true");
    body.classList.remove("modal-open");
  }

  if (cerrarModalResultado) {
    cerrarModalResultado.addEventListener("click", cerrarModalResultadoFn);
  }

  document.querySelectorAll('[data-close-modal="resultado"]').forEach((el) => {
    el.addEventListener("click", cerrarModalResultadoFn);
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && modalResultado && !modalResultado.classList.contains("hidden")) {
      cerrarModalResultadoFn();
    }
  });

  // abrir automáticamente si el backend devolvió resultado
  const bodyResultado = modalResultado?.querySelector(".modal-resultado__body");
  if (bodyResultado && bodyResultado.textContent.trim() !== "") {
    abrirModalResultado();
  }
});

document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("form-control-glicemia");

  if (form) {
    form.addEventListener("keydown", function (e) {
      if (e.key === "Enter" && e.target.tagName !== "TEXTAREA") {
        e.preventDefault();
        form.requestSubmit();
      }
    });
  }
});