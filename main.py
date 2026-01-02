import requests
import time
import sys
from datetime import datetime

# Python output buffering'i kapat
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

# API Endpoints
BINANCE_OI_URL = "https://fapi.binance.com/fapi/v1/openInterest"
BINANCE_PRICE_URL = "https://fapi.binance.com/fapi/v1/ticker/price"  # Futures API kullan

previous_ratio = None

def get_open_interest():
    """Binance'tan BTCUSDT.P (Perpetual) Open Interest verisi çeker"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        # Binance Futures için sembol BTCUSDT (API'de .P olmadan)
        params = {"symbol": "BTCUSDT"}
        response = requests.get(BINANCE_OI_URL, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        oi = float(data['openInterest'])
        print(f"✓ Open Interest: {oi:,.2f} BTC", flush=True)
        return oi
    except Exception as e:
        print(f"✗ Open Interest hatası: {e}")
        return None

def get_marketcap():
    """Binance'tan BTC fiyatını çekip market cap hesaplar (yaklaşık)"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        # BTC fiyatını çek
        price_url = "https://api.binance.com/api/v3/ticker/price"
        params = {"symbol": "BTCUSDT"}
        response = requests.get(price_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        btc_price = float(data['price'])
        
        # Sabit BTC supply (yaklaşık 19.5M BTC)
        btc_supply = 19_500_000
        marketcap = btc_price * btc_supply
        
        print(f"✓ BTC Fiyat: ${btc_price:,.2f}", flush=True)
        print(f"✓ Market Cap (yaklaşık): ${marketcap:,.0f}", flush=True)
        return marketcap
    except Exception as e:
        print(f"✗ Market Cap hatası: {e}")
        return None

def generate_signal(current_ratio):
    """Önceki oran ile karşılaştırıp sinyal üretir"""
    global previous_ratio
    
    if previous_ratio is None:
        previous_ratio = current_ratio
        print("⏳ İlk oran kaydedildi, bir sonraki döngüde sinyal gelecek...")
        return None
    
    if current_ratio < previous_ratio:
        signal = "🟢 LONG"
        change = ((current_ratio - previous_ratio) / previous_ratio) * 100
    elif current_ratio > previous_ratio:
        signal = "🔴 SHORT"
        change = ((current_ratio - previous_ratio) / previous_ratio) * 100
    else:
        signal = "⚪ NÖTR"
        change = 0
    
    print(f"\n{'='*50}")
    print(f"📊 SİNYAL: {signal}")
    print(f"📈 Oran Değişimi: {change:+.4f}%")
    print(f"📉 Önceki Oran: {previous_ratio:.6f}")
    print(f"📊 Şimdiki Oran: {current_ratio:.6f}")
    print(f"{'='*50}\n")
    
    previous_ratio = current_ratio
    return signal

def main():
    """Ana döngü - 30 saniyede bir çalışır"""
    print("🚀 Binance Signal Bot Başlatıldı!", flush=True)
    print(f"⏰ Her 30 saniyede bir kontrol edilecek...\n", flush=True)
    
    while True:
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n⏰ Zaman: {timestamp}")
            print("-" * 50)
            
            # Verileri çek
            oi = get_open_interest()
            marketcap = get_marketcap()
            
            # Hata durumunda biraz bekle
            if not (oi and marketcap):
                print("⚠️ Veri alınamadı, 10 saniye sonra tekrar denenecek...", flush=True)
                time.sleep(10)
                continue
                # Oranı hesapla (Open Interest / Market Cap)
                # OI BTC cinsinden, MarketCap USD cinsinden - normalize edelim
                ratio = (oi * 1e8) / marketcap  # Daha okunabilir sayılar için
                print(f"📊 OI/MarketCap Oranı: {ratio:.6f}")
                
                # Sinyal üret
                generate_signal(ratio)
            else:
                print("⚠️ Veri alınamadı, bir sonraki döngüde tekrar denenecek...")
            
            # 30 saniye bekle
            print(f"💤 Bir sonraki kontrol 30 saniye sonra...\n")
            time.sleep(30)
            
        except KeyboardInterrupt:
            print("\n\n👋 Bot durduruldu.")
            break
        except Exception as e:
            print(f"❌ Beklenmeyen hata: {e}")
            time.sleep(30)

if __name__ == "__main__":
    main()
