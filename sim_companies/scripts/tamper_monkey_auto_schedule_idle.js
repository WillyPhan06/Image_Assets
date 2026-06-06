// ==UserScript==
// @name         Auto VClock Idle Alarm
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  Open a vClock timer for the next idle building.
// @author       Willy Phan (The Simco Loli Youtube)
// @match        https://www.simcompanies.com/*
// @grant        none
// ==/UserScript==

(function () {
'use strict';

function buildVClockUrl(targetDate) {
    const formatted =
        `${targetDate.getFullYear()}-` +
        `${String(targetDate.getMonth() + 1).padStart(2, '0')}-` +
        `${String(targetDate.getDate()).padStart(2, '0')}T` +
        `${String(targetDate.getHours()).padStart(2, '0')}:` +
        `${String(targetDate.getMinutes()).padStart(2, '0')}:` +
        `${String(targetDate.getSeconds()).padStart(2, '0')}`;

    return `https://vclock.com/timer/#date=${formatted}&sound=xylophone&loop=1`;
}

function createTimer() {
    const timeEl = document.querySelector('time[datetime]');

    if (!timeEl) {
        console.log('[Idle Alarm] No time element found.');
        return false;
    }

    const isoTime = timeEl.getAttribute('datetime');

    if (!isoTime) {
        console.log('[Idle Alarm] No datetime attribute found.');
        return false;
    }

    const targetDate = new Date(isoTime);

    if (isNaN(targetDate.getTime())) {
        console.log('[Idle Alarm] Invalid date.');
        return false;
    }

    const url = buildVClockUrl(targetDate);

    console.log('[Idle Alarm] Opening VClock:', url);

    window.open(url, '_blank');

    return true;
}

const waitForTimer = setInterval(() => {
    if (createTimer()) {
        clearInterval(waitForTimer);
    }
}, 1000);


})();
