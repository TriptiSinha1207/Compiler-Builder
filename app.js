document.addEventListener("DOMContentLoaded", () => {
  const tableElements = document.querySelectorAll(".table-output[data-endpoint]");
  tableElements.forEach((container) => {
    const endpoint = container.dataset.endpoint;
    if (!endpoint) return;
    fetch(endpoint)
      .then((res) => res.json())
      .then((data) => {
        renderTable(container, data.items || []);
      })
      .catch((error) => {
        container.innerHTML = `<pre class="error">${error}</pre>`;
      });
  });

  const forms = document.querySelectorAll(".ui-form");
  forms.forEach((form) => {
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      submitForm(form);
    });
  });

  const promptForm = document.getElementById("prompt-form");
  if (promptForm) {
    promptForm.addEventListener("submit", (event) => {
      event.preventDefault();
      submitPrompt(promptForm);
    });
  }
});

function submitPrompt(form) {
  const prompt = form.querySelector("textarea[name=prompt]").value.trim();
  const status = document.getElementById("prompt-status");
  const result = document.getElementById("generate-result");
  if (!prompt) {
    status.textContent = "Please enter a prompt first.";
    return;
  }
  status.textContent = "Generating your app...";
  result.classList.add("hidden");
  fetch("/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt }),
  })
    .then((res) => res.json())
    .then((payload) => {
      if (!payload.success) {
        status.textContent = payload.error || "Failed to generate the app.";
        result.innerHTML = renderGenerateError(payload);
        result.classList.remove("hidden");
        return;
      }
      window.generatedAppConfig = payload.config;
      window.generatedPrompt = payload.intent.prompt;
      status.textContent = "App generated successfully.";
      result.innerHTML = renderGenerateResult(payload);
      const downloadButton = document.getElementById("download-config");
      if (downloadButton) {
        downloadButton.addEventListener("click", () => downloadConfig());
      }
      result.classList.remove("hidden");
    })
    .catch((err) => {
      status.textContent = "Request failed.";
      result.innerHTML = `<pre class="error">${err}</pre>`;
      result.classList.remove("hidden");
    });
}

function renderGenerateError(payload) {
  const lines = [];
  if (payload.clarification) {
    lines.push(`<strong>Clarification needed:</strong> ${payload.clarification.join(" ")}`);
  }
  if (payload.assumptions) {
    lines.push(`<strong>Assumptions:</strong> ${payload.assumptions.join(" ")}`);
  }
  if (payload.errors) {
    lines.push(`<strong>Errors:</strong> <pre>${JSON.stringify(payload.errors, null, 2)}</pre>`);
  }
  return `<div class="generate-error">${lines.join("<br>")}</div>`;
}

function renderGenerateResult(payload) {
  const pageLinks = payload.pages
    .map((page) => `<li><strong>${page.name}</strong> — ${page.path}</li>`)
    .join("");
  return `
    <div class="generate-summary">
      <h3>Compiled application configuration</h3>
      <button class="button download-config" type="button" id="download-config">Download config</button>
      <p><strong>Pages generated:</strong></p>
      <ul>${pageLinks}</ul>
      <h4>Intent</h4>
      <pre>${JSON.stringify(payload.intent, null, 2)}</pre>
      <h4>Strict generated config</h4>
      <pre>${JSON.stringify(payload.config, null, 2)}</pre>
    </div>
  `;
}

function downloadConfig() {
  const config = window.generatedAppConfig;
  const prompt = window.generatedPrompt || "generated";
  if (!config) {
    return;
  }
  const blob = new Blob([JSON.stringify(config, null, 2)], { type: "application/json" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  const safePrompt = prompt.replace(/[^a-z0-9]/gi, "_").substring(0, 40) || "generated";
  link.download = `app_config_${safePrompt}.json`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

function renderTable(container, items) {
  if (!Array.isArray(items) || items.length === 0) {
    container.textContent = "No records available.";
    return;
  }

  const rows = items.map((item) => (Array.isArray(item) ? item : [item]));
  const headerRow = rows[0].map((_, index) => `Column ${index + 1}`);
  const table = document.createElement("table");
  const thead = document.createElement("thead");
  const headRow = document.createElement("tr");
  headerRow.forEach((heading) => {
    const th = document.createElement("th");
    th.textContent = heading;
    headRow.appendChild(th);
  });
  thead.appendChild(headRow);
  table.appendChild(thead);

  const tbody = document.createElement("tbody");
  rows.forEach((row) => {
    const tr = document.createElement("tr");
    row.forEach((cell) => {
      const td = document.createElement("td");
      td.textContent = cell;
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  });
  table.appendChild(tbody);
  container.innerHTML = "";
  container.appendChild(table);
}

function submitForm(form) {
  const action = form.dataset.action;
  if (!action) {
    return;
  }
  const data = {};
  form.querySelectorAll("input[name]").forEach((input) => {
    data[input.name] = input.value;
  });
  const status = form.querySelector(".form-status");
  fetch(action, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  })
    .then((res) => res.json())
    .then((payload) => {
      status.textContent = "Submitted successfully.";
      console.log(payload);
    })
    .catch((err) => {
      status.textContent = "Request failed.";
      console.error(err);
    });
}
