from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from signal_engine import generate_signal

app = FastAPI(title="Dakar Fx")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/signal")
def get_signal():
    # This data will come from your market data provider
    market_data = {
        "prices_1h": [...],
        "prices_4h": [...],
        "prices_15m": [...],
        "candles_15m": [...],
        "current_price": 2032.10,
        "support": 2025.00,
        "resistance": 2045.00,
        "fib_zone": (2028.00, 2034.00),
        "structure_sl": 2024.50,
        "structure_tp": 2055.00
    }

    return generate_signal(market_data)
