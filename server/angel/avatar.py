from PIL import Image
from common import ExceptionWithResponse
from django.core.files import File
from io import BytesIO


class AvatarException(ExceptionWithResponse):
    def __init__(self, message):
        super().__init__(message)


def unify(uploaded_file):
    if uploaded_file.size > 1 * 1024 * 1024:  # 1MB
        raise AvatarException('uploaded file is too large')
    try:
        image = Image.open(uploaded_file)
    except IOError:
        raise AvatarException('cannot open uploaded file as image')
    if image.width < 128 or image.height < 128:
        raise AvatarException('uploaded image is too small')
    if image.format == 'JPEG':
        return uploaded_file
    else:
        output_file = BytesIO()
        image.save(output_file, format='jpeg')
        unified_image = File(
            BytesIO(output_file.getbuffer()), uploaded_file.name)
        return unified_image
