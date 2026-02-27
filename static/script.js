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

    // Strip markdown to plain text for cleaner translation
    const plainText = currentRecommendation
      .replace(/#{1,6}\s*/g, '')          // headers
      .replace(/\*\*(.+?)\*\*/g, '$1')    // bold
      .replace(/\*(.+?)\*/g, '$1')        // italic
      .replace(/`(.+?)`/g, '$1')          // inline code
      .replace(/- /g, '• ')              // bullet points
      .replace(/\n{3,}/g, '\n\n')        // excess newlines
      .trim();

    try {
      const response = await fetch("/translate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: plainText,
          language: targetLang
        })
      });
      const data = await response.json();
      
      if (data.translated) {
        aiModalContent.innerHTML = marked.parse(data.translated);
      } else if (data.error) {
        aiModalContent.innerHTML = `<p style="color:#c62828;">⚠️ Translation failed: ${data.error}</p>`;
      } else {
        aiModalContent.innerHTML = `<p style="color:#c62828;">⚠️ Translation returned empty. Try again.</p>`;
      }
    } catch (e) {
      console.error("Translate Error:", e);
      aiModalContent.innerHTML = `<p style="color:#c62828;">❌ Network error. Check your connection and try again.</p>`;
    } finally {
      translateBtn.innerText = "🌐 Translate";
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

    riskEl.innerText = 100 - finalRisk;
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

        // Update Sustainable Index (100 - SHRS)
        if (data.shrs !== undefined) {
          riskEl.innerText = 100 - data.shrs;
        }

        // Trend display
        const trendDisplay = document.getElementById("trendDisplay");
        const trendIcon = document.getElementById("trendIcon");
        const trendValue = document.getElementById("trendValue");
        if (data.trend && trendDisplay) {
          const trendMap = {
            "Increasing Risk": { icon: "📈", color: "#c62828" },
            "Decreasing Risk": { icon: "📉", color: "#2e7d32" },
            "Stable": { icon: "➡️", color: "var(--text-light)" },
            "Insufficient Data": { icon: "❓", color: "var(--text-light)" }
          };
          const t = trendMap[data.trend] || trendMap["Insufficient Data"];
          trendIcon.textContent = t.icon;
          trendValue.textContent = data.trend;
          trendValue.style.color = t.color;
          trendDisplay.style.opacity = "1";
        }

        // Practice escalation warnings
        const warningEl = document.getElementById("practiceWarning");
        if (data.practice_warning && data.practice_warning.length > 0 && warningEl) {
          warningEl.innerHTML = data.practice_warning
            .map(w => `🚨 ${w}`)
            .join("<br>");
          warningEl.style.display = "block";
        } else if (warningEl) {
          warningEl.style.display = "none";
        }

      } else {
        aiAdviceEl.innerText = "⚠️ No AI recommendation generated.";
      }

    } catch (err) {
      console.error("AI ERROR:", err);
      aiAdviceEl.innerText =
        "❌ AI service unavailable. Please try again.";
    }

    // Refresh history sidebar after test
    loadHistory();
  };

  // ========== SIDEBAR LOGIC ==========
  const sidebar = document.getElementById("historySidebar");
  const sidebarToggle = document.getElementById("sidebarToggle");
  const historyList = document.getElementById("historyList");
  const clearHistoryBtn = document.getElementById("clearHistoryBtn");
  const dashboardEl = document.querySelector(".dashboard");

  let sidebarOpen = false;

  if (sidebarToggle) {
    sidebarToggle.onclick = () => {
      sidebarOpen = !sidebarOpen;
      sidebar.classList.toggle("open", sidebarOpen);
      sidebarToggle.classList.toggle("shifted", sidebarOpen);
      if (dashboardEl) dashboardEl.classList.toggle("shifted", sidebarOpen);
      sidebarToggle.querySelector(".toggle-icon").textContent = sidebarOpen ? "✕" : "📋";
    };
  }

  if (clearHistoryBtn) {
    clearHistoryBtn.onclick = async () => {
      await fetch("/history/clear", { method: "POST" });
      loadHistory();
    };
  }

  async function loadHistory() {
    try {
      const res = await fetch("/history");
      const records = await res.json();

      if (!records.length) {
        historyList.innerHTML = `<div class="sidebar-empty">No tests recorded yet.<br>Run a test to see records here.</div>`;
        return;
      }

      historyList.innerHTML = records.map(r => {
        const shrsClass = r.shrs <= 30 ? "shrs-low" : r.shrs <= 60 ? "shrs-mid" : "shrs-high";
        const trendIcons = {
          "Increasing Risk": "📈",
          "Decreasing Risk": "📉",
          "Stable": "➡️",
          "Insufficient Data": "❓"
        };
        const trendIcon = trendIcons[r.trend] || "❓";

        return `
          <div class="history-item" data-id="${r.id}" onclick="loadRecord(${r.id})">
            <div class="history-item-top">
              <span class="history-id">Test #${r.id}</span>
              <span class="history-shrs ${shrsClass}">SHRS ${r.shrs}</span>
            </div>
            <div class="history-details">
              <span class="history-tag">pH ${r.sensor.ph}</span>
              <span class="history-tag">${r.sensor.temp}°C</span>
              <span class="history-tag">💧 ${r.sensor.moisture}%</span>
              <span class="history-tag">🌿 ${r.practices.crop || "—"}</span>
            </div>
            <div class="history-trend">${trendIcon} ${r.trend}</div>
            <div class="history-time">${r.timestamp}</div>
          </div>
        `;
      }).join("");
    } catch (e) {
      console.error("Failed to load history:", e);
    }
  }

  // Make loadRecord globally accessible
  window.loadRecord = function(id) {
    fetch("/history")
      .then(r => r.json())
      .then(records => {
        const record = records.find(r => r.id === id);
        if (!record) return;

        // Highlight active item
        document.querySelectorAll(".history-item").forEach(el => el.classList.remove("active"));
        const activeEl = document.querySelector(`[data-id="${id}"]`);
        if (activeEl) activeEl.classList.add("active");

        // Populate dashboard fields
        phEl.innerText = record.sensor.ph;
        tempEl.innerText = record.sensor.temp;
        moistureEl.innerText = record.sensor.moisture;
        humidityEl.innerText = record.sensor.humidity;
        riskEl.innerText = 100 - record.shrs;
        cropDisplay.innerText = record.practices.crop || "--";
        irrigationDisplay.innerText = record.practices.irrigation || "--";
        fertilizerDisplay.innerText = record.practices.fertilizer || "--";

        // Populate AI advice
        if (record.recommendation) {
          currentRecommendation = record.recommendation;
          const formattedText = marked.parse(currentRecommendation);
          aiAdviceEl.innerHTML = formattedText;
          aiModalContent.innerHTML = formattedText;
          readMoreBtn.classList.remove("hidden");
        }

        // Populate trend
        const trendDisplay = document.getElementById("trendDisplay");
        const trendIcon = document.getElementById("trendIcon");
        const trendValueEl = document.getElementById("trendValue");
        if (trendDisplay && record.trend) {
          const tMap = {
            "Increasing Risk": { icon: "📈", color: "#c62828" },
            "Decreasing Risk": { icon: "📉", color: "#2e7d32" },
            "Stable": { icon: "➡️", color: "var(--text-light)" },
            "Insufficient Data": { icon: "❓", color: "var(--text-light)" }
          };
          const t = tMap[record.trend] || tMap["Insufficient Data"];
          trendIcon.textContent = t.icon;
          trendValueEl.textContent = record.trend;
          trendValueEl.style.color = t.color;
          trendDisplay.style.opacity = "1";
        }
      });
  };

  // Load history on page load
  loadHistory();
});