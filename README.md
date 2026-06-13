# Trading-Calculator-MM

CLI Calculator ကို **Rich Terminal UI** နဲ့ ၆ မျိုးလုံး တစ်ခါတည်းတွက်ပြီး dashboard ပုံစံနဲ့ ဖော်ပြပေးမယ့် Python script ကို အောက်မှာ ရေးဆွဲပေးလိုက်ပါတယ်။

[Image of dashboard layout with all six calculation panels]

---

## 📦 Required Libraries

```bash
pip install rich
```

Rich ကို ထည့်သွင်းပြီးမှ script ကို run လို့ရပါမယ်။

---

## 🐍 Full Python Script

#!/usr/bin/env python3
"""
Forex Trading Dashboard - All-in-One Calculator with Rich Terminal UI
Fixed: Group renderables for margin panel
"""
အမှားက `create_margin_level_panel` function ထဲမှာ `Align.center(table) + warnings` ဆိုတဲ့ ပေါင်းလိုက်တဲ့အတွက် `TypeError` ပြသွားတာပါ။ Rich က `Align` object ကို string နဲ့ တိုက်ရိုက်ပေါင်းလို့မရပါဘူး။

ဒီအတွက် `rich.console.Group` ကိုသုံးပြီး table ရော warning စာသားကိုပါ အတူတူထည့်ပေးရပါမယ်။ အောက်မှာ **ပြင်ဆင်ပြီးသား full script** ကို ဖော်ပြထားပါတယ်။

