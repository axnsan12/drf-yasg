"use strict";

var currentPath = window.location.protocol + "//" + window.location.host + window.location.pathname;
var specURL = currentPath + '?format=openapi';
var redoc = document.createElement("redoc");
redoc.setAttribute("spec-url", specURL);

var redocSettings = JSON.parse(document.getElementById('redoc-settings').innerHTML);
if (redocSettings.lazyRendering) {
    redoc.setAttribute("lazy-rendering", '');
}
if (redocSettings.pathInMiddle) {
    redoc.setAttribute("path-in-middle-panel", '');
}
if (redocSettings.hideHostname) {
    redoc.setAttribute("hide-hostname", '');
}
redoc.setAttribute("expand-responses", redocSettings.expandResponses);
document.body.appendChild(redoc);

function hideEmptyVersion() {
    // 'span.api-info-version' is for redoc 1.x, 'div.api-info span' is for redoc 2-alpha
    var apiVersion = document.querySelector('span.api-info-version') || document.querySelector('div.api-info span');
    if (!apiVersion) {
        console.log("WARNING: could not find API versionString element (span.api-info-version)");
        return;
    }

    var versionString = apiVersion.innerText;
    if (versionString) {
        // trim spaces and surrounding ()
        versionString = versionString.replace(/ /g,'');
        versionString = versionString.replace(/(^\()|(\)$)/g,'');
    }

    if (!versionString) {
        // hide version element if empty
        apiVersion.classList.add("hidden");
    }
}

if (document.querySelector('span.api-info-version') || document.querySelector('div.api-info span')) {
    hideEmptyVersion();
}
else {
    insertionQ('span.api-info-version').every(hideEmptyVersion);
    insertionQ('div.api-info span').every(hideEmptyVersion);
}
