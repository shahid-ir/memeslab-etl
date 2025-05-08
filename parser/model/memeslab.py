from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass
class MemesLabEvent:
    __tablename__ = "memeslab_trade_event"
    tx_hash: str
    trace_id: str
    event_time: int
    jetton_master: str
    event_type: str  # Buy, Sell
    trader_address: Optional[str]
    ton_amount: Decimal
    jetton_amount: Decimal
    volume_usd: Optional[Decimal]
    query_id: Optional[Decimal]
    real_base_reserve: Decimal
    real_quote_reserve: Decimal
    book_id: Optional[str]
