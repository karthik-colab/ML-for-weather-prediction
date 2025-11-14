document.getElementById('predict-btn').addEventListener('click', async function() {
    const location = document.getElementById('location').value.trim();
    const date = document.getElementById('date').value.trim();
    const resultDiv = document.getElementById('result');
    const forecastLocation = document.getElementById('forecast-location');
    const forecastBoxes = document.querySelector('.forecast-boxes');
    const recommendations = document.querySelector('.recommendations p');

    if (!location || !date) {
        resultDiv.innerHTML = '⚠️ Please enter both location and date.';
        return;
    }

    resultDiv.innerHTML = '⏳ Predicting...';

    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ location, date })
        });

        const data = await response.json();

        if (data.error) {
            resultDiv.innerHTML = `❌ ${data.error}`;
            return;
        }

        // Display single-day prediction
        resultDiv.innerHTML = `
            🌤️ Temperature for <b>${data.location}</b> on ${data.date}: 
            <br><span class="highlight">${data.temperature}°C</span>
        `;

        forecastLocation.textContent = data.location;

        // Function to decide icon based on temp
        const getIcon = (temp) => {
            if (temp > 32) return "clear.png";
            else if (temp > 25) return "drizzel.png";
            else if (temp > 20) return "mist.png";
            else if (temp > 15) return "rain.png";
            else return "cloude.png";
        };

        // Display 7-day forecast
        forecastBoxes.innerHTML = '';
        data.forecast.forEach(day => {
            const icon = getIcon(day.temp);
            forecastBoxes.innerHTML += `
                <div class="day-box">
                    <p>${day.date}</p>
                    <!-- ✅ FIX: Load from static folder -->
                    <img src="/static/${icon}" alt="Weather Icon">
                    <p>${day.temp}°C</p>
                </div>
            `;
        });

        // Display recommendation
        recommendations.textContent = data.recommendation;

    } catch (error) {
        resultDiv.innerHTML = '❌ Error connecting to server.';
    }
});
