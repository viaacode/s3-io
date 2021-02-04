#!/bin/bash
## $1 imagename s3-io 
## $2 ENV eg qas
## $3 tag eg v1.1
## $4 dc back
## $5 dc front
login_oc.sh https://do-prd-okp-m0.do.viaa.be:8443/ 1>/dev/null
oc project s3-components
echo ..... Rolling out "${2}" to version "${3}" ..... 
trap "exit" INT TERM ERR
trap "kill 0" EXIT
  oc rollout cancel dc/"${4}" & 
  oc tag "${1}":"${3}" "${1}":"${2}" || exit 1
  sleep 3 && oc rollout latest dc/"${4}" && sleep 3 &&
  oc rollout status dc/"${4}" || exit 1
  oc rollout cancel dc/"${5}" &
  sleep 3 && oc rollout latest dc/"${5}" && sleep 3 &&
  oc rollout status dc/"${5}" || exit 1


wait