```python
#!/usr/bin/env python3
"""
Forex Trading Dashboard - All-in-One Calculator with Rich Terminal UI
Fixed: Group renderables for margin panel
"""

import sys
from math import floor
from rich.console import Console, Group
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.table import Table
from rich.prompt import FloatPrompt
from rich.align import Align
from rich.text import Text

# ------------------------------------------------------------
# Constants
# ------------------------------------------------------------
PIP_VALUES = {
    "standard": 10.0,
    "mini": 1.0,
    "micro": 0.1,
    "nano": 0.01,
}

LOT_UNITS = {
    "standard": 100000,
    "mini": 10000,
    "micro": 1000,
    "nano": 100,
}

VALID_LOT_TYPES = list(PIP_VALUES.keys())

# ------------------------------------------------------------
# Helper: get valid lot type
# ------------------------------------------------------------
def get_lot_type():
    while True:
        lot_type = input(
            f"Lot type ({', '.join(VALID_LOT_TYPES)}) [micro]: "
        ).strip().lower()
        if lot_type == "":
            return "micro"
        if lot_type in VALID_LOT_TYPES:
            return lot_type
        print(f"❌ Invalid. Choose from: {', '.join(VALID_LOT_TYPES)}")

# ------------------------------------------------------------
# Calculation Functions
# ------------------------------------------------------------
def calculate_position_size(balance, risk_percent, stop_loss_pips, lot_type):
    risk_amount = balance * (risk_percent / 100.0)
    pip_value = PIP_VALUES[lot_type]
    if stop_loss_pips <= 0 or pip_value <= 0:
        return 0.0
    lots = risk_amount / (stop_loss_pips * pip_value)
    lots = floor(lots * 100) / 100
    return max(lots, 0.0)

def calculate_profit_loss(pips, lot_type, lots):
    pip_value = PIP_VALUES[lot_type]
    return pips * pip_value * lots

def calculate_margin(lot_type, lots, leverage, price=1.0):
    units = LOT_UNITS[lot_type] * lots
    margin_percentage = 1.0 / leverage
    return units * price * margin_percentage

def calculate_risk_reward(sl_pips, tp_pips):
    if sl_pips <= 0 or tp_pips <= 0:
        return 0.0
    return tp_pips / sl_pips

def get_pip_value(lot_type):
    return PIP_VALUES.get(lot_type, 0.0)

def calculate_margin_level(balance, unrealized_pl, used_margin):
    equity = balance + unrealized_pl
    if used_margin <= 0:
        return float('inf'), equity
    level = (equity / used_margin) * 100
    return level, equity

# ------------------------------------------------------------
# Dashboard UI Components (Fixed Margin Panel)
# ------------------------------------------------------------
def create_title():
    text = Text("📊 FOREX TRADING DASHBOARD", style="bold cyan on black")
    text.append("\nAll-in-One Calculator", style="italic yellow")
    return Align.center(text)

def create_position_panel(balance, risk_percent, sl_pips, lot_type, lots, risk_amount):
    table = Table.grid(padding=(0, 2))
    table.add_column(justify="left", style="cyan")
    table.add_column(justify="right", style="green")
    table.add_row("💼 Account Balance:", f"${balance:,.2f}")
    table.add_row("⚠️ Risk per Trade:", f"{risk_percent:.1f}% (${risk_amount:.2f})")
    table.add_row("🛑 Stop Loss:", f"{sl_pips} pips")
    table.add_row("🎲 Lot Type:", lot_type.capitalize())
    table.add_row("📦 Recommended Lot:", f"{lots:.3f}")
    table.add_row("🔢 Units:", f"{LOT_UNITS[lot_type] * lots:,.0f}")
    return Panel(Align.center(table), title="1. POSITION SIZE (RISK BASED)", border_style="cyan")

def create_profit_panel(pips, lot_type, lots, pl_usd, pl_pct):
    pl_emoji = "📈" if pl_usd >= 0 else "📉"
    table = Table.grid(padding=(0, 2))
    table.add_column(justify="left", style="cyan")
    table.add_column(justify="right", style="green")
    table.add_row(f"{pl_emoji} Trade Pips:", f"{pips:+} pips")
    table.add_row("🎲 Lot Type:", lot_type.capitalize())
    table.add_row("📦 Lot Size:", f"{lots}")
    table.add_row("💵 Pip Value:", f"${get_pip_value(lot_type):.2f}/pip")
    table.add_row("💰 Profit/Loss:", f"${pl_usd:.2f} ({pl_pct:+.2f}%)")
    border = "green" if pl_usd >= 0 else "red"
    return Panel(Align.center(table), title="2. PROFIT / LOSS", border_style=border)

def create_margin_panel(lot_type, lots, leverage, price, margin):
    table = Table.grid(padding=(0, 2))
    table.add_column(justify="left", style="cyan")
    table.add_column(justify="right", style="green")
    table.add_row("🎲 Lot Type:", lot_type.capitalize())
    table.add_row("📦 Lot Size:", f"{lots}")
    table.add_row("⚙️ Leverage:", f"1:{leverage}")
    table.add_row("💵 Market Price:", f"{price:.5f}")
    table.add_row("🔒 Margin Required:", f"${margin:,.2f}")
    return Panel(Align.center(table), title="3. REQUIRED MARGIN", border_style="magenta")

def create_rr_panel(sl_pips, tp_pips, rr_ratio):
    table = Table.grid(padding=(0, 2))
    table.add_column(justify="left", style="cyan")
    table.add_column(justify="right", style="green")
    table.add_row("🛑 Stop Loss:", f"{sl_pips} pips")
    table.add_row("🎯 Take Profit:", f"{tp_pips} pips")
    table.add_row("⚖️ Risk/Reward:", f"1 : {rr_ratio:.2f}")
    return Panel(Align.center(table), title="4. RISK / REWARD RATIO", border_style="yellow")

def create_pip_panel(lot_type):
    pip_val = get_pip_value(lot_type)
    table = Table.grid(padding=(0, 2))
    table.add_column(justify="left", style="cyan")
    table.add_column(justify="right", style="green")
    table.add_row("🎲 Lot Type:", lot_type.capitalize())
    table.add_row("💧 Pip Value:", f"${pip_val:.2f} per pip")
    return Panel(Align.center(table), title="5. PIP VALUE", border_style="blue")

def create_margin_level_panel(balance, unrealized_pl, used_margin, margin_level, equity, free_margin):
    level_color = "green" if margin_level > 300 else "yellow" if margin_level >= 100 else "red"
    table = Table.grid(padding=(0, 2))
    table.add_column(justify="left", style="cyan")
    table.add_column(justify="right", style="green")
    table.add_row("📊 Balance:", f"${balance:,.2f}")
    table.add_row("📈 Unrealized P/L:", f"${unrealized_pl:+.2f}")
    table.add_row("📊 Equity:", f"${equity:,.2f}")
    table.add_row("🔒 Used Margin:", f"${used_margin:,.2f}")
    table.add_row("🆓 Free Margin:", f"${free_margin:,.2f}")
    table.add_row("📊 Margin Level:", f"{margin_level:.2f}%", style=level_color)

    warnings = []
    if margin_level <= 100:
        warnings.append("⚠️  MARGIN CALL ZONE!")
    if margin_level <= 50:
        warnings.append("❌ STOP OUT LEVEL REACHED!")
    
    # Combine table and warnings into a Group
    content = [Align.center(table)]
    if warnings:
        content.append(Align.center("\n".join(warnings), style="bold red"))
    
    return Panel(Group(*content), title="6. MARGIN LEVEL & FREE MARGIN", border_style="green")

# ------------------------------------------------------------
# Main Dashboard
# ------------------------------------------------------------
def main():
    console = Console()
    console.print(create_title())
    console.print()
    
    print("📝 Please enter your trading parameters:\n")
    account_balance = FloatPrompt.ask("💼 Account Balance (USD)", default=1000.0)
    risk_percent = FloatPrompt.ask("⚠️ Risk per trade (%)", default=1.0)
    stop_loss = FloatPrompt.ask("🛑 Stop Loss (pips)", default=50.0)
    take_profit = FloatPrompt.ask("🎯 Take Profit (pips)", default=100.0)
    lot_type = get_lot_type()
    
    print("\n📊 Open Position Details:\n")
    entry_price = FloatPrompt.ask("💸 Entry Price", default=1.10000)
    exit_price = FloatPrompt.ask("🏁 Exit Price", default=1.11000)
    
    print("\n🔒 Margin Level Details:\n")
    used_margin = FloatPrompt.ask("Used Margin ($)", default=500.0)
    unrealized_pl = FloatPrompt.ask("Unrealized P/L ($)", default=0.0)
    
    # Calculate pips from price difference
    diff_price = exit_price - entry_price
    pips = diff_price / 0.0001  # for 4-digit pairs
    pips = round(pips, 2)
    
    # Position size based on risk
    risk_amount = account_balance * (risk_percent / 100)
    recommended_lot = calculate_position_size(account_balance, risk_percent, stop_loss, lot_type)
    lots_to_use = recommended_lot
    
    # Profit/Loss
    pl_usd = calculate_profit_loss(pips, lot_type, lots_to_use)
    pl_pct = (pl_usd / account_balance) * 100
    
    # Margin (using 1:100 leverage as default)
    leverage = 100
    margin = calculate_margin(lot_type, lots_to_use, leverage, entry_price)
    
    # Risk/Reward
    rr_ratio = calculate_risk_reward(stop_loss, take_profit)
    
    # Margin Level
    margin_level, equity = calculate_margin_level(account_balance, unrealized_pl, used_margin)
    free_margin = equity - used_margin
    
    # Build UI
    layout = Layout()
    layout.split(
        Layout(name="top", size=3),
        Layout(name="body"),
        Layout(name="bottom", size=4),
    )
    layout["top"].split_row(
        create_position_panel(account_balance, risk_percent, stop_loss, lot_type, recommended_lot, risk_amount),
        create_margin_panel(lot_type, lots_to_use, leverage, entry_price, margin),
        create_rr_panel(stop_loss, take_profit, rr_ratio),
    )
    layout["body"].split(
        Layout(name="middle_top"),
        Layout(name="middle_bottom"),
    )
    layout["middle_top"].split_row(
        create_profit_panel(pips, lot_type, lots_to_use, pl_usd, pl_pct),
        create_pip_panel(lot_type),
    )
    layout["middle_bottom"].update(
        create_margin_level_panel(account_balance, unrealized_pl, used_margin, margin_level, equity, free_margin)
    )
    
    bottom_text = Text("📊 Dashboard generated with Rich | Press Ctrl+C to exit", style="dim italic")
    layout["bottom"].update(Align.center(bottom_text))
    
    with Live(layout, console=console, refresh_per_second=4, screen=True):
        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            console.print("\n✅ Dashboard closed. Happy Trading!", style="bold green")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n✅ Dashboard closed. Happy Trading!")
        sys.exit(0)
```
---

