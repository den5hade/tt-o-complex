document.addEventListener('DOMContentLoaded', function() {
    const cityInput = document.getElementById('cityInput');
    const searchBtn = document.getElementById('searchBtn');
    const weatherResults = document.getElementById('weatherResults');
    const recentCitiesContainer = document.getElementById('recentCities');

    // Load recent cities from localStorage
    let recentCities = JSON.parse(localStorage.getItem('recentCities') || '[]');
    updateRecentCities();

    // Handle search button click
    searchBtn.addEventListener('click', searchWeather);

    // Handle Enter key press
    cityInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            searchWeather();
        }
    });

    // Search weather function
    async function searchWeather() {
        const city = cityInput.value.trim();
        if (!city) return;

        try {
            const response = await fetch(`/api/weather/${encodeURIComponent(city)}`);
            if (!response.ok) {
                throw new Error('City not found');
            }
            
            const data = await response.json();
            displayWeather(data);
            
            // Update recent cities
            updateRecentCitiesList(city);
        } catch (error) {
            weatherResults.innerHTML = `
                <div class="alert alert-danger" role="alert">
                    ${error.message}
                </div>
            `;
        }
    }

    // Display weather data
    function displayWeather(data) {
        const forecast = data.forecast;
        const currentTemp = forecast.hourly.temperature_2m[0];
        const currentPrecip = forecast.hourly.precipitation_probability[0];
        
        weatherResults.innerHTML = `
            <div class="weather-card">
                <h3>${data.city}</h3>
                <div class="temperature">${currentTemp}°C</div>
                <div class="weather-details">
                    <div class="weather-detail-item">
                        <div>Precipitation</div>
                        <div>${currentPrecip}%</div>
                    </div>
                    <div class="weather-detail-item">
                        <div>Max Today</div>
                        <div>${forecast.daily.temperature_2m_max[0]}°C</div>
                    </div>
                    <div class="weather-detail-item">
                        <div>Min Today</div>
                        <div>${forecast.daily.temperature_2m_min[0]}°C</div>
                    </div>
                </div>
            </div>
        `;
    }

    // Update recent cities list
    function updateRecentCitiesList(city) {
        recentCities = [city, ...recentCities.filter(c => c !== city)].slice(0, 5);
        localStorage.setItem('recentCities', JSON.stringify(recentCities));
        updateRecentCities();
    }

    // Update recent cities display
    function updateRecentCities() {
        recentCitiesContainer.innerHTML = recentCities
            .map(city => `
                <div class="recent-city-chip" onclick="document.getElementById('cityInput').value = '${city}'; searchWeather();">
                    ${city}
                </div>
            `)
            .join('');
    }
}); 