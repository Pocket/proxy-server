import os

dsn = os.environ.get('SENTRY_DSN', '')
sample_rate_traces = os.environ.get('SENTRY_TRACES_SAMPLE_RATE', 0.0)
sample_rate_profiles = os.environ.get('SENTRY_PROFILE_SAMPLE_RATE', 0.0)

production = staging = development = test = {
    'dsn': dsn,
    'traces_sample_rate': sample_rate_traces,
    'profiles_sample_rate': sample_rate_profiles,
}
