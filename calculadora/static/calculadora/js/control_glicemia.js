document.addEventListener("DOMContentLoaded", function () {
  const inputActual = document.getElementById("id_glicemia_actual");
  const radiosInfusion = document.querySelectorAll('input[name="infusion_activa"]');

  const hipoHelperBox = document.getElementById("hipo_helper_box");
  const bloqueContexto = document.getElementById("bloque_contexto");
  const helperPreviaContainer = document.getElementById("helper_previa_container");
  const helperPrevia = document.getElementById("helper_previa");

  const ajusteContainer = document.getElementById("ajuste_container");
  const previasBox = document.getElementById("previas_box");
  const btnLimpiar = document.getElementById("btn-limpiar");
  const anteriorContainer = document.getElementById("anterior_container");
  const algoritmoContainer = document.getElementById("algoritmo_container");

  const labelPreviaHint = document.getElementById("label_previa_hint");

  const secuenciaMediciones = document.getElementById("secuencia_mediciones");
  const stepAnterior = document.getElementById("step-anterior");
  const stepPrevia = document.getElementById("step-previa");
  const stepActual = document.getElementById("step-actual");

  const arrowAnteriorPrevia = document.getElementById("arrow-anterior-previa");
  const arrowPreviaActual = document.getElementById("arrow-previa-actual");

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

  // Lista de elementos que usan transición animada en lugar de display:none brusco
  const ANIMABLES = new Set([
    "bloque_contexto",
    "previas_box",
    "anterior_container",
    "algoritmo_container",
    "helper_previa_container",
    "ajuste_container",
    "secuencia_mediciones",
    "hipo_helper_box",
  ]);

  // Ocultar sin animación (para inicialización)
  function ocultarInmediato(el) {
    if (!el) return;
    el.classList.remove("campo-visible");
    el.classList.add("campo-oculto");
    el.style.display = "none";
  }

  // Inicializar todos los animables en estado oculto sin transición
  ANIMABLES.forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.classList.add("campo-animable");
      el.classList.remove("hidden");
      ocultarInmediato(el);
    }
  });

  function mostrar(el) {
    if (!el) return;
    if (ANIMABLES.has(el.id)) {
      el.style.display = "";
      // requestAnimationFrame doble para forzar repaint antes de la transición
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          el.classList.remove("campo-oculto");
          el.classList.add("campo-visible");
        });
      });
    } else {
      el.classList.remove("hidden");
      el.style.display = "";
    }
  }

  function ocultar(el) {
    if (!el) return;
    if (ANIMABLES.has(el.id)) {
      el.classList.remove("campo-visible");
      el.classList.add("campo-oculto");
      // Esperar a que termine la transición para retirar del flujo
      el.addEventListener("transitionend", function handler() {
        if (el.classList.contains("campo-oculto")) {
          el.style.display = "none";
        }
        el.removeEventListener("transitionend", handler);
      });
    } else {
      el.classList.add("hidden");
      el.style.display = "none";
    }
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
      ocultar(ajusteContainer);
      ocultar(previasBox);
      ocultar(anteriorContainer);
      ocultar(algoritmoContainer);
      ocultar(secuenciaMediciones);
      ocultar(btnLimpiar);
      return;
    }

    mostrar(btnLimpiar);

    if (actual <= 70) {
      mostrar(hipoHelperBox);
      ocultar(bloqueContexto);
      ocultar(helperPreviaContainer);
      ocultar(ajusteContainer);
      ocultar(previasBox);
      ocultar(anteriorContainer);
      ocultar(algoritmoContainer);
      ocultar(secuenciaMediciones);
      return;
    }

    ocultar(hipoHelperBox);
    mostrar(bloqueContexto);

    if (infusion === null) {
      ocultar(helperPreviaContainer);
      ocultar(ajusteContainer);
      ocultar(previasBox);
      ocultar(anteriorContainer);
      ocultar(algoritmoContainer);
      ocultar(secuenciaMediciones);
      return;
    }

    mostrar(helperPreviaContainer);
    mostrar(previasBox);

    if (infusion) {
      mostrar(ajusteContainer);
      if (helperPrevia) {
        helperPrevia.textContent = "La glicemia previa es obligatoria para evaluar tendencia.";
      }
      if (labelPreviaHint) {
        labelPreviaHint.textContent = "(obligatoria)";
      }

      if (infusion === true && actual > 120) {
        mostrar(algoritmoContainer);
        seleccionarAlgoritmo1PorDefecto()
      } else {
        ocultar(algoritmoContainer);
        //seleccionarAlgoritmo1PorDefecto();
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

      ajusteContainer.querySelectorAll('input[type="radio"]').forEach(r => r.checked = false);
      ocultar(ajusteContainer);
      ocultar(anteriorContainer);
      ocultar(algoritmoContainer);
      ocultar(secuenciaMediciones);
      //seleccionarAlgoritmo1PorDefecto();
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

  function limpiarFormulario() {
    btnLimpiar?.classList.add("is-clearing");
    setTimeout(() => btnLimpiar?.classList.remove("is-clearing"), 500);

    document.getElementById("form-glicemia")?.reset();

    if (inputActual) {
      inputActual.classList.add("input-cleared");
      inputActual.addEventListener("animationend", () => {
        inputActual.classList.remove("input-cleared");
      }, { once: true });
      inputActual.focus();
    }

    actualizarFormulario();
  }

  btnLimpiar?.addEventListener("click", limpiarFormulario);

  inputActual?.addEventListener("input", actualizarFormulario);
  radiosInfusion.forEach((r) => r.addEventListener("change", actualizarFormulario));

  // Auto-selección del campo glucemia actual al recibir foco
  inputActual?.addEventListener("focus", function () {
    this.select();
  });

  // Estado de carga en botón Evaluar al hacer submit
  const formGlicemia = document.getElementById("form-glicemia");
  const btnEvaluar = formGlicemia?.querySelector('button[type="submit"]');

  if (formGlicemia && btnEvaluar) {
    formGlicemia.addEventListener("submit", function () {
      btnEvaluar.disabled = true;
      btnEvaluar.classList.add("btn-cargando");
      btnEvaluar.innerHTML =
        '<span class="btn-spinner" aria-hidden="true"></span>Evaluando...';
    });
  }

  actualizarFormulario();
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
    // Forzar reflow para que la animación CSS de entrada se ejecute
    void modalResultado.offsetWidth;
    modalResultado.classList.add("modal-resultado--entrando");
    modalResultado.addEventListener("animationend", function handler() {
      modalResultado.classList.remove("modal-resultado--entrando");
      modalResultado.removeEventListener("animationend", handler);
    });
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

  document.querySelectorAll("[data-close-resultado]").forEach((el) => {
    el.addEventListener("click", cerrarModalResultadoFn);
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && modalResultado && !modalResultado.classList.contains("hidden")) {
      cerrarModalResultadoFn();
    }
  });

  const bodyResultado = modalResultado?.querySelector(".modal-resultado__body");
  if (bodyResultado && bodyResultado.textContent.trim() !== "") {
    abrirModalResultado();
  }
});
