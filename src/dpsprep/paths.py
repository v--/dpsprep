from pathlib import Path
import hashlib
import os
import tempfile

from loguru import logger


HASHING_BUFFER_SIZE = 64 * 1024


# Based on
# https://stackoverflow.com/posts/22058673/revisions
def get_file_hash(path: os.PathLike | str):
    h = hashlib.sha1()

    with open(path, 'rb') as file:
        data = file.read(HASHING_BUFFER_SIZE)

        while len(data) > 0:
            h.update(data)
            data = file.read(HASHING_BUFFER_SIZE)

    return h.hexdigest()


class PdfPaths:
    src: Path
    dest: Path
    working: Path

    def __init__(self, src: os.PathLike | str, dest: os.PathLike | str | None):
        self.src = Path(src)

        if dest is None:
            self.dest = Path(Path(src).with_suffix('.pdf').name)
        else:
            self.dest = Path(dest)

        # Working path
        # If possible, we avoid the ephemeral storage /tmp
        persistent_tmp = Path('/var/tmp')

        if persistent_tmp.exists() and (persistent_tmp.stat().st_mode & (os.W_OK | os.X_OK)):
            logger.debug('Using non-ephemeral storage "/var/tmp"')
            root = persistent_tmp
        else:
            logger.debug(f'Using default system storage {repr(tempfile.gettempdir())}')
            root = Path(tempfile.gettempdir())

        self.working = root / 'dpsprep' / get_file_hash(self.src)

        if not self.working.exists():
            logger.debug(f'Creating {repr(str(self.working))}')
            self.working.mkdir(parents=True)

    def get_page_pdf_path(self, i: int):
        return self.working / f'{i + 1}.pdf'
