/* =====================================================
   NAKHDRISHTI
   FRONTEND JAVASCRIPT  (connected to the Flask backend)
===================================================== */

document.addEventListener("DOMContentLoaded", () => {

    /* =================================================
       CONFIG
       - Served by Flask (python app.py)  -> same origin, no setup.
       - Opened straight from disk (file://) -> talks to localhost:8000.
       - Deployed API elsewhere -> set window.NAKHDRISHTI_API before this script.
    ================================================= */

    const API_BASE =
        window.NAKHDRISHTI_API ??
        (window.location.protocol === "file:" ? "http://localhost:8000" : "");

    const MAX_MB = 10;
    const REQUEST_TIMEOUT_MS = 60000;


    /* =================================================
       ELEMENTS
    ================================================= */

    const $ = (id) => document.getElementById(id);

    const imageInput = $("imageInput");
    const browseButton = $("browseButton");
    const uploadBox = $("uploadBox");
    const uploadContent = $("uploadContent");
    const previewContainer = $("previewContainer");
    const previewImage = $("previewImage");
    const removeImage = $("removeImage");
    const fileName = $("fileName");
    const analyzeButton = $("analyzeButton");
    const scanError = $("scanError");
    const scanErrorText = $("scanErrorText");

    const resultCard = $("resultCard");
    const resultTitle = $("resultTitle");
    const resultIcon = $("resultIcon");
    const resultAlert = $("resultAlert");
    const resultAlertText = $("resultAlertText");
    const confidenceValue = $("confidenceValue");
    const confidenceBar = $("confidenceBar");
    const resultMessage = $("resultMessage");
    const resultSigns = $("resultSigns");
    const resultAdvice = $("resultAdvice");
    const resultDoctor = $("resultDoctor");
    const resultTop = $("resultTop");
    const modelVotes = $("modelVotes");
    const newAnalysis = $("newAnalysis");

    const ANALYZE_LABEL = `
        <i class="fa-solid fa-wand-magic-sparkles"></i>
        Analyze Nail
    `;

    // The file we will upload. Kept in a variable (not only in the <input>)
    // because dropped files are NOT placed into input.files by the browser.
    let selectedFile = null;


    /* =================================================
       SMALL HELPERS
    ================================================= */

    function el(tag, className, text) {
        const node = document.createElement(tag);
        if (className) node.className = className;
        if (text !== undefined) node.textContent = text;
        return node;
    }

    function showError(message) {
        scanErrorText.textContent = message;
        scanError.hidden = false;
    }

    function clearError() {
        scanError.hidden = true;
        scanErrorText.textContent = "";
    }

    function setSeverity(node, severity) {
        node.classList.remove("sev-ok", "sev-moderate", "sev-attention", "sev-urgent");
        if (severity) node.classList.add("sev-" + severity);
    }

    function prettyClass(name) {
        return name.replace(/_/g, " ");
    }


    /* =================================================
       SERVER STATUS (hero card)
    ================================================= */

    const serverStatus = $("serverStatus");
    const statusTitle = $("statusTitle");
    const statusText = $("statusText");
    const statusIcon = $("statusIcon");

    function setStatus(state, title, text) {
        serverStatus.classList.remove("offline", "connecting");
        if (state !== "online") serverStatus.classList.add(state);

        statusTitle.textContent = title;
        statusText.textContent = text;

        statusIcon.className =
            state === "online" ? "fa-solid fa-check-circle"
                : state === "offline" ? "fa-solid fa-circle-xmark"
                    : "fa-solid fa-spinner fa-spin";
    }

    async function checkServer() {
        setStatus("connecting", "Connecting to AI model...", "Please wait");

        try {
            const response = await fetch(API_BASE + "/api/health", { cache: "no-store" });
            const data = await response.json();

            if (data.model_loaded) {
                setStatus("online", "AI Model Ready", "Upload an image to begin");
                return true;
            }
            throw new Error("Model not loaded");

        } catch (err) {
            setStatus("offline", "AI Model Offline", "Start the server: python app.py");
            return false;
        }
    }


    /* =================================================
       OPEN FILE SELECTOR
    ================================================= */

    browseButton.addEventListener("click", (event) => {
        event.stopPropagation();
        imageInput.click();
    });

    uploadContent.classList.add("upload-content-click");
    uploadContent.addEventListener("click", () => imageInput.click());


    /* =================================================
       IMAGE SELECTED
    ================================================= */

    imageInput.addEventListener("change", (event) => {
        const file = event.target.files[0];
        if (file) processImage(file);
    });


    /* =================================================
       PROCESS IMAGE
    ================================================= */

    function processImage(file) {

        clearError();

        if (!file.type.startsWith("image/")) {
            showError("Please upload a valid image file (JPG, PNG or WEBP).");
            return;
        }

        if (file.size > MAX_MB * 1024 * 1024) {
            showError(`That image is too large. Please choose one under ${MAX_MB} MB.`);
            return;
        }

        selectedFile = file;

        const reader = new FileReader();

        reader.onload = function (event) {

            previewImage.src = event.target.result;

            fileName.textContent = file.name;

            uploadContent.style.display = "none";

            previewContainer.style.display = "block";

            analyzeButton.disabled = false;

            hideResult();
        };

        reader.readAsDataURL(file);
    }


    /* =================================================
       DRAG & DROP
    ================================================= */

    uploadBox.addEventListener("dragover", (event) => {
        event.preventDefault();
        uploadBox.classList.add("dragging");
    });

    uploadBox.addEventListener("dragleave", () => {
        uploadBox.classList.remove("dragging");
    });

    uploadBox.addEventListener("drop", (event) => {
        event.preventDefault();
        uploadBox.classList.remove("dragging");

        const file = event.dataTransfer.files[0];
        if (file) processImage(file);
    });


    /* =================================================
       RESET / REMOVE
    ================================================= */

    function resetUploader() {
        selectedFile = null;
        imageInput.value = "";
        previewImage.src = "";
        fileName.textContent = "";
        previewContainer.style.display = "none";
        uploadContent.style.display = "block";
        analyzeButton.disabled = true;
        analyzeButton.innerHTML = ANALYZE_LABEL;
        clearError();
        hideResult();
    }

    function hideResult() {
        resultCard.classList.remove("show");
        confidenceBar.style.width = "0%";
        document.querySelectorAll(".condition-card.is-result")
            .forEach((card) => card.classList.remove("is-result"));
    }

    removeImage.addEventListener("click", (event) => {
        event.stopPropagation();
        resetUploader();
    });


    /* =================================================
       ANALYZE BUTTON  ->  POST /api/predict
    ================================================= */

    analyzeButton.addEventListener("click", async () => {

        if (!selectedFile) return;

        clearError();
        hideResult();

        analyzeButton.disabled = true;
        analyzeButton.innerHTML = `
            <i class="fa-solid fa-spinner fa-spin"></i>
            Analyzing...
        `;

        const formData = new FormData();
        formData.append("image", selectedFile);

        const controller = new AbortController();
        const timer = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

        try {

            const response = await fetch(API_BASE + "/api/predict", {
                method: "POST",
                body: formData,
                signal: controller.signal
            });

            let data = null;
            try { data = await response.json(); } catch (_) { /* non-JSON error page */ }

            if (!response.ok || !data || !data.success) {
                throw new Error(
                    (data && data.error) ||
                    `The server returned an error (${response.status}).`
                );
            }

            showResult(data);
            setStatus("online", "AI Model Ready", "Upload an image to begin");

        } catch (err) {

            if (err.name === "AbortError") {
                showError("The analysis took too long. Please try again.");
            } else if (err instanceof TypeError) {
                // fetch() itself failed -> server unreachable
                showError(
                    "Cannot reach the AI server. Make sure it is running " +
                    "(python app.py) and try again."
                );
                setStatus("offline", "AI Model Offline", "Start the server: python app.py");
            } else {
                showError(err.message);
            }

        } finally {

            clearTimeout(timer);
            analyzeButton.disabled = false;
            analyzeButton.innerHTML = ANALYZE_LABEL;
        }
    });


    /* =================================================
       SHOW RESULT
    ================================================= */

    function showResult(data) {

        const info = data.condition;

        setSeverity(resultCard, info.severity);

        resultTitle.textContent = info.title;

        resultIcon.innerHTML = "";
        const icon = el("i", "fa-solid " + (info.icon || "fa-check"));
        resultIcon.appendChild(icon);

        confidenceValue.textContent = data.confidence.toFixed(1) + "%";

        resultMessage.textContent = info.summary;
        resultSigns.textContent = info.signs;

        // Next steps
        resultAdvice.innerHTML = "";
        info.advice.forEach((line) => resultAdvice.appendChild(el("li", null, line)));

        // When to see a doctor
        resultDoctor.innerHTML = "";
        resultDoctor.appendChild(el("strong", null, "When to see a doctor"));
        resultDoctor.appendChild(document.createTextNode(info.see_doctor));

        // Caution banner (low confidence and/or the two models disagreed)
        const cautions = [];
        if (data.low_confidence) {
            cautions.push(
                "The model is not very certain about this image. Try a sharper, " +
                "well-lit, close-up photo of a single nail."
            );
        }
        if (!data.models_agree) {
            cautions.push(
                "The two underlying models initially disagreed " +
                `(SVM: ${prettyClass(data.svm.prediction)}, ` +
                `XGBoost: ${prettyClass(data.xgboost.prediction)}); ` +
                "the ensemble chose the more reliable one."
            );
        }
        if (cautions.length) {
            resultAlertText.textContent = cautions.join(" ");
            resultAlert.hidden = false;
        } else {
            resultAlert.hidden = true;
        }

        // Other possibilities (top 3 blended probabilities)
        resultTop.innerHTML = "";
        data.top_predictions
            .filter((item) => item.class !== data.prediction)
            .slice(0, 2)
            .forEach((item) => {
            const row = el("div", "alt-row");
            setSeverity(row, item.severity);
            row.appendChild(el("span", null, item.title));
            row.appendChild(el("strong", null, item.probability.toFixed(1) + "%"));
            const track = el("div", "alt-bar");
            const fill = el("div");
            fill.style.width = Math.max(item.probability, 1) + "%";
            track.appendChild(fill);
            row.appendChild(track);
            resultTop.appendChild(row);
        });

        // Individual model votes
        modelVotes.innerHTML = "";
        [
            ["SVM", data.svm],
            ["XGBoost", data.xgboost]
        ].forEach(([name, m]) => {
            const span = el("span");
            span.appendChild(el("b", null, name + ": "));
            span.appendChild(document.createTextNode(
                `${prettyClass(m.prediction)} (${m.confidence.toFixed(0)}%)`
            ));
            modelVotes.appendChild(span);
        });
        modelVotes.appendChild(el("span", null, `${data.processing_time_ms} ms`));

        // Highlight the matching condition card in the grid above
        document.querySelectorAll(".condition-card").forEach((card) => {
            card.classList.toggle("is-result", card.dataset.class === data.prediction);
        });

        resultCard.classList.add("show");

        setTimeout(() => {
            confidenceBar.style.width = data.confidence + "%";
        }, 100);

        resultCard.scrollIntoView({ behavior: "smooth", block: "center" });
    }


    /* =================================================
       NEW ANALYSIS
    ================================================= */

    newAnalysis.addEventListener("click", () => {

        resetUploader();

        $("scanner").scrollIntoView({ behavior: "smooth" });
    });


    /* =================================================
       MODEL METRICS (from /api/info, measured on the test set)
    ================================================= */

    function barRow(label, value, best) {
        const row = el("div", "bar-row" + (best ? " best" : ""));
        row.appendChild(el("span", null, label));

        const track = el("div", "bar-track");
        const fill = el("div");
        track.appendChild(fill);
        row.appendChild(track);

        row.appendChild(el("span", "bar-val", value.toFixed(1) + "%"));

        // animate once rendered
        requestAnimationFrame(() => requestAnimationFrame(() => {
            fill.style.width = value + "%";
        }));
        return row;
    }

    async function loadMetrics() {

        try {
            const response = await fetch(API_BASE + "/api/info");
            const info = await response.json();
            const m = info.metrics;
            if (!m) return;

            // headline stat in the stats strip
            $("statAccuracy").textContent = m.accuracy.hybrid.toFixed(1) + "%";

            // overall accuracy bars
            const acc = $("accuracyBars");
            acc.innerHTML = "";
            [
                ["Hybrid ensemble", m.accuracy.hybrid, true],
                ["SVM", m.accuracy.svm, false],
                ["XGBoost", m.accuracy.xgboost, false]
            ].forEach(([label, value, best]) =>
                acc.appendChild(barRow(label, value, best)));

            $("metricsNote").textContent =
                `Measured on ${m.test_images} images that were held out from ` +
                "training. Photos taken in everyday conditions may perform " +
                "differently from this curated dataset.";

            // per-class F1
            const cls = $("classBars");
            cls.innerHTML = "";
            const titles = {};
            info.classes.forEach((c) => { titles[c.key] = c.title; });

            m.per_class.forEach((c) => {
                const label = (titles[c.class] || prettyClass(c.class))
                    .replace(/\s*\(.*\)/, "");
                cls.appendChild(barRow(label, c.f1, false));
            });

            $("metricsPanel").hidden = false;

        } catch (err) {
            // Backend offline: the section simply stays hidden.
        }
    }


    /* =================================================
       MOBILE MENU
    ================================================= */

    const mobileMenu = $("mobileMenu");
    const navLinks = document.querySelector(".nav-links");

    mobileMenu.setAttribute("aria-label", "Toggle menu");

    mobileMenu.addEventListener("click", () => {
        navLinks.classList.toggle("mobile-open");
    });

    navLinks.querySelectorAll("a").forEach((link) => {
        link.addEventListener("click", () => navLinks.classList.remove("mobile-open"));
    });


    /* =================================================
       NAVBAR SCROLL EFFECT
    ================================================= */

    window.addEventListener("scroll", () => {

        const navbar = document.querySelector(".navbar");

        navbar.style.boxShadow =
            window.scrollY > 30 ? "0 8px 30px rgba(15,60,80,0.08)" : "none";
    });


    /* =================================================
       START
    ================================================= */

    checkServer().then((online) => {
        if (online) loadMetrics();
    });

});