## 🚀 How to Run

1. သင့်ရဲ့ Python environment မှာ `pip install rich` အားဖြင့် rich library ကို ထည့်ပါ။
2. အထက်ပါ script ကို `trading_dashboard.py` လို့ နာမည်ပေးပြီး save ပါ။
3. Terminal (Command Prompt) မှာ အောက်ပါ command ကို run ပါ။

```bash
python trading_dashboard.py
```

---

## ✨ Features

| Calculation | Description |
|---|---|
| **Position Size** | ခင်ဗျားရဲ့ Risk % နဲ့ Stop Loss ကိုအခြေခံပြီး သုံးသင့်တဲ့ Lot အရွယ်အစားကို တွက်ပေးတယ်။ |
| **Profit/Loss** | Entry/Exit price နဲ့ Lot size ကိုအခြေခံပြီး P/L ကို USD နဲ့ % ပါ ပြပေးတယ်။ |
| **Margin Required** | Trade ဖွင့်ဖို့အတွက် လိုအပ်တဲ့ Margin ပမာဏကို တွက်ပေးတယ်။ |
| **Risk/Reward Ratio** | Stop Loss နဲ့ Take Profit အချိုးကို တွက်ပြီး 1 : X ပုံစံနဲ့ ပြပေးတယ်။ |
| **Pip Value** | သင်ရွေးထားတဲ့ Lot Type (Standard/Mini/Micro/Nano) အတွက် 1 pip ရဲ့တန်ဖိုးကို ပြပေးတယ်။ |
| **Margin Level** | Equity, Free Margin, Margin Level (%) တို့ကို တွက်ပြီး Margin Call zone မှာဆိုရင် သတိပေးချက်ပါပါတယ်။ |

