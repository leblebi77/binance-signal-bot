import requests
import time
import sys
from datetime import datetime

# Python output buffering'i kapat
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

# API Endpoints
BINANCE_OI_URL = "https://fapi.binance.com/fapi/v1/openInterest"
COINPAPRIKA_URL = "https://api.coinpaprika.com/v1/tickers/btc-bitcoin"

previous_ratio = None

def get_open_interest():
    """Binance'tan BTCUSDT.P (Perpetual) Open Interest verisi çeker"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        params = {"symbol": "BTCUSDT"}
        response = requests.get(BINANCE_OI_URL, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        oi = float(data['openInterest'])
        print(f"✓ Open Interest: {oi:,.2f} BTC", flush=True)
        return oi
    except Exception as e:
        print(f"✗ Open Interest hatası: {e}", flush=True)
        return None

def get_marketcap():
    """CoinPaprika'dan Bitcoin market cap verisi çeker"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(COINPAPRIKA_URL, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        marketcap = float(data['quotes']['USD']['market_cap'])
        btc_price = float(data['quotes']['USD']['price'])
        
        print(f"✓ BTC Fiyat: ${btc_price:,.2f}", flush=True)
        print(f"✓ Market Cap: ${marketcap:,.0f}", flush=True)
        return marketcap
    except Exception as e:
        print(f"✗ Market Cap hatası: {e}", flush=True)
        return None

def generate_signal(current_ratio):
    """Önceki oran ile karşılaştırıp sinyal üretir"""
    global previous_ratio
    
    if previous_ratio is None:
        previous_ratio = current_ratio
        print("⏳ İlk oran kaydedildi, bir sonraki döngüde sinyal gelecek...", flush=True)
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
    
    print(f"\n{'='*50}", flush=True)
    print(f"📊 SİNYAL: {signal}", flush=True)
    print(f"📈 Oran Değişimi: {change:+.4f}%", flush=True)
    print(f"📉 Önceki Oran: {previous_ratio:.6f}", flush=True)
    print(f"📊 Şimdiki Oran: {current_ratio:.6f}", flush=True)
    print(f"{'='*50}\n", flush=True)
    
    previous_ratio = current_ratio
    return signal

def main():
    """Ana döngü - 30 saniyede bir çalışır"""
    print("🚀 Bitcoin Signal Bot Başlatıldı!", flush=True)
    print(f"📡 Binance Futures (OI) + CoinPaprika (Market Cap)", flush=True)
    print(f"⏰ Her 5 dakikada bir kontrol edilecek...\n", flush=True)
    
    while True:
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n⏰ Zaman: {timestamp}", flush=True)
            print("-" * 50, flush=True)
            
            # Verileri çek
            oi = get_open_interest()
            marketcap = get_marketcap()
            
            # Hata durumunda 1 dakika bekle
            if not (oi and marketcap):
                print("⚠️ Veri alınamadı, 1 dakika sonra tekrar denenecek...", flush=True)
                time.sleep(60)
                continue
            
            # Oranı hesapla (Open Interest / Market Cap)
            # OI BTC cinsinden, MarketCap USD cinsinden - normalize edelim
            ratio = (oi * 1e8) / marketcap  # Daha okunabilir sayılar için
            print(f"📊 OI/MarketCap Oranı: {ratio:.6f}", flush=True)
            
            # Sinyal üret
            generate_signal(ratio)
            
            # 5 dakika bekle (300 saniye)
            print(f"💤 Bir sonraki kontrol 5 dakika sonra...\n", flush=True)
            time.sleep(300)
            
        except KeyboardInterrupt:
            print("\n\n👋 Bot durduruldu.", flush=True)
            break
        except Exception as e:
            print(f"❌ Beklenmeyen hata: {e}", flush=True)
            time.sleep(60)  # Hata durumunda 1 dakika bekle

if __name__ == "__main__":
    main()
