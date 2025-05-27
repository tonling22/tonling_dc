# 使用 Python 3.10 或以上
FROM python:3.10-slim

# 安裝系統相依套件與 Chrome、ChromeDriver
RUN apt-get update && apt-get install -y \
    wget gnupg unzip curl fonts-liberation libappindicator3-1 libasound2 libatk-bridge2.0-0 \
    libatk1.0-0 libcups2 libdbus-1-3 libgdk-pixbuf2.0-0 libnspr4 libnss3 libx11-xcb1 libxcomposite1 \
    libxdamage1 libxrandr2 xdg-utils libu2f-udev libvulkan1 \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update && apt-get install -y google-chrome-stable \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 安裝 Python 套件
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# 加入你的應用程式
COPY . /app
WORKDIR /app

# 預設啟動指令（視你的 app.py 而定）
CMD ["python", "linebot_app.py"]
