// Initialize the map centered on Pasig City
const map = L.map('map').setView([14.5764, 121.0851], 13);

// Add OpenStreetMap tiles
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

// Store markers for businesses
const businessMarkers = {};

// Function to add a business marker to the map
function addBusinessMarker(business) {
    const marker = L.marker([business.latitude, business.longitude])
        .bindPopup(`
            <strong>${business.business_name}</strong><br>
            Type: ${business.business_type}<br>
            Address: ${business.address}<br>
            Barangay: ${business.barangay}<br>
            <button onclick="showBusinessDetails(${business.id})">View Details</button>
        `);
    
    marker.addTo(map);
    businessMarkers[business.id] = marker;
}

// Function to show business details
function showBusinessDetails(businessId) {
    fetch(`/api/businesses/${businessId}`)
        .then(response => response.json())
        .then(data => {
            // Update the business statistics panel
            const statsHtml = `
                <h6>${data.business_name}</h6>
                <div class="row">
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-body">
                                <h6>Current Revenue</h6>
                                <p>₱${data.current_revenue.toLocaleString()}</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-body">
                                <h6>Predicted Growth</h6>
                                <p>${data.growth_prediction}%</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-body">
                                <h6>Business Status</h6>
                                <p>${data.status}</p>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            document.getElementById('businessStats').innerHTML = statsHtml;
        })
        .catch(error => console.error('Error:', error));
}

// Function to load all businesses
function loadBusinesses() {
    fetch('/bploop-capstone/public/api/businesses.php')
        .then(response => response.json())
        .then(response => {
            if (response.success && Array.isArray(response.data)) {
                response.data.forEach(business => {
                    addBusinessMarker(business);
                });
            } else {
                console.error("API did not return expected data:", response);
            }
        })
        .catch(error => console.error('Error:', error));
}

// Function to filter businesses by type
function filterBusinesses(businessType) {
    // Clear existing markers
    Object.values(businessMarkers).forEach(marker => marker.remove());
    businessMarkers = {};

    // Load filtered businesses
    fetch(`/api/businesses?type=${businessType}`)
        .then(response => response.json())
        .then(businesses => {
            businesses.forEach(business => {
                addBusinessMarker(business);
            });
        })
        .catch(error => console.error('Error:', error));
}

// Function to show business clusters
function showBusinessClusters() {
    // Implement clustering logic here
    // This could use Leaflet.MarkerCluster plugin
}

// Load businesses when the page loads
document.addEventListener('DOMContentLoaded', loadBusinesses);

// Add event listeners for filters
document.getElementById('businessTypeFilter')?.addEventListener('change', (e) => {
    filterBusinesses(e.target.value);
}); 