import sys
from googleapiclient.errors import HttpError
from app.drive.uploader import get_drive_service, get_file_metadata

def check_file_exists(file_id: str):
    service = get_drive_service()
    try:
        metadata = get_file_metadata(file_id, service)
        print("✅ EXISTE:", file_id)
        print("📋 Metadata:", metadata)
    except HttpError as e:
        if e.resp.status == 404:
            print("❌ NO EXISTE:", file_id)
        else:
            print("💥 ERROR en la API:", e)
    except Exception as e:
        print("💣 EXCEPCIÓN:", str(e))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❗ Uso: python check_drive_file.py <file_id>")
        sys.exit(1)

    file_id = sys.argv[1]
    check_file_exists(file_id)
