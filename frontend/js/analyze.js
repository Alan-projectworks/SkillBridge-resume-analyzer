/**
 * Skillora 2.0 - Resume Analysis Interface Controller
 * Handles PDF drag-and-drop, validation, example JD loaders,
 * multi-stage loading animation, and API communication.
 */

document.addEventListener("DOMContentLoaded", function () {
    const dropzone = document.getElementById("dropzone");
    const resumeInput = document.getElementById("resume-input");
    const fileSelectedBox = document.getElementById("file-selected-box");
    const fileNameDisplay = document.getElementById("file-name-display");
    const fileSizeDisplay = document.getElementById("file-size-display");
    const btnRemoveFile = document.getElementById("btn-remove-file");

    const jdTextarea = document.getElementById("job-description");
    const jdCharCount = document.getElementById("jd-char-count");
    const btnClearJd = document.getElementById("btn-clear-jd");

    const btnAnalyze = document.getElementById("btn-analyze");
    const btnReset = document.getElementById("btn-reset");
    const alertBanner = document.getElementById("alert-banner");
    const alertMessage = document.getElementById("alert-message");
    const alertClose = document.getElementById("alert-close");

    const loadingOverlay = document.getElementById("loading-overlay");

    const API_URL = "http://127.0.0.1:8000/analyze";

    let selectedFile = null;

    // Presets for quick evaluation
    const EXAMPLE_JDS = {
        fullstack: `Full Stack Developer (Python & React)
We are seeking a talented Full Stack Developer to build performant, customer-facing web applications.
Core Requirements:
- 3+ years experience building web applications using Python and FastAPI or Django.
- Strong proficiency with React.js, TypeScript, HTML5, and CSS3.
- Proven experience designing relational databases with PostgreSQL or SQL.
- Must have experience with Docker containerization and Git version control.
- Solid understanding of REST APIs and Microservices architecture.
- Excellent communication skills, problem solving, and agile collaboration.
Nice to Have:
- Familiarity with Kubernetes, Redis caching, or AWS cloud infrastructure.`,

        ml: `Machine Learning Engineer / Data Scientist
Join our AI Intelligence team to research, train, and deploy predictive systems.
Essential Requirements:
- Demonstrated experience in Python and core numerical libraries: NumPy, Pandas, and Scikit-learn.
- Strong background in Machine Learning, Deep Learning, and PyTorch or TensorFlow.
- Experience with Natural Language Processing (NLP) or Computer Vision models.
- Proficiency writing complex SQL queries and managing data pipelines.
- Familiarity with Git, Linux environments, and automated Unit Testing.
- Excellent analytical thinking and critical problem solving.
Bonus Qualifications:
- Exposure to FastAPI for model serving and Docker deployment.`,

        devops: `Cloud DevOps & Infrastructure Engineer
We are looking for an experienced DevOps Engineer to scale our cloud platforms and CI/CD pipelines.
Key Responsibilities & Requirements:
- Deep expertise with Docker and Kubernetes orchestration in production.
- Hands-on experience with AWS cloud services (EC2, S3, RDS, IAM) or GCP.
- Strong scripting skills in Python and Linux shell scripting (Bash).
- Demonstrated experience building CI/CD automation pipelines (GitHub Actions or GitLab CI).
- Understanding of infrastructure monitoring, Prometheus, and security best practices.
- Strong team communication and incident response discipline.`
    };

    // Helper: Show Error Banner
    function showError(message) {
        alertMessage.textContent = message;
        alertBanner.classList.add("active");
        alertBanner.scrollIntoView({ behavior: "smooth", block: "center" });
    }

    // Helper: Dismiss Error Banner
    function dismissError() {
        alertBanner.classList.remove("active");
        alertMessage.textContent = "";
    }

    if (alertClose) {
        alertClose.addEventListener("click", dismissError);
    }

    // Format File Size
    function formatBytes(bytes) {
        if (bytes < 1024) return bytes + " bytes";
        else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + " KB";
        else return (bytes / 1048576).toFixed(2) + " MB";
    }

    // Validate and Assign File
    function handleSelectedFile(file) {
        dismissError();

        if (!file) return;

        const isPdf = file.type === "application/pdf" || file.name.toLowerCase().endsWith(".pdf");
        if (!isPdf) {
            showError("Please upload a valid PDF document (.pdf).");
            resetFileInput();
            return;
        }

        const maxBytes = 5 * 1024 * 1024; // 5 MB
        if (file.size > maxBytes) {
            showError("File size exceeds 5 MB limit. Please upload a smaller resume PDF.");
            resetFileInput();
            return;
        }

        selectedFile = file;
        fileNameDisplay.textContent = file.name;
        fileSizeDisplay.textContent = formatBytes(file.size);
        fileSelectedBox.classList.add("active");
        dropzone.style.display = "none";
    }

    function resetFileInput() {
        selectedFile = null;
        resumeInput.value = "";
        fileSelectedBox.classList.remove("active");
        dropzone.style.display = "block";
    }

    // Dropzone Click & Change
    dropzone.addEventListener("click", () => resumeInput.click());

    resumeInput.addEventListener("change", (e) => {
        if (e.target.files && e.target.files[0]) {
            handleSelectedFile(e.target.files[0]);
        }
    });

    // Drag & Drop Listeners
    ["dragenter", "dragover"].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.add("dragover");
        });
    });

    ["dragleave", "drop"].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.remove("dragover");
        });
    });

    dropzone.addEventListener("drop", (e) => {
        const dt = e.dataTransfer;
        if (dt.files && dt.files[0]) {
            handleSelectedFile(dt.files[0]);
        }
    });

    // Remove File Button
    btnRemoveFile.addEventListener("click", (e) => {
        e.stopPropagation();
        resetFileInput();
    });

    // Textarea Character & Word Counter
    function updateJdStats() {
        const text = jdTextarea.value.trim();
        const chars = text.length;
        const words = text ? text.split(/\s+/).length : 0;
        jdCharCount.textContent = `${chars} characters (${words} words)`;
    }

    jdTextarea.addEventListener("input", updateJdStats);

    // Clear JD Textarea
    if (btnClearJd) {
        btnClearJd.addEventListener("click", () => {
            jdTextarea.value = "";
            updateJdStats();
            jdTextarea.focus();
        });
    }

    // Example JD Preset Chips
    document.querySelectorAll(".chip-btn[data-preset]").forEach(chip => {
        chip.addEventListener("click", () => {
            const presetKey = chip.getAttribute("data-preset");
            if (EXAMPLE_JDS[presetKey]) {
                jdTextarea.value = EXAMPLE_JDS[presetKey];
                updateJdStats();
                dismissError();
            }
        });
    });

    // Reset All Fields
    btnReset.addEventListener("click", () => {
        resetFileInput();
        jdTextarea.value = "";
        updateJdStats();
        dismissError();
    });

    // Multi-Step Loading Indicator Sequence
    function runLoadingAnimation() {
        loadingOverlay.classList.add("active");
        const steps = document.querySelectorAll(".loading-step-item");
        steps.forEach((s, idx) => {
            s.className = "loading-step-item" + (idx === 0 ? " active" : "");
        });

        const stepDelays = [700, 1500, 2200];
        stepDelays.forEach((delay, idx) => {
            setTimeout(() => {
                if (loadingOverlay.classList.contains("active")) {
                    if (steps[idx]) {
                        steps[idx].className = "loading-step-item completed";
                    }
                    if (steps[idx + 1]) {
                        steps[idx + 1].className = "loading-step-item active";
                    }
                }
            }, delay);
        });
    }

    function stopLoadingAnimation() {
        loadingOverlay.classList.remove("active");
    }

    // Submit & Analyze Resume
    btnAnalyze.addEventListener("click", async () => {
        dismissError();

        if (!selectedFile) {
            showError("Please upload your resume in PDF format before analyzing.");
            return;
        }

        const jd = jdTextarea.value.trim();
        if (!jd) {
            showError("Please paste or choose a target job description.");
            jdTextarea.focus();
            return;
        }

        if (jd.length < 20) {
            showError("The job description is too short. Please provide a more detailed role description for meaningful skill matching.");
            jdTextarea.focus();
            return;
        }

        const formData = new FormData();
        formData.append("resume", selectedFile);
        formData.append("job_description", jd);

        runLoadingAnimation();

        try {
            const response = await fetch(API_URL, {
                method: "POST",
                body: formData
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || "Resume analysis service returned an error.");
            }

            if (!data.success || !data.analysis) {
                throw new Error("Invalid response format received from analysis engine.");
            }

            // Save results to sessionStorage for results page
            sessionStorage.setItem("skilloraResults", JSON.stringify(data));
            sessionStorage.setItem("skillBridgeResults", JSON.stringify(data));

            // Also save to recent history in localStorage
            try {
                const historyItem = {
                    id: "analysis_" + Date.now(),
                    timestamp: new Date().toISOString(),
                    filename: selectedFile.name,
                    match_percentage: data.analysis.match_percentage,
                    matched_count: data.analysis.matched_skills.length,
                    missing_count: data.analysis.missing_skills.length
                };
                let history = JSON.parse(localStorage.getItem("skilloraHistory") || "[]");
                history.unshift(historyItem);
                localStorage.setItem("skilloraHistory", JSON.stringify(history.slice(0, 10)));
            } catch (storageErr) {
                console.warn("Could not save to history:", storageErr);
            }

            // Small delay to ensure smooth transition
            setTimeout(() => {
                window.location.href = "results.html";
            }, 600);

        } catch (error) {
            stopLoadingAnimation();
            console.error("Skillora Analysis Error:", error);

            let msg = error.message;
            if (error.name === "TypeError" && error.message.includes("fetch")) {
                msg = "Could not connect to the Skillora backend server at " + API_URL + ". Please ensure the FastAPI backend is running.";
            }

            showError(msg);
        }
    });

    // Initialize stats
    updateJdStats();
});
