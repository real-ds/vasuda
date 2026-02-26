document.addEventListener("DOMContentLoaded", () => {

  let intervalId = null;

  const startBtn = document.getElementById("startBtn");
  const sensorModal = document.getElementById("sensorModal");
  const farmerModal = document.getElementById("farmerModal");
  const progressBar = document.getElementById("progressBar");
  const sensorText = document.getElementById("sensorText");

  const cropDisplay = document.getElementById("cropDisplay");
  const irrigationDisplay = document.getElementById("irrigationDisplay");
  const fertilizerDisplay = document.getElementById("fertilizerDisplay");

  const phEl = document.getElementById("ph");
  const tempEl = document.getElementById("temp");
  const moistureEl = document.getElementById("moisture");
  const humidityEl = document.getElementById("humidity");
  const riskEl = document.getElementById("riskScore");
  const aiAdviceEl = document.getElementById("aiAdvice");
  const readMoreBtn = document.getElementById("readMoreBtn");
  const aiModal = document.getElementById("aiModal");
  const aiModalContent = document.getElementById("aiModalContent");

  // ---------- AI MODAL LOGIC ----------
  readMoreBtn.onclick = () => {
    aiModal.classList.remove("hidden");
  };

  // Close AI modal when clicking outside
  aiModal.onclick = (e) => {
    if (e.target === aiModal) {
      aiModal.classList.add("hidden");
    }
  };

  const langSelect = document.getElementById("langSelect");
  const translateBtn = document.getElementById("translateBtn");
  let currentRecommendation = "";

  translateBtn.onclick = async () => {
    if (!currentRecommendation) return;
    const targetLang = langSelect.value;
    
    translateBtn.innerText = "Translating...";
    translateBtn.disabled = true;

    try {
      const response = await fetch("/translate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: currentRecommendation,
          language: targetLang
        })
      });
      const data = await response.json();
      
      if (data.translated) {
        aiModalContent.innerHTML = marked.parse(data.translated);
      } else {
        alert("Translation failed.");
      }
    } catch (e) {
      console.error("Translate Error:", e);
      alert("Error translating content.");
    } finally {
      translateBtn.innerText = "Translate";
      translateBtn.disabled = false;
    }
  };
  
  // ---------- START TEST ----------
  startBtn.onclick = async () => {
    sensorModal.classList.remove("hidden");
    progressBar.style.width = "0%";
    sensorText.innerText = "0 / 10";

    await fetch("/start-test", { method: "POST" });

    intervalId = setInterval(async () => {
      const summary = await fetch("/summary").then(r => r.json());
      const count = summary.count || 0;

      progressBar.style.width = (count * 10) + "%";
      sensorText.innerText = `${count} / 10`;

      if (count === 10) {
        clearInterval(intervalId);
        sensorModal.classList.add("hidden");
        farmerModal.classList.remove("hidden");

        window.soilConditionRisk = summary.soil_condition_risk;

        phEl.innerText = summary.avg_ph;
        tempEl.innerText = summary.avg_temp;
        moistureEl.innerText = summary.avg_moisture;
        humidityEl.innerText = summary.avg_humidity;
      }
    }, 3000);
  };

  // ---------- COMPUTE RISK + AI ----------
  document.getElementById("computeRisk").onclick = async () => {

    const crop = document.getElementById("crop").value;
    const irrigation = document.getElementById("irrigation").value;
    const fertilizer = document.getElementById("fertilizer").value;

    cropDisplay.innerText = crop;
    irrigationDisplay.innerText = irrigation;
    fertilizerDisplay.innerText = fertilizer;

    const cropRisk = { Rice:10, Wheat:15, Maize:20, Cotton:30, Vegetables:25 };
    const irrigationRisk = {
      "Daily":5, "Alternate Days":10, "Weekly":20, "Irregular":30
    };
    const fertilizerRisk = {
      "Weekly":5, "Monthly":10, "Rare":20, "None":30
    };

    const practiceRisk =
      cropRisk[crop] +
      irrigationRisk[irrigation] +
      fertilizerRisk[fertilizer];

    const finalRisk = Math.round(
      0.6 * window.soilConditionRisk +
      0.4 * practiceRisk
    );

    riskEl.innerText = finalRisk;
    farmerModal.classList.add("hidden");

    // ---------- FORCE AI ----------
    aiAdviceEl.innerText = "🔍 Generating AI recommendations...";
    console.log("AI CALL STARTED");

    try {
      const response = await fetch("/ai-recommendation", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          avg_ph: parseFloat(phEl.innerText),
          avg_temp: parseFloat(tempEl.innerText),
          avg_moisture: parseFloat(moistureEl.innerText),
          avg_humidity: parseFloat(humidityEl.innerText),
          crop,
          irrigation,
          fertilizer,
          risk_score: finalRisk
        })
      });

      const data = await response.json();
      console.log("AI RESPONSE:", data);

      if (data.recommendation) {
        currentRecommendation = data.recommendation;
        // Parse markdown text using marked library added to base.html
        const formattedText = marked.parse(currentRecommendation);
        aiAdviceEl.innerHTML = formattedText;
        aiModalContent.innerHTML = formattedText;
        readMoreBtn.classList.remove("hidden");
        if(langSelect) langSelect.value = "Hindi"; // reset select
        if(translateBtn) {
            translateBtn.innerText = "Translate";
            translateBtn.disabled = false;
        }
      } else {
        aiAdviceEl.innerText = "⚠️ No AI recommendation generated.";
      }

    } catch (err) {
      console.error("AI ERROR:", err);
      aiAdviceEl.innerText =
        "❌ AI service unavailable. Please try again.";
    }
  };
});