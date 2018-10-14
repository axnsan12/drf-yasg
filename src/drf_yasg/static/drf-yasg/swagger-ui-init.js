"use strict";
var currentPath = window.location.protocol + "//" + window.location.host + window.location.pathname;
var defaultSpecUrl = currentPath + '?format=openapi';
var savedAuth = Immutable.fromJS({});
try {
    savedAuth = Immutable.fromJS(JSON.parse(localStorage.getItem("drf-yasg-auth")) || {});
} catch (e) {
    localStorage.removeItem("drf-yasg-auth");
}
var swaggerUiConfig = {
    url: defaultSpecUrl,
    dom_id: '#swagger-ui',
    displayRequestDuration: true,
    presets: [
        SwaggerUIBundle.presets.apis,
        SwaggerUIStandalonePreset
    ],
    plugins: [
        SwaggerUIBundle.plugins.DownloadUrl
    ],
    layout: "StandaloneLayout",
    filter: true,
    requestInterceptor: function (request) {
        var headers = request.headers || {};
        var csrftoken = document.querySelector("[name=csrfmiddlewaretoken]");
        if (csrftoken) {
            headers["X-CSRFToken"] = csrftoken.value;
        }

        if (request.loadSpec) {
            applyAuth(savedAuth, headers);
        }
        return request;
    },
    onComplete: function () {
        preauthorizeAny(savedAuth, window.ui);
        hookAuthActions(window.ui);
    },
};

function patchSwaggerUi() {
    if (document.querySelector('.auth-wrapper #django-session-auth')) {
        return;
    }

    var authWrapper = document.querySelector('.auth-wrapper');
    var authorizeButton = document.querySelector('.auth-wrapper .authorize');
    var djangoSessionAuth = document.querySelector('#django-session-auth');

    if (!djangoSessionAuth) {
        console.log("WARNING: session auth disabled");
        return;
    }

    djangoSessionAuth = djangoSessionAuth.cloneNode(true);
    authWrapper.insertBefore(djangoSessionAuth, authorizeButton);
    djangoSessionAuth.classList.remove("hidden");
}

function initSwaggerUi() {
    if (window.ui) {
        console.log("WARNING: skipping initSwaggerUi() because window.ui is already defined");
        return;
    }

    var swaggerSettings = JSON.parse(document.getElementById('swagger-settings').innerHTML);
    if (!('oauth2RedirectUrl' in swaggerSettings)) {
        var oauth2RedirectUrl = document.getElementById('oauth2-redirect-url');
        if (oauth2RedirectUrl) {
            swaggerSettings['oauth2RedirectUrl'] = oauth2RedirectUrl.href;
            oauth2RedirectUrl.parentNode.removeChild(oauth2RedirectUrl);
        }
    }

    console.log('swaggerSettings', swaggerSettings);
    for (var p in swaggerSettings) {
        if (swaggerSettings.hasOwnProperty(p)) {
            swaggerUiConfig[p] = swaggerSettings[p];
        }
    }

    var oauth2Config = JSON.parse(document.getElementById('oauth2-config').innerHTML);
    console.log('oauth2Config', oauth2Config);
    window.ui = SwaggerUIBundle(swaggerUiConfig);
    window.ui.initOAuth(oauth2Config);
}

function preauthorizeAny(savedAuth, sui) {
    var schemeName = savedAuth.get("name"), schemeType = savedAuth.getIn(["schema", "type"]);
    if (schemeType === "basic" && schemeName) {
        var username = savedAuth.getIn(["value", "username"]);
        var password = savedAuth.getIn(["value", "password"]);
        if (username && password) {
            sui.preauthorizeBasic(schemeName, username, password);
        }
    } else if (schemeType === "apiKey" && schemeName) {
        var key = savedAuth.get("value");
        if (key) {
            sui.preauthorizeApiKey(schemeName, key);
        }
    }
}

function applyAuth(savedAuth, requestHeaders) {
    var schemeName = savedAuth.get("name"), schemeType = savedAuth.getIn(["schema", "type"]);
    if (schemeType === "basic" && schemeName) {
        var username = savedAuth.getIn(["value", "username"]);
        var password = savedAuth.getIn(["value", "password"]);
        if (username && password) {
            requestHeaders["Authorization"] = "Basic " + btoa(username + ":" + password);
        }
    } else if (schemeType === "apiKey" && schemeName) {
        var key = savedAuth.get("value"), _in = savedAuth.getIn(["schema", "in"]);
        var paramName = savedAuth.getIn(["schema", "name"]);
        if (key && paramName && _in === "header") {
            requestHeaders[paramName] = key;
        }
        if (_in === "query") {
            console.warn("WARNING: cannot apply apiKey query parameter via interceptor");
        }
    }
}

function hookAuthActions(sui) {
    var originalAuthorize = sui.authActions.authorize;
    sui.authActions.authorize = function (authorization) {
        originalAuthorize(authorization);
        // authorization is map of scheme name to scheme object
        // need to use ImmutableJS because schema is already an ImmutableJS object
        var schemes = Immutable.fromJS(authorization);
        var auth = schemes.valueSeq().first();
        localStorage.setItem("drf-yasg-auth", JSON.stringify(auth.toJSON()));
        savedAuth = auth;
        sui.specActions.download();
    };

    var originalLogout = sui.authActions.logout;
    sui.authActions.logout = function (authorization) {
        if (savedAuth.get("name") === authorization[0]) {
            localStorage.removeItem("drf-yasg-auth");
            savedAuth = Immutable.fromJS({});
        }
        originalLogout(authorization);
    };
}

window.addEventListener('load', function () {
    initSwaggerUi();

    if (document.querySelector('.auth-wrapper .authorize')) {
        patchSwaggerUi();
    }
    else {
        insertionQ('.auth-wrapper .authorize').every(patchSwaggerUi);
    }
});
