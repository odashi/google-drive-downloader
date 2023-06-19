# google-drive-downloader
Downloads files from Google Drive to local.

## Prerequisites

This script requires Google Cloud OAuth2 client with the following access scopes:

* `https://www.googleapis.com/auth/drive`

```shell
pip install \
  google-api-python-client \
  google-auth-httplib2 \
  google-auth-oauthlib \
  oauth2client
```

## Usage

```shell
python downloader.py \
  --src-drive {DRIVE_ID} \
  --src-id {FOLDER_ID} \
  --dest {LOCAL_FOLDER} \
  --token {OAUTH2_REFRESH_TOKEN_JSON} \
  [--secret {OAUTH2_CLIENT_SECRET_JSON}]
```