import pickle
from pathlib import Path

from libxslt import cleanup


def save_to_pickle_file(file_path: str, data) -> None:
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as file:
        pickle.dump(data, file, protocol=4)

def load_pickle_file(file_path: Path):
    with open(file_path, "rb") as file:
        contents = file.read()
        try:
            return pickle.loads(contents)
        except pickle.UnpicklingError as e:
            cleanup()
            exit(1)
