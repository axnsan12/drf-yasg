#!/bin/bash
set -ev
npm update

cp node_modules/redoc/bundles/redoc.standalone.js src/drf_yasg/static/drf-yasg/redoc/redoc.min.js
cp node_modules/redoc/bundles/redoc.standalone.js.map src/drf_yasg/static/drf-yasg/redoc/
cp node_modules/redoc/LICENSE src/drf_yasg/static/drf-yasg/redoc/LICENSE
curl -o src/drf_yasg/static/drf-yasg/redoc-old/redoc.min.js https://rebilly.github.io/ReDoc/releases/v1.x.x/redoc.min.js
curl -o src/drf_yasg/static/drf-yasg/redoc-old/redoc.min.js.map https://rebilly.github.io/ReDoc/releases/v1.x.x/redoc.min.js.map
curl -o src/drf_yasg/static/drf-yasg/redoc-old/LICENSE https://raw.githubusercontent.com/Redocly/redoc/v1.x/LICENSE

cp -r node_modules/swagger-ui-dist src/drf_yasg/static/drf-yasg/
pushd src/drf_yasg/static/drf-yasg/swagger-ui-dist/ >/dev/null
rm -f package.json .npmignore README.md favicon-16x16.png
rm -f  swagger-ui.js index.html
popd >/dev/null
