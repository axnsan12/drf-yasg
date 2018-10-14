"use strict";
var currentPath = window.location.protocol + "//" + window.location.host + window.location.pathname;
var defaultSpecUrl = currentPath + '?format=openapi';

// load the saved authorization state from localStorage; ImmutableJS is used for consistency with swagger-ui state
var savedAuth = Immutable.fromJS({});

// global SwaggerUI config object; can be changed directly or by hooking initSwaggerUiConfig
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

        return request;
    }
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
    if (document.querySelector('.auth-wrapper .authorize')) {
        patchSwaggerUi();
    }
    else {
        insertionQ('.auth-wrapper .authorize').every(patchSwaggerUi);
    }

    var swaggerSettings = JSON.parse(document.getElementById('swagger-settings').innerHTML);

    var oauth2RedirectUrl = document.getElementById('oauth2-redirect-url');
    if (oauth2RedirectUrl) {
        if (!('oauth2RedirectUrl' in swaggerSettings)) {
            if (oauth2RedirectUrl) {
                swaggerSettings['oauth2RedirectUrl'] = oauth2RedirectUrl.href;
            }
        }
        oauth2RedirectUrl.parentNode.removeChild(oauth2RedirectUrl);
    }

    console.log('swaggerSettings', swaggerSettings);
    var oauth2Config = JSON.parse(document.getElementById('oauth2-config').innerHTML);
    console.log('oauth2Config', oauth2Config);

    initSwaggerUiConfig(swaggerSettings, oauth2Config);
    window.ui = SwaggerUIBundle(swaggerUiConfig);
    window.ui.initOAuth(oauth2Config);
}

/**
 * Initialize the global swaggerUiConfig with any given additional settings.
 * @param swaggerSettings SWAGGER_SETTINGS from Django settings
 * @param oauth2Settings OAUTH2_CONFIG from Django settings
 */
function initSwaggerUiConfig(swaggerSettings, oauth2Settings) {
    var persistAuth = swaggerSettings.persistAuth;
    var refetchWithAuth = swaggerSettings.refetchWithAuth;
    var refetchOnLogout = swaggerSettings.refetchOnLogout;
    delete swaggerSettings['persistAuth'];
    delete swaggerSettings['refetchWithAuth'];
    delete swaggerSettings['refetchOnLogout'];

    for (var p in swaggerSettings) {
        if (swaggerSettings.hasOwnProperty(p)) {
            swaggerUiConfig[p] = swaggerSettings[p];
        }
    }

    if (persistAuth || refetchWithAuth) {
        var hookedAuth = false;
        if (persistAuth) {
            try {
                savedAuth = Immutable.fromJS(JSON.parse(localStorage.getItem("drf-yasg-auth")) || {});
            } catch (e) {
                localStorage.removeItem("drf-yasg-auth");
            }
        }

        var oldOnComplete = swaggerUiConfig.onComplete;
        swaggerUiConfig.onComplete = function () {
            if (persistAuth) {
                preauthorizeAny(savedAuth, window.ui);
            }

            if (!hookedAuth) {
                hookAuthActions(window.ui, persistAuth, refetchWithAuth, refetchOnLogout);
                hookedAuth = true;
            }
            if (oldOnComplete) {
                oldOnComplete();
            }
        };

        var specRequestsInFlight = [];
        var oldRequestInterceptor = swaggerUiConfig.requestInterceptor;
        swaggerUiConfig.requestInterceptor = function (request) {
            var headers = request.headers || {};
            if (refetchWithAuth && request.loadSpec) {
                var newUrl = applyAuth(savedAuth, request.url, headers) || request.url;
                if (newUrl !== request.url) {
                    request.url = newUrl;
                }

                // need to manually remember requests for spec urls because
                // responseInterceptor has no reference to the request...
                specRequestsInFlight.push(request.url);
            }

            if (oldRequestInterceptor) {
                request = oldRequestInterceptor(request);
            }
            return request;
        };

        var oldResponseInterceptor = swaggerUiConfig.responseInterceptor;
        swaggerUiConfig.responseInterceptor = function (response) {
            if (refetchWithAuth && specRequestsInFlight.indexOf(response.url) !== -1) {
                // need setTimeout here because swagger-ui insists to updateUrl with the initial request url...
                if (response.ok) {
                    setTimeout(function () {
                        window.ui.specActions.updateUrl(response.url);
                    });
                }
                specRequestsInFlight = specRequestsInFlight.filter(function (val) {
                    return val !== response.url;
                });
            }

            if (oldResponseInterceptor) {
                response = oldResponseInterceptor(response);
            }
            return response;
        }
    }
}