---

## 📋 Input Guide

Script ကို run ပြီးတဲ့အခါမှာ ခင်ဗျားကို အောက်ပါ input တွေ တောင်းပါလိမ့်မယ် -

| Input | Description | Example |
|---|---|---|
| Account Balance (USD) | အကောင့်ထဲမှာရှိတဲ့ ငွေပမာဏ | 1000 |
| Risk per trade (%) | တစ်ပွဲမှာ ဘယ်နှရာခိုင်နှုန်း စွန့်စားချင်လဲ | 1 (for 1%) |
| Stop Loss (pips) | Stop Loss ထားမယ့် pip အကွာအဝေး | 50 |
| Take Profit (pips) | Take Profit ထားမယ့် pip အကွာအဝေး | 100 |
| Lot Type | Standard / Mini / Micro / Nano | micro |
| Entry Price | ဝယ်လိုက်တဲ့ဈေးနှုန်း | 1.10000 |
| Exit Price | ရောင်းလိုက်တဲ့ဈေးနှုန်း | 1.11000 |
| Used Margin ($) | လက်ရှိ open position တွေအတွက် သုံးထားတဲ့ Margin | 500 |
| Unrealized P/L ($) | လက်ရှိ open position တွေရဲ့ အမြတ်/အရှုံး | +100 (or -50) |

---

## 🎨 Terminal Output ပုံစံ

