#!/usr/bin/env python3
"""
Forex Trading Calculator - CLI Version
Supports: Position Size, P/L, Margin, Pip Value, Risk/Reward, Margin Level
"""

import sys
import argparse
from math import floor

# ------------------------------------------------------------
# ပုံသေသတ်မှတ်ချက်များ
# ------------------------------------------------------------
PIP_VALUES = {
    "standard": 10.0,   # 1 standard lot = 100,000 units -> 1 pip = $10 (for USD quote pairs)
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

# ------------------------------------------------------------
# အခြေခံ Pip Value တွက်ချက်ခြင်း
# ------------------------------------------------------------
def get_pip_value(lot_type, quote_currency="USD", account_currency="USD", exchange_rate=1.0):
    """
    lot_type: 'standard', 'mini', 'micro', 'nano'
    account_currency နဲ့ quote_currency မတူရင် conversion လုပ်ပေးတယ်။
    (ဒီ version မှာ ရိုးရှင်းအောင် USD-based ပဲထားပါတယ်)
    """
    if lot_type not in PIP_VALUES:
        raise ValueError(f"Invalid lot type: {lot_type}")
    pip_usd = PIP_VALUES[lot_type]
    if account_currency == "USD" and quote_currency == "USD":
        return pip_usd
    # လိုအပ်ရင် conversion logic ထည့်လို့ရတယ်။ ဥပမာ EUR account အတွက် လတ်တလော rate နဲ့စား။
    # ဒီမှာ ရိုးရိုးအတွက် USD ပဲယူဆပါတယ်။
    return pip_usd * exchange_rate  # အနီးစပ်ဆုံး

# ------------------------------------------------------------
# 1. Position Size Calculator (Risk-based)
# ------------------------------------------------------------
def position_size(balance, risk_percent, stop_loss_pips, lot_type="micro"):
    """
    balance: account balance in USD
    risk_percent: % of account to risk (e.g., 1 for 1%)
    stop_loss_pips: stop loss distance in pips
    lot_type: 'standard', 'mini', 'micro', 'nano'
    Returns: lot size (e.g., 0.05 for micro lots)
    """
    risk_amount = balance * (risk_percent / 100.0)
    pip_value = get_pip_value(lot_type)
    if stop_loss_pips <= 0 or pip_value <= 0:
        return 0.0
    lots = risk_amount / (stop_loss_pips * pip_value)
    # round down to nearest 0.01 lot (most brokers support 0.01 minimum)
    lots = floor(lots * 100) / 100
    return max(lots, 0.0)

# ------------------------------------------------------------
# 2. Profit / Loss Calculator
# ------------------------------------------------------------
def profit_loss(pips, lot_type, lots=1.0):
    """pips: positive for profit, negative for loss"""
    pip_value = get_pip_value(lot_type)
    return pips * pip_value * lots

# ------------------------------------------------------------
# 3. Margin Required
# ------------------------------------------------------------
def margin_required(lot_type, lots, leverage, price=1.0):
    """
    lot_type: 'standard', 'mini', 'micro', 'nano'
    lots: number of lots (e.g., 0.05)
    leverage: e.g., 100 for 1:100
    price: current market price (for non-USD pairs, but here simple version)
    """
    units = LOT_UNITS[lot_type] * lots
    margin_percentage = 1.0 / leverage
    margin = units * price * margin_percentage
    return margin

# ------------------------------------------------------------
# 4. Risk / Reward Ratio
# ------------------------------------------------------------
def risk_reward(stop_loss_pips, take_profit_pips):
    if stop_loss_pips <= 0:
        return float('inf')
    return stop_loss_pips / take_profit_pips

# ------------------------------------------------------------
# 5. Pip Value ပြခြင်း
# ------------------------------------------------------------
def pip_value_display(lot_type):
    return get_pip_value(lot_type)

# ------------------------------------------------------------
# 6. Margin Level & Free Margin
# ------------------------------------------------------------
def margin_level(balance, unrealized_pl, used_margin):
    equity = balance + unrealized_pl
    if used_margin <= 0:
        return float('inf')
    level = (equity / used_margin) * 100
    return level, equity

def free_margin(equity, used_margin):
    return equity - used_margin

# ------------------------------------------------------------
# CLI Menu (Interactive)
# ------------------------------------------------------------
def interactive_mode():
    print("\n📊 Forex Trading Calculator (CLI)")
    print("=" * 40)
    print("1. Position Size (Risk based)")
    print("2. Profit / Loss")
    print("3. Required Margin")
    print("4. Risk / Reward Ratio")
    print("5. Pip Value")
    print("6. Margin Level & Free Margin")
    print("0. Exit")
    
    choice = input("\nSelect option: ").strip()
    
    if choice == "1":
        bal = float(input("Account Balance (USD): "))
        risk_pct = float(input("Risk per trade (%): "))
        sl_pips = float(input("Stop Loss (pips): "))
        lot_type = input("Lot type (standard/mini/micro/nano) [micro]: ").strip().lower() or "micro"
        lots = position_size(bal, risk_pct, sl_pips, lot_type)
        print(f"\n✅ You can trade: {lots} {lot_type} lot(s)")
        print(f"   Risk amount: ${bal * risk_pct / 100:.2f}")
        
    elif choice == "2":
        pips = float(input("Profit/Loss (pips, positive or negative): "))
        lot_type = input("Lot type (standard/mini/micro/nano) [micro]: ").strip().lower() or "micro"
        lots = float(input("Number of lots: "))
        pl = profit_loss(pips, lot_type, lots)
        print(f"\n💰 P/L: ${pl:.2f}")
        
    elif choice == "3":
        lot_type = input("Lot type (standard/mini/micro/nano) [micro]: ").strip().lower() or "micro"
        lots = float(input("Number of lots: "))
        lev = int(input("Leverage (e.g., 100 for 1:100): "))
        price = float(input("Market price (e.g., 1.2000): "))
        margin = margin_required(lot_type, lots, lev, price)
        print(f"\n🔒 Required Margin: ${margin:.2f}")
        
    elif choice == "4":
        sl = float(input("Stop Loss (pips): "))
        tp = float(input("Take Profit (pips): "))
        rr = risk_reward(sl, tp)
        print(f"\n⚖️ Risk/Reward Ratio: 1 : {1/rr if rr !=0 else 0:.2f}" if rr > 0 else "Invalid")
        
    elif choice == "5":
        lot_type = input("Lot type (standard/mini/micro/nano) [micro]: ").strip().lower() or "micro"
        pv = pip_value_display(lot_type)
        print(f"\n💧 1 pip value for 1 {lot_type} lot: ${pv:.2f}")
        
    elif choice == "6":
        bal = float(input("Current Balance (USD): "))
        unrealized = float(input("Unrealized P/L (USD, positive or negative): "))
        used_margin = float(input("Used Margin (from open positions): "))
        level, eq = margin_level(bal, unrealized, used_margin)
        fm = free_margin(eq, used_margin)
        print(f"\n📈 Equity: ${eq:.2f}")
        print(f"🆓 Free Margin: ${fm:.2f}")
        print(f"📊 Margin Level: {level:.2f}%")
        if level <= 100:
            print("⚠️  WARNING: Margin Call zone!")
        if level <= 50:
            print("❌ STOP OUT level reached!")
            
    elif choice == "0":
        print("Goodbye!")
        sys.exit(0)
    else:
        print("Invalid choice")

# ------------------------------------------------------------
# Command line non-interactive mode (argparse)
# ------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Forex Trading Calculator CLI")
    parser.add_argument("--mode", choices=["pos", "pl", "margin", "rr", "pip", "marginlevel"], required=True,
                        help="Calculation mode")
    parser.add_argument("--balance", type=float, help="Account balance")
    parser.add_argument("--risk", type=float, help="Risk percentage")
    parser.add_argument("--sl", type=float, help="Stop loss in pips")
    parser.add_argument("--tp", type=float, help="Take profit in pips")
    parser.add_argument("--lottype", default="micro", help="standard/mini/micro/nano")
    parser.add_argument("--lots", type=float, help="Number of lots")
    parser.add_argument("--pips", type=float, help="Profit/Loss in pips")
    parser.add_argument("--leverage", type=int, help="Leverage (e.g., 100)")
    parser.add_argument("--price", type=float, default=1.0, help="Market price for margin")
    parser.add_argument("--unrealized", type=float, default=0.0, help="Unrealized P/L")
    parser.add_argument("--usedmargin", type=float, help="Used margin")
    
    args = parser.parse_args()
    
    if args.mode == "pos":
        if not all([args.balance, args.risk, args.sl]):
            print("Need --balance, --risk, --sl")
            return
        lots = position_size(args.balance, args.risk, args.sl, args.lottype)
        print(f"{lots}")
    elif args.mode == "pl":
        if not all([args.pips, args.lots]):
            print("Need --pips, --lots")
            return
        pl = profit_loss(args.pips, args.lottype, args.lots)
        print(f"{pl:.2f}")
    elif args.mode == "margin":
        if not all([args.lots, args.leverage]):
            print("Need --lots, --leverage")
            return
        margin = margin_required(args.lottype, args.lots, args.leverage, args.price)
        print(f"{margin:.2f}")
    elif args.mode == "rr":
        if not all([args.sl, args.tp]):
            print("Need --sl, --tp")
            return
        rr = risk_reward(args.sl, args.tp)
        print(f"{rr:.2f}")
    elif args.mode == "pip":
        pv = pip_value_display(args.lottype)
        print(f"{pv:.4f}")
    elif args.mode == "marginlevel":
        if not all([args.balance, args.usedmargin]):
            print("Need --balance, --usedmargin")
            return
        level, eq = margin_level(args.balance, args.unrealized, args.usedmargin)
        fm = free_margin(eq, args.usedmargin)
        print(f"Equity:{eq:.2f},FreeMargin:{fm:.2f},MarginLevel:{level:.2f}%")
    else:
        parser.print_help()

# ------------------------------------------------------------
# Entry point
# ------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) == 1:
        # no arguments -> interactive mode
        while True:
            interactive_mode()
            input("\nPress Enter to continue...")
    else:
        main()