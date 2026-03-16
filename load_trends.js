fetch("news/trends.json")
.then(response => response.json())
.then(data => {

const container = document.getElementById("trends");

data.forEach(item => {

const div = document.createElement("div");

div.innerHTML = `#${item.keyword} (${item.count})`;

container.appendChild(div);

});

});