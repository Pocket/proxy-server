#!/usr/bin/env bash

usage="$(basename "$0") [-a <app ecr uri>] [-n <nginx ecr uri>]

where:
    -a  uri of app ECR image
    -n  uri of nginx ECR image"

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

while getopts ':hp:a:n:' option; do
  case "$option" in
    h) echo "$usage"
       exit
       ;;
    a) APP_URI=$OPTARG
       ;;
    n) NGINX_URI=$OPTARG
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

if [[ -z ${APP_URI} ]] && [[ -z ${NGINX_URI} ]]
then
    Error "app or nginx uri needs to be provided"
    echo "$usage"
    exit 1
fi

# Login to ECR
Print "Logging in..."
$(aws ecr get-login --no-include-email --region us-east-1)

Deploy()
{
    DOCKER_FILE=$1
    CONTEXT=$2
    IMAGE=$3
    URI=$4

    if [[ ! -z ${URI} ]]
    then
        Print "Building ${DOCKER_FILE}..."
        TAG=`date +"%Y%m%d%H%M%S"` # tags uniquely with date, hour, minute and second
        docker build -f ${DOCKER_FILE} -t ${IMAGE}:${TAG} -t "${IMAGE}:latest" ${CONTEXT} &&
        docker tag ${IMAGE}:${TAG} ${URI}:${TAG} &&
        docker tag ${IMAGE}:${TAG} "${URI}:latest" &&   # move the 'latest' designation to the last timestamp
        Print "Pushing ${URI}:${TAG}..."
        docker push ${URI}:${TAG}
        docker push "${URI}:latest"
    fi
}

Deploy "images/nginx/Dockerfile" "images/nginx/" "proxy-server-nginx" ${NGINX_URI}
Deploy "images/app/Dockerfile" "." "proxy-server-app" ${APP_URI}

Print "Done."
