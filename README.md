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