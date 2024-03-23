from dataclasses import dataclass
import pathlib
from typing import Union

@dataclass
class FileOrigin:
    origin_host : str
    origin_path : Union[pathlib.Path, str]
    mtime_sec : int

@dataclass
class FileReplica:
    origin_host : str
    origin_path : Union[pathlib.Path, str]
    origin_mtime_sec : int
    hostname : str
    replica_path : Union[pathlib.Path, str]
