const exhibitions = [
  { name: "spring_colors", students: 24, artworks: 41, views: 1200, likes: 215, avgGrade: 83.4 },
  { name: "digital_future", students: 18, artworks: 35, views: 980, likes: 190, avgGrade: 88.2 },
  { name: "animals_and_friends", students: 31, artworks: 52, views: 1470, likes: 266, avgGrade: 79.5 }
];

const drilldown = {
  spring_colors: [
    { name: "6-9", students: 7, artworks: 12, views: 280, likes: 44, avgGrade: 78.5 },
    { name: "10-13", students: 11, artworks: 18, views: 560, likes: 101, avgGrade: 84.2 },
    { name: "14-17", students: 6, artworks: 11, views: 360, likes: 70, avgGrade: 87.4 }
  ],
  digital_future: [
    { name: "10-13", students: 5, artworks: 9, views: 260, likes: 46, avgGrade: 82.7 },
    { name: "14-17", students: 13, artworks: 26, views: 720, likes: 144, avgGrade: 90.3 }
  ],
  animals_and_friends: [
    { name: "6-9", students: 19, artworks: 31, views: 910, likes: 165, avgGrade: 77.9 },
    { name: "10-13", students: 12, artworks: 21, views: 560, likes: 101, avgGrade: 82.1 }
  ]
};

let selected = null;

function render(rows) {
  const maxViews = Math.max(...rows.map((row) => row.views));
  document.querySelector("#chart").innerHTML = rows.map((row) => `
    <button class="bar-row" data-name="${row.name}">
      <span class="bar-label">${row.name}</span>
      <span class="bar-track"><span class="bar-fill" style="width: ${(row.views / maxViews) * 100}%"></span></span>
      <span>${row.views.toLocaleString("ru-RU")}</span>
    </button>
  `).join("");

  document.querySelector("#metrics").innerHTML = rows.map((row) => `
    <button class="metric" data-name="${row.name}">
      <span>${row.name}</span>
      <strong>${row.views.toLocaleString("ru-RU")}</strong>
      <small>${row.students} художников, ${row.artworks} работ, средний балл ${row.avgGrade}</small>
    </button>
  `).join("");

  document.querySelectorAll("[data-name]").forEach((item) => {
    item.addEventListener("click", () => {
      if (!selected && drilldown[item.dataset.name]) {
        selected = item.dataset.name;
        document.querySelector("#status").textContent = `Drill-down: ${selected} -> возрастные группы`;
        render(drilldown[selected]);
      }
    });
  });
}

document.querySelector("#reset").addEventListener("click", () => {
  selected = null;
  document.querySelector("#status").textContent = "Drill-down: выставки";
  render(exhibitions);
});

render(exhibitions);
