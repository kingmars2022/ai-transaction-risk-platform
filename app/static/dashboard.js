const formatScore = (value) => Number(value || 0).toFixed(3);

function transactionPayload(form) {
  const data = new FormData(form);

  return {
    amount: Number(data.get("amount")),
    old_balance: Number(data.get("old_balance")),
    new_balance: Number(data.get("new_balance")),
    transaction_type: String(data.get("transaction_type")),
    hour: Number(data.get("hour")),
  };
}

function setButtonsDisabled(disabled) {
  document.querySelectorAll(".form-actions button").forEach((button) => {
    button.disabled = disabled;
  });
}

function renderSyncResult(data) {
  const box = document.getElementById("result-box");
  const riskClass = data.is_high_risk ? "high-risk" : "normal-risk";
  const flagLabel = data.is_high_risk ? "High Risk" : "Normal";

  box.className = `result-box ${riskClass}`;
  box.innerHTML = `
    <span class="result-label">Synchronous prediction</span>
    <strong>${formatScore(data.risk_score)}</strong>
    <div class="result-details">
      <div class="result-detail"><span>Prediction ID</span><b>${data.prediction_id}</b></div>
      <div class="result-detail"><span>Decision</span><b>${flagLabel}</b></div>
    </div>
  `;
}

function renderAsyncResult(data) {
  const box = document.getElementById("result-box");

  box.className = "result-box";
  box.innerHTML = `
    <span class="result-label">Asynchronous job queued</span>
    <strong>${data.status}</strong>
    <div class="result-details">
      <div class="result-detail"><span>Job ID</span><b>${data.job_id}</b></div>
      <div class="result-detail"><span>Status</span><b>${data.status}</b></div>
    </div>
  `;
}

function renderError(message) {
  const box = document.getElementById("result-box");

  box.className = "result-box error";
  box.innerHTML = `
    <span class="result-label">Request failed</span>
    <strong>Error</strong>
    <p>${message}</p>
  `;
}

async function submitTransaction(mode) {
  const form = document.getElementById("transaction-form");
  const endpoint = mode === "async" ? "/api/v1/jobs" : "/api/v1/predict";
  const response = await fetch(endpoint, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(transactionPayload(form)),
  });
  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Transaction request failed");
  }

  if (mode === "async") {
    renderAsyncResult(data);
  } else {
    renderSyncResult(data);
  }

  await loadDashboard();
}

function renderRiskChart(buckets) {
  const chart = document.getElementById("risk-chart");
  const labels = ["low", "medium", "high"];
  const values = labels.map((label) => buckets[label] || 0);
  const maxValue = Math.max(...values, 1);

  chart.innerHTML = labels
    .map((label, index) => {
      const value = values[index];
      const height = Math.max((value / maxValue) * 100, value > 0 ? 8 : 0);

      return `
        <div class="risk-bar-group">
          <div class="risk-value">${value}</div>
          <div class="risk-track">
            <div class="risk-bar ${label}" style="height: ${height}%"></div>
          </div>
          <div class="risk-name">${label}</div>
        </div>
      `;
    })
    .join("");
}

function renderJobStatus(jobStatus) {
  const container = document.getElementById("job-status-list");
  const entries = Object.entries(jobStatus);

  if (entries.length === 0) {
    container.innerHTML = '<div class="status-row"><span>No jobs yet</span><strong>0</strong></div>';
    return;
  }

  container.innerHTML = entries
    .map(([status, count]) => `<div class="status-row"><span>${status}</span><strong>${count}</strong></div>`)
    .join("");
}

function renderRows(predictions) {
  const tbody = document.getElementById("prediction-rows");

  if (!predictions.length) {
    tbody.innerHTML = '<tr><td colspan="6">No predictions yet</td></tr>';
    return;
  }

  tbody.innerHTML = predictions
    .map((prediction) => {
      const flagClass = prediction.is_high_risk ? "high" : "normal";
      const flagLabel = prediction.is_high_risk ? "High risk" : "Normal";

      return `
        <tr>
          <td>${prediction.id}</td>
          <td>${prediction.transaction_type}</td>
          <td>$${Number(prediction.amount).toFixed(2)}</td>
          <td>${prediction.hour}:00</td>
          <td>${formatScore(prediction.risk_score)}</td>
          <td><span class="flag ${flagClass}">${flagLabel}</span></td>
        </tr>
      `;
    })
    .join("");
}

async function loadDashboard() {
  const response = await fetch("/api/v1/metrics");
  const metrics = await response.json();

  document.getElementById("prediction-count").textContent = metrics.prediction_count;
  document.getElementById("high-risk-count").textContent = metrics.high_risk_count;
  document.getElementById("average-risk-score").textContent = formatScore(metrics.average_risk_score);

  renderRiskChart(metrics.risk_buckets);
  renderJobStatus(metrics.job_status);
  renderRows(metrics.recent_predictions);
}

loadDashboard().catch(() => {
  document.getElementById("prediction-rows").innerHTML =
    '<tr><td colspan="6">Dashboard data is unavailable</td></tr>';
});

document.getElementById("transaction-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  setButtonsDisabled(true);

  try {
    await submitTransaction("sync");
  } catch (error) {
    renderError(error.message);
  } finally {
    setButtonsDisabled(false);
  }
});

document.getElementById("queue-job-button").addEventListener("click", async () => {
  setButtonsDisabled(true);

  try {
    await submitTransaction("async");
    window.setTimeout(loadDashboard, 1200);
  } catch (error) {
    renderError(error.message);
  } finally {
    setButtonsDisabled(false);
  }
});
