from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

@dataclass
class MemesLabEvent:
    __tablename__ = 'memeslab_trade_event'
    tx_hash: str
    trace_id: str
    event_time: int
    bcl_master: str
    event_type: str  # Buy, Sell
    trader_address: Optional[str]
    ton_amount: Decimal
    bcl_amount: Decimal
    volume_usd: Optional[Decimal]
