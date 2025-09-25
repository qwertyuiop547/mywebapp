// Barangay Burgos, Basey, Samar coordinates (approximate center)
const BARANGAY_CENTER = [11.2588, 125.0078];
let map;
let residentsLayer;
let satelliteLayer;
let isSatelliteView = false;

document.addEventListener('DOMContentLoaded', function() {
    initializeMap();
    loadResidents();
});

function initializeMap() {
    // Initialize the map
    map = L.map('residents-map').setView(BARANGAY_CENTER, 15);
    
    // Add OpenStreetMap tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© <a href="https://openstreetmap.org">OpenStreetMap</a> contributors',
        maxZoom: 19
    }).addTo(map);
    
    // Add satellite layer (Esri World Imagery)
    satelliteLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        attribution: 'Tiles © Esri'
    });
    
    // Create layer group for residents
    residentsLayer = L.layerGroup().addTo(map);
    
    // Add barangay boundary marker
    const barangayMarker = L.marker(BARANGAY_CENTER, {
        icon: L.divIcon({
            html: '<i class="fas fa-building" style="color: #dc3545; font-size: 20px;"></i>',
            iconSize: [30, 30],
            className: 'barangay-marker'
        })
    }).addTo(map);
    
    barangayMarker.bindPopup('<div class="text-center"><strong>Barangay Burgos Hall</strong><br><small>Basey, Samar</small></div>');
}

function loadResidents() {
    // Get residents data from global variable set by Django template
    const residentsData = window.residentsData || [];
    
    // Filter out residents without valid coordinates
    const residents = residentsData.filter(resident => 
        resident.lat !== null && resident.lng !== null && 
        resident.lat !== 0 && resident.lng !== 0
    );
    
    residents.forEach(function(resident) {
        if (resident.lat && resident.lng) {
            const marker = L.marker([resident.lat, resident.lng], {
                icon: L.divIcon({
                    html: `<div style="
                        background: #0038a8; 
                        width: 20px; 
                        height: 20px; 
                        border-radius: 50%; 
                        border: 3px solid white;
                        box-shadow: 0 2px 5px rgba(0,0,0,0.3);
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    ">
                        <i class="fas fa-home" style="color: white; font-size: 8px;"></i>
                    </div>`,
                    iconSize: [26, 26],
                    className: 'resident-marker'
                })
            });
            
            marker.bindPopup(`
                <div class="resident-popup">
                    <div class="name">${resident.name}</div>
                    <div class="address">${resident.address}</div>
                    <div style="margin-top: 8px; font-size: 11px; color: #28a745;">
                        <i class="fas fa-check-circle"></i> Approved Resident
                    </div>
                </div>
            `);
            
            residentsLayer.addLayer(marker);
        }
    });
    
    // Fit map to show all residents
    if (residentsLayer.getLayers().length > 0) {
        const group = new L.featureGroup(residentsLayer.getLayers());
        map.fitBounds(group.getBounds().pad(0.1));
    }
}

function centerMap() {
    map.setView(BARANGAY_CENTER, 15);
}

function toggleSatellite() {
    if (isSatelliteView) {
        map.removeLayer(satelliteLayer);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© <a href="https://openstreetmap.org">OpenStreetMap</a> contributors',
            maxZoom: 19
        }).addTo(map);
        isSatelliteView = false;
    } else {
        map.eachLayer(function(layer) {
            if (layer instanceof L.TileLayer) {
                map.removeLayer(layer);
            }
        });
        satelliteLayer.addTo(map);
        isSatelliteView = true;
    }
}

// Filter functionality
document.addEventListener('DOMContentLoaded', function() {
    const filterSelect = document.getElementById('filter-by-area');
    if (filterSelect) {
        filterSelect.addEventListener('change', function() {
            const selectedArea = this.value;
            
            residentsLayer.eachLayer(function(layer) {
                if (selectedArea === '') {
                    layer.setOpacity(1);
                } else {
                    // This is a placeholder - you would implement actual filtering logic
                    // based on resident zones or areas
                    layer.setOpacity(0.5);
                }
            });
        });
    }
});
