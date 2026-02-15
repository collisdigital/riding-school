# Backlog

## Pending Features

- **Invite Flow**: Implement an email invitation system for users created without a password (e.g., parents or riders added by admins). This should include generating a temporary token, sending an email with a link to set a password, and transitioning the user to a fully active state.
- **Soft Delete Cleanup**: Implement a scheduled task (e.g., cron job or Celery beat) to permanently delete records that have been soft-deleted for more than X days (e.g., 30 days) to maintain database hygiene and compliance with data retention policies.
- **Parent-Child Relationships**: Re-implement the ability for Parents to link to Rider accounts (children). The previous implementation was removed during the multi-tenant refactor. Needs a new `UserRelationship` or `Family` model that is tenant-aware.
