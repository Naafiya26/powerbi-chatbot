import duckdb
from .config import DB_PATH

_con = None

def get_con():
    global _con
    if _con is None:
        _con = duckdb.connect(str(DB_PATH), read_only=True)  
    return _con