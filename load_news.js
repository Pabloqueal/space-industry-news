

fetch("news/posts.json")
.then(response => response.json())
.then(data => {

    const container = document.getElementById("news-container");

    data.forEach(article => {

        const div = document.createElement("div");
        div.className = "article";

        div.innerHTML = `
            <img src="${article.image}" class="news-image">
            <div class="article-content">
            <h2>${article.title}</h2>
            <p class="meta">
            ${article.category} | ${article.date}
            </p>
            <p>${article.summary}</p>
            <a href="${article.link}" target="_blank">Read full article</a>
            </div>
            `;

        container.appendChild(div);

    });

});
