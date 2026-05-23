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
    CONFIG
    ============================================================

    FORMAT:

    "ORIGINAL_KEYWORD": {
        image: "CUSTOM_IMAGE_URL",
        land:  "LAND_TILE_URL"
    }

    ============================================================
    */
    const DEFAULT_LAND_URL = "/static/images/buildings/tiles/concrete-0000.f92fedbaba84.png"

    const REPLACEMENTS = {

        // SALES OFFICE TIER 6
        "sales_offices_tier06": {

            image:
            "https://cdn.jsdelivr.net/gh/WillyPhan06/Image_Assets@main/sim_companies/sales_office_level_15_japan_v4.png",

            land:
            DEFAULT_LAND_URL
        },

        "refinery_tier06": {
            image:
            "https://cdn.jsdelivr.net/gh/WillyPhan06/Image_Assets@main/sim_companies/refinery_level_15_japan_v2.png",

            land:
            DEFAULT_LAND_URL
        },

        "factory_tier06": {
            image:
            "https://cdn.jsdelivr.net/gh/WillyPhan06/Image_Assets@main/sim_companies/factory_level_15_japan.png",

            land:
            DEFAULT_LAND_URL
        },

        "factory_tier05": {
            image:
            "https://cdn.jsdelivr.net/gh/WillyPhan06/Image_Assets@main/sim_companies/factory_level_15_japan.png",

            land:
            DEFAULT_LAND_URL
        },

        "propulsion_factory_tier04": {
            image:
            "https://cdn.jsdelivr.net/gh/WillyPhan06/Image_Assets@main/sim_companies/propulsion_factory_level_15_japan.png",

            land:
            DEFAULT_LAND_URL
        },

        "propulsion_factory_tier06": {
            image:
            "https://cdn.jsdelivr.net/gh/WillyPhan06/Image_Assets@main/sim_companies/propulsion_factory_level_15_japan.png",

            land:
            DEFAULT_LAND_URL
        },

        "aerospace_factory_tier04": {
            image:
            "https://cdn.jsdelivr.net/gh/WillyPhan06/Image_Assets@main/sim_companies/aerospace_factory_level_15_japan_v2.png",

            land:
            DEFAULT_LAND_URL
        },

        "aerospace_factory_tier06": {
            image:
            "https://cdn.jsdelivr.net/gh/WillyPhan06/Image_Assets@main/sim_companies/aerospace_factory_level_15_japan_v2.png",

            land:
            DEFAULT_LAND_URL
        },

        "hangar_tier04": {
            image:
            "https://cdn.jsdelivr.net/gh/WillyPhan06/Image_Assets@main/sim_companies/hangar_level_15_japan.png",

            land:
            DEFAULT_LAND_URL
        },

        "hangar_tier06": {
            image:
            "https://cdn.jsdelivr.net/gh/WillyPhan06/Image_Assets@main/sim_companies/hangar_level_15_japan.png",

            land:
            DEFAULT_LAND_URL
        },

        "vertical_integration_facility_tier03": {
            image:
            "https://cdn.jsdelivr.net/gh/WillyPhan06/Image_Assets@main/sim_companies/vertical_integration_facility_level_15_japan_v2.png",

            land:
            DEFAULT_LAND_URL
        },

        "vertical_integration_facility_tier06": {
            image:
            "https://cdn.jsdelivr.net/gh/WillyPhan06/Image_Assets@main/sim_companies/vertical_integration_facility_level_15_japan_v2.png",

            land:
            DEFAULT_LAND_URL
        },

        "electronics_factory_tier04": {
            image:
            "https://cdn.jsdelivr.net/gh/WillyPhan06/Image_Assets@main/sim_companies/electronic_factory_level_15_japan.png",

            land:
            DEFAULT_LAND_URL
        },

        "electronics_factory_tier05": {
            image:
            "https://cdn.jsdelivr.net/gh/WillyPhan06/Image_Assets@main/sim_companies/electronic_factory_level_15_japan.png",

            land:
            DEFAULT_LAND_URL
        },

        "electronics_factory_tier06": {
            image:
            "https://cdn.jsdelivr.net/gh/WillyPhan06/Image_Assets@main/sim_companies/electronic_factory_level_15_japan.png",

            land:
            DEFAULT_LAND_URL
        },

        "aerospace_electronics_tier05": {
            image:
            "https://cdn.jsdelivr.net/gh/WillyPhan06/Image_Assets@main/sim_companies/aerospace_electronics_level_15_japan_v2.png",

            land:
            DEFAULT_LAND_URL
        },

        "aerospace_electronics_tier06": {
            image:
            "https://cdn.jsdelivr.net/gh/WillyPhan06/Image_Assets@main/sim_companies/aerospace_electronics_level_15_japan_v2.png",

            land:
            DEFAULT_LAND_URL
        },

        "carfactory-lvl1": {
            image:
            "https://cdn.jsdelivr.net/gh/WillyPhan06/Image_Assets@main/sim_companies/car_factory_level_15_japan.png",

            land:
            DEFAULT_LAND_URL
        },

        "carfactory-lvl2": {
            image:
            "https://cdn.jsdelivr.net/gh/WillyPhan06/Image_Assets@main/sim_companies/car_factory_level_15_japan.png",

            land:
            DEFAULT_LAND_URL
        },

        "academy_tier03": {
            image:
            "https://cdn.jsdelivr.net/gh/WillyPhan06/Image_Assets@main/sim_companies/academy_level_20_japan.png",

            land:
            DEFAULT_LAND_URL
        },

        "academy_tier04": {
            image:
            "https://cdn.jsdelivr.net/gh/WillyPhan06/Image_Assets@main/sim_companies/academy_level_20_japan.png",

            land:
            DEFAULT_LAND_URL
        },

        "academy_tier05": {
            image:
            "https://cdn.jsdelivr.net/gh/WillyPhan06/Image_Assets@main/sim_companies/academy_level_20_japan.png",

            land:
            DEFAULT_LAND_URL
        },

        "exchange_tier10": {
            image:
            "https://cdn.jsdelivr.net/gh/WillyPhan06/Image_Assets@main/sim_companies/exchange_japan.png",

            land:
            DEFAULT_LAND_URL
        },

        "hq-uk-bell-tower": {
            image:
            "https://cdn.jsdelivr.net/gh/WillyPhan06/Image_Assets@main/sim_companies/uk_hq_bell_tower_japan.png",

            land:
            DEFAULT_LAND_URL
        },

        "town_square_01": {
            image:
            "https://cdn.jsdelivr.net/gh/WillyPhan06/Image_Assets@main/sim_companies/town_square_japan.png",

            land:
            DEFAULT_LAND_URL
        },

        "forrest_02": {
            image:
            "https://cdn.jsdelivr.net/gh/WillyPhan06/Image_Assets@main/sim_companies/forest_japan.png",

            land:
            DEFAULT_LAND_URL
        },

        "residential_02": {
            image:
            "https://cdn.jsdelivr.net/gh/WillyPhan06/Image_Assets@main/sim_companies/forest_japan.png",

            land:
            DEFAULT_LAND_URL
        },

        "lake_tier03": {
            image:
            "https://cdn.jsdelivr.net/gh/WillyPhan06/Image_Assets@main/sim_companies/lake_japan.png",

            land:
            DEFAULT_LAND_URL
        },

        "oil_rig_tier05": {
            image:
            "https://cdn.jsdelivr.net/gh/WillyPhan06/Image_Assets@main/sim_companies/oil_rig_level_15_japan.png",

            land:
            DEFAULT_LAND_URL
        },

        "oil_rig_tier06": {
            image:
            "https://cdn.jsdelivr.net/gh/WillyPhan06/Image_Assets@main/sim_companies/oil_rig_level_15_japan.png",

            land:
            DEFAULT_LAND_URL
        },

        "sc_background_main_dark_2k_v2": {
            image:
            "https://cdn.jsdelivr.net/gh/WillyPhan06/Image_Assets@main/sim_companies/main_background_japan_v6.jpg",

            land:
            DEFAULT_LAND_URL
        },

    };

    /*
    ============================================================
    REPLACEMENT LOGIC
    ============================================================
    */

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
                div.style.backgroundImage = `url(${replacement.image})`;

                div.style.backgroundSize = "cover";
                div.style.backgroundPosition = "center";
                div.style.backgroundRepeat = "no-repeat";

            } else {
                div.style.backgroundImage =
                    `url(${replacement.image}), url(${replacement.land})`;

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

            img.src = replacement.image;

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
    INITIAL RUN
    ============================================================
    */

    window.addEventListener('load', () => {

        console.log("[Sim Skin Loader] Loaded");

        replaceBuildings();
    });

})();