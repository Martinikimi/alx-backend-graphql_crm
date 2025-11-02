INSTALLED_APPS = [
    # ... other apps ...
    'django_crontab',
]
INSTALLED_APPS = [
    # ... other apps ...
    'django_crontab',
]
# django-crontab configuration
CRONJOBS = [
    ('*/5 * * * *', 'crm.cron.log_crm_heartbeat'),
    ('0 */12 * * *', 'crm.cron.update_low_stock'),
]
