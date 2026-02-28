# Dev Assessment - Webhook Receiver

Please use this repository for constructing the Flask webhook receiver.

*******************
## Architecture
- Uses Flask for the weblogger
- Uses HTMX and Jinja2 templating for reactive UI and 15-sec polling
- Project-wide logger utility for debugging

## Setup
- Download the Cloudflared binary for Windows(x64 version) from: ```https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/downloads/```
- Place it in /tools/ (create folder if not present)
- Batch file ```run_tunnel.bat``` is provided to expose local Flask API to a random public URL using the binary
- The URI in the actions-originator repo's ```action-trigger.yml``` will need to be replaced by the new one each time a tunnel is created anew

## Testing
- Testing was done by creating a basic .yml workflow file in the github-actions-originator repo (```https://github.com/NSGCommando/github-actions-originator```), which runs on all push and pull_requests and POSTS to an exposed webhook API
- Webhook API is exposed through tunnelling ```localhost:5000``` to public network via Cloudflared binary (Windows x64)
- Cloudflared terminal will output the random URL, example ```https://dealtime-clothing-intl-ciao.trycloudflare.com/```

- Append ```/webhook/dashboard``` to the URL
- Add the resulting URL to the  ```-Uri=""``` property in the ```action-trigger.yml``` file in the github-actions-originator repo
- Replace any old URL present there if needed
- Database was run on port localhost:27017 in Docker via MongoDB 8.2.5 Image
- Mongo Image Hash: ```sha256:474f5c3bf0e355bb97dafda730e725169a4d51c5578abf7be9ec7ad3fdee4481```
- ```project_logger.py``` provides a logger utliity that outputs to /logs/eventLogs.log


## Demo
![repo-webhook-listener-demo](https://github.com/user-attachments/assets/6f79fc0c-1c42-42e6-8ee7-16c23f553f0b)
*******************
