import Adafruit_DHT  
DHT11=Adafruit_DHT.DHT11  # Adafruit_DHT.DHT22 for DHT22 sensor.
while True:  
    try:  
        temp,humid=Adafruit_DHT.read_retry(DHT11,4) # 4 is ithe GPIO number you can change this to your required need  
        print("TEMP={0:0.1f}°C HUMIDITY={1:0.1f}%".format(temp,humid))
    except KeyboardInterrupt:  
        break  