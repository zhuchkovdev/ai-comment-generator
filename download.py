import requests

def _download_file_from_google_drive(id, destination):
    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params = { 'id' : id }, stream = True)
    token = _get_confirm_token(response)

    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)

    _save_response_content(response, destination)    

def _get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value

    return None

def _save_response_content(response, destination):
    CHUNK_SIZE = 32768

    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)

def download_checkpoint(destination):
    file_id = "1UWiJrSYE9AVYY1b_94YDdzlu1vtORz8V"
    _download_file_from_google_drive(file_id, destination)

def download_vocab(destination):
    file_id = "19Qqr1e88UnMyMdPG4GdSI0lav4xpVcq6"
    _download_file_from_google_drive(file_id, destination)