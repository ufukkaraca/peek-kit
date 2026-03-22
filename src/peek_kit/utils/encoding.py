import base64
from io import BytesIO

def encode_image_base64(fp: BytesIO) -> str:
    return base64.b64encode(fp.getvalue()).decode('utf-8')
