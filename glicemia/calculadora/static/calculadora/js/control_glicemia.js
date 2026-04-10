document.addEventListener("DOMContentLoaded", function () {
  const inputActual = document.getElementById("id_glicemia_actual");
  const inputPrevia = document.getElementById("id_glicemia_previa");
  const inputAnterior = document.getElementById("id_tercera_medicion");

  const bloqueContexto = document.getElementById("bloque_contexto");
  const hipoHelperBox = document.getElementById("hipo_helper_box");
  const helperPreviaContainer = document.getElementById("helper_previa_container");
  const helperPrevia = document.getElementById("helper_previa");
  const previasBox = document.getElementById("previas_box");
  const anteriorContainer = document.getElementById("anterior_container");
  const secuenciaMediciones = document.getElementById("secuencia_mediciones");
  const labelPreviaHint = document.getElementById("label_previa_hint");

  const stepAnterior = document.getElementById("step-anterior");
  const stepPrevia = document.getElementById("step-previa");
  const stepActual = document.getElementById("step-actual");
  const arrowAnteriorPrevia = document.getElementById("arrow-anterior-previa");

  const radiosInfusion = document.querySelectorAll('input[name="infusion_activa"]');

  function mostrar(el) {
    if (!el) return;
    el.classList.remove("hidden");
  }

  function ocultar(el) {
    if (!el) return;
    el.classList.add("hidden");
  }

  function limpiarNumero(input) {
    if (!input) return;
    let valor = input.value.replace(/[^\d]/g, "");

    if (valor === "") {
      input.value = "";
      return;
    }

    let numero = parseInt(valor, 10);

    if (Number.isNaN(numero)) {
      input.value = "";
      return;
    }

    if (numero < 0) numero = 0;
    if (numero > 999) numero = 999;

    input.value = String(numero);
  }

  function protegerInput(input) {
    if (!input) return;

    input.setAttribute("min", "0");
    input.setAttribute("max", "999");
    input.setAttribute("step", "1");
    input.setAttribute("inputmode", "numeric");

    input.addEventListener("input", function () {
      limpiarNumero(input);
      actualizarFormulario();
    });

    input.addEventListener("blur", function () {
      limpiarNumero(input);
    });

    input.addEventListener("keydown", function (e) {
      const permitidas = [
        "Backspace",
        "Delete",
        "Tab",
        "ArrowLeft",
        "ArrowRight",
        "Home",
        "End"
      ];

      if (permitidas.includes(e.key) || /^\d$/.test(e.key)) {
        return;
      }

      e.preventDefault();
    });

    input.addEventListener("paste", function (e) {
      e.preventDefault();
      const texto = (e.clipboardData || window.clipboardData).getData("text");
      input.value = texto;
      limpiarNumero(input);
      actualizarFormulario();
    });
  }

  function obtenerActual() {
    if (!inputActual || inputActual.value === "") return null;
    const n = parseInt(inputActual.value, 10);
    return Number.isNaN(n) ? null : n;
  }

  function obtenerInfusion() {
    const checked = document.querySelector('input[name="infusion_activa"]:checked');
    if (!checked) return null;
    return checked.value === "true";
  }

  function resetSecuencia() {
    if (stepAnterior) {
      stepAnterior.textContent = "Anterior (1)";
      stepAnterior.className = "glicemia-secuencia__step glicemia-secuencia__step--muted";
    }

    if (stepPrevia) {
      stepPrevia.textContent = "Previa (2)";
      stepPrevia.className = "glicemia-secuencia__step";
    }

    if (stepActual) {
      stepActual.textContent = "Actual (3)";
      stepActual.className = "glicemia-secuencia__step glicemia-secuencia__step--active";
    }

    if (arrowAnteriorPrevia) {
      mostrar(arrowAnteriorPrevia);
    }
  }

  function ponerSecuenciaDosMediciones(obligatoria) {
    resetSecuencia();

    if (stepAnterior) ocultar(stepAnterior);
    if (arrowAnteriorPrevia) ocultar(arrowAnteriorPrevia);

    if (stepPrevia) {
      stepPrevia.textContent = obligatoria ? "Previa (obligatoria)" : "Previa";
      stepPrevia.className = obligatoria
        ? "glicemia-secuencia__step glicemia-secuencia__step--required"
        : "glicemia-secuencia__step";
    }

    if (stepActual) {
      stepActual.textContent = "Actual";
      stepActual.className = "glicemia-secuencia__step glicemia-secuencia__step--active";
    }
  }

  function ponerSecuenciaTresMediciones() {
    resetSecuencia();

    if (stepAnterior) mostrar(stepAnterior);
    if (arrowAnteriorPrevia) mostrar(arrowAnteriorPrevia);

    if (stepPrevia) {
      stepPrevia.textContent = "Previa (2)";
      stepPrevia.className = "glicemia-secuencia__step glicemia-secuencia__step--required";
    }

    if (stepActual) {
      stepActual.textContent = "Actual (3)";
      stepActual.className = "glicemia-secuencia__step glicemia-secuencia__step--active";
    }
  }

  function actualizarFormulario() {
    const actual = obtenerActual();
    const infusion = obtenerInfusion();

    if (inputPrevia) inputPrevia.required = false;
    if (inputAnterior) inputAnterior.required = false;

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
      if (inputPrevia) inputPrevia.value = "";
      if (inputAnterior) inputAnterior.value = "";
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

    if (infusion === true) {
      if (helperPrevia) {
        helperPrevia.textContent = "La glicemia previa es obligatoria si hay infusión activa.";
      }
      if (labelPreviaHint) {
        labelPreviaHint.textContent = "(obligatoria)";
      }
      if (inputPrevia) inputPrevia.required = true;

      if (actual > 200 && actual < 360) {
        mostrar(anteriorContainer);
        mostrar(secuenciaMediciones);
        ponerSecuenciaTresMediciones();
      } else {
        ocultar(anteriorContainer);
        ocultar(secuenciaMediciones);
        if (inputAnterior) inputAnterior.value = "";
        ponerSecuenciaDosMediciones(true);
      }
    } else {
      if (helperPrevia) {
        helperPrevia.textContent = "La glicemia previa ayuda a evaluar la tendencia.";
      }
      if (labelPreviaHint) {
        labelPreviaHint.textContent = "(opcional)";
      }

      ocultar(anteriorContainer);
      ocultar(secuenciaMediciones);
      if (inputAnterior) inputAnterior.value = "";
      ponerSecuenciaDosMediciones(false);
    }
  }

  protegerInput(inputActual);
  protegerInput(inputPrevia);
  protegerInput(inputAnterior);

  radiosInfusion.forEach((radio) => {
    radio.addEventListener("change", actualizarFormulario);
  });

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