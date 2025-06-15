// Modo oscuro / claro
const toggleButton = document.getElementById('theme-toggle');
toggleButton.addEventListener('click', () => {
  document.body.classList.toggle('dark-mode');
});

// Filtro de gráficos
const filtro = document.getElementById('filtro');
filtro.addEventListener('change', () => {
  const tipo = filtro.value;
  const tarjetas = document.querySelectorAll('.chart-card');

  tarjetas.forEach(tarjeta => {
    const tipoTarjeta = tarjeta.getAttribute('data-type');
    if (tipo === 'todos' || tipo === tipoTarjeta) {
      tarjeta.style.display = 'block';
    } else {
      tarjeta.style.display = 'none';
    }
  });
});

// Cargar gráficos dinámicamente
async function cargarGraficos() {
  const response = await fetch('/api/dashboard');
  const data = await response.json();

  // Gráfico de carreras
  new Chart(document.getElementById('carreraChart'), {
    type: 'pie',
    data: {
      labels: data.carreras.labels,
      datasets: [{
        label: 'Estudiantes',
        data: data.carreras.counts,
        backgroundColor: ['#ffd6e0', '#c5dff8', '#caf0f8', '#e0bbff', '#fff7ae']
      }]
    },
    options: {
      plugins: {
        legend: {
          position: 'bottom'
        }
      }
    }
  });

  // Gráfico de notas
  new Chart(document.getElementById('promedioNotasChart'), {
    type: 'bar',
    data: {
      labels: data.notas.labels,
      datasets: [{
        label: 'Promedio de Notas',
        data: data.notas.values,
        backgroundColor: '#caf0f8'
      }]
    },
    options: {
      plugins: {
        legend: {
          display: false
        }
      },
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  });

  // Gráfico de semestres
  new Chart(document.getElementById('semestreChart'), {
    type: 'doughnut',
    data: {
      labels: data.semestres.labels,
      datasets: [{
        label: 'Estudiantes por Semestre',
        data: data.semestres.counts,
        backgroundColor: ['#fff7ae', '#ffd6e0', '#e0bbff']
      }]
    },
    options: {
      plugins: {
        legend: {
          position: 'bottom'
        }
      }
    }
  });

  // Gráfico de rendimiento
  new Chart(document.getElementById('rendimientoChart'), {
    type: 'line',
    data: {
      labels: data.rendimiento.labels,
      datasets: [{
        label: 'Promedio por Curso',
        data: data.rendimiento.values,
        borderColor: '#e0bbff',
        backgroundColor: '#c5dff8',
        tension: 0.4,
        fill: true
      }]
    },
    options: {
      plugins: {
        legend: {
          position: 'bottom'
        }
      },
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  });
}

// Ejecutar al cargar la página
cargarGraficos();
