FROM python:3.8.10

WORKDIR /app

# Copy requirements.txt from the app directory
COPY apps/crypto/app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the sesto folder
COPY sesto /app/sesto

# Copy the app directory contents
COPY apps/crypto/app .

# Create log file and set permissions
RUN touch /var/log/app.log && chmod 666 /var/log/app.log

CMD ["python", "main.py"]