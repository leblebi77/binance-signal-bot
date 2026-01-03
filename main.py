import requests
import time
import sys
from datetime import datetime

# Python output buffering'i kapat
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

# API Endpoints
COINGLASS_OI_URL = "https://open-api.coinglass.com/public/v2/open_interest"
COINPAPRIKA_PRICE_URL = "https://api.coinpaprika.com/v1/tickers/btc-bitcoin"  # Alternatif, güvenilir API

previous_ratio = None

def get_open_interest():
    """CoinGlass'tan Bitcoin Open Interest verisi çeker"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'accept': 'application/json'
        }
        # CoinGlass API - Bitcoin OI
        params = {
            "symbol": "BTC",
            "interval": "0"  # Anlık veri
        }
        response = requests.get(COINGLASS_OI_URL, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if data.get('success') and data.get('data'):
            # Total OI (USD cinsinden)
            oi_usd = float(data['data'][0]['openInterest'])
            print(f"✓ Open Interest: ${oi_usd:,.0f}", flush=True)
            return oi_usd
        else:
            print(f"✗ Open Interest verisi alınamadı", flush=True)
            return None
    except Exception as e:
        print(f"✗ Open Interest hatası: {e}", flush=True)
        return None

def get_marketcap():
    """CoinPaprika'dan Bitcoin market cap verisi çeker (güvenilir, ücretsiz)"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(COINPAPRIKA_PRICE_URL, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        # CoinPaprika direkt market cap veriyor
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
    print("🚀 Binance Signal Bot Başlatıldı!", flush=True)
    print(f"📡 CoinGlass (OI) + CoinPaprika (Market Cap)", flush=True)
    print(f"⏰ Her 30 saniyede bir kontrol edilecek...\n", flush=True)
    
    while True:
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n⏰ Zaman: {timestamp}", flush=True)
            print("-" * 50, flush=True)
            
            # Verileri çek
            oi = get_open_interest()
            marketcap = get_marketcap()
            
            # Hata durumunda biraz bekle
            if not (oi and marketcap):
                print("⚠️ Veri alınamadı, 10 saniye sonra tekrar denenecek...", flush=True)
                time.sleep(10)
                continue
            
            # Oranı hesapla (OI / MarketCap)
            ratio = oi / marketcap
            print(f"📊 OI/MarketCap Oranı: {ratio:.8f}", flush=True)
            
            # Sinyal üret
            generate_signal(ratio)
            
            # 30 saniye bekle
            print(f"💤 Bir sonraki kontrol 30 saniye sonra...\n", flush=True)
            time.sleep(30)
            
        except KeyboardInterrupt:
            print("\n\n👋 Bot durduruldu.", flush=True)
            break
        except Exception as e:
            print(f"❌ Beklenmeyen hata: {e}", flush=True)
            time.sleep(30)

if __name__ == "__main__":
    main()
