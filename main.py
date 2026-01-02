import requests
import time
from datetime import datetime

# API Endpoints
BINANCE_OI_URL = "https://fapi.binance.com/fapi/v1/openInterest"
COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price"

previous_ratio = None

def get_open_interest():
    """Binance'tan BTCUSDT.P Open Interest verisi çeker"""
    try:
        params = {"symbol": "BTCUSDT"}
        response = requests.get(BINANCE_OI_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        oi = float(data['openInterest'])
        print(f"✓ Open Interest: {oi:,.2f} BTC")
        return oi
    except Exception as e:
        print(f"✗ Open Interest hatası: {e}")
        return None

def get_marketcap():
    """CoinGecko'dan Bitcoin Market Cap verisi çeker (USD)"""
    try:
        params = {
            "ids": "bitcoin",
            "vs_currencies": "usd",
            "include_market_cap": "true"
        }
        response = requests.get(COINGECKO_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        marketcap = data['bitcoin']['usd_market_cap']
        print(f"✓ Market Cap: ${marketcap:,.0f}")
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
    print("🚀 Binance Signal Bot Başlatıldı!")
    print(f"⏰ Her 30 saniyede bir kontrol edilecek...\n")
    
    while True:
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n⏰ Zaman: {timestamp}")
            print("-" * 50)
            
            # Verileri çek
            oi = get_open_interest()
            marketcap = get_marketcap()
            
            if oi and marketcap:
                # Oranı hesapla (Open Interest / Market Cap)
                # OI BTC cinsinden, MarketCap USD cinsinden - normalize edelim
                ratio = (oi * 1e8) / marketcap  # Daha okunabilir sayılar için
                print(f"📊 OI/MarketCap Oranı: {ratio:.6f}")
                
                # Sinyal üret
                generate_signal(ratio)
            else:
                print("⚠️ Veri alınamadı, bir sonraki döngüde tekrar denenecek...")
            
            # 30 saniye bekle
            time.sleep(30)
            
        except KeyboardInterrupt:
            print("\n\n👋 Bot durduruldu.")
            break
        except Exception as e:
            print(f"❌ Beklenmeyen hata: {e}")
            time.sleep(30)

if __name__ == "__main__":
    main()
