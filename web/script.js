const form = document.querySelector("#destination-form");
const destinationInput = document.querySelector("#destination");
const suggestions = document.querySelector("#destination-options");
const formStatus = document.querySelector("#form-status");
const routeLine = document.querySelector("#route-line");
const routePoints = document.querySelector("#route-points");

let appData = null;
let destinationOptions = [];
let destinations = new Set();
let activeSuggestion = -1;

async function loadRoutingData() {
    if (window.ROUTING_DATA) {
        appData = window.ROUTING_DATA;
        destinationOptions = appData.destinations || [];
        destinations = new Set(destinationOptions);
        return;
    }

    try {
        const response = await fetch("data.json");
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        appData = await response.json();
        destinationOptions = appData.destinations || [];
        destinations = new Set(destinationOptions);
    } catch (error) {
        formStatus.textContent = "Fehler beim Laden der Routing-Daten.";
        formStatus.setAttribute("data-error", "true");
        console.error("Routing data load failed:", error);
    }
}

function closeSuggestions() {
    suggestions.classList.remove("is-open");
    destinationInput.setAttribute("aria-expanded", "false");
    activeSuggestion = -1;
}

function renderSuggestions(showAll = false) {
    const query = showAll ? "" : destinationInput.value.trim().toLowerCase();
    const matches = destinationOptions.filter((destination) => destination.includes(query));

    suggestions.replaceChildren();
    matches.forEach((destination, index) => {
        const suggestion = document.createElement("li");
        suggestion.className = "suggestion";
        suggestion.setAttribute("role", "option");
        suggestion.textContent = destination;
        suggestion.addEventListener("mousedown", (event) => {
            event.preventDefault();
            destinationInput.value = destination;
            closeSuggestions();
        });
        suggestion.dataset.index = index;
        suggestions.appendChild(suggestion);
    });

    activeSuggestion = -1;
    suggestions.classList.toggle("is-open", matches.length > 0);
    destinationInput.setAttribute("aria-expanded", String(matches.length > 0));
}

destinationInput.addEventListener("input", renderSuggestions);
destinationInput.addEventListener("focus", () => renderSuggestions(true));
destinationInput.addEventListener("click", () => renderSuggestions(true));
destinationInput.addEventListener("keydown", (event) => {
    const items = [...suggestions.querySelectorAll(".suggestion")];

    if (event.key === "Escape") {
        closeSuggestions();
        return;
    }

    if (!items.length || !suggestions.classList.contains("is-open")) {
        return;
    }

    if (event.key === "ArrowDown" || event.key === "ArrowUp") {
        event.preventDefault();
        activeSuggestion = (activeSuggestion + (event.key === "ArrowDown" ? 1 : -1) + items.length) % items.length;
        items.forEach((item, index) => item.classList.toggle("is-active", index === activeSuggestion));
        destinationInput.value = items[activeSuggestion].textContent;
    }

    if (event.key === "Enter" && activeSuggestion >= 0) {
        event.preventDefault();
        closeSuggestions();
    }
});

document.addEventListener("click", (event) => {
    if (!event.target.closest(".input-field")) {
        closeSuggestions();
    }
});

function drawPath(path) {
    if (!appData || !appData.points) {
        return;
    }

    routeLine.setAttribute(
        "points",
        path.map((point) => appData.points[point].join(",")).join(" ")
    );
    routeLine.classList.remove("route-visible");
    void routeLine.offsetWidth;
    routeLine.classList.add("route-visible");
    routePoints.replaceChildren();

    for (const [index, point] of path.entries()) {
        const marker = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        marker.setAttribute("cx", appData.points[point][0]);
        marker.setAttribute("cy", appData.points[point][1]);
        marker.setAttribute("r", index === 0 || index === path.length - 1 ? "9" : "5");
        marker.setAttribute("class", index === path.length - 1 ? "route-point destination-point" : "route-point");
        routePoints.appendChild(marker);
    }
}

form.addEventListener("submit", (event) => {
    event.preventDefault();

    if (!appData) {
        formStatus.textContent = "Routing-Daten werden noch geladen. Bitte warten.";
        formStatus.setAttribute("data-error", "true");
        return;
    }

    const destination = destinationInput.value.trim().toLowerCase();

    if (!destinations.has(destination)) {
        routeLine.setAttribute("points", "");
        routeLine.classList.remove("route-visible");
        routePoints.replaceChildren();
        formStatus.textContent = "Bitte wähle ein bekanntes Ziel aus der Liste.";
        formStatus.setAttribute("data-error", "true");
        return;
    }

    const path = appData.routes ? appData.routes[destination] : null;

    if (!path) {
        formStatus.textContent = "Für dieses Ziel wurde kein Weg gefunden.";
        formStatus.setAttribute("data-error", "true");
        return;
    }

    drawPath(path);
    formStatus.removeAttribute("data-error");
    formStatus.textContent = `Weg zu „${destination}“ angezeigt.`;
});

loadRoutingData();