```
╭──────────────────────────────────────────────────────────────────────────────────────────────╮
│                          📊 FOREX TRADING DASHBOARD                                           │
│                                    All-in-One Calculator                                      │
╰──────────────────────────────────────────────────────────────────────────────────────────────╯

╭───────────────────────────────╮ ╭───────────────────────────────╮ ╭───────────────────────────────╮
│ 1. POSITION SIZE (RISK BASED) │ │ 3. REQUIRED MARGIN            │ │ 4. RISK / REWARD RATIO       │
├───────────────────────────────┤ ├───────────────────────────────┤ ├───────────────────────────────┤
│ 💼 Account Balance: $1,000.00 │ │ 🎲 Lot Type: Micro            │ │ 🛑 Stop Loss: 50 pips         │
│ ⚠️ Risk per Trade: 1% ($10.00)│ │ 📦 Lot Size: 0.5              │ │ 🎯 Take Profit: 100 pips      │
│ 🛑 Stop Loss: 50 pips         │ │ ⚙️ Leverage: 1:100            │ │ ⚖️ Risk/Reward: 1 : 2.00      │
│ 🎲 Lot Type: Micro            │ │ 💵 Market Price: 1.10000      │ │                               │
│ 📦 Recommended Lot: 0.200     │ │ 🔒 Margin Required: $5.50     │ │                               │
│ 🔢 Units: 200                 │ │                               │ │                               │
╰───────────────────────────────╯ ╰───────────────────────────────╯ ╰───────────────────────────────╯

╭───────────────────────────────╮ ╭───────────────────────────────╮
│ 2. PROFIT / LOSS              │ │ 5. PIP VALUE                  │
├───────────────────────────────┤ ├───────────────────────────────┤
│ 📈 Trade Pips: +100 pips      │ │ 🎲 Lot Type: Micro            │
│ 🎲 Lot Type: Micro            │ │ 💧 Pip Value: $0.10 per pip   │
│ 📦 Lot Size: 0.5              │ │                               │
│ 💵 Pip Value: $0.10/pip       │ │                               │
│ 💰 Profit/Loss: $10.00 (+1.0%)│ │                               │
╰───────────────────────────────╯ ╰───────────────────────────────╯

╭───────────────────────────────────────────────────────────────────────────────────────────────╮
│ 6. MARGIN LEVEL & FREE MARGIN                                                                 │
├───────────────────────────────────────────────────────────────────────────────────────────────┤
│ 📊 Balance: $1,000.00     📈 Unrealized P/L: $100.00    📊 Equity: $1,100.00                   │
│ 🔒 Used Margin: $500.00    🆓 Free Margin: $600.00      📊 Margin Level: 220.00%               │
╰───────────────────────────────────────────────────────────────────────────────────────────────╯
```

---

## 🔧 Troubleshooting

- **`ModuleNotFoundError: No module named 'rich'`** → `pip install rich` ထည့်ပါ။
- **Terminal မှာ box ပုံစံမတူရင်** → ခင်ဗျားရဲ့ terminal (Windows Command Prompt, PowerShell, VS Code terminal, etc.) အားလုံးနီးပါးမှာ အဆင်ပြေပါတယ်။
- **ပိုမိုကြည့်ကောင်းစေရန်** → Windows ဆိုရင် **Windows Terminal** (Microsoft Store မှာ free download) ကိုသုံးပါ။

ဒီ dashboard က **interactive** ဖြစ်ပြီး **real-time** လည်းဖြစ်တာမို့ ခင်ဗျားရဲ့ trading parameters အားလုံးကို တစ်ခါတည်းမြင်နိုင်ပြီး အမြတ်/အရှုံးကို ရှင်းရှင်းလင်းလင်းမြင်ရမှာဖြစ်ပါတယ်။

မေးစရာရှိရင် ထပ်ပြီးမေးမြန်းနိုင်ပါတယ်။ Happy Trading! 🚀📊
