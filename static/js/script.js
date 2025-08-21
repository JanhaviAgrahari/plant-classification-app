// File upload handling
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const resultsSection = document.getElementById('resultsSection');

// Initially hide results section
resultsSection.style.display = 'none';

dropZone.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', function () {
    handleFiles(this.files);
});

// Drag and drop functionality
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

['dragenter', 'dragover'].forEach(eventName => {
    dropZone.addEventListener(eventName, highlight, false);
});

['dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, unhighlight, false);
});

function highlight() {
    dropZone.classList.add('highlight');
}

function unhighlight() {
    dropZone.classList.remove('highlight');
}

dropZone.addEventListener('drop', handleDrop, false);

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    handleFiles(files);
}

function handleFiles(files) {
    if (files.length) {
        const file = files[0];
        if (file.type.startsWith('image/')) {
            displayImage(file);
            uploadAndClassify(file);
        }
    }
}

function displayImage(file) {
    const reader = new FileReader();
    reader.onload = function (e) {
        document.getElementById('uploadedImage').src = e.target.result;
    resultsSection.style.display = 'block';
        // Smooth scroll to results
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }
    reader.readAsDataURL(file);
}

// Replace the simulation with actual API call
function uploadAndClassify(file) {
    console.log("Uploading file:", file.name);

    // Show loading state
    document.getElementById('plantName').textContent = "Analyzing...";
    document.getElementById('scientificName').textContent = "";
    document.getElementById('confidenceText').textContent = "Processing";
    document.getElementById('confidenceFill').style.width = "0%";
    // Hide DB details initially
    const dbDetails = document.getElementById('dbDetails');
    if (dbDetails) dbDetails.style.display = 'none';

    const formData = new FormData();
    formData.append('file', file);

    fetch('/upload-image/', {
        method: 'POST',
        body: formData
    })
        .then(response => {
            console.log("Response status:", response.status);
            if (!response.ok) {
                return response.text().then(text => {
                    console.error("Server error response:", text);
                    throw new Error(`Server error: ${response.status}`);
                });
            }
            return response.json();
        })
        .then(data => {
            console.log("Received data:", data);
            if (data.plant_info) {
                console.log("Plant info from DB:", data.plant_info);
            } else {
                console.log("No plant info found in DB for this classification.");
            }

            // Update UI with prediction results
            const confidencePercent = data.prediction.confidence * 100;

            if (data.prediction.is_plant) {
                document.getElementById('plantName').textContent = data.prediction.class_name;
                if (data.plant_info && data.plant_info.scientific_name) {
                    document.getElementById('scientificName').textContent = data.plant_info.scientific_name;
                } else {
                    document.getElementById('scientificName').textContent = "(Identified Plant)";
                }
                document.getElementById('confidenceText').textContent = `${confidencePercent.toFixed(2)}% confidence`;
                document.getElementById('confidenceFill').style.width = `${confidencePercent}%`;

                // Populate description & other DB driven info if available
                if (data.plant_info) {
                    document.getElementById('plantDescription').textContent = data.plant_info.description || `Identified as ${data.prediction.class_name}.`;
                    // Use origin & uses temporarily in existing slots until custom labels added
                    document.getElementById('lightReq').textContent = data.plant_info.origin || "Origin unknown";
                    document.getElementById('waterReq').textContent = data.plant_info.uses || "Uses info unavailable";
                    // Show DB panel
                    if (dbDetails) {
                        dbDetails.style.display = 'block';
                        document.getElementById('dbFamily').textContent = data.plant_info.family || '—';
                        document.getElementById('dbOrigin').textContent = data.plant_info.origin || '—';
                        document.getElementById('dbUses').textContent = data.plant_info.uses || '—';
                        const dbImageWrapper = document.getElementById('dbImageWrapper');
                        if (data.plant_info.image_url) {
                            document.getElementById('dbImage').src = data.plant_info.image_url;
                            dbImageWrapper.style.display = 'block';
                        } else {
                            dbImageWrapper.style.display = 'none';
                        }
                        console.log('DB details updated in DOM');
                    }
                    // Ensure section is visible (in case not yet shown by displayImage due to async timing)
                    resultsSection.style.display = 'block';
                } else {
                    document.getElementById('lightReq').textContent = "Sunlight requirements vary";
                    document.getElementById('waterReq').textContent = "Check watering needs";
                    document.getElementById('plantDescription').textContent =
                        `This has been identified as ${data.prediction.class_name} with ${confidencePercent.toFixed(2)}% confidence.`;
                }
            } else {
                document.getElementById('plantName').textContent = "Not a recognized plant";
                document.getElementById('scientificName').textContent = "";
                document.getElementById('confidenceText').textContent = `${confidencePercent.toFixed(2)}% confidence`;
                document.getElementById('confidenceFill').style.width = `${confidencePercent}%`;

                document.getElementById('lightReq').textContent = "N/A";
                document.getElementById('waterReq').textContent = "N/A";
                document.getElementById('plantDescription').textContent =
                    "This doesn't appear to be one of the plants our AI can currently identify. Please try with a different image.";
                if (dbDetails) dbDetails.style.display = 'none';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('plantName').textContent = "Error";
            document.getElementById('scientificName').textContent = error.message;
            document.getElementById('plantDescription').textContent = "An error occurred while processing your image. Please try again.";
        });
}

// Plant facts carousel
let currentFact = 0;
const facts = document.querySelectorAll('.fact');
const dots = document.querySelectorAll('.carousel-dot');

function showFact(index) {
    facts.forEach(fact => fact.classList.remove('active'));
    dots.forEach(dot => dot.classList.remove('active'));

    facts[index].classList.add('active');
    dots[index].classList.add('active');
    currentFact = index;
}

// Add click events to dots
dots.forEach(dot => {
    dot.addEventListener('click', function () {
        const index = parseInt(this.getAttribute('data-index'));
        showFact(index);
    });
});

// Auto-rotate facts
setInterval(() => {
    currentFact = (currentFact + 1) % facts.length;
    showFact(currentFact);
}, 5000);

// Initialize the page
document.addEventListener('DOMContentLoaded', function () {
    // Any initialization code can go here
});
