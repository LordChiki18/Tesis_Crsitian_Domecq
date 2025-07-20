document.getElementById("exportarCSV").addEventListener("click", function () {
    const tabla = document.getElementById("tablaDatos");
    const filas = tabla.querySelectorAll("tr");
    let csv = [];
  
    filas.forEach((fila) => {
      const datosFila = [];
      fila.querySelectorAll("td").forEach((celda) => {
        datosFila.push(celda.textContent);
      });
      csv.push(datosFila.join(","));
    });
  
    // Combina las filas en un solo CSV
    const contenidoCSV = csv.join("\n");
  
    // Crea un objeto Blob y un enlace para descargar el archivo CSV
    const blob = new Blob([contenidoCSV], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.style.display = "none";
    a.href = url;
    a.download = "datos.csv";
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
  });
  