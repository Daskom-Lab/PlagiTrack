function displayFileName() {
    const fileInputs = document.querySelectorAll('[id^="file-upload"]'); 
    const fileNameDisplays = document.querySelectorAll('[id^="file-name"]'); 
    
    // lopping
    fileInputs.forEach((fileInput, index) => {
        const fileNameDisplay = fileNameDisplays[index];
        
        // kondisi
        if (fileInput.files && fileInput.files[0]) {
            const fileName = fileInput.files[0].name;
            fileNameDisplay.textContent = fileName;
        } else {
            fileNameDisplay.textContent = '';
        }
    });
}

document.querySelectorAll('[id^="file-upload"]').forEach(input => {
    input.addEventListener('change', displayFileName);
});
