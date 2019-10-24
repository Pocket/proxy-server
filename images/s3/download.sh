#! /bin/bash
set -e

SOURCE_BUCKET="pocket-geoip-dev"
FAKE_ENDPOINT="http://localhost:4569"
FAKE_BUCKET="pocket-geoip"
AWS_PROFILE="default"

Print () {
    GREEN=`tput setaf 2`
    NC=`tput sgr0` # No Color
    printf "${GREEN}${1}${NC}\n"
}

Warn () {
    YELLOW=`tput setaf 3`
    NC=`tput sgr0` # No Color
    printf "${YELLOW}${1}${NC}\n"
}

# Code in the finish function always runs.
function finish {
    if [ -d "$TMPDIR" ]; then
        Print "Removing $TMPDIR"
        rm -rf $TMPDIR
    fi
}
trap finish EXIT

# Parse arguments
while getopts ":p:b:" opt; do
  case $opt in
    b) SOURCE_BUCKET=$OPTARG
    ;;
    p) AWS_PROFILE=$OPTARG
    ;;
    \?) Warn "Invalid option -$OPTARG"
    ;;
  esac
done

TMPDIR=$(mktemp -d)
Print "Downloading $SOURCE_BUCKET to $TMPDIR"
aws --profile $AWS_PROFILE s3 cp s3://$SOURCE_BUCKET $TMPDIR --recursive

Print "Creating fake_s3 aws profile"
aws configure set aws_access_key_id 'foobar' --profile 'fake_s3'
aws configure set aws_secret_access_key 'foobar' --profile 'fake_s3'

Print "Copying $TMPDIR to fake s3"
aws --profile 'fake_s3' --endpoint-url $FAKE_ENDPOINT s3 cp $TMPDIR s3://$FAKE_BUCKET --recursive
