let allArticles = [];
let currentCategory = "All";

fetch("news/posts.json")
.then(response => response.json())
.then(data => {

    allArticles = data;

    displayNews(data);

});

function displayNews(data){

const container = document.getElementById("news-container");

container.innerHTML = "";

data.forEach(article => {

const div = document.createElement("div");
div.className = "article";

div.innerHTML = `

<img src="${article.image}" class="news-image">

<div class="article-content">

<h2>${article.title}</h2>

<p class="meta">
${article.category} | ${article.company}
</p>

<p>${article.summary}</p>

<a href="${article.link}" target="_blank">Read full article</a>

</div>
`;

container.appendChild(div);

});

}

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

if(currentCategory !== "All"){

filtered = filtered.filter(article =>
article.category === currentCategory
);

}

filtered = filtered.filter(article =>

article.title.toLowerCase().includes(query) ||
article.summary.toLowerCase().includes(query) ||
article.company.toLowerCase().includes(query)

);

displayNews(filtered);

}

function renderNews(articles) {
  const container = document.getElementById("news");
  container.innerHTML = "";

  articles.forEach(article => {
    const card = document.createElement("div");
    card.className = "news-card";

    card.innerHTML = `
      <img src="${article.image}" class="news-image"/>
      <div class="news-content">
        <h3>${article.title}</h3>
        <p>${article.summary}</p>
        <div class="meta">
          <span>${article.category}</span>
          <span>${article.company}</span>
        </div>
        <a href="${article.link}" target="_blank">Read more →</a>
      </div>
    `;

    container.appendChild(card);
  });
}
