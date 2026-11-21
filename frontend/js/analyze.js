
const resumeInput = document.getElementById("resume");
const fileInfo = document.getElementById("file-info");
const analyzeBtn = document.getElementById("analyze-btn");
const jobDescription = document.getElementById("job-description");
const analysisStatus = document.getElementById("analysis-status");

const API_URL = "http://127.0.0.1:8000/analyze";

let selectedResume = null;

// PDF UPLOAD
resumeInput.addEventListener("change", function () {
    const file = resumeInput.files[0];

    if (!file) return;

    const isPDF =
        file.type === "application/pdf" ||
        file.name.toLowerCase().endsWith(".pdf");

    if (!isPDF) {
        alert("Please upload a PDF file.");
        resumeInput.value = "";
        selectedResume = null;
        fileInfo.innerHTML = "";
        return;
    }

    const maxSize = 5 * 1024 * 1024;

    if (file.size > maxSize) {
        alert("Your resume must be smaller than 5 MB.");
        resumeInput.value = "";
        selectedResume = null;
        fileInfo.innerHTML = "";
        return;
    }

    selectedResume = file;

    fileInfo.innerHTML = `
        <h3>✓ Resume Uploaded!</h3>
        <p>${file.name.replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")}</p>
        <p>Size: ${(file.size / (1024 * 1024)).toFixed(2)} MB</p>
        <button type="button" id="remove-file" class="upload-button">
            Remove File
        </button>
    `;

    analysisStatus.textContent = "";
});

// REMOVE FILE
fileInfo.addEventListener("click", function (event) {
    if (event.target.id === "remove-file") {
        resumeInput.value = "";
        selectedResume = null;
        fileInfo.innerHTML = "";
        analysisStatus.textContent = "";
    }
});

// ANALYZE RESUME
analyzeBtn.addEventListener("click", async function () {

    const jobText = jobDescription.value.trim();

    if (!selectedResume) {
        alert("Please upload your resume first.");
        return;
    }

    if (!jobText) {
        alert("Please enter a job description.");
        return;
    }

    const formData = new FormData();

    formData.append("resume", selectedResume);
    formData.append("job_description", jobText);

    try {
        analyzeBtn.disabled = true;
        analyzeBtn.textContent = "Analyzing...";
        analysisStatus.textContent =
            "Please wait! SkillBridge is analyzing your resume...";

        const response = await fetch(API_URL, {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "Resume analysis failed."
            );
        }

        if (!data.success || !data.analysis) {
            throw new Error("Invalid analysis response from server.");
        }

        // Save results for the results page
        sessionStorage.setItem(
            "skillBridgeResults",
            JSON.stringify(data)
        );

        // Redirect to results page
        window.location.href = "results.html";

    } catch (error) {
        console.error("SkillBridge Error:", error);

        analysisStatus.textContent =
            error.message || "Something went wrong. Please try again.";

        analyzeBtn.disabled = false;
        analyzeBtn.textContent = "Analyse My Resume →";
    }
});
