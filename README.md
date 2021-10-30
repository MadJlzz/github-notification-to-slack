gcloud builds submit --tag eu.gcr.io/madproject-271618/github-notification-to-slack

gcloud run deploy github-notification-to-slack --image eu.gcr.io/madproject-271618/github-notification-to-slack --allow-unauthenticated --set-env-vars "SECRET=,WEBHOOK_URL="