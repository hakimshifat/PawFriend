// Global variables
let map;
let userMarker;
let clinicMarkers = [];
let directionsService;
let directionsRenderer;
let userLocation = { lat: parseFloat(USER_LAT), lng: parseFloat(USER_LNG) };

// Initialize the map
function initMap() {
    // Create a new map centered on the user's location
    map = new google.maps.Map(document.getElementById('map'), {
        center: userLocation,
        zoom: 12,
        styles: [
            {
                "featureType": "poi.business",
                "stylers": [{ "visibility": "on" }]
            },
            {
                "featureType": "poi.medical",
                "stylers": [{ "visibility": "on" }]
            }
        ]
    });
    
    // Create a marker for the user's location
    userMarker = new google.maps.Marker({
        position: userLocation,
        map: map,
        title: 'Your Location',
        icon: {
            path: google.maps.SymbolPath.CIRCLE,
            scale: 10,
            fillColor: '#4285F4',
            fillOpacity: 1,
            strokeWeight: 2,
            strokeColor: '#FFFFFF'
        }
    });
    
    // Initialize directions service and renderer
    directionsService = new google.maps.DirectionsService();
    directionsRenderer = new google.maps.DirectionsRenderer({
        map: map,
        suppressMarkers: true,
        polylineOptions: {
            strokeColor: '#FF0000',
            strokeWeight: 5,
            strokeOpacity: 0.7
        }
    });
    
    // Add the nearest clinic marker if available
    if (NEAREST_CLINIC) {
        const clinicPosition = {
            lat: NEAREST_CLINIC.lat,
            lng: NEAREST_CLINIC.lng
        };
        
        addClinicMarker(
            clinicPosition.lat,
            clinicPosition.lng,
            NEAREST_CLINIC.name,
            NEAREST_CLINIC.distance,
            NEAREST_CLINIC.isEmergency
        );
        
        // Fit bounds to include both user and clinic
        const bounds = new google.maps.LatLngBounds();
        bounds.extend(userLocation);
        bounds.extend(clinicPosition);
        map.fitBounds(bounds);
    }
    
    // Set up event listeners
    setupEventListeners();
}

// Get user's current location
function getUserLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                const lat = position.coords.latitude;
                const lng = position.coords.longitude;
                updateUserLocation(lat, lng);
            },
            (error) => {
                console.error('Error getting location:', error);
                alert('Unable to get your location. Please enter your address or try again.');
            }
        );
    } else {
        alert('Geolocation is not supported by your browser.');
    }
}

// Update user location on map
function updateUserLocation(lat, lng) {
    userLocation = { lat, lng };
    
    // Update user marker
    userMarker.setPosition(userLocation);
    
    // Center map on new location
    map.setCenter(userLocation);
    
    // Auto-search for nearest clinic
    searchNearestClinic(lat, lng);
}

// Add a clinic marker to the map
function addClinicMarker(lat, lng, name, distance, isEmergency) {
    const clinicPosition = { lat, lng };
    
    // Create marker
    const marker = new google.maps.Marker({
        position: clinicPosition,
        map: map,
        title: name,
        icon: {
            url: 'https://maps.google.com/mapfiles/ms/icons/' + (isEmergency ? 'red' : 'blue') + '-dot.png'
        },
        animation: google.maps.Animation.DROP
    });
    
    // Create info window
    const infoWindow = new google.maps.InfoWindow({
        content: `
            <div style="padding: 10px; max-width: 200px;">
                <h5 style="margin-top: 0;">${name}</h5>
                <p style="margin-bottom: 5px;">
                    ${isEmergency ? 
                        '<span style="color: red; font-weight: bold;">24/7 Emergency Care</span>' : 
                        '<span>Standard Hours</span>'}
                </p>
                <p style="margin-bottom: 0;">
                    <strong>${distance} km</strong> from your location
                </p>
            </div>
        `
    });
    
    // Add click listener to open info window
    marker.addListener('click', () => {
        // Close any open info windows
        clinicMarkers.forEach(m => {
            if (m.infoWindow) m.infoWindow.close();
        });
        
        // Open this info window
        infoWindow.open(map, marker);
        
        // Calculate and display route
        calculateAndDisplayRoute(userLocation, clinicPosition);
    });
    
    // Store the marker and info window
    clinicMarkers.push({
        marker: marker,
        infoWindow: infoWindow,
        position: clinicPosition,
        name: name,
        isEmergency: isEmergency,
        distance: distance
    });
    
    return marker;
}

// Clear all clinic markers from the map
function clearClinicMarkers() {
    clinicMarkers.forEach(m => {
        m.marker.setMap(null);
        if (m.infoWindow) m.infoWindow.close();
    });
    
    clinicMarkers = [];
    
    // Clear directions
    directionsRenderer.setDirections({ routes: [] });
}

// Calculate and display route between two points
function calculateAndDisplayRoute(origin, destination) {
    directionsService.route(
        {
            origin: origin,
            destination: destination,
            travelMode: google.maps.TravelMode.DRIVING
        },
        (response, status) => {
            if (status === google.maps.DirectionsStatus.OK) {
                directionsRenderer.setDirections(response);
                
                // Display directions info
                const route = response.routes[0];
                const leg = route.legs[0];
                
                // Update UI with directions info (if needed)
                console.log(`Distance: ${leg.distance.text}, Duration: ${leg.duration.text}`);
            } else {
                console.error('Directions request failed due to ' + status);
            }
        }
    );
}

