
// ========================================
// SKILLBRIDGE - RESULTS DASHBOARD
// ========================================

// GET ANALYSIS RESULTS
let results = null;

try {
    results = JSON.parse(
        sessionStorage.getItem("skillBridgeResults") || "null"
    );
} catch (error) {
    console.error("Could not read analysis results:", error);
}

const container = document.getElementById("learning-plan");

// SAFE HTML DISPLAY

function escapeHTML(value) {
    return String(value ?? "").replace(/[&<>"']/g, char => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;"
    })[char]);
}

// CHECK ANALYSIS


if (!results || !results.analysis) {

    alert("No analysis found. Please analyze your resume first.");
    window.location.href = "analyze.html";

} else {

    const analysis = results.analysis;

    
    // RESUME SKILLS
    

    const resumeSkills = analysis.resume_skills || [];

    document.getElementById("resume-skills").innerHTML =
        resumeSkills.length
            ? resumeSkills.map(skill => `
                <span class="skill-tag">
                    ${escapeHTML(skill)}
                </span>
            `).join("")
            : "<p>No resume skills extracted.</p>";

    
    // REQUIRED SKILLS

    const requiredSkills = analysis.required_skills || [];

    document.getElementById("required-skills").innerHTML =
        requiredSkills.length
            ? requiredSkills.map(skill => `
                <span class="skill-tag">
                    ${escapeHTML(skill)}
                </span>
            `).join("")
            : "<p>No required skills identified.</p>";

     
    // MATCH PERCENTAGE AND SCORE COLOR
    

    const percentage = Number(analysis.match_percentage) || 0;

    const percentageElement =
        document.getElementById("match-percentage");

    const scoreCircle =
        document.querySelector(".score-circle");

    percentageElement.textContent = `${percentage}%`;

    // Below 70% = RED
    // 70% or above = GREEN

    if (scoreCircle) {

        scoreCircle.classList.remove("low-score", "high-score");

        if (percentage < 70) {
            scoreCircle.classList.add("low-score");
        } else {
            scoreCircle.classList.add("high-score");
        }
    }

    // MATCHED SKILLS

    const matchedSkills = analysis.matched_skills || [];

    document.getElementById("matched-skills").innerHTML =
        matchedSkills.length
            ? matchedSkills.map(skill => `
                <span class="skill-tag">
                    ${escapeHTML(skill)}
                </span>
            `).join("")
            : "<p>No matched skills found.</p>";

    // MISSING SKILLS WITH EXPLANATIONS

    const missingSkills = analysis.missing_skill_details || [];

    document.getElementById("missing-skills").innerHTML =
        missingSkills.length
            ? missingSkills.map(item => {

                const lines = item.job_description_lines || [];

                return `
                    <div class="missing-skill">

                        <h3>${escapeHTML(item.skill)}</h3>

                        <p>
                            ${escapeHTML(
                                item.reason ||
                                "This skill was not found in your resume."
                            )}
                        </p>

                        <strong>Relevant Job Description:</strong>

                        <ul>
                            ${lines.map(line => `
                                <li>${escapeHTML(line)}</li>
                            `).join("")}
                        </ul>

                    </div>
                `;
            }).join("")
            : "<p>Congratulations! No missing skills found.</p>";

    // UNIQUE PROGRESS KEY FOR EACH ANALYSIS

    const analysisIdentity = JSON.stringify({
        filename: results.filename || "",
        resumeSkills: analysis.resume_skills || [],
        requiredSkills: analysis.required_skills || [],
        missingSkills: analysis.missing_skill_details || []
    });

    // Generate a simple deterministic hash
    function generateHash(value) {
        let hash = 0;

        for (let i = 0; i < value.length; i++) {
            hash = ((hash << 5) - hash) + value.charCodeAt(i);
            hash |= 0;
        }

        return Math.abs(hash).toString(36);
    }

    const progressKey =
        "skillBridgeProgress_" + generateHash(analysisIdentity);

    // 14-DAY PERSONALIZED LEARNING PLAN


    function displayLearningPlan() {

        const plan = Array.isArray(analysis.learning_plan)
            ? analysis.learning_plan
            : [];

        if (!plan.length) {

            container.innerHTML = `
                <p>
                    🎉 No learning plan was returned.
                    Keep improving your existing skills!
                </p>
            `;

            return;
        }

        if (plan.length !== 14) {
            console.warn(
                "Expected 14 learning days, received:",
                plan.length
            );
        }

        // GET SAVED PROGRESS
        let completedDays = [];

        try {
            completedDays = JSON.parse(
                sessionStorage.getItem(progressKey) || "[]"
            );

            if (!Array.isArray(completedDays)) {
                completedDays = [];
            }
        } catch {
            completedDays = [];
        }

        // CREATE LEARNING PLAN

        container.innerHTML = `

            <div class="learning-progress">

                <h3>Your Learning Progress</h3>

                <div
                    class="progress-bar"
                    role="progressbar"
                    aria-valuemin="0"
                    aria-valuemax="${plan.length}"
                    aria-valuenow="0"
                    id="progress-bar"
                >
                    <div
                        id="progress-fill"
                        style="width: 0%"
                    ></div>
                </div>

                <p id="progress-text">
                    0 of ${plan.length} days completed
                </p>

            </div>

            <div class="learning-days">

                ${plan.map(item => {

                    const day = Number(item.day);
                    const isCompleted = completedDays.includes(day);

                    return `

                        <div class="learning-day ${isCompleted ? "completed" : ""}">

                            <label>

                                <input
                                    type="checkbox"
                                    class="learning-checkbox"
                                    data-day="${day}"
                                    ${isCompleted ? "checked" : ""}
                                >

                                <span>

                                    <strong>DAY ${day}</strong>

                                    <h3>
                                        ${escapeHTML(item.skill)}
                                    </h3>

                                    <h4>
                                        ${escapeHTML(item.topic)}
                                    </h4>

                                    <p>
                                        ${escapeHTML(item.task)}
                                    </p>

                                </span>

                            </label>

                        </div>

                    `;

                }).join("")}

            </div>
        `;

        // PROGRESS TRACKING
        

        const checkboxes = container.querySelectorAll(
            ".learning-checkbox"
        );

        const progressFill =
            document.getElementById("progress-fill");

        const progressText =
            document.getElementById("progress-text");

        const progressBar =
            document.getElementById("progress-bar");

        function updateProgress() {

            const completed = [...checkboxes]
                .filter(checkbox => checkbox.checked);

            const completedCount = completed.length;

            const percentage =
                (completedCount / plan.length) * 100;

            progressFill.style.width = `${percentage}%`;

            progressText.textContent =
                `${completedCount} of ${plan.length} days completed`;

            progressBar.setAttribute(
                "aria-valuenow",
                completedCount
            );

            // SAVE PROGRESS
            const savedDays = completed.map(checkbox =>
                Number(checkbox.dataset.day)
            );

            sessionStorage.setItem(
                progressKey,
                JSON.stringify(savedDays)
            );

            // UPDATE CARD APPEARANCE
            checkboxes.forEach(checkbox => {

                const card = checkbox.closest(".learning-day");

                card.classList.toggle(
                    "completed",
                    checkbox.checked
                );

            });

            if (completedCount === plan.length) {

                progressText.textContent =
                    "🎉 Congratulations! You completed your learning journey!";

            }
        }

        checkboxes.forEach(checkbox => {
            checkbox.addEventListener("change", updateProgress);
        });

        // INITIALIZE SAVED PROGRESS
        updateProgress();
    }

    // DISPLAY LEARNING PLAN
    displayLearningPlan();

}
