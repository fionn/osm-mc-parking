#!/bin/bash

set -euo pipefail

base_url="https://www.hkemobility.gov.hk"

function main {
    url="$base_url/api/drss/layer/map/"

    lat=("22.1868" "22.5461")
    long=("113.8264" "114.4844")

    filter="(VEHICLE_TYPE = 'Motor Cycles') AND BBOX(SHAPE, ${long[0]},${lat[0]},${long[1]},${lat[1]})"

    curl "$url" -H 'Accept: application/json' -H "Referer: $base_url" \
        -d "typeName=DRSS:VW_ON_STREET_PARKING" \
        -d "service=WFS" \
        -d "version=1.0.0" \
        -d "request=GetFeature" \
        -d "outputFormat=application/json" \
        -d "styles=OSP_Type_ALL" \
        -d "cql_filter=$filter"
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@" | jq .
fi
