function displayFileName() {
    const fileInputs = document.querySelectorAll('[id^="file-upload"]');
    const fileNameDisplays = document.querySelectorAll('[id^="file-name"]');

    fileInputs.forEach((fileInput, index) => {
        const fileNameDisplay = fileNameDisplays[index];
        fileNameDisplay.textContent = fileInput.files?.[0]?.name || '';
    });
}

// Attach the displayFileName handler to all file inputs
document.querySelectorAll('[id^="file-upload"]').forEach(input => {
    input.addEventListener('change', displayFileName);
});

const fileInput = document.getElementById("multi-file-upload");
const filesContainer = document.getElementById("files-container");
const fileUploadSection = document.querySelector("form.flex");

const uploadForm = document.getElementById("upload-form");
const clearButton = document.getElementById("clear-button");

fileInput.addEventListener("change", function () {
    const files = this.files;
    filesContainer.innerHTML = ""; // Clear previous files

    if (files.length > 0) {
        // Hide the upload section and show the buttons
        fileUploadSection.style.display = "none";
        

        // Create cards for each file
        Array.from(files).forEach(file => {
            const card = createFileCard(file.name);
            filesContainer.appendChild(card);
        });
    } else {
        // Reset UI if no files
        resetUI();
    }

    // Automatically submit the form
    uploadForm.submit();
});

// Clear button functionality
clearButton.addEventListener("click", resetUI);

// Helper: Create a file card
function createFileCard(fileName) {
    const card = document.createElement("div");
    card.className = "border-2 border-deep-blue rounded-lg p-6 flex flex-col items-center justify-center shadow-md text-center";
    card.style.width = "200px";

    const img = document.createElement("img");
    img.src = "/static/images/File.png";
    img.alt = "File Icon";
    img.className = "h-14 mb-4";

    const fileNameDiv = document.createElement("div");
    fileNameDiv.className = "text-deep-blue font-bold text-center";
    fileNameDiv.textContent = fileName;
    fileNameDiv.style.whiteSpace = "normal";
    fileNameDiv.style.wordWrap = "break-word";
    fileNameDiv.style.overflow = "hidden";
    fileNameDiv.style.textOverflow = "ellipsis";
    fileNameDiv.style.maxWidth = "180px";
    fileNameDiv.style.display = "-webkit-box";
    fileNameDiv.style.webkitLineClamp = "2";
    fileNameDiv.style.webkitBoxOrient = "vertical";

    card.appendChild(img);
    card.appendChild(fileNameDiv);

    return card;
}

// Helper: Reset UI to its initial state
function resetUI() {
    fileInput.value = ""; // Clear file input
    filesContainer.innerHTML = ""; // Clear file cards
    fileUploadSection.style.display = "flex"; // Show the upload section
}
