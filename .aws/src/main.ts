import {Construct} from 'constructs';
import {App, DataTerraformRemoteState, RemoteBackend, TerraformStack} from 'cdktf';
import {
  AwsProvider,
  DataAwsCallerIdentity,
  DataAwsKmsAlias,
  DataAwsRegion,
  DataAwsSnsTopic
} from '../.gen/providers/aws';
import {config} from './config';
import {PocketALBApplication} from "@pocket/terraform-modules";
import {PocketPagerDuty} from "@pocket/terraform-modules/dist/src/pocket/PocketPagerDuty";
import {PagerdutyProvider} from "../.gen/providers/pagerduty";

class ProxyServer extends TerraformStack {
  constructor(scope: Construct, name: string) {
    super(scope, name);

    new AwsProvider(this, 'aws', {
      region: 'us-east-1',
    });

    new PagerdutyProvider(this, 'pagerduty_provider', {
      token: undefined
    });

    new RemoteBackend(this, {
      hostname: 'app.terraform.io',
      organization: 'Pocket',
      workspaces: [
        {
          prefix: `${config.name}-`,
        },
      ],
    });

    const incidentManagement = new DataTerraformRemoteState(this, 'incident_management', {
      organization: 'Pocket',
      workspaces: {
        name: 'incident-management'
      }
    });

    const pagerDuty = new PocketPagerDuty(this, 'pagerduty', {
      prefix: config.prefix,
      service: {
        criticalEscalationPolicyId: incidentManagement.get('policy_backend_critical_id'),
        nonCriticalEscalationPolicyId: incidentManagement.get('policy_backend_non_critical_id')
      },
    })

    const region = new DataAwsRegion(this, 'region');
    const caller = new DataAwsCallerIdentity(this, 'caller');
    const secretsManager = new DataAwsKmsAlias(this, 'kms_alias', {
      name: 'alias/aws/secretsmanager'
    });

    const snsTopic = new DataAwsSnsTopic(this, 'backend_notifications', {
      name: `Backend-${config.environment}-ChatBot`
    })

    new PocketALBApplication(this, 'application', {
      internal: false,
      prefix: config.prefix,
      alb6CharacterPrefix: config.shortName,
      tags: config.tags,
      cdn: false,
      domain: config.domain,
      taskSize: {
        cpu: 2048,
        memory: 4096,
      },
      containerConfigs: [
        {
          name: 'app',
          hostPort: 8000,
          containerPort: 8000,
          healthCheck: {
            command: ["CMD-SHELL", "curl -f http://localhost:8000/pulse || exit 1" ],
            interval: 30,
            retries: 3,
            timeout: 5,
            startPeriod: 0,
          },
          envVars: [
            {
              name: 'APP_ENV',
              value: config.environment,
            },
            {
              name: 'GEOIP_S3_BUCKET',
              value: config.geoIpS3Bucket
            },
          ],
          secretEnvVars: [
            {
              name: 'SENTRY_DSN',
              valueFrom: `arn:aws:ssm:${region.name}:${caller.accountId}:parameter/${config.name}/${config.environment}/SENTRY_DSN`
            },
            {
              name: 'ADZERK_API_KEY',
              valueFrom: `arn:aws:ssm:${region.name}:${caller.accountId}:parameter/${config.name}/${config.environment}/ADZERK_API_KEY`
            },
          ]
        },
        {
          name: 'xray-daemon',
          containerImage: 'amazon/aws-xray-daemon',
          hostPort: 2000,
          containerPort: 2000,
          protocol: 'udp',
          command: ['--region', 'us-east-1', '--local-mode'],
        }
      ],
      codeDeploy: {
        useCodeDeploy: true,
        snsNotificationTopicArn: snsTopic.arn,
      },
      exposedContainer: {
        name: 'app',
        port: 8000,
        healthCheckPath: '/pulse'
      },
      ecsIamConfig: {
        prefix: config.prefix,
        taskExecutionRolePolicyStatements: [
          //This policy could probably go in the shared module in the future.
          {
            actions: [
              "ssm:GetParameter*"
            ],
            resources: [
              `arn:aws:ssm:${region.name}:${caller.accountId}:parameter/${config.name}/${config.environment}`,
              `arn:aws:ssm:${region.name}:${caller.accountId}:parameter/${config.name}/${config.environment}/*`,
            ],
            effect: 'Allow'
          }
        ],
        taskRolePolicyStatements: [
          {
            actions: [
              'xray:PutTraceSegments',
              'xray:PutTelemetryRecords',
              'xray:GetSamplingRules',
              'xray:GetSamplingTargets',
              'xray:GetSamplingStatisticSummaries'
            ],
            resources: ['*'],
            effect: 'Allow'
          }
        ],
        taskExecutionDefaultAttachmentArn: 'arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy',
      },
      autoscalingConfig: {
        targetMinCapacity: 50,
        targetMaxCapacity: 250
      },
      alarms: {
        http5xxError: {
          threshold: 3,
          evaluationPeriods: 2,
          period: 300,
          actions: config.environment == 'Dev' ? [] : [pagerDuty.snsCriticalAlarmTopic.arn]
        },
        httpLatency: {
          threshold: 0.5,
          evaluationPeriods: 2,
          period: 300,
          actions: config.environment == 'Dev' ? [] : [pagerDuty.snsCriticalAlarmTopic.arn]
        },
        httpRequestCount: {
          threshold: 5000,
          evaluationPeriods: 2,
          period: 300,
          // We raise a non-critical alarm on request count, because a higher-than-expected
          // request volume does not have to result an outage. The above two critical alarms cover that.
          actions: config.environment == 'Dev' ? [] : [pagerDuty.snsNonCriticalAlarmTopic.arn]
        }
      }
    });
  }
}

const app = new App();
new ProxyServer(app, 'proxy-server');
app.synth();
