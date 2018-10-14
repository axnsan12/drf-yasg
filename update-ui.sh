#!/bin/bash
set -ev
npm update

cp node_modules/redoc/bundles/redoc.standalone.js src/drf_yasg/static/drf-yasg/redoc/redoc.min.js
wget https://rebilly.github.io/ReDoc/releases/v1.x.x/redoc.min.js -O src/drf_yasg/static/drf-yasg/redoc-old/redoc.min.js

cp -r node_modules/swagger-ui-dist src/drf_yasg/static/drf-yasg/
pushd src/drf_yasg/static/drf-yasg/swagger-ui-dist/ >/dev/null
rm -f package.json .npmignore README.md favicon-16x16.png
rm -f  swagger-ui.js index.html *.map
popd >/dev/null
