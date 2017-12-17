#!/bin/bash
set -e

npm update
cp node_modules/redoc/dist/redoc.min.js src/drf_yasg/static/drf-yasg/redoc/redoc.min.js
cp -r node_modules/swagger-ui-dist src/drf_yasg/static/drf-yasg/
rm -f src/drf_yasg/static/drf-yasg/swagger-ui-dist/package.json src/drf_yasg/static/drf-yasg/swagger-ui-dist/.npmignore
