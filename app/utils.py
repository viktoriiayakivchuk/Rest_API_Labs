import base64
import uuid
from typing import Optional, Tuple, Any

def encode_cursor(id: uuid.UUID, sort_by: str, sort_val: Any) -> str:
    raw_cursor = f"{sort_val}|{id}"
    return base64.b64encode(raw_cursor.encode()).decode()

def decode_cursor(cursor: str) -> Tuple[Optional[Any], Optional[uuid.UUID]]:
    try:
        decoded_str = base64.b64decode(cursor).decode()
        parts = decoded_str.split('|')
        if len(parts) != 2:
            return None, None
        
        val_str, id_str = parts
        return val_str, uuid.UUID(id_str)
    except Exception:
        return None, None