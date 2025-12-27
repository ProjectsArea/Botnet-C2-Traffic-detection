const ctx = document.getElementById('riskChart').getContext('2d');

const chart = new Chart(ctx, {
  type: 'line',
  data: {
    labels: [],
    datasets: [{
      label: 'Botnet Risk',
      data: [],
      borderWidth: 2,
      tension: 0.3
    }]
  }
});

function updateFlow() {
  fetch('/api/flows')
    .then(r => r.json())
    .then(d => {
      chart.data.labels.push(d.time);
      chart.data.datasets[0].data.push(d.risk);
      if (chart.data.labels.length > 30) {
        chart.data.labels.shift();
        chart.data.datasets[0].data.shift();
      }
      chart.update();
    });
}

function updateLogs() {
  fetch('/api/logs')
    .then(r => r.json())
    .then(data => {
      const table = document.getElementById("attackTable");
      table.innerHTML = "";
      data.forEach(l => {
        table.innerHTML += `
          <tr>
            <td>${l.time}</td>
            <td>${l.source_ip}</td>
            <td>${l.risk}</td>
            <td style="color:red">${l.status}</td>
          </tr>`;
      });
    });
}

setInterval(updateFlow, 2000);
setInterval(updateLogs, 3000);
