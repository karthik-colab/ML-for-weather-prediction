// Placeholder for JavaScript functionality
document.getElementById('predict-btn').addEventListener('click', function() {
    const location = document.getElementById('location').value;
    const date = document.getElementById('date').value;
    const resultDiv = document.getElementById('result');
    const forecastLocation = document.getElementById('forecast-location');

    if (location && date) {
        // Simulate prediction
        const temperature = Math.floor(Math.random() * 30) + 10; // Random temp between 10-40
        resultDiv.innerHTML = `Temperature for ${location} on ${date} is<br><span class="highlight">${temperature}°C <img src="clear.png" alt="Sunny" style="width: 30px;"></span>`;
        forecastLocation.textContent = location;
    } else {
        resultDiv.innerHTML = 'Please enter both location and date.';
    }
});