/**
 * Call sui.preauthorize### according to the type of savedAuth.
 * @param savedAuth auth object saved from authActions.authorize
 * @param sui SwaggerUI or SwaggerUIBundle instance
 */
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

function _usp(url, fn) {
    url = url.split('?');
    var usp = new URLSearchParams(url[1]);
    fn(usp);
    url[1] = usp.toString();
    return url.join('?');
}

function addQueryParam(url, key, value) {
    return _usp(url, function (usp) {
        usp.set(key, value);
    })
}

function removeQueryParam(url, key) {
    return _usp(url, function (usp) {
        usp.delete(key);
    })
}

/**
 * Manually apply auth headers from the given auth object.
 * @param {object} authScheme auth object saved from authActions.authorize
 * @param {string} requestUrl the request url
 * @param {object} requestHeaders target headers
 * @return string new request url
 */
function applyAuth(authScheme, requestUrl, requestHeaders) {
    requestHeaders = requestHeaders || {};
    var schemeName = authScheme.get("name"), schemeType = authScheme.getIn(["schema", "type"]);
    if (schemeType === "basic" && schemeName) {
        var username = authScheme.getIn(["value", "username"]);
        var password = authScheme.getIn(["value", "password"]);
        if (username && password) {
            requestHeaders["Authorization"] = "Basic " + btoa(username + ":" + password);
        }
    } else if (schemeType === "apiKey" && schemeName) {
        var _in = authScheme.getIn(["schema", "in"]), paramName = authScheme.getIn(["schema", "name"]);
        var key = authScheme.get("value");
        if (key && paramName) {
            if (_in === "header") {
                requestHeaders[paramName] = key;
            }
            if (_in === "query") {
                if (requestUrl) {
                    requestUrl = addQueryParam(requestUrl, paramName, key);
                }
                else {
                    console.warn("WARNING: cannot apply apiKey query parameter via interceptor");
                }
            }
        }
    }

    return requestUrl;
}

/**
 * Remove the given authorization scheme from the url.
 * @param {object} authScheme
 * @param {string} requestUrl
 */
function deauthUrl(authScheme, requestUrl) {
    var schemeType = authScheme.getIn(["schema", "type"]);
    if (schemeType === "apiKey") {
        var _in = authScheme.getIn(["schema", "in"]), paramName = authScheme.getIn(["schema", "name"]);
        if (_in === "query" && requestUrl && paramName) {
            requestUrl = removeQueryParam(requestUrl, paramName);
        }
    }
    return requestUrl;
}

/**
 * Hook the authorize and logout actions of SwaggerUI.
 * The hooks are used to persist authorization data and trigger schema refetch.
 * @param sui SwaggerUI or SwaggerUIBundle instance
 * @param {boolean} persistAuth true to save auth to local storage
 * @param {boolean} refetchWithAuth true to trigger schema fetch on login
 * @param {boolean} refetchOnLogout true to trigger schema fetch on logout
 */
function hookAuthActions(sui, persistAuth, refetchWithAuth, refetchOnLogout) {
    if (!persistAuth && !refetchWithAuth) {
        // nothing to do
        return;
    }

    var originalAuthorize = sui.authActions.authorize;
    sui.authActions.authorize = function (authorization) {
        originalAuthorize(authorization);
        // authorization is map of scheme name to scheme object
        // need to use ImmutableJS because schema is already an ImmutableJS object
        var schemes = Immutable.fromJS(authorization);
        savedAuth = schemes.valueSeq().first();

        if (persistAuth) {
            localStorage.setItem("drf-yasg-auth", JSON.stringify(savedAuth.toJSON()));
        }

        if (refetchWithAuth) {
            var url = sui.specSelectors.url();
            url = applyAuth(savedAuth, url) || url;
            sui.specActions.download(url);
        }
    };

    var originalLogout = sui.authActions.logout;
    sui.authActions.logout = function (authorization) {
        if (savedAuth.get("name") === authorization[0]) {
            var oldAuth = savedAuth.set("value", null);
            savedAuth = Immutable.fromJS({});
            if (persistAuth) {
                localStorage.removeItem("drf-yasg-auth");
            }

            if (refetchWithAuth) {
                var url = sui.specSelectors.url();
                url = deauthUrl(oldAuth, url) || url;
                sui.specActions.download(url);
            }
        }
        originalLogout(authorization);
    };
}

window.addEventListener('load', initSwaggerUi);
