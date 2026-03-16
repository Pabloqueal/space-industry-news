fetch("news/companies.json")
.then(res=>res.json())
.then(data=>{

const container=document.getElementById("companies");

data.forEach(c=>{

const div=document.createElement("div");

div.innerHTML=`${c.company} (${c.mentions})`;

container.appendChild(div);

});

});