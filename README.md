# Dev Assessment - Webhook Receiver

Please use this repository for constructing the Flask webhook receiver.

*******************
## Architecture
- Uses Flask for the webhook logger
- Uses HTMX and Jinja2 templating for reactive UI and 15-sec polling
- Project-wide logger utility for debugging

## Setup
- Download the Cloudflared binary for Windows(x64 version) from: ```https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/downloads/```
- Place it in /tools/ (create folder if not present)
- Batch file ```run_tunnel.bat``` is provided to expose local Flask API to a random public URL using the binary
- The URI in the actions-originator repo's ```action-trigger.yml``` will need to be replaced by the new one each time a tunnel is created anew

## Testing
- Testing is done by creating a native webhook in the github-actions-originator repo (```https://github.com/NSGCommando/github-actions-originator```), which runs on all push and pull_requests and POSTS to an exposed webhook API
- Webhook API is exposed through tunnelling ```localhost:5000``` to public network via Cloudflared binary (Windows x64)
- Cloudflared terminal will output the random URL, example ```https://dealtime-clothing-intl-ciao.trycloudflare.com/```
- Append ```/webhook/receiver``` to the URL
- Copy the resulting URL in the "Payload URL" property in the webhook's settings in github-actions-originator repo
- Database was run on port localhost:27017 in Docker via MongoDB 8.2.5 Image
- Mongo Image Hash: ```sha256:474f5c3bf0e355bb97dafda730e725169a4d51c5578abf7be9ec7ad3fdee4481```
- ```project_logger.py``` provides a logger utliity that outputs to /logs/eventLogs.log

## Logic
- Backend Flask app checks for PUSH, PULL_REQUEST and MERGE via chacking if:
 - response data has "event" as "push"
 - response data has "event" as "pull_request"
  - if response data has "merged" value and "action" is "closed"
- "merged" property is only populated on successful merging of a pull request

## Demo
![native-webhook-listener-demo](https://github.com/user-attachments/assets/08f70c54-8a43-4d81-82cd-ccb97be759a3)
*******************
