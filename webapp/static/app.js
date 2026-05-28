const CUBE_API_URL = "/cubejs-api/v1";
const measures = [
  "ArtworkEngagement.studentCount",
  "ArtworkEngagement.artworkCount",
  "ArtworkEngagement.views",
  "ArtworkEngagement.likes",
  "ArtworkEngagement.avgGrade"
];

let selected = null;

async function cubeLoad(query) {
  const response = await fetch(`${CUBE_API_URL}/load`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query })
  });

  if (!response.ok) {
    throw new Error(`Cube API returned ${response.status}`);
  }

  const payload = await response.json();
  return payload.data || [];
}

function normalizeRows(rows, dimension) {
  return rows.map((row) => ({
    name: row[dimension],
    students: Number(row["ArtworkEngagement.studentCount"] || 0),
    artworks: Number(row["ArtworkEngagement.artworkCount"] || 0),
    views: Number(row["ArtworkEngagement.views"] || 0),
    likes: Number(row["ArtworkEngagement.likes"] || 0),
    avgGrade: Number(row["ArtworkEngagement.avgGrade"] || 0).toFixed(1)
  }));
}

async function loadRows() {
  const dimension = selected ? "ArtworkEngagement.ageGroup" : "ArtworkEngagement.exhibitionId";
  const query = {
    measures,
    dimensions: [dimension],
    filters: selected
      ? [{ member: "ArtworkEngagement.exhibitionId", operator: "equals", values: [selected] }]
      : [],
    order: { "ArtworkEngagement.views": "desc" }
  };

  const data = await cubeLoad(query);
  return normalizeRows(data, dimension);
}

function render(rows) {
  const chart = document.querySelector("#chart");
  const metrics = document.querySelector("#metrics");
  const maxViews = Math.max(...rows.map((row) => row.views), 1);

  if (!rows.length) {
    chart.innerHTML = "<p class=\"empty\">Нет данных из Cube API</p>";
    metrics.innerHTML = "";
    return;
  }

  chart.innerHTML = rows.map((row) => `
    <button class="bar-row" data-name="${row.name}">
      <span class="bar-label">${row.name}</span>
      <span class="bar-track"><span class="bar-fill" style="width: ${(row.views / maxViews) * 100}%"></span></span>
      <span>${row.views.toLocaleString("ru-RU")}</span>
    </button>
  `).join("");

  metrics.innerHTML = rows.map((row) => `
    <button class="metric" data-name="${row.name}">
      <span>${row.name}</span>
      <strong>${row.views.toLocaleString("ru-RU")}</strong>
      <small>${row.students} художников, ${row.artworks} работ, средний балл ${row.avgGrade}</small>
    </button>
  `).join("");

  document.querySelectorAll("[data-name]").forEach((item) => {
    item.addEventListener("click", async () => {
      if (!selected) {
        selected = item.dataset.name;
        document.querySelector("#status").textContent = `Drill-down: ${selected} -> возрастные группы`;
        await refresh();
      }
    });
  });
}

function renderError(error) {
  document.querySelector("#chart").innerHTML = `<p class="error">${error.message}</p>`;
  document.querySelector("#metrics").innerHTML = "";
}

async function refresh() {
  document.querySelector("#chart").innerHTML = "<p class=\"empty\">Загрузка данных из Cube API...</p>";
  try {
    render(await loadRows());
  } catch (error) {
    renderError(error);
  }
}

document.querySelector("#reset").addEventListener("click", async () => {
  selected = null;
  document.querySelector("#status").textContent = "Drill-down: выставки";
  await refresh();
});

refresh();
