from dataclasses import dataclass
from supabase.client import Client
@dataclass
class RuntimeContex:
    db: Client
