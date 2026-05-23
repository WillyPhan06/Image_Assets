// ==UserScript==
// @name         Sim Companies Multi Skin Loader
// @namespace    http://tampermonkey.net/
// @version      3.0
// @description  Replace multiple Sim Companies building skins
// @author       Willy Phan (The Simco Loli Youtube)
// @match        https://www.simcompanies.com/*
// @grant        none
// ==/UserScript==

(function () {
    'use strict';

    /*
    ============================================================
    THEME SELECTION
    ============================================================
    */

    const STORAGE_KEY = "simCompaniesTheme";
    const AVAILABLE_THEMES = ["galaxy", "japan", "vietnam"];
    let selectedTheme = null;
    let menuOpen = false;

    /*
    ============================================================
    INITIALIZE THEME
    ============================================================
    */

    function initializeTheme() {
        // Check if user manually selected a theme (from menu click)
        const stored = localStorage.getItem(STORAGE_KEY);
        
        if (stored) {
            selectedTheme = stored;
            localStorage.removeItem(STORAGE_KEY); // Clear after using
            console.log("[Sim Skin Loader] Using manually selected theme:", selectedTheme);
            return;
        }

        // Otherwise, randomly select a theme
        selectedTheme = AVAILABLE_THEMES[Math.floor(Math.random() * AVAILABLE_THEMES.length)];
        console.log("[Sim Skin Loader] Randomly selected theme:", selectedTheme);
    }

    /*
    ============================================================
    THEME SELECTOR UI
    ============================================================
    */

    function showThemeSelector() {
        menuOpen = true;
        return new Promise((resolve) => {
            const overlay = document.createElement("div");
            overlay.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.7);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 999999;
                font-family: Arial, sans-serif;
            `;

            const modal = document.createElement("div");
            modal.style.cssText = `
                background: white;
                padding: 30px;
                border-radius: 10px;
                text-align: center;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            `;

            const title = document.createElement("h2");
            title.textContent = "Sim Companies Theme";
            title.style.marginBottom = "20px";
            title.style.marginTop = "0";
            modal.appendChild(title);

            const buttonContainer = document.createElement("div");
            buttonContainer.style.display = "flex";
            buttonContainer.style.gap = "15px";
            buttonContainer.style.justifyContent = "center";
            buttonContainer.style.flexWrap = "wrap";

            // Theme icons mapping
            const themeIcons = {
                japan: "🇯🇵",
                vietnam: "🇻🇳"
            };

            AVAILABLE_THEMES.forEach((theme) => {
                const btn = document.createElement("button");
                const icon = themeIcons[theme] || "🎨";
                const label = theme.charAt(0).toUpperCase() + theme.slice(1);
                btn.innerHTML = `${icon}<br>${label}`;
                btn.style.cssText = `
                    padding: 15px 20px;
                    font-size: 14px;
                    cursor: pointer;
                    border: 2px solid #007bff;
                    border-radius: 8px;
                    background: ${selectedTheme === theme ? "#007bff" : "white"};
                    color: ${selectedTheme === theme ? "white" : "#007bff"};
                    transition: all 0.3s;
                    min-width: 100px;
                    font-weight: bold;
                `;

                btn.onmouseover = () => {
                    btn.style.background = "#007bff";
                    btn.style.color = "white";
                };

                btn.onmouseout = () => {
                    btn.style.background = selectedTheme === theme ? "#007bff" : "white";
                    btn.style.color = selectedTheme === theme ? "white" : "#007bff";
                };

                btn.onclick = () => {
                    localStorage.setItem(STORAGE_KEY, theme);
                    selectedTheme = theme;
                    console.log("[Sim Skin Loader] Theme changed to:", theme);
                    console.log("[Sim Skin Loader] Reloading page...");
                    location.reload();
                };

                buttonContainer.appendChild(btn);
            });

            modal.appendChild(buttonContainer);

            const closeHint = document.createElement("p");
            closeHint.textContent = "Press ESC or M to close";
            closeHint.style.cssText = `
                margin-top: 20px;
                font-size: 12px;
                color: #666;
            `;
            modal.appendChild(closeHint);

            overlay.appendChild(modal);
            document.body.appendChild(overlay);

            // Close on ESC and M key
            const escHandler = (e) => {
                if (e.key === "Escape" || e.key === "m" || e.key === "M") {
                    menuOpen = false;
                    overlay.remove();
                    document.removeEventListener("keydown", escHandler);
                    resolve(null);
                }
            };
            document.addEventListener("keydown", escHandler);
        });
    }

    /*
    ============================================================
    CONFIG
    ============================================================

    FORMAT:

    "ORIGINAL_KEYWORD": {
        image: "BASE_IMAGE_NAME",
        land:  "LAND_TILE_URL"
    }

    ============================================================
    */
    const DEFAULT_LAND_URL = "/static/images/buildings/tiles/concrete-0000.f92fedbaba84.png"
    const CDN_BASE_URL = "https://cdn.jsdelivr.net/gh/WillyPhan06/Image_Assets@main/sim_companies/themes";

    /*
    ============================================================
    BUILD IMAGE URL DYNAMICALLY
    ============================================================
    */

    function buildImageUrl(baseImageName, theme) {
        const ext = baseImageName.includes(".jpg") ? ".jpg" : ".png";
        const nameWithoutExt = baseImageName.replace(/\.(png|jpg)$/, "");

        // Extract version part if it exists (e.g., "_v4")
        const versionMatch = nameWithoutExt.match(/(_v\d+)$/);
        const version = versionMatch ? versionMatch[1] : "";
        const baseName = nameWithoutExt.replace(/(_v\d+)$/, "");

        return `${CDN_BASE_URL}/${theme}/${baseName}_${theme}${version}${ext}`;
    }

    const REPLACEMENTS = {

        // SALES OFFICE TIER 6
        "sales_offices_tier06": {

            image:
            "sales_office_level.png",

            land:
            DEFAULT_LAND_URL
        },

        "refinery_tier06": {
            image:
            "refinery_level.png",

            land:
            DEFAULT_LAND_URL
        },

        "factory_tier06": {
            image:
            "factory_level.png",

            land:
            DEFAULT_LAND_URL
        },

        "factory_tier05": {
            image:
            "factory_level.png",

            land:
            DEFAULT_LAND_URL
        },

        "propulsion_factory_tier04": {
            image:
            "propulsion_factory_level.png",

            land:
            DEFAULT_LAND_URL
        },

        "propulsion_factory_tier06": {
            image:
            "propulsion_factory_level.png",

            land:
            DEFAULT_LAND_URL
        },

        "aerospace_factory_tier04": {
            image:
            "aerospace_factory_level.png",

            land:
            DEFAULT_LAND_URL
        },

        "aerospace_factory_tier06": {
            image:
            "aerospace_factory_level.png",

            land:
            DEFAULT_LAND_URL
        },

        "hangar_tier04": {
            image:
            "hangar_level.png",

            land:
            DEFAULT_LAND_URL
        },

        "hangar_tier06": {
            image:
            "hangar_level.png",

            land:
            DEFAULT_LAND_URL
        },

        "vertical_integration_facility_tier03": {
            image:
            "vertical_integration_facility_level.png",

            land:
            DEFAULT_LAND_URL
        },

        "vertical_integration_facility_tier06": {
            image:
            "vertical_integration_facility_level.png",

            land:
            DEFAULT_LAND_URL
        },

        "electronics_factory_tier04": {
            image:
            "electronic_factory_level.png",

            land:
            DEFAULT_LAND_URL
        },

        "electronics_factory_tier05": {
            image:
            "electronic_factory_level.png",

            land:
            DEFAULT_LAND_URL
        },

        "electronics_factory_tier06": {
            image:
            "electronic_factory_level.png",

            land:
            DEFAULT_LAND_URL
        },

        "aerospace_electronics_tier05": {
            image:
            "aerospace_electronics_level.png",

            land:
            DEFAULT_LAND_URL
        },

        "aerospace_electronics_tier06": {
            image:
            "aerospace_electronics_level.png",

            land:
            DEFAULT_LAND_URL
        },

        "carfactory-lvl1": {
            image:
            "car_factory_level.png",

            land:
            DEFAULT_LAND_URL
        },

        "carfactory-lvl2": {
            image:
            "car_factory_level.png",

            land:
            DEFAULT_LAND_URL
        },

        "academy_tier03": {
            image:
            "academy_level.png",

            land:
            DEFAULT_LAND_URL
        },

        "academy_tier04": {
            image:
            "academy_level.png",

            land:
            DEFAULT_LAND_URL
        },

        "academy_tier05": {
            image:
            "academy_level.png",

            land:
            DEFAULT_LAND_URL
        },

        "exchange_tier10": {
            image:
            "exchange.png",

            land:
            DEFAULT_LAND_URL
        },

        "hq-uk-bell-tower": {
            image:
            "uk_hq_bell_tower.png",

            land:
            DEFAULT_LAND_URL
        },

        "town_square_01": {
            image:
            "town_square.png",

            land:
            DEFAULT_LAND_URL
        },

        "forrest_02": {
            image:
            "forest.png",

            land:
            DEFAULT_LAND_URL
        },

        "residential_02": {
            image:
            "forest.png",

            land:
            DEFAULT_LAND_URL
        },

        "lake_tier03": {
            image:
            "lake.png",

            land:
            DEFAULT_LAND_URL
        },

        "oil_rig_tier05": {
            image:
            "oil_rig_level.png",

            land:
            DEFAULT_LAND_URL
        },

        "oil_rig_tier06": {
            image:
            "oil_rig_level.png",

            land:
            DEFAULT_LAND_URL
        },

        "sc_background_main_dark_2k_v2": {
            image:
            "main_background_v8.jpg",

            land:
            DEFAULT_LAND_URL
        },

        "portrait": {
            image:
            "portrait.jpg",

            land:
            DEFAULT_LAND_URL
        },

    };

    /*
    ============================================================
    REPLACEMENT LOGIC
    ============================================================
    */

    function clearReplacementMarkers() {
        const divs = document.querySelectorAll("[data-skin-replaced]");
        divs.forEach(div => {
            delete div.dataset.skinReplaced;
        });

        const images = document.querySelectorAll("img[data-skin-replaced]");
        images.forEach(img => {
            delete img.dataset.skinReplaced;
        });
    }

    function replaceBuildings() {

        const divs = document.querySelectorAll("div");

        divs.forEach(div => {

            const style = window.getComputedStyle(div);

            const bgImage = style.backgroundImage;

            if (!bgImage) return;

            // Find matching keyword
            const matchedKey = Object.keys(REPLACEMENTS).find(
                key => bgImage.includes(`/${key}.`)
            );

            if (!matchedKey) return;

            // Prevent infinite loop
            if (div.dataset.skinReplaced === "true") return;

            console.log(
                "[Sim Skin Loader] Replacing:",
                matchedKey
            );

            const replacement = REPLACEMENTS[matchedKey];
            const imageUrl = buildImageUrl(replacement.image, selectedTheme);

            /*
            ============================================================
            PRESERVE ORIGINAL SIZE
            ============================================================
            */

            const width = style.width;
            const height = style.height;

            /*
            ============================================================
            REPLACE BACKGROUND IMAGE
            ============================================================
            */

            const isMainBackground =
                  matchedKey === "sc_background_main_dark_2k_v2";

            if (isMainBackground) {
                div.style.backgroundImage = `url(${imageUrl})`;

                div.style.backgroundSize = "cover";
                div.style.backgroundPosition = "center";
                div.style.backgroundRepeat = "no-repeat";

            } else {
                div.style.backgroundImage =
                    `url(${imageUrl}), url(${replacement.land})`;

                div.style.backgroundSize =
                    `${width} ${height}, ${width} ${height}`;

                div.style.backgroundRepeat =
                    "no-repeat, no-repeat";

                div.style.backgroundPosition =
                    "0px 0px, 0px 0px";
            }

            div.style.backgroundRepeat =
            "no-repeat, no-repeat";

            div.style.backgroundPosition =
            "0px 0px, 0px 0px";

            div.style.isolation = "isolate";

            div.dataset.skinReplaced = "true";
        });

        const images = document.querySelectorAll("img");

        images.forEach(img => {
            const src = img.src;
            if (!src) return;

            const matchedKey = Object.keys(REPLACEMENTS).find(
                key => src.includes(`/${key}.`)
            );

            if (!matchedKey) return;

            if (img.dataset.skinReplaced === "true") return;

            console.log("[Sim Skin Loader] Replacing IMG:", matchedKey);

            const replacement = REPLACEMENTS[matchedKey];
            const imageUrl = buildImageUrl(replacement.image, selectedTheme);

            img.src = imageUrl;

            img.dataset.skinReplaced = "true";
});
    }

    /*
    ============================================================
    OBSERVER
    ============================================================
    */

    const observer = new MutationObserver(() => {
        replaceBuildings();
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true
    });

    /*
    ============================================================
    KEYBOARD SHORTCUT FOR THEME MENU
    ============================================================
    */

    document.addEventListener("keydown", (e) => {
        if ((e.key === "m" || e.key === "M") && !e.ctrlKey && !e.altKey) {
            if (!menuOpen) {
                console.log("[Sim Skin Loader] Theme menu opened (M key)");
                showThemeSelector();
            }
        }
    });

    /*
    ============================================================
    INITIAL RUN
    ============================================================
    */

    window.addEventListener('load', () => {

        console.log("[Sim Skin Loader] Initializing...");

        // Initialize theme (randomize if not stored)
        initializeTheme();

        console.log("[Sim Skin Loader] Loaded - Using theme:", selectedTheme);

        replaceBuildings();
    });

})();