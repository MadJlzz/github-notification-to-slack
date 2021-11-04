# github-notification-to-slack

This repository was created to play with Slack and GitHub API and see how they can work together in terms of
`webhooks`, `slash commands`, `...`

# Build & deployment

Build with `Cloud Build`:
```shell
gcloud builds submit --tag eu.gcr.io/madproject-271618/github-notification-to-slack
```

Deploy in Cloud Run:
```shell
gcloud run deploy github-notification-to-slack --image eu.gcr.io/madproject-271618/github-notification-to-slack --service-account github-notification-to-slack@madproject-271618.iam.gserviceaccount.com --allow-unauthenticated --set-env-vars "WEBHOOK_URL=" --set-secrets="GITHUB_SIGNING_SECRET=github-webhook-signature-secret:1,SLACK_SIGNING_SECRET=github-notification-to-slack-signing-secret:1"
```

:information_source: Do not forget to set correctly the value of the different environment variables like `WEBHOOK_URL`
and also create secrets in GCP `Secret Manager`