// Set up event listeners for buttons
function setupEventListeners() {
    // Use current location button
    document.getElementById('use-current-location').addEventListener('click', getUserLocation);
    
    // Find nearest clinic button
    document.getElementById('find-nearest').addEventListener('click', () => {
        searchNearestClinic(userLocation.lat, userLocation.lng);
    });
    
    // Show all clinics button
    document.getElementById('show-all-clinics').addEventListener('click', showAllClinics);
    
    // Get directions button
    const getDirectionsBtn = document.getElementById('get-directions');
    if (getDirectionsBtn && NEAREST_CLINIC) {
        getDirectionsBtn.addEventListener('click', () => {
            const clinicPosition = {
                lat: NEAREST_CLINIC.lat,
                lng: NEAREST_CLINIC.lng
            };
            
            calculateAndDisplayRoute(userLocation, clinicPosition);
            
            // Scroll to map
            document.getElementById('map').scrollIntoView({ behavior: 'smooth' });
        });
    }
    
    // View on map buttons for clinic cards
    document.querySelectorAll('.view-on-map').forEach(btn => {
        btn.addEventListener('click', function() {
            const clinicId = this.getAttribute('data-id');
            // This would usually fetch clinic data from the server
            // For this demo, we'll use hardcoded data based on ID
            
            // Create a fake API response
            const clinicData = {
                "1": { name: "Downtown Pet Hospital", lat: 40.7128, lng: -74.0060, isEmergency: true },
                "3": { name: "Brooklyn Veterinary Center", lat: 40.6782, lng: -73.9442, isEmergency: true },
                "5": { name: "Bronx Animal Hospital", lat: 40.8448, lng: -73.8648, isEmergency: true }
            };
            
            if (clinicData[clinicId]) {
                const clinic = clinicData[clinicId];
                const distance = calculateDistance(
                    userLocation.lat, userLocation.lng,
                    clinic.lat, clinic.lng
                );
                
                // Clear existing markers
                clearClinicMarkers();
                
                // Add the selected clinic marker
                addClinicMarker(
                    clinic.lat, clinic.lng,
                    clinic.name, distance.toFixed(2),
                    clinic.isEmergency
                );
                
                // Calculate route
                calculateAndDisplayRoute(
                    userLocation,
                    { lat: clinic.lat, lng: clinic.lng }
                );
                
                // Fit bounds to include both user and clinic
                const bounds = new google.maps.LatLngBounds();
                bounds.extend(userLocation);
                bounds.extend({ lat: clinic.lat, lng: clinic.lng });
                map.fitBounds(bounds);
                
                // Scroll to map
                document.getElementById('map').scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
}

// Search for nearest clinic
function searchNearestClinic(lat, lng) {
    // In a real application, this would make an AJAX request to the server
    // For this demo, we'll simulate a response with the pre-loaded NEAREST_CLINIC data
    
    // Clear existing markers
    clearClinicMarkers();
    
    if (NEAREST_CLINIC) {
        const clinicPosition = {
            lat: NEAREST_CLINIC.lat,
            lng: NEAREST_CLINIC.lng
        };
        
        // Recalculate distance based on current location
        const distance = calculateDistance(
            lat, lng,
            clinicPosition.lat, clinicPosition.lng
        );
        
        // Add clinic marker
        addClinicMarker(
            clinicPosition.lat,
            clinicPosition.lng,
            NEAREST_CLINIC.name,
            distance.toFixed(2),
            NEAREST_CLINIC.isEmergency
        );
        
        // Calculate route
        calculateAndDisplayRoute(userLocation, clinicPosition);
        
        // Fit bounds to include both user and clinic
        const bounds = new google.maps.LatLngBounds();
        bounds.extend(userLocation);
        bounds.extend(clinicPosition);
        map.fitBounds(bounds);
    } else {
        alert('No emergency clinics found nearby. Please try again later.');
    }
}

// Show all clinics on the map
function showAllClinics() {
    // In a real application, this would fetch all clinics from the server
    // For this demo, we'll use hardcoded data
    
    // Clear existing markers
    clearClinicMarkers();
    
    // Sample clinic data
    const clinics = [
        { id: "1", name: "Downtown Pet Hospital", lat: 40.7128, lng: -74.0060, isEmergency: true },
        { id: "2", name: "Uptown Animal Clinic", lat: 40.7831, lng: -73.9712, isEmergency: false },
        { id: "3", name: "Brooklyn Veterinary Center", lat: 40.6782, lng: -73.9442, isEmergency: true },
        { id: "4", name: "Queens Pet Care", lat: 40.7282, lng: -73.7949, isEmergency: false },
        { id: "5", name: "Bronx Animal Hospital", lat: 40.8448, lng: -73.8648, isEmergency: true }
    ];
    
    // Add markers for all clinics
    const bounds = new google.maps.LatLngBounds();
    bounds.extend(userLocation);
    
    clinics.forEach(clinic => {
        // Calculate distance
        const distance = calculateDistance(
            userLocation.lat, userLocation.lng,
            clinic.lat, clinic.lng
        );
        
        // Add marker
        addClinicMarker(
            clinic.lat, clinic.lng,
            clinic.name, distance.toFixed(2),
            clinic.isEmergency
        );
        
        bounds.extend({ lat: clinic.lat, lng: clinic.lng });
    });
    
    // Fit map to show all markers
    map.fitBounds(bounds);
}

// Calculate distance between two points using the Haversine formula
function calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371; // Radius of the earth in km
    const dLat = deg2rad(lat2 - lat1);
    const dLon = deg2rad(lon2 - lon1);
    const a = 
        Math.sin(dLat/2) * Math.sin(dLat/2) +
        Math.cos(deg2rad(lat1)) * Math.cos(deg2rad(lat2)) * 
        Math.sin(dLon/2) * Math.sin(dLon/2); 
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a)); 
    const distance = R * c; // Distance in km
    return distance;
}

function deg2rad(deg) {
    return deg * (Math.PI/180);
}
