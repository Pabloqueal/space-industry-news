let allArticles = [];
let currentCategory = "All";

// -----------------------------
// LOAD DATA
// -----------------------------
fetch("news/posts.json")
  .then(response => response.json())
  .then(data => {
    allArticles = data;
    renderNews(data);
  });

// -----------------------------
// RENDER NEWS (NEW CARD DESIGN)
// -----------------------------
function renderNews(articles) {

  const container = document.getElementById("news-container");
  container.innerHTML = "";

  articles.forEach(article => {

    const card = document.createElement("div");
    card.className = "news-card";

    card.innerHTML = `
      <img src="${article.image}" class="news-image"/>

      <div class="news-content">
        <h3>${article.title}</h3>

        <div class="meta">
          <span class="badge">${article.category}</span>
          <span class="company">${article.company}</span>
        </div>

        <p>${article.summary}</p>

        <a href="${article.link}" target="_blank" class="read-more">
          Read more →
        </a>
      </div>
    `;

    container.appendChild(card);
  });
}

// -----------------------------
// SEARCH + FILTER
// -----------------------------
function searchNews(){
  applyFilters();
}

function filterCategory(category){
  currentCategory = category;
  applyFilters();
}

function applyFilters(){

  const query = document
    .getElementById("searchInput")
    .value
    .toLowerCase();

  let filtered = allArticles;

  // 🔹 CATEGORY FILTER (mejorado)
  if(currentCategory !== "All"){
    filtered = filtered.filter(article =>
      article.category.toLowerCase().includes(currentCategory.toLowerCase())
    );
  }

  // 🔹 SEARCH FILTER
  filtered = filtered.filter(article =>
    article.title.toLowerCase().includes(query) ||
    article.summary.toLowerCase().includes(query) ||
    article.company.toLowerCase().includes(query)
  );

  renderNews(filtered);
}
