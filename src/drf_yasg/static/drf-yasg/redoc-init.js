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
