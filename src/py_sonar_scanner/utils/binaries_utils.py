import zipfile

def write_binaries(scanner_res: bytes, destination: str):
    with open(destination, "wb") as output:
        output.write(scanner_res.read())

def unzip_binaries(scanner_zip_path: str, destination: str):
    with zipfile.ZipFile(scanner_zip_path, "r") as zip_ref:
        zip_ref.extractall(destination)
