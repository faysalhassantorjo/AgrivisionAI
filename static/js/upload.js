/**
 * AgrivisionAI 2.0 — Studio Workspace Upload, Ajax Engine & Live Pathology Rendering
 */

document.addEventListener("DOMContentLoaded", () => {
    const uploadForm = document.getElementById("uploadForm");
    const imageInput = document.getElementById("imageInput");
    const previewImg = document.getElementById("previewImg");
    const previewWrap = document.getElementById("previewWrap");
    const previewName = document.getElementById("previewName");
    const dropZone = document.getElementById("dropZone");
    const submitBtn = document.getElementById("submitBtn");
    const clientError = document.getElementById("clientError");
    const clientErrorMsg = document.getElementById("clientErrorMsg");
    const btnClearPreview = document.getElementById("btnClearPreview");

    // Dynamic state panels
    const emptyState = document.getElementById("emptyState");
    const loadingState = document.getElementById("loadingState");
    const resultCard = document.getElementById("resultCard");

    // Diagnostic report fields
    const resultDiseaseName = document.getElementById("resultDiseaseName");
    const resultStatusTag = document.getElementById("resultStatusTag");
    const resultConfLevelText = document.getElementById("resultConfLevelText");
    const resultConfPct = document.getElementById("resultConfPct");
    const confBar = document.getElementById("confBar");
    const resultLeafImg = document.getElementById("resultLeafImg");
    const resultOverviewSection = document.getElementById("resultOverviewSection");
    const resultOverviewText = document.getElementById("resultOverviewText");
    const resultTreatmentSection = document.getElementById("resultTreatmentSection");
    const resultTreatmentText = document.getElementById("resultTreatmentText");
    const resultBreakdownSection = document.getElementById("resultBreakdownSection");
    const resultProbBars = document.getElementById("resultProbBars");
    const btnResetDiagnosis = document.getElementById("btnResetDiagnosis");

    const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
    const ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp"];

    let currentLeafImageUrl = "";

    function showError(message) {
        if (clientError && clientErrorMsg) {
            clientErrorMsg.textContent = message;
            clientError.style.display = "flex";
        } else {
            alert(message);
        }
    }

    function clearError() {
        if (clientError) {
            clientError.style.display = "none";
        }
        const serverError = document.getElementById("serverError");
        if (serverError) {
            serverError.style.display = "none";
        }
    }

    function validateFile(file) {
        if (!file) return false;

        // Size check
        if (file.size > MAX_FILE_SIZE) {
            showError(`Specimen size (${(file.size / (1024 * 1024)).toFixed(1)}MB) exceeds maximum allowed 10MB.`);
            return false;
        }

        // Type check
        if (!ALLOWED_TYPES.includes(file.type.toLowerCase()) && !/\.(jpe?g|png|webp)$/i.test(file.name)) {
            showError("Invalid format. Please supply a valid JPG, PNG, or WebP leaf photograph.");
            return false;
        }

        clearError();
        return true;
    }

    function loadFile(file) {
        if (!validateFile(file)) {
            resetFileInput();
            return;
        }

        if (currentLeafImageUrl && currentLeafImageUrl.startsWith("blob:")) {
            URL.revokeObjectURL(currentLeafImageUrl);
        }
        currentLeafImageUrl = URL.createObjectURL(file);

        if (previewImg) previewImg.src = currentLeafImageUrl;
        if (previewWrap) previewWrap.style.display = "block";
        if (previewName) {
            const sizeKb = (file.size / 1024).toFixed(0);
            previewName.textContent = `${file.name} (${sizeKb} KB)`;
        }
    }

    function resetFileInput() {
        if (imageInput) imageInput.value = "";
        if (previewWrap) previewWrap.style.display = "none";
        if (previewImg) previewImg.src = "";
        if (currentLeafImageUrl && currentLeafImageUrl.startsWith("blob:")) {
            URL.revokeObjectURL(currentLeafImageUrl);
            currentLeafImageUrl = "";
        }
    }

    if (btnClearPreview) {
        btnClearPreview.addEventListener("click", () => {
            resetFileInput();
            clearError();
        });
    }

    if (imageInput) {
        imageInput.addEventListener("change", () => {
            if (imageInput.files && imageInput.files[0]) {
                loadFile(imageInput.files[0]);
            }
        });
    }

    // Drag-and-drop
    if (dropZone && imageInput) {
        ["dragenter", "dragover"].forEach(name => {
            dropZone.addEventListener(name, e => {
                e.preventDefault();
                dropZone.classList.add("drag-over");
            });
        });

        ["dragleave", "drop"].forEach(name => {
            dropZone.addEventListener(name, e => {
                e.preventDefault();
                dropZone.classList.remove("drag-over");
            });
        });

        dropZone.addEventListener("drop", e => {
            const file = e.dataTransfer.files[0];
            if (file) {
                const dt = new DataTransfer();
                dt.items.add(file);
                imageInput.files = dt.files;
                loadFile(file);
            }
        });
    }

    // ── Ajax Form Submission ──
    if (uploadForm) {
        uploadForm.addEventListener("submit", async e => {
            e.preventDefault();

            if (!imageInput || !imageInput.files || imageInput.files.length === 0) {
                showError("Please select or drop a leaf specimen first.");
                return;
            }

            const file = imageInput.files[0];
            if (!validateFile(file)) {
                return;
            }

            clearError();

            // Set UI to loading state in-place in right pane
            if (submitBtn) {
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> Computing Pathology...';
                submitBtn.disabled = true;
            }

            if (emptyState) emptyState.style.display = "none";
            if (resultCard) resultCard.style.display = "none";
            if (loadingState) loadingState.style.display = "flex";

            const formData = new FormData(uploadForm);
            const csrfToken = uploadForm.querySelector("[name=csrfmiddlewaretoken]")?.value || "";

            try {
                const response = await fetch(uploadForm.action || window.location.href, {
                    method: "POST",
                    headers: {
                        "X-Requested-With": "XMLHttpRequest",
                        "Accept": "application/json",
                        "X-CSRFToken": csrfToken,
                    },
                    body: formData,
                });

                const data = await response.json();

                if (!response.ok || data.status === "error" || data.error) {
                    throw new Error(data.error || "An error occurred during inference.");
                }

                // Render result dynamically in right pane
                renderDiagnosisResult(data.result);

            } catch (err) {
                console.error("Diagnosis error:", err);
                if (loadingState) loadingState.style.display = "none";
                if (emptyState) emptyState.style.display = "flex";
                showError(err.message || "Failed to analyze leaf specimen. Please try another image.");
            } finally {
                if (submitBtn) {
                    submitBtn.innerHTML = '<i class="bi bi-cpu-fill"></i> Run Neural Diagnosis';
                    submitBtn.disabled = false;
                }
            }
        });
    }

    function renderDiagnosisResult(res) {
        if (!res) return;

        // Hide loader and idle state
        if (loadingState) loadingState.style.display = "none";
        if (emptyState) emptyState.style.display = "none";

        // 1. Diagnosed Condition Name
        if (resultDiseaseName) {
            resultDiseaseName.textContent = res.class || "Analyzed Condition";
        }

        // 2. Status Badge (Healthy / Diseased / Aging)
        if (resultStatusTag) {
            resultStatusTag.textContent = res.status || "Analyzed";
            resultStatusTag.className = "badge-status";
            const s = (res.status || "").toLowerCase();
            if (s === "healthy") {
                resultStatusTag.classList.add("healthy");
            } else if (s === "aging") {
                resultStatusTag.classList.add("aging");
            } else {
                resultStatusTag.classList.add("diseased");
            }
        }

        // 3. Confidence level text
        const confLevel = res.confidence_level || (res.confidence >= 75 ? "High Confidence" : "Moderate Confidence");
        if (resultConfLevelText) resultConfLevelText.textContent = confLevel;

        // 4. Confidence Percentage & Progress Bar
        if (resultConfPct) resultConfPct.textContent = res.confidence;
        if (confBar) {
            confBar.style.width = "0%";
            setTimeout(() => {
                confBar.style.width = (res.confidence || 0) + "%";
            }, 80);
        }

        // 5. SHOW THE ANALYZED SPECIMEN IMAGE PROMINENTLY
        const imageSource = res.image_url || currentLeafImageUrl;
        if (resultLeafImg && imageSource) {
            resultLeafImg.src = imageSource;
        }

        // 6. Pathology Overview Text
        if (resultOverviewText && resultOverviewSection) {
            if (res.description) {
                resultOverviewText.textContent = res.description;
                resultOverviewSection.style.display = "block";
            } else {
                resultOverviewSection.style.display = "none";
            }
        }

        // 7. Agronomic Prescription
        if (resultTreatmentText && resultTreatmentSection) {
            if (res.treatment) {
                resultTreatmentText.textContent = res.treatment;
                resultTreatmentSection.style.display = "block";
            } else {
                resultTreatmentSection.style.display = "none";
            }
        }

        // 8. Alternative Candidate Probabilities
        if (resultBreakdownSection && resultProbBars) {
            if (res.top_scores && res.top_scores.length > 0) {
                resultProbBars.innerHTML = res.top_scores.map(item => `
                    <div class="alt-prob-row">
                        <div class="alt-prob-labels">
                            <span>${item.class}</span>
                            <span>${item.score}%</span>
                        </div>
                        <div class="alt-prob-track">
                            <div class="alt-prob-fill" style="width: ${item.score}%;"></div>
                        </div>
                    </div>
                `).join("");
                resultBreakdownSection.style.display = "block";
            } else {
                resultBreakdownSection.style.display = "none";
            }
        }

        // 9. Update Print Timestamp
        const printDateMeta = document.getElementById("printDateMeta");
        if (printDateMeta) {
            const now = new Date();
            const dateStr = now.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
            const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            printDateMeta.textContent = `Generated: ${dateStr} ${timeStr} · Neural Diagnostic Verification`;
        }

        // Display report pane
        if (resultCard) {
            resultCard.style.display = "flex";
        }
    }

    // Reset button
    if (btnResetDiagnosis) {
        btnResetDiagnosis.addEventListener("click", () => {
            resetFileInput();
            clearError();
            if (resultCard) resultCard.style.display = "none";
            if (loadingState) loadingState.style.display = "none";
            if (emptyState) emptyState.style.display = "flex";
        });
    }

    // Print button handler
    const btnPrintReport = document.getElementById("btnPrintReport");
    if (btnPrintReport) {
        btnPrintReport.addEventListener("click", () => {
            window.print();
        });
    }

    // Initialize animation on page load if server rendered
    if (confBar && confBar.getAttribute("data-width")) {
        const target = confBar.getAttribute("data-width");
        setTimeout(() => {
            confBar.style.width = target + "%";
        }, 120);
    }
});
