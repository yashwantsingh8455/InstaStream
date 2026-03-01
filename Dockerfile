FROM python:3.11-slim

# Step 1: Install Chrome and dependencies
RUN apt-get update && apt-get install -y \
    wget gnupg unzip curl \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/local/sources.list.d/google-chrome.list' \
    && apt-get update && apt-get install -y google-chrome-stable

# Step 2: Copy your code
WORKDIR /app
COPY . /app

# Step 3: Install python libraries
RUN pip install --no-cache-dir -r requirements.txt

# Step 4: Run script
CMD ["python", "insta.py"]