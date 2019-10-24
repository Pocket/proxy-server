Real documentation pending. We're using nested stacks and therefore must sync the local templates to s3 before updating the main VPC stack.

Quick commands to update VPC:

`aws-vault exec pocket-proxy-rw -- aws s3 sync . s3://pocket-proxy-cloudformation/`
`aws-vault exec pocket-proxy-rw -- aws cloudformation update-stack --stack-name VPC --template-body file://vpc.yaml --parameters file://vpc_parameters.json`


