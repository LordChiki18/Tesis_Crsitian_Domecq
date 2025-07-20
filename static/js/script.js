function redirigirAInicio() {
  window.location.href = '/';
}

var valorOriginalCtte = "";

function ocultarMontoCtte() {
  var btnCuentaCtte = document.getElementById("hideAmountCtte");
  var montoCuentaCtte = document.getElementById("amountCtte");

  if (btnCuentaCtte.textContent === "Ocultar monto") {
    valorOriginalCtte = montoCuentaCtte.textContent; // Guardo el valor original
    var asteriscos = "********";
    montoCuentaCtte.textContent = asteriscos;
    btnCuentaCtte.textContent = "Mostrar monto";
  } else {
    montoCuentaCtte.textContent = valorOriginalCtte;
    btnCuentaCtte.textContent = "Ocultar monto";
  }
}

var valorOriginalCaja = "";

function ocultarMontoCaja() {
  var btnCuentaCaja = document.getElementById("hideAmountCaja");
  var montoCuentaCaja = document.getElementById("amountCaja");

  if (btnCuentaCaja.textContent === "Ocultar monto") {
    valorOriginalCaja = montoCuentaCaja.textContent; // Guardo el valor original
    var asteriscos = "********";
    montoCuentaCaja.textContent = asteriscos;
    btnCuentaCaja.textContent = "Mostrar monto";
  } else {
    montoCuentaCaja.textContent = valorOriginalCaja;
    btnCuentaCaja.textContent = "Ocultar monto";
  }
}

function mostrarFechas() {
  const fechaDesdeInput = document.getElementById("fechaDesde");
  const fechaHastaInput = document.getElementById("fechaHasta");
  const resultados = document.getElementById("resultados");

  const fechaDesde = fechaDesdeInput.value;
  const fechaHasta = fechaHastaInput.value;

  resultados.textContent = `Mostrando Desde: ${fechaDesde}, Hasta: ${fechaHasta}`;
}

document.addEventListener("DOMContentLoaded", function () {
  const fechaDesdeInput = document.getElementById("fechaDesde");
  const fechaHastaInput = document.getElementById("fechaHasta");

  const fechaHoy = new Date();
  const fechaPrimerDiaMes = new Date(fechaHoy.getFullYear(), fechaHoy.getMonth(), 1);

  fechaDesdeInput.valueAsDate = fechaPrimerDiaMes;
  fechaHastaInput.valueAsDate = fechaHoy;

  mostrarFechas(); // Muestra las fechas por defecto al cargar la página

  const botonMostrar = document.querySelector("button");
  botonMostrar.addEventListener("click", mostrarFechas);
});

$(document).ready(function() {
  $("select[name='tipo_cuenta']").prepend('<option value="" disabled selected>Seleccione el tipo de cuenta</option>');
  $("select[name='moneda']").prepend('<option value="" disabled selected>Seleccione la moneda</option>');
});