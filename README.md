# e-post

A tool for extracting new postal data from Deutsche Post E-Post Solutions WebTransfer.

It also allows to send all new files to a Slack channel automatically.

## How to use

This tool is available as a Docker image and therefore includes all dependencies like python packages, as well as `Chrome` and `chromedriver` for browser emulation.

Create a directory which will contain the configuration or data of `e-post`.
For example create the directory `~/e-post`.

Create a `docker-compose.yml` file containing the configuration.
You need to configure the environment variables.

```docker-compose.yml
services:
  e-post:
    image: ghcr.io/timephy/e-post:main
    container_name: e-post
    volumes:
      - "./files/:/app/files"
    environment:
      - USERNAME=
      - PASSWORD=
      - SLACK_BOT_TOKEN=
      - SLACK_CHANNEL=
```

You can set up `cron` to run this tool periodically by running `crontab -e` and including the following job:

```crontab
0 6,9,12,15,18,21 * * * /usr/local/bin/docker-compose -f ~/e-post/docker-compose.yml up --force-recreate >> ~/e-post/output.log 2>&1
```

### Slack App

Create a slack app and give it `files:read` and `files:write` permissions.
Add the app to your slack workspace and add the bot/app to the channel in question.
Lastly include the oauth `token` and `channel_id` in the environment variables.

### Update

To update to the latest version simply pull the newest docker image by running:

```bash
docker pull ghcr.io/timephy/e-post:main
```

When `cron` schedules the next job, the new version will be executed.
