import asyncio
import json
import math
import random
import time
import websockets

def clamp(val, low, high):
    return max(low, min(val, high))

# =========================================================================
# 🐋 DYNAMIC WHALE WALL / SPOOFER BEHAVIOR
# =========================================================================
class FlashLiquidityWall:
    def __init__(self, price, volume, is_bid, duration_ticks, behavior="PULL"):
        self.price = price
        self.volume = volume
        self.is_bid = is_bid
        self.ticks_left = duration_ticks
        self.behavior = behavior  # "PULL" (Spoof), "HOLD" (Absorb), "CHASE" (Step closer)

# =========================================================================
# 🏛️ PRO-GRADE ACTIVE LOB ENGINE WITH WHALE WALL SPIKES
# =========================================================================
class ProMarketSimulator:
    def __init__(self, base_price=85000.0, tick_size=0.50):
        self.tick_size = tick_size
        self.mid_price = base_price
        self.fair_value = base_price
        
        # Central Limit Order Book: Absolute Price -> Volume (BTC)
        self.bids = {}
        self.asks = {}
        
        # Active Dynamic Whale Walls
        self.active_flash_walls = []
        self.wall_spawn_cooldown = 120
        
        # Micro-momentum state
        self.momentum = 0.0
        self.momentum_ticks = 0
        
        self._init_order_book()

    def _round(self, p):
        return round(round(p / self.tick_size) * self.tick_size, 2)

    def _init_order_book(self):
        best_bid = self._round(self.mid_price - (self.tick_size / 2.0))
        best_ask = self._round(self.mid_price + (self.tick_size / 2.0))

        # Fill 60 Bid Levels (10 - 35 BTC)
        for i in range(60):
            p = self._round(best_bid - (i * self.tick_size))
            self.bids[p] = round(random.uniform(10.0, 32.0), 2)

        # Fill 60 Ask Levels (10 - 35 BTC)
        for i in range(60):
            p = self._round(best_ask + (i * self.tick_size))
            self.asks[p] = round(random.uniform(10.0, 32.0), 2)

    def get_best_bid(self):
        return max(self.bids.keys()) if self.bids else self._round(self.mid_price - 0.50)

    def get_best_ask(self):
        return min(self.asks.keys()) if self.asks else self._round(self.mid_price + 0.50)

    def manage_whale_walls(self):
        """Spawns, steps, and cancels massive institutional liquidity walls."""
        best_bid = self.get_best_bid()
        best_ask = self.get_best_ask()

        # 1. Randomly spawn a massive new wall (Every 2-5 seconds / 150-350 ticks)
        if self.wall_spawn_cooldown <= 0:
            if len(self.active_flash_walls) < 3:
                is_bid = random.random() < 0.5
                # Offset 4 to 15 ticks away from current market price
                offset_ticks = random.randint(4, 15)
                
                if is_bid:
                    target_p = self._round(best_bid - (offset_ticks * self.tick_size))
                else:
                    target_p = self._round(best_ask + (offset_ticks * self.tick_size))

                # Massive size: 85.0 to 220.0 BTC!
                wall_volume = round(random.uniform(85.0, 220.0), 2)
                
                # Randomized Behavior
                roll = random.random()
                if roll < 0.50: behavior = "PULL"   # 50% Spoof & Cancel
                elif roll < 0.80: behavior = "HOLD" # 30% Absorb & Defend
                else: behavior = "CHASE"            # 20% Step Closer

                duration = random.randint(250, 700) # Lasts 1 to 3 seconds
                wall = FlashLiquidityWall(target_p, wall_volume, is_bid, duration, behavior)
                self.active_flash_walls.append(wall)

                # Inject into the order book
                if is_bid: self.bids[target_p] = wall_volume
                else: self.asks[target_p] = wall_volume

                side_str = "BID (BUY WALL)" if is_bid else "ASK (SELL WALL)"
                print(f"🔥 >>> [WHALE DROP] {side_str} @ ${target_p:,.2f} | Volume: {wall_volume:,.1f} BTC | Intent: {behavior}")

            self.wall_spawn_cooldown = random.randint(180, 450)
        else:
            self.wall_spawn_cooldown -= 1

        # 2. Update & Age Active Whale Walls
        for wall in list(self.active_flash_walls):
            wall.ticks_left -= 1
            
            # Check if wall was eaten by market orders
            current_book_vol = self.bids.get(wall.price, 0.0) if wall.is_bid else self.asks.get(wall.price, 0.0)
            if current_book_vol <= 5.0:
                self.active_flash_walls.remove(wall)
                print(f"💥 >>> [WALL CONSUMED] Whale order @ ${wall.price:,.2f} completely eaten by market orders!")
                continue

            # If wall lifespan expired
            if wall.ticks_left <= 0:
                if wall.behavior == "PULL":
                    # Cancel / Spoof order pulled!
                    if wall.is_bid and wall.price in self.bids:
                        self.bids[wall.price] = round(random.uniform(8.0, 22.0), 2)
                    elif not wall.is_bid and wall.price in self.asks:
                        self.asks[wall.price] = round(random.uniform(8.0, 22.0), 2)
                    
                    self.active_flash_walls.remove(wall)
                    print(f"🚫 >>> [SPOOF CANCELLED] Whale pulled {wall.volume:.1f} BTC from ${wall.price:,.2f}")

                elif wall.behavior == "CHASE":
                    # Cancel old price and step 2 ticks closer to market!
                    old_p = wall.price
                    if wall.is_bid and old_p in self.bids: self.bids[old_p] = round(random.uniform(8.0, 20.0), 2)
                    elif not wall.is_bid and old_p in self.asks: self.asks[old_p] = round(random.uniform(8.0, 20.0), 2)

                    step_ticks = 2
                    if wall.is_bid:
                        new_p = self._round(min(best_bid - self.tick_size, old_p + (step_ticks * self.tick_size)))
                        self.bids[new_p] = wall.volume
                    else:
                        new_p = self._round(max(best_ask + self.tick_size, old_p - (step_ticks * self.tick_size)))
                        self.asks[new_p] = wall.volume

                    wall.price = new_p
                    wall.ticks_left = random.randint(200, 400)
                    wall.behavior = "HOLD" # Sits after chasing
                    print(f"⚡ >>> [WALL STEPPING] Whale moved size closer to ${new_p:,.2f}!")

                else: # "HOLD"
                    # Keep holding
                    wall.ticks_left = 300

    def simulate_hft_order_churn(self):
        """Simulates rapid micro-cancellations across the top 20 levels."""
        best_bid = self.get_best_bid()
        best_ask = self.get_best_ask()
        active_wall_prices = {w.price for w in self.active_flash_walls}

        # 1. Churn active Bid levels
        active_bids = [p for p in self.bids.keys() if best_bid - (20 * self.tick_size) <= p <= best_bid]
        if active_bids:
            for p in random.sample(active_bids, min(4, len(active_bids))):
                if p not in active_wall_prices:
                    delta = random.uniform(-2.5, 3.0)
                    self.bids[p] = round(clamp(self.bids[p] + delta, 5.0, 40.0), 2)

        # 2. Churn active Ask levels
        active_asks = [p for p in self.asks.keys() if best_ask <= p <= best_ask + (20 * self.tick_size)]
        if active_asks:
            for p in random.sample(active_asks, min(4, len(active_asks))):
                if p not in active_wall_prices:
                    delta = random.uniform(-2.5, 3.0)
                    self.asks[p] = round(clamp(self.asks[p] + delta, 5.0, 40.0), 2)

    def maintain_market_maker_depth(self):
        """Replenishes depth and maintains tight spreads."""
        best_bid = self.get_best_bid()
        best_ask = self.get_best_ask()
        spread_ticks = int(round((best_ask - best_bid) / self.tick_size))
        active_wall_prices = {w.price for w in self.active_flash_walls}

        # Dynamic Spread breathing (1 to 3 ticks)
        if spread_ticks > 3 or (spread_ticks > 1 and random.random() < 0.70):
            if random.random() < 0.5:
                tight_bid = self._round(best_bid + self.tick_size)
                if tight_bid < best_ask:
                    self.bids[tight_bid] = round(random.uniform(8.0, 22.0), 2)
                    best_bid = tight_bid
            else:
                tight_ask = self._round(best_ask - self.tick_size)
                if tight_ask > best_bid:
                    self.asks[tight_ask] = round(random.uniform(8.0, 22.0), 2)
                    best_ask = tight_ask

        # Maintain 50 levels of depth
        for i in range(1, 55):
            p_bid = self._round(best_bid - (i * self.tick_size))
            if p_bid not in self.bids and p_bid not in active_wall_prices:
                self.bids[p_bid] = round(random.uniform(8.0, 30.0), 2)

            p_ask = self._round(best_ask + (i * self.tick_size))
            if p_ask not in self.asks and p_ask not in active_wall_prices:
                self.asks[p_ask] = round(random.uniform(8.0, 30.0), 2)

        # Clean cross-book edge cases
        for p in list(self.bids.keys()):
            if p >= best_ask: del self.bids[p]
        for p in list(self.asks.keys()):
            if p <= best_bid: del self.asks[p]

    def step(self):
        # 1. Update Momentum
        if self.momentum_ticks <= 0:
            self.momentum = random.uniform(-0.10, 0.10)
            self.momentum_ticks = random.randint(80, 250)
        else:
            self.momentum_ticks -= 1

        dist_from_fair = (self.mid_price - self.fair_value) / 20.0
        buy_prob = 0.50 + self.momentum - (dist_from_fair * 0.12)
        buy_prob = clamp(buy_prob, 0.38, 0.62)
        
        is_buy_order = random.random() < buy_prob

        # 2. Active Market Order Sizing
        dice = random.random()
        if dice < 0.80:
            incoming_size = round(random.uniform(0.02, 0.35), 4) # Retail noise
        elif dice < 0.96:
            incoming_size = round(random.uniform(0.60, 2.20), 3) # Medium algo flow
        else:
            incoming_size = round(random.uniform(3.50, 8.50), 2) # Whale sweep

        # 3. Match Order Against Order Book
        executed_trades = []
        remaining = incoming_size

        if is_buy_order:
            while remaining > 0.0001 and self.asks:
                best_ask = min(self.asks.keys())
                avail = self.asks[best_ask]

                if remaining < avail:
                    self.asks[best_ask] = round(avail - remaining, 4)
                    executed_trades.append((best_ask, round(remaining, 4), False))
                    remaining = 0
                else:
                    executed_trades.append((best_ask, round(avail, 4), False))
                    remaining = round(remaining - avail, 4)
                    del self.asks[best_ask] # Level swept!
        else:
            while remaining > 0.0001 and self.bids:
                best_bid = max(self.bids.keys())
                avail = self.bids[best_bid]

                if remaining < avail:
                    self.bids[best_bid] = round(avail - remaining, 4)
                    executed_trades.append((best_bid, round(remaining, 4), True))
                    remaining = 0
                else:
                    executed_trades.append((best_bid, round(avail, 4), True))
                    remaining = round(remaining - avail, 4)
                    del self.bids[best_bid] # Level swept!

        # 4. Manage Whale Wall Spikes & HFT Churn
        self.manage_whale_walls()
        self.simulate_hft_order_churn()
        self.maintain_market_maker_depth()

        best_bid = self.get_best_bid()
        best_ask = self.get_best_ask()
        self.mid_price = self._round((best_bid + best_ask) / 2.0)
        self.fair_value += (self.mid_price - self.fair_value) * 0.002

        return executed_trades, best_bid, best_ask

