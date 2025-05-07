import traceback
from typing import Optional
from decimal import Decimal
from loguru import logger
from pytoniq_core import Cell
from model.parser import NonCriticalParserError, Parser, TOPIC_MESSAGES
from model.memeslab import MemesLabEvent
from db import DB
from parsers.message.swap_volume import USDT

# Opcode mapping for event types
EVENT_TYPES = {
    Parser.opcode_signed(0xace8e777),  # Buy
    Parser.opcode_signed(0xace8e778),  # Sell
}

def parse_memeslab_event(opcode: int, cs: Cell) -> Optional[dict]:

    cs.load_uint(32)  # opcode
    cs.load_uint(64)  # query_id
    cs.load_uint(64)  # real_base_reserves
    cs.load_uint(64)  # real_quote_reserves

    ton_amount = cs.load_uint(64)      # TON in
    token_amount = cs.load_uint(64)    # Jetton in/out
    trader = cs.load_address()         # sender
    cs.load_uint(4)                    # reserved (0 or 1)
    _ = cs.load_slice()                # book_id, not used

    return {
        "type": "Buy" if opcode == 0xace8e777 else "Sell",
        "trader": trader,
        "ton_amount": ton_amount,
        "bcl_amount": token_amount,
    }

def make_event(obj: dict, trade_data: dict, price_usd: float) -> MemesLabEvent:

    return MemesLabEvent(
        tx_hash=obj["tx_hash"],
        trace_id=obj["trace_id"],
        event_time=obj["created_at"],
        bcl_master=obj["source"],
        event_type=trade_data["type"],
        trader_address=trade_data["trader"],
        ton_amount=int(trade_data["ton_amount"]),
        bcl_amount=int(trade_data["bcl_amount"]),
        volume_usd=int(trade_data["ton_amount"]) * price_usd / 1e6
    )

class MemesLabTrade(Parser):

    topics = lambda _: [TOPIC_MESSAGES]

    predicate = lambda _, obj: (
        obj.get("opcode") in EVENT_TYPES and obj.get("direction") == "out"
    )

    def handle_internal(self, obj: dict, db: DB) -> None:
        try:
            cs = Parser.message_body(obj, db).begin_parse()
            trade_data = parse_memeslab_event(obj["opcode"], cs)
            if trade_data:
                ton_price = db.get_core_price(USDT, Parser.require(obj.get('created_at')))
                ton_price = ton_price or 0
                event = make_event(obj, trade_data, ton_price)
                db.serialize(event)
        except Exception as e:
            logger.error(f"MemesLab parse error: {e}\n{traceback.format_exc()}")
            raise NonCriticalParserError(f"MemesLab parse error: {e}") from e
