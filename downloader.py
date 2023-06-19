import argparse
import io
import logging
import pathlib
from typing import Optional

import googleapiclient.discovery
import googleapiclient.errors
import googleapiclient.http
import httplib2
import oauth2client.file

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Downloader:
    def __init__(self, token_path: str, secret_path: Optional[str] = None) -> None:
        store = oauth2client.file.Storage(token_path)
        creds = store.get()

        if not creds or creds.invalid:
            if not secret_path:
                raise ValueError(
                    "secret_path must be set if the existing token is invalid."
                )
            scopes = ["https://www.googleapis.com/auth/drive"]
            flow = oauth2client.client.flow_from_clientsecrets(secret_path, scopes)
            creds = oauth2client.tools.run_flow(flow, store)

        self._drive_service = googleapiclient.discovery.build(
            "drive", "v3", http=creds.authorize(httplib2.Http())
        )

    def download_file(self, file_id: str) -> bytes:
        response = self._drive_service.files().get_media(
            fileId=file_id,
            acknowledgeAbuse=True,
            supportsAllDrives=True,
        )

        data = io.BytesIO()
        downloader = googleapiclient.http.MediaIoBaseDownload(data, response)

        while True:
            _, done = downloader.next_chunk()
            if done:
                break

        return data.getvalue()

    def list_files(self, drive_id: str, parent_id: str) -> dict[str, str]:
        files = []
        page_token = None

        while True:
            response = (
                self._drive_service.files()
                .list(
                    corpora="drive",
                    driveId=drive_id,
                    q=f"'{parent_id}' in parents",
                    fields="nextPageToken, files(id, name, mimeType)",
                    includeItemsFromAllDrives=True,
                    supportsAllDrives=True,
                    pageToken=page_token,
                )
                .execute()
            )

            for file in response.get("files", []):
                # print(file)
                files.append(file)

            page_token = response.get("nextPageToken")
            if not page_token:
                break

        return sorted(files, key=lambda x: x["name"])


def recurse(dl: Downloader, parent_path: pathlib.Path, drive_id: str, parent_id: str):
    logging.info(f"Folder: {parent_path}")

    for child_info in dl.list_files(drive_id, parent_id):
        child_path = parent_path / child_info["name"]

        if child_info["mimeType"] == "application/pdf":
            logging.info(f"PDF: {child_path}")
            data = dl.download_file(child_info["id"])
            parent_path.mkdir(parents=True, exist_ok=True)
            child_path.write_bytes(data)

        elif child_info["mimeType"] == "application/vnd.google-apps.folder":
            recurse(dl, child_path, drive_id, child_info["id"])


if __name__ == "__main__":
    p = argparse.ArgumentParser("Copy Google Drive files to local.")
    p.add_argument("--src-drive", required=True, help="Source drive ID")
    p.add_argument("--src-id", required=True, help="Source folder ID")
    p.add_argument(
        "--dest", type=pathlib.Path, required=True, help="Local destination folder"
    )
    p.add_argument(
        "--token",
        type=pathlib.Path,
        required=True,
        help="Path to the OAuth2 refresh JSON file.",
    )
    p.add_argument(
        "--secret",
        type=pathlib.Path,
        help="Path to the OAuth2 client secret JSON file.",
    )
    args = p.parse_args()

    recurse(Downloader(args.token), args.dest, args.src_drive, args.src_id)
