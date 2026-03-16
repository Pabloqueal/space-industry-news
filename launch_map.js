var map = L.map('map').setView([20,0],2);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{
maxZoom:5
}).addTo(map);

var sites=[
["Cape Canaveral",28.3922,-80.6077],
["Vandenberg",34.742,-120.5724],
["Baikonur",45.965,-63.305],
["Kourou",5.239,-52.768]
];

sites.forEach(site=>{
L.marker([site[1],site[2]]).addTo(map)
.bindPopup(site[0]);
});