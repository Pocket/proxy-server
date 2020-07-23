#!/usr/bin/env bash

usage="$(basename "$0") -s <ecr server> [-a <app repository name>] [-n <nginx repository name>]

where:
    -s  ECR server uri, e.g. \"1234.dkr.ecr.us-east-1.amazonaws.com\"
    -a  ECR app repository name (or omit to not push it)
    -n  ECR nginx repository name (or omit to not push it)"

PROFILE=""
NGINX_URI=""
APP_URI=""

Print () {
    GREEN=`tput setaf 2`
    NC=`tput sgr0` # No Color
    printf "${GREEN}${1}${NC}\n"
}

Error () {
    RED=`tput setaf 1`
    NC=`tput sgr0` # No Color
    printf "${RED}${1}${NC}\n"
}

while getopts ':hp:s:a:n:' option; do
  case "$option" in
    h) echo "$usage"
       exit
       ;;
    s) SERVER=$OPTARG
       ;;
    a) APP_REPO=$OPTARG
       ;;
    n) NGINX_REPO=$OPTARG
       ;;
    :) Error "missing argument for -${OPTARG}\n"
       echo "$usage"
       exit 1
       ;;
   \?) Error "illegal option: -${OPTARG}\n"
       echo "$usage"
       exit 1
       ;;
  esac
done
shift $((OPTIND - 1))

if [[ -z ${SERVER} ]]
then
    Error "server needs to be provided"
    echo "$usage"
    exit 1
fi

if [[ -z ${APP_REPO} ]] && [[ -z ${NGINX_REPO} ]]
then
    Error "app or nginx repo needs to be provided"
    echo "$usage"
    exit 1
fi

# Login to ECR
Print "Logging in..."
LOGIN=$(aws ecr get-login --no-include-email --region us-east-1)
if [ $? -ne 0 ]
then
    Error "Failed to login to ECR"
    exit 1
fi

Deploy()
{
    DOCKER_FILE=$1
    CONTEXT=$2
    IMAGE=$3
    SERVER=$4
    REPO=$5
    URI="${SERVER}/${REPO}"

    if [[ ! -z ${REPO} ]]
    then
        Print "Building ${DOCKER_FILE}..."
        TAG=`date +"%Y%m%d%H%M%S"` # tags uniquely with date, hour, minute and second
        docker build -f ${DOCKER_FILE} -t ${IMAGE}:${TAG} -t "${IMAGE}:latest" ${CONTEXT} &&
        docker tag ${IMAGE}:${TAG} ${URI}:${TAG} &&
        docker tag ${IMAGE}:${TAG} "${URI}:latest" &&   # move the 'latest' designation to the last timestamp
        Print "Pushing ${URI}:${TAG}..." &&
        docker push ${URI}:${TAG} &&
        docker push "${URI}:latest"
    fi
}

Deploy "images/nginx/Dockerfile" "images/nginx/" "proxy-server-nginx" ${SERVER} ${NGINX_REPO} &&
Deploy "images/app/Dockerfile" "." "proxy-server-app" ${SERVER} ${APP_REPO} &&

Print "Done."
