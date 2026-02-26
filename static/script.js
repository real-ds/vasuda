let intervalId = null;
let isRecording = false;

// UI elements
const startBtn = document.getElementById("startBtn");
const modal = document.getElementById("modal");
const modalText = document.getElementById("modalText");
const progressBar = document.getElementById("progressBar");

// Metric elements
const phEl = document.getElementById("ph");
const tempEl = document.getElementById("temp");
const moistureEl = document.getElementById("moisture");
const humidityEl = document.getElementById("humidity");
const riskEl = document.getElementById("riskScore");

// ----------------- CHART SETUP -----------------
const ctx = document.getElementById("soilChart").getContext("2d");

let labels = [];
let moistureData = [];

const soilChart = new Chart(ctx, {
    type: "line",
    data: {
        labels: labels,
        datasets: [{
            label: "Soil Moisture (%)",
            data: moistureData,
            tension: 0.4,
            borderWidth: 2
        }]
    },
    options: {
        responsive: true,
        scales: {
            y: {
                beginAtZero: true,
                max: 100
            }
        }
    }
});

// ----------------- FUNCTIONS -----------------
function updateDashboard(data) {
    phEl.innerText = data.avg_ph;
    tempEl.innerText = data.avg_temp + " °C";
    moistureEl.innerText = data.avg_moisture + " %";
    humidityEl.innerText = data.avg_humidity + " %";
    riskEl.innerText = data.risk_score;
}

function resetChart() {
    labels.length = 0;
    moistureData.length = 0;
    soilChart.update();
}

// ----------------- START TEST -----------------
startBtn.addEventListener("click", async () => {
    if (isRecording) return;

    isRecording = true;
    startBtn.disabled = true;

    // Reset UI
    modal.classList.remove("hidden");
    modalText.innerText = "Recording 0 / 10";
    progressBar.style.width = "0%";
    resetChart();

    await fetch("/start-test", { method: "POST" });

    intervalId = setInterval(async () => {
        // Fetch progress
        const summary = await fetch("/summary").then(res => res.json());
        const count = summary.count || 0;

        progressBar.style.width = (count / 10) * 100 + "%";
        modalText.innerText = `Recording ${count} / 10`;

        // Fetch latest live reading
        const latest = await fetch("/latest").then(res => res.json());
        if (latest.soil_moisture !== undefined) {
            labels.push(`R${labels.length + 1}`);
            moistureData.push(latest.soil_moisture);
            soilChart.update();
        }

        // Finish test
        if (count === 10) {
            clearInterval(intervalId);
            isRecording = false;

            updateDashboard(summary);

            setTimeout(() => {
                modal.classList.add("hidden");
                startBtn.disabled = false;
            }, 600);
        }
    }, 3000);
});