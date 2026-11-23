/**
 * Skillora 2.0 - Results Dashboard Controller
 * Minimal Premium SaaS Career Intelligence Dashboard
 */

document.addEventListener("DOMContentLoaded", function () {
    // 1. Retrieve Analysis Payload
    let rawResults = sessionStorage.getItem("skilloraResults") || sessionStorage.getItem("skillBridgeResults");
    let results = null;

    try {
        results = rawResults ? JSON.parse(rawResults) : null;
    } catch (e) {
        console.error("Failed to parse analysis payload:", e);
    }

    if (!results || !results.analysis) {
        alert("No resume analysis found. Please upload and analyze a resume first.");
        window.location.href = "analyze.html";
        return;
    }

    const analysis = results.analysis;
    const filename = results.filename || "Resume.pdf";
    const pageCount = results.page_count || 1;

    // Helper: Safe HTML Escaping
    function escapeHTML(str) {
        return String(str ?? "").replace(/[&<>"']/g, char => ({
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#039;"
        })[char]);
    }

    // Helper: Deterministic Hash for persistent storage
    function getAnalysisHash() {
        const str = (filename + "_" + (analysis.required_skills || []).join("_"));
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            hash = ((hash << 5) - hash) + str.charCodeAt(i);
            hash |= 0;
        }
        return "skillora_sprint_" + Math.abs(hash).toString(36);
    }

    // =========================================================================
    // HEADER & METADATA
    // =========================================================================
    const filenameEl = document.getElementById("report-filename");
    if (filenameEl) filenameEl.textContent = filename;

    const pageCountEl = document.getElementById("report-pagecount");
    if (pageCountEl) pageCountEl.textContent = `${pageCount} page${pageCount > 1 ? "s" : ""}`;

    const dateEl = document.getElementById("report-date");
    if (dateEl) {
        const now = new Date();
        dateEl.textContent = now.toLocaleDateString(undefined, {
            year: "numeric",
            month: "short",
            day: "numeric"
        });
    }

    // =========================================================================
    // A. OVERVIEW SECTION
    // =========================================================================
    const matchPercentage = Number(analysis.match_percentage) || 0;
    const matchedSkills = analysis.matched_skills || [];
    const missingSkills = analysis.missing_skills || [];
    const partialSkills = analysis.partial_skills || analysis.partially_matched_skills || [];
    const requiredSkills = analysis.required_skills || [];
    const totalRequired = requiredSkills.length || (matchedSkills.length + missingSkills.length + partialSkills.length) || 1;

    // Circular SVG Score Indicator
    const scoreValEl = document.getElementById("score-value-text");
    const progRing = document.getElementById("score-prog-ring");
    const ratingBadgeEl = document.getElementById("score-rating-badge");

    if (scoreValEl) scoreValEl.textContent = Math.round(matchPercentage);

    if (progRing) {
        const radius = 70;
        const circumference = 2 * Math.PI * radius;
        progRing.style.strokeDasharray = `${circumference} ${circumference}`;

        // Animate stroke dashoffset
        const offset = circumference - (matchPercentage / 100) * circumference;
        setTimeout(() => {
            progRing.style.strokeDashoffset = offset;
        }, 150);

        // Score ring color & rating badge
        if (matchPercentage >= 75) {
            progRing.style.stroke = "var(--primary)";
            if (ratingBadgeEl) {
                ratingBadgeEl.textContent = "Strong Alignment";
                ratingBadgeEl.className = "score-rating-badge badge-high";
            }
        } else if (matchPercentage >= 50) {
            progRing.style.stroke = "var(--accent-amber)";
            if (ratingBadgeEl) {
                ratingBadgeEl.textContent = "Moderate Alignment";
                ratingBadgeEl.className = "score-rating-badge badge-mid";
            }
        } else {
            progRing.style.stroke = "var(--accent-rose)";
            if (ratingBadgeEl) {
                ratingBadgeEl.textContent = "Growth Required";
                ratingBadgeEl.className = "score-rating-badge badge-low";
            }
        }
    }

    // Key Metric Stat Cards
    const matchedCountEl = document.getElementById("stat-matched-count");
    if (matchedCountEl) matchedCountEl.textContent = matchedSkills.length;

    const matchedPercentEl = document.getElementById("stat-matched-sub");
    if (matchedPercentEl) {
        const pct = Math.round((matchedSkills.length / totalRequired) * 100);
        matchedPercentEl.textContent = `${pct}% of required`;
    }

    const missingCountEl = document.getElementById("stat-missing-count");
    if (missingCountEl) missingCountEl.textContent = missingSkills.length;

    const partialCountEl = document.getElementById("stat-partial-count");
    if (partialCountEl) partialCountEl.textContent = partialSkills.length;

    const totalCountEl = document.getElementById("stat-total-count");
    if (totalCountEl) totalCountEl.textContent = totalRequired;

    // AI Analysis Summary
    const aiSummaryEl = document.getElementById("ai-summary-content");
    if (aiSummaryEl) {
        aiSummaryEl.textContent = analysis.ai_summary || "Candidate competencies evaluated successfully.";
    }

    // Skill Distribution Category Chart
    const distContainer = document.getElementById("category-bars-list");
    if (distContainer && analysis.skill_distribution) {
        distContainer.innerHTML = "";
        const dist = analysis.skill_distribution;
        const categories = Object.keys(dist);

        categories.forEach(cat => {
            const data = dist[cat];
            const requiredCount = data.required || 0;
            const resumeCount = data.resume || 0;

            if (requiredCount > 0 || resumeCount > 0) {
                const ratio = requiredCount > 0 ? Math.min(Math.round((resumeCount / requiredCount) * 100), 100) : 100;
                const row = document.createElement("div");
                row.className = "category-bar-row";
                row.innerHTML = `
                    <div class="category-bar-label">${escapeHTML(cat)}</div>
                    <div class="category-bar-track">
                        <div class="category-bar-fill" style="width: ${ratio}%"></div>
                    </div>
                    <div class="category-bar-count">${resumeCount} / ${requiredCount} skills</div>
                `;
                distContainer.appendChild(row);
            }
        });
    }

    // =========================================================================
    // B & C. SKILL GAP ANALYSIS & EVIDENCE
    // =========================================================================
    const skillsGrid = document.getElementById("skills-result-grid");
    const searchInput = document.getElementById("skill-search-input");
    const categorySelect = document.getElementById("skill-category-select");
    const tabBtns = document.querySelectorAll(".tab-btn[data-tab]");

    // Aggregate all required skills into a unified display model
    const matchedDetailsMap = new Map((analysis.matched_skill_details || []).map(d => [d.skill, d]));
    const partialDetailsMap = new Map((analysis.partial_skill_details || []).map(d => [d.skill, d]));
    const missingDetailsMap = new Map((analysis.missing_skill_details || []).map(d => [d.skill, d]));

    const unifiedSkills = [];

    // Add Matched Skills
    matchedSkills.forEach(skill => {
        const d = matchedDetailsMap.get(skill) || {};
        unifiedSkills.push({
            skill: skill,
            status: "matched",
            category: d.category || "General",
            priority: d.priority || "Medium",
            evidence: d.evidence || `Extracted directly from resume.`,
            jdLines: d.job_description_lines || []
        });
    });

    // Add Partial Skills
    partialSkills.forEach(skill => {
        const d = partialDetailsMap.get(skill) || {};
        unifiedSkills.push({
            skill: skill,
            status: "partial",
            category: d.category || "General",
            priority: d.priority || "Medium",
            foundation: d.foundation_skill || "Related engineering practices",
            explanation: d.explanation || `Found foundational experience enabling rapid skill acquisition.`,
            jdLines: d.job_description_lines || []
        });
    });

    // Add Missing Skills
    missingSkills.forEach(skill => {
        const d = missingDetailsMap.get(skill) || {};
        unifiedSkills.push({
            skill: skill,
            status: "missing",
            category: d.category || "General",
            priority: d.priority || "Medium",
            reason: d.reason || `Required by job description but not detected in resume text.`,
            jdLines: d.job_description_lines || []
        });
    });

    // Populate Category Dropdown Options
    if (categorySelect) {
        const uniqueCategories = Array.from(new Set(unifiedSkills.map(s => s.category))).filter(Boolean).sort();
        uniqueCategories.forEach(cat => {
            const opt = document.createElement("option");
            opt.value = cat;
            opt.textContent = cat;
            categorySelect.appendChild(opt);
        });
    }

    let activeTab = "all";

    function renderSkillsList() {
        if (!skillsGrid) return;

        const searchTerm = (searchInput ? searchInput.value : "").trim().toLowerCase();
        const selectedCat = categorySelect ? categorySelect.value : "all";

        const filtered = unifiedSkills.filter(item => {
            // Tab filter
            if (activeTab === "matched" && item.status !== "matched") return false;
            if (activeTab === "missing" && item.status !== "missing") return false;
            if (activeTab === "partial" && item.status !== "partial") return false;

            // Category filter
            if (selectedCat !== "all" && item.category !== selectedCat) return false;

            // Search filter
            if (searchTerm && !item.skill.toLowerCase().includes(searchTerm)) return false;

            return true;
        });

        if (filtered.length === 0) {
            skillsGrid.innerHTML = `
                <div style="grid-column: 1 / -1; text-align: center; padding: 40px 20px; color: var(--text-muted);">
                    <p style="font-size: 15px; font-weight: 600;">No skills found matching your filter criteria.</p>
                    <p style="font-size: 13px;">Try clearing search keywords or selecting "All Skills".</p>
                </div>
            `;
            return;
        }

        skillsGrid.innerHTML = filtered.map(item => {
            let statusBadge = "";
            let drawerContent = "";

            if (item.status === "matched") {
                statusBadge = `<span class="status-badge status-matched">✓ Matched</span>`;
                drawerContent = `
                    <div class="evidence-content" id="drawer-${escapeHTML(item.skill)}">
                        <strong style="color: var(--primary);">Resume Evidence:</strong>
                        <div class="evidence-snippet-box">"${escapeHTML(item.evidence)}"</div>
                        ${item.jdLines.length ? `
                            <div style="margin-top: 8px;">
                                <strong style="color: var(--text-muted);">Job Description Requirement:</strong>
                                <ul class="jd-citation-list">
                                    ${item.jdLines.map(l => `<li>${escapeHTML(l)}</li>`).join("")}
                                </ul>
                            </div>
                        ` : ""}
                    </div>
                `;
            } else if (item.status === "partial") {
                statusBadge = `<span class="status-badge status-partial">~ Partial Match</span>`;
                drawerContent = `
                    <div class="evidence-content" id="drawer-${escapeHTML(item.skill)}">
                        <strong style="color: var(--accent-amber-text);">Foundational Capability:</strong>
                        <p style="margin: 4px 0 8px;">${escapeHTML(item.explanation)}</p>
                        ${item.jdLines.length ? `
                            <strong style="color: var(--text-muted);">Job Description Requirement:</strong>
                            <ul class="jd-citation-list">
                                ${item.jdLines.map(l => `<li>${escapeHTML(l)}</li>`).join("")}
                            </ul>
                        ` : ""}
                    </div>
                `;
            } else {
                const prioTag = item.priority === "High"
                    ? `<span style="font-size: 10px; background: #FFE4E6; color: #9F1239; padding: 2px 6px; border-radius: 4px; font-weight: 700; margin-left: 4px;">HIGH PRIORITY</span>`
                    : "";
                statusBadge = `<span class="status-badge status-missing">! Missing ${prioTag}</span>`;
                drawerContent = `
                    <div class="evidence-content" id="drawer-${escapeHTML(item.skill)}">
                        <strong style="color: var(--accent-rose-text);">Requirement Rationale:</strong>
                        <p style="margin: 4px 0 8px;">${escapeHTML(item.reason)}</p>
                        ${item.jdLines.length ? `
                            <strong style="color: var(--text-muted);">Job Description Requirement:</strong>
                            <ul class="jd-citation-list">
                                ${item.jdLines.map(l => `<li>${escapeHTML(l)}</li>`).join("")}
                            </ul>
                        ` : ""}
                    </div>
                `;
            }

            return `
                <div class="skill-result-card" data-skill="${escapeHTML(item.skill)}">
                    <div class="skill-card-top">
                        <div>
                            <div class="skill-name-title">${escapeHTML(item.skill)}</div>
                            <div class="skill-category-sub">${escapeHTML(item.category)}</div>
                        </div>
                        ${statusBadge}
                    </div>
                    <div class="evidence-drawer-toggle" onclick="toggleEvidenceDrawer('${escapeHTML(item.skill)}')">
                        <span>View Evidence &amp; Context</span>
                        <span id="drawer-arrow-${escapeHTML(item.skill)}">▾</span>
                    </div>
                    ${drawerContent}
                </div>
            `;
        }).join("");
    }

    // Toggle Drawer Helper
    window.toggleEvidenceDrawer = function (skillName) {
        const drawer = document.getElementById("drawer-" + skillName);
        const arrow = document.getElementById("drawer-arrow-" + skillName);
        if (drawer) {
            const isExpanded = drawer.classList.contains("expanded");
            drawer.classList.toggle("expanded", !isExpanded);
            if (arrow) arrow.textContent = isExpanded ? "▾" : "▴";
        }
    };

    // Filter Listeners
    if (searchInput) searchInput.addEventListener("input", renderSkillsList);
    if (categorySelect) categorySelect.addEventListener("change", renderSkillsList);

    tabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            tabBtns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            activeTab = btn.getAttribute("data-tab");
            renderSkillsList();
        });
    });

    renderSkillsList();

    // =========================================================================
    // D. SKILL PRIORITIES SECTION
    // =========================================================================
    const prioritiesContainer = document.getElementById("top3-priorities-grid");
    const skillPriorities = analysis.skill_priorities || [];

    if (prioritiesContainer) {
        if (skillPriorities.length > 0) {
            prioritiesContainer.innerHTML = skillPriorities.map((item, idx) => `
                <div class="priority-item-card">
                    <span class="priority-rank-badge">PRIORITY ${idx + 1} • ${escapeHTML(item.priority || "HIGH")}</span>
                    <h3>${escapeHTML(item.skill)}</h3>
                    <p>${escapeHTML(item.reason || "High importance skill identified in core role specifications.")}</p>
                    <div class="priority-impact-box">
                        <strong>Strategic Impact:</strong> ${escapeHTML(item.impact || "Directly improves hiring alignment.")}
                    </div>
                </div>
            `).join("");
        } else {
            prioritiesContainer.innerHTML = `
                <div style="grid-column: 1 / -1; background: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 12px; padding: 24px; text-align: center; color: var(--primary);">
                    <h3 style="margin-bottom: 6px;">🎉 No Critical Skill Gaps Identified</h3>
                    <p style="font-size: 14px;">Your resume strongly aligns with all high-priority technical requirements for this role.</p>
                </div>
            `;
        }
    }

    // =========================================================================
    // E. 7-DAY PERSONALIZED LEARNING ROADMAP
    // =========================================================================
    const roadmapDaysContainer = document.getElementById("roadmap-days-grid");
    const roadmapProgressBar = document.getElementById("roadmap-progress-fill");
    const roadmapProgressText = document.getElementById("roadmap-progress-text");
    const btnResetRoadmap = document.getElementById("btn-reset-roadmap");

    const storageKey = getAnalysisHash();
    let completedDays = [];

    try {
        completedDays = JSON.parse(localStorage.getItem(storageKey) || "[]");
        if (!Array.isArray(completedDays)) completedDays = [];
    } catch {
        completedDays = [];
    }

    const learningPlan = analysis.learning_plan || [];

    function updateRoadmapProgress() {
        const total = learningPlan.length || 7;
        const count = completedDays.length;
        const pct = Math.round((count / total) * 100);

        if (roadmapProgressBar) roadmapProgressBar.style.width = `${pct}%`;
        if (roadmapProgressText) {
            roadmapProgressText.textContent = `${count} of ${total} days completed (${pct}%)`;
        }

        try {
            localStorage.setItem(storageKey, JSON.stringify(completedDays));
        } catch (e) {
            console.warn("Failed to persist roadmap progress:", e);
        }
    }

    if (roadmapDaysContainer && learningPlan.length > 0) {
        roadmapDaysContainer.innerHTML = learningPlan.map(dayItem => {
            const dayNum = Number(dayItem.day);
            const isDone = completedDays.includes(dayNum);

            return `
                <div class="roadmap-day-card ${isDone ? "completed" : ""}" id="day-card-${dayNum}">
                    <label class="roadmap-day-label">
                        <input
                            type="checkbox"
                            class="roadmap-checkbox"
                            data-day="${dayNum}"
                            ${isDone ? "checked" : ""}
                        >
                        <div class="roadmap-day-content">
                            <div>
                                <span class="day-badge-pill">DAY ${dayNum}</span>
                                <span class="roadmap-day-skill">${escapeHTML(dayItem.skill)}</span>
                            </div>
                            <div class="roadmap-topic-title">${escapeHTML(dayItem.topic)}</div>
                            <div class="roadmap-task-desc">${escapeHTML(dayItem.task)}</div>
                        </div>
                    </label>
                </div>
            `;
        }).join("");

        // Attach Checkbox Change Listeners
        roadmapDaysContainer.querySelectorAll(".roadmap-checkbox").forEach(cb => {
            cb.addEventListener("change", (e) => {
                const d = Number(e.target.dataset.day);
                const card = document.getElementById("day-card-" + d);

                if (e.target.checked) {
                    if (!completedDays.includes(d)) completedDays.push(d);
                    if (card) card.classList.add("completed");
                } else {
                    completedDays = completedDays.filter(day => day !== d);
                    if (card) card.classList.remove("completed");
                }

                updateRoadmapProgress();
            });
        });

        if (btnResetRoadmap) {
            btnResetRoadmap.addEventListener("click", () => {
                completedDays = [];
                roadmapDaysContainer.querySelectorAll(".roadmap-checkbox").forEach(cb => {
                    cb.checked = false;
                });
                roadmapDaysContainer.querySelectorAll(".roadmap-day-card").forEach(c => {
                    c.classList.remove("completed");
                });
                updateRoadmapProgress();
            });
        }

        updateRoadmapProgress();
    }

    // =========================================================================
    // F. CAREER RECOMMENDATIONS SECTION
    // =========================================================================
    const careerContainer = document.getElementById("career-cards-grid");
    const recommendations = analysis.career_recommendations || [];

    if (careerContainer && recommendations.length > 0) {
        careerContainer.innerHTML = recommendations.map(role => `
            <div class="career-role-card">
                <div>
                    <div class="role-header-top">
                        <div class="role-title">${escapeHTML(role.title)}</div>
                        <div class="role-compat-badge">${Math.round(role.match_score)}% Match</div>
                    </div>
                    <div class="role-desc">${escapeHTML(role.description)}</div>
                    <div class="overlap-skills-title">Overlapping Resume Competencies</div>
                    <div class="overlap-chips-wrap">
                        ${(role.overlapping_skills || []).map(s => `
                            <span class="overlap-chip">${escapeHTML(s)}</span>
                        `).join("")}
                    </div>
                </div>
                <div class="role-rationale-box">
                    <strong>Why this fits:</strong> ${escapeHTML(role.relevance_reason)}
                </div>
            </div>
        `).join("");
    }

    // =========================================================================
    // G. WHAT-IF SIMULATOR
    // =========================================================================
    const simCheckboxContainer = document.getElementById("sim-checkboxes-list");
    const simBaseScoreEl = document.getElementById("sim-base-score");
    const simProjScoreEl = document.getElementById("sim-projected-score");
    const simGainBadgeEl = document.getElementById("sim-gain-badge");
    const simFillProj = document.getElementById("sim-fill-projected");

    // Pool of skills eligible for simulation: missing + partial
    const simEligibleSkills = Array.from(new Set([...missingSkills, ...partialSkills]));
    const simulatedSelected = new Set();

    if (simBaseScoreEl) simBaseScoreEl.textContent = `${Math.round(matchPercentage)}%`;

    function recalculateSimulation() {
        let earnedPoints = matchedSkills.length * 1.0;

        // In the original analysis, partial gave 0.5 credit
        partialSkills.forEach(s => {
            if (simulatedSelected.has(s)) {
                earnedPoints += 1.0; // upgraded to full match
            } else {
                earnedPoints += 0.5;
            }
        });

        // Missing skills give 0 unless simulated
        missingSkills.forEach(s => {
            if (simulatedSelected.has(s)) {
                earnedPoints += 1.0;
            }
        });

        const newScore = Math.min(Math.round((earnedPoints / totalRequired) * 100), 100);
        const gain = Math.max(newScore - Math.round(matchPercentage), 0);

        if (simProjScoreEl) simProjScoreEl.textContent = `${newScore}%`;
        if (simGainBadgeEl) simGainBadgeEl.textContent = `+${gain}% Projected Gain`;
        if (simFillProj) simFillProj.style.width = `${newScore}%`;
    }

    if (simCheckboxContainer) {
        if (simEligibleSkills.length > 0) {
            simCheckboxContainer.innerHTML = simEligibleSkills.map(s => `
                <label class="sim-checkbox-label">
                    <input type="checkbox" class="sim-checkbox" data-skill="${escapeHTML(s)}">
                    <span>${escapeHTML(s)}</span>
                </label>
            `).join("");

            simCheckboxContainer.querySelectorAll(".sim-checkbox").forEach(cb => {
                cb.addEventListener("change", (e) => {
                    const sk = e.target.dataset.skill;
                    if (e.target.checked) {
                        simulatedSelected.add(sk);
                    } else {
                        simulatedSelected.delete(sk);
                    }
                    recalculateSimulation();
                });
            });
        } else {
            simCheckboxContainer.innerHTML = `
                <p style="font-size: 13px; color: var(--text-muted);">All required skills are already mastered in your resume.</p>
            `;
        }
    }

    recalculateSimulation();

    // =========================================================================
    // H. DOWNLOADABLE REPORT / PRINT
    // =========================================================================
    const btnDownloadPdf = document.getElementById("btn-download-pdf");
    if (btnDownloadPdf) {
        btnDownloadPdf.addEventListener("click", () => {
            // Expand all drawers so they appear in the printed PDF
            document.querySelectorAll(".evidence-content").forEach(el => {
                el.classList.add("expanded");
            });

            window.print();
        });
    }
});
