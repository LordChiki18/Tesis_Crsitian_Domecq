document.getElementById("exportarXLSX").addEventListener("click", function () {
    const tabla = document.getElementById("tablaDatos");
    const datos = [];
    const cabeceras = [];
    const filas = tabla.querySelectorAll("tr");
  
    // Obtener las cabeceras de la tabla
    const cabeceraFila = filas[0];
    cabeceraFila.querySelectorAll("th").forEach((celda) => {
      cabeceras.push(celda.textContent);
    });
  
    // Agregar las cabeceras como la primera fila de datos
    datos.push(cabeceras);
  
    // Obtener el resto de los datos de la tabla
    for (let i = 1; i < filas.length; i++) {
      const fila = filas[i];
      const rowData = [];
      fila.querySelectorAll("td").forEach((celda) => {
        rowData.push(celda.textContent);
      });
      datos.push(rowData);
    }
  
    const workbook = XLSX.utils.book_new();
    const ws = XLSX.utils.aoa_to_sheet(datos);
    XLSX.utils.book_append_sheet(workbook, ws, "Datos");
  
    // Crear un archivo XLSX y descargarlo
    XLSX.writeFile(workbook, "datos.xlsx");
  });
  