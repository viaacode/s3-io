VERSION = ${shell (git describe --tags || echo latest)}
REPO = https://github.com/viaacode/s3-io.git
.ONESHELL:
SHELL = /bin/bash

.PHONY: all

NAMESPACE = s3-components
OC_PROJECT = ${NAMESPACE}

APP_NAME = s3-io
IMAGE_NAME = ${NAMESPACE}/${APP_NAME}
REGISTRY = docker-registry-default.apps.do-prd-okp-m0.do.viaa.be
login:
	login_oc.sh https://do-prd-okp-m0.do.viaa.be:8443
	oc project "${OC_PROJECT}"
build-local: login
	rm /tmp/s3io -rf 2>/dev/null ;cd /tmp && git clone ${REPO} && cd s3io && cat README.md &&
	docker build --target test-image -t "${REGISTRY}/${IMAGE_NAME}:tst" .

dummy-env:
	export `egrep -v '^#' dummy.envs | xargs` && echo "$${REMOTECURL_HOST}"

build:
	echo $${UID}
	cp ./config.yml.docker ./config.yml
	docker build --build-arg GUID=`echo $${UID}` --target run-image  -t "${REGISTRY}/${IMAGE_NAME}:${VERSION}" .
test: dummy-env
	docker build --target test-image -t "${REGISTRY}/${IMAGE_NAME}:tst" . &&
	docker rm ${APP_NAME}_test 2>/dev/null ; docker container run --env-file dummy.envs --name "${APP_NAME}_test" \
					--entrypoint python "${REGISTRY}/${IMAGE_NAME}:tst" \
					"-m" "pytest" "--cov=./tests" "--junit-xml=./tests/test_results.xml" &&
	docker commit "${APP_NAME}_test" s3iotests:${VERSION} &&
	docker run -t --entrypoint=sh s3iotests:${VERSION} -c "cat tests/test_results.xml" > tests/test_results.xml
lint:
	docker build --target test-image -t "${REGISTRY}/${IMAGE_NAME}:tst" . &&
#	docker rm ${APP_NAME}_lint 2>/dev/null &&
#	docker container run --name "${APP_NAME}_lint" \
#					--entrypoint flake8 "${REGISTRY}/${IMAGE_NAME}:${VERSION}" \
#					--exit-zero \
#					--max-line-length=88 > ${APP_NAME}_lint.txt &&
	docker run -t --entrypoint=sh "${REGISTRY}/${IMAGE_NAME}:${VERSION}" -c "flake8 > s3io_lint.txt; flake8_junit s3io_lint.txt 1>/dev/null s3io_lint.xml; cat s3io_lint.xml " > tests/s3io_lint.xml

push: 	login
	docker push ${REGISTRY}/${IMAGE_NAME}:${VERSION}

tag-int:
	oc tag ${IMAGE_NAME}:${VERSION} ${IMAGE_NAME}:int
deploy-int:
test-int:

tag-qas:
	echo "... disabled ..."
	#oc tag ${IMAGE_NAME}:${VERSION} ${IMAGE_NAME}:qas
deploy-qas:
	bash ./openshift/rollout.sh s3-io qas ${VERSION} s3-io-worker-qas s3-io-front-qas
test-qas:

tag-prd:
	oc tag ${IMAGE_NAME}:${VERSION} ${IMAGE_NAME}:prd
deploy-prd:

approved:
	echo "Approved"

post-clean:
	docker container rm "${APP_NAME}_test"