# =========================================================================
# 🌐 WEBSOCKET BROADCASTER (300 Ticks / Sec)
# =========================================================================
sim = ProMarketSimulator(base_price=85000.0, tick_size=0.50)
connected_clients = set()

async def handler(websocket):
    connected_clients.add(websocket)
    print(f"[Simulator] Terminal connected! Total active: {len(connected_clients)}")
    try:
        await websocket.wait_closed()
    finally:
        connected_clients.remove(websocket)
        print(f"[Simulator] Terminal disconnected. Total active: {len(connected_clients)}")

async def exchange_loop():
    tick_counter = 0
    last_fps_time = time.time()
    depth_counter = 0

    while True:
        now_ms = int(time.time() * 1000)
        trades, best_bid, best_ask = sim.step()

        if connected_clients:
            # 1. BBO Quote Update
            bbo_payload = json.dumps({
                "stream": "btcusdt@bookTicker",
                "data": {
                    "b": f"{best_bid:.2f}",
                    "B": f"{sim.bids.get(best_bid, 10.0):.3f}",
                    "a": f"{best_ask:.2f}",
                    "A": f"{sim.asks.get(best_ask, 10.0):.3f}"
                }
            })

            # 2. Executed Trades
            trade_payloads = [
                json.dumps({
                    "stream": "btcusdt@aggTrade",
                    "data": {
                        "p": f"{p:.2f}",
                        "q": f"{q}",
                        "m": is_sell,
                        "T": now_ms
                    }
                }) for p, q, is_sell in trades
            ]

            # 3. L2 Depth Snapshot (every ~100ms / 2 ticks)
            depth_payload = None
            if depth_counter % 2 == 0:
                sorted_bids = sorted([[f"{p:.2f}", f"{v:.3f}"] for p, v in sim.bids.items()], key=lambda x: -float(x[0]))
                sorted_asks = sorted([[f"{p:.2f}", f"{v:.3f}"] for p, v in sim.asks.items()], key=lambda x: float(x[0]))

                depth_payload = json.dumps({
                    "stream": "btcusdt@depth20@100ms",
                    "data": {
                        "bids": sorted_bids[:50],
                        "asks": sorted_asks[:50]
                    }
                })

            for client in list(connected_clients):
                try:
                    await client.send(bbo_payload)
                    for tp in trade_payloads:
                        await client.send(tp)
                    if depth_payload:
                        await client.send(depth_payload)
                except Exception:
                    pass

        tick_counter += 1
        depth_counter += 1

        # Real-time console metrics
        now = time.time()
        if now - last_fps_time >= 1.0:
            spread = best_ask - best_bid
            print(f">>> [MARKET ENGINE] Mid: ${sim.mid_price:,.2f} | Spread: ${spread:.2f} | Active Walls: {len(sim.active_flash_walls)} | Speed: ~{tick_counter} t/s")
            tick_counter = 0
            last_fps_time = now

        # 300 Ticks / Second (3.3 ms)
        await asyncio.sleep(0.0033)

async def main():
    server = await websockets.serve(handler, "127.0.0.1", 8765)
    print("=" * 80)
    print("🏛️  ACTIVE LOB ENGINE WITH WHALE WALL INJECTION RUNNING ON ws://127.0.0.1:8765")
    print("    • Spawns massive institutional spikes (90 - 220 BTC)")
    print("    • Realistic Spoof & Pull, Absorption, and Chasing behaviors")
    print("=" * 80)
    await exchange_loop()

if __name__ == "__main__":
    asyncio.run(main())
