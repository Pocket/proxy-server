const name = 'ProxyServer';
let environment;
let domain;
let geoIpS3Bucket;
let ecsServiceTaskMinCount;
let ecsServiceTaskMaxCount;

if (process.env.NODE_ENV === 'development') {
  environment = 'Dev';
  domain = 'spocs-v2.getpocket.dev';
  geoIpS3Bucket = 'pocket-geoip-dev';
  ecsServiceTaskMinCount = 8;
  ecsServiceTaskMaxCount = 250;
} else {
  environment = 'Prod';
  domain = 'spocs-v2.getpocket.com';
  geoIpS3Bucket = 'pocket-geoip';
  ecsServiceTaskMinCount = 50;
  ecsServiceTaskMaxCount = 250;
}

export const config = {
  name,
  prefix: `${name}-${environment}`,
  circleCIPrefix: `/${name}/CircleCI/${environment}`,
  shortName: 'PROXY',
  environment,
  domain,
  geoIpS3Bucket,
  ecsServiceTaskMinCount,
  ecsServiceTaskMaxCount,
  tags: {
    service: name,
    environment
  }
};
