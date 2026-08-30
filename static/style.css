const imageInput = document.getElementById("imageInput");
const preview = document.getElementById("preview");
const uploadText = document.getElementById("uploadText");
const imageBtn = document.getElementById("analyzeImageBtn");
const loading = document.getElementById("loading");
const results = document.getElementById("results");

document.querySelectorAll(".tab").forEach(btn => {
  btn.onclick = () => {
    document.querySelectorAll(".tab").forEach(x => x.classList.remove("active"));
    document.querySelectorAll(".tab-content").forEach(x => x.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById(btn.dataset.tab).classList.add("active");
  };
});

imageInput.onchange = () => {
  const file = imageInput.files[0];
  if (!file) return;
  preview.src = URL.createObjectURL(file);
  preview.style.display = "block";
  uploadText.style.display = "none";
  imageBtn.disabled = false;
};

imageBtn.onclick = async () => {
  const file = imageInput.files[0];
  if (!file) return;
  const form = new FormData();
  form.append("image", file);
  await request("/analyze", {method:"POST", body:form});
};

document.getElementById("analyzeTextBtn").onclick = async () => {
  const text = document.getElementById("smsText").value.trim();
  if (!text) return alert("Maglagay muna ng SMS text.");
  await request("/analyze-text", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({text})
  });
};

async function request(url, options){
  loading.classList.remove("hidden");
  results.classList.add("hidden");
  try{
    const response = await fetch(url, options);
    const data = await response.json();
    if(!response.ok) throw new Error(data.error || "Analysis failed");
    showResult(data);
  }catch(e){ alert(e.message); }
  finally{ loading.classList.add("hidden"); }
}

function showResult(data){
  results.classList.remove("hidden");
  const score = data.risk_score;
  document.getElementById("riskLevel").textContent = data.risk_level;
  document.getElementById("score").textContent = score;
  document.getElementById("meterBar").style.width = score + "%";
  document.getElementById("recommendation").textContent = data.recommendation;
  document.getElementById("extractedText").textContent = data.extracted_text;
  document.getElementById("disclaimer").textContent = data.disclaimer;

  const indicators = document.getElementById("indicators");
  indicators.innerHTML = "";
  data.indicators.forEach(i => {
    const li = document.createElement("li"); li.textContent = i; indicators.appendChild(li);
  });

  const urls = document.getElementById("urls");
  urls.innerHTML = "";
  if(!data.urls.length){ urls.textContent = "Walang link na nakita."; return; }
  data.urls.forEach(u => {
    const div = document.createElement("div"); div.className = "url-item";
    div.textContent = u.url;
    if(u.reasons.length){
      const small = document.createElement("small");
      small.textContent = u.reasons.join(" • ");
      div.appendChild(small);
    }
    urls.appendChild(div);
  });
  results.scrollIntoView({behavior:"smooth"});
}
