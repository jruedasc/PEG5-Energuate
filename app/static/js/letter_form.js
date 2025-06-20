function filterByUser() {
  const selectedUser = document.getElementById('userFilter').value.toLowerCase();
  const rows = document.querySelectorAll('table tbody tr');

  rows.forEach(row => {
    const userCell = row.querySelectorAll('td')[1]; // Segunda columna: nombre del usuario
    if (!userCell) return;
    const userName = userCell.textContent.toLowerCase();

    if (!selectedUser || userName.includes(selectedUser)) {
      row.style.display = '';
    } else {
      row.style.display = 'none';
    }
  });
}
