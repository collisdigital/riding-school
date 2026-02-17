# Backlog

## Pending Features

- **Invite Flow**: Implement an email invitation system for users created without a password (e.g., parents or riders added by admins). This should include generating a temporary token, sending an email with a link to set a password, and transitioning the user to a fully active state.

- **Soft Delete Cleanup**: Implement a scheduled task (e.g., cron job or Celery beat) to permanently delete records that have been soft-deleted for more than X days (e.g., 30 days) to maintain database hygiene and compliance with data retention policies.

- **Parent-Child Relationships**: Re-implement the ability for Parents to link to Rider accounts (children). The previous implementation was removed during the multi-tenant refactor. Needs a new `UserRelationship` or `Family` model that is tenant-aware.

## Pending Chores

- **Chrome Autocomplete Suggestion**: `[DOM] Input elements should have autocomplete attributes (suggested: "current-password"): (More info: https://goo.gl/9p2vKq) <input id=​"password" required class=​"block w-full border border-gray-300 rounded-md shadow-sm p-2 pr-10 focus:​ring-blue-500 focus:​border-blue-500" type=​"password" value>​`

