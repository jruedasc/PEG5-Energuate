document.addEventListener('DOMContentLoaded', () => {
  const dropArea  = document.getElementById('dropArea');
  const fileInput = document.getElementById('fileInput');
  const fileList  = document.getElementById('fileList');

  // Aquí almacenamos todos los archivos seleccionados
  let selectedFiles = [];

  // Actualiza la lista de vista previa
  function updateList() {
    fileList.innerHTML = '';
    selectedFiles.forEach(f => {
      const sizeMB = (f.size / 1024 / 1024).toFixed(2);
      const row = document.createElement('div');
      row.className = 'mb-3 p-3 border rounded';
      row.innerHTML = `
        <div class="d-flex justify-content-between align-items-center mb-2">
          <div>
            <i class="fa fa-check-circle text-success mr-2"></i>
            <strong>${f.name}</strong>
            <small class="text-muted">(${sizeMB} MB)</small>
          </div>
        </div>
        <div class="progress">
          <div class="progress-bar bg-success" role="progressbar"
               style="width:100%" aria-valuenow="100"
               aria-valuemin="0" aria-valuemax="100">
            100%
          </div>
        </div>`;
      fileList.appendChild(row);
    });
  }

  // Añade nuevos archivos, limita a 20 y reconstruye fileInput.files
  function addFiles(files) {
    selectedFiles = selectedFiles
      .concat(Array.from(files))
      .slice(0, 20);

    const dt = new DataTransfer();
    selectedFiles.forEach(f => dt.items.add(f));
    fileInput.files = dt.files;

    if (selectedFiles.length > 20) {
      alert('Solo puedes seleccionar hasta 20 archivos');
      selectedFiles = selectedFiles.slice(0, 20);
      const dt2 = new DataTransfer();
      selectedFiles.forEach(f => dt2.items.add(f));
      fileInput.files = dt2.files;
    }

    updateList();
  }

  // Eventos de drag & drop
  ['dragenter','dragover'].forEach(evt =>
    dropArea.addEventListener(evt, e => {
      e.preventDefault();
      dropArea.classList.add('bg-light');
    })
  );
  ['dragleave','drop'].forEach(evt =>
    dropArea.addEventListener(evt, e => {
      e.preventDefault();
      dropArea.classList.remove('bg-light');
      if (evt === 'drop') addFiles(e.dataTransfer.files);
    })
  );

  // Selección por clic
  fileInput.addEventListener('change', e => addFiles(e.target.files));
});
