import numpy as np

# ---------- INDICATORS ----------

def ema(prices, period):
    return np.mean(prices[-period:])

def rsi(prices, period=14):
    deltas = np.diff(prices)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, abs(deltas), 0)

    avg_gain = np.mean(gains[-period:])
    avg_loss = np.mean(losses[-period:])

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


# ---------- STEP 1: HTF BIAS ----------

def get_htf_bias(prices_1h, prices_4h):
    ema50_1h = ema(prices_1h, 50)
    ema200_1h = ema(prices_1h, 200)

    ema50_4h = ema(prices_4h, 50)
    ema200_4h = ema(prices_4h, 200)

    if ema50_1h > ema200_1h and ema50_4h > ema200_4h:
        return "BULLISH"

    if ema50_1h < ema200_1h and ema50_4h < ema200_4h:
        return "BEARISH"

    return "RANGE"


# ---------- STEP 2: GOOD POSITION FILTER ----------

def at_key_level(price, support, resistance, fib_zone):
    if support <= price <= support * 1.002:
        return True
    if resistance * 0.998 <= price <= resistance:
        return True
    if fib_zone[0] <= price <= fib_zone[1]:
        return True
    return False


# ---------- STEP 3: MOMENTUM ----------

def momentum_confirm(prices_15m, bias):
    rsi_val = rsi(prices_15m)

    if bias == "BULLISH" and rsi_val > 50 and rsi_val < 70:
        return True

    if bias == "BEARISH" and rsi_val < 50 and rsi_val > 30:
        return True

    return False


# ---------- STEP 4: PRICE ACTION ----------

def bullish_engulfing(candles):
    last = candles[-1]
    prev = candles[-2]

    return (
        prev["close"] < prev["open"]
        and last["close"] > last["open"]
        and last["close"] > prev["open"]
        and last["open"] < prev["close"]
    )

def bearish_engulfing(candles):
    last = candles[-1]
    prev = candles[-2]

    return (
        prev["close"] > prev["open"]
        and last["close"] < last["open"]
        and last["open"] > prev["close"]
        and last["close"] < prev["open"]
    )


# ---------- STEP 5: TRADE BUILD ----------

def build_trade(price, bias, structure_sl, structure_tp):
    if bias == "BULLISH":
        entry = price
        sl = structure_sl
        tp = structure_tp
    else:
        entry = price
        sl = structure_sl
        tp = structure_tp

    rr = abs(tp - entry) / abs(entry - sl)

    if rr < 3:
        return None

    return {
        "entry": round(entry, 2),
        "sl": round(sl, 2),
        "tp": round(tp, 2),
        "rr": round(rr, 2)
    }


# ---------- FINAL SIGNAL DECISION ----------

def generate_signal(market_data):
    bias = get_htf_bias(
        market_data["prices_1h"],
        market_data["prices_4h"]
    )

    if bias == "RANGE":
        return {"status": "WAIT", "reason": "HTF ranging"}

    price = market_data["current_price"]

    if not at_key_level(
        price,
        market_data["support"],
        market_data["resistance"],
        market_data["fib_zone"]
    ):
        return {"status": "WAIT", "reason": "Not at good position"}

    if not momentum_confirm(market_data["prices_15m"], bias):
        return {"status": "WAIT", "reason": "Momentum not aligned"}

    candles = market_data["candles_15m"]

    if bias == "BULLISH" and not bullish_engulfing(candles):
        return {"status": "WAIT", "reason": "No bullish price action"}

    if bias == "BEARISH" and not bearish_engulfing(candles):
        return {"status": "WAIT", "reason": "No bearish price action"}

    trade = build_trade(
        price,
        bias,
        market_data["structure_sl"],
        market_data["structure_tp"]
    )

    if trade is None:
        return {"status": "WAIT", "reason": "RR below 1:3"}

    return {
        "status": "SIGNAL",
        "bias": bias,
        **trade
    }
