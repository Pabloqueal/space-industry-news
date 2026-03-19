fetch("news/companies.json")
.then(response => response.json())
.then(data => {

const container = document.getElementById("companies-ranking");

data.forEach((company,index)=>{

let medal = "";

if(index === 0) medal = "🥇";
else if(index === 1) medal = "🥈";
else if(index === 2) medal = "🥉";

const div = document.createElement("div");

div.className = "company-card";

div.innerHTML = `

<div class="company-rank">${medal}</div>

<div class="company-name">${company.company}</div>

<div class="company-mentions">
${company.mentions} news mentions
</div>

`;

container.appendChild(div);

});

});
