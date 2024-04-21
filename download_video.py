import gdown
from pytube import YouTube


def downloader_from_YouTube(link: str, output_path: str) -> None:
    youtubeObject = YouTube(link)
    youtubeObject = youtubeObject.streams.get_highest_resolution()
    try:
        youtubeObject.download(output_path=output_path)
    except:
        print("An error has occurred")
    print("Download is completed successfully")


def downloader_from_google_drive(url_video: str, output: str) -> None:

    file_id = url_video.split('/')[-2]
    prefix = 'https://drive.google.com/uc?/export=download&id='

    gdown.download(prefix+file_id, output=output)