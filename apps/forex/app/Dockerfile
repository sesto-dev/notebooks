FROM python:3.12

WORKDIR /app

# Copy requirements.txt from the app directory
COPY apps/forex/app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the sesto folder
COPY sesto /app/sesto

# Copy the app directory contents
COPY apps/forex/app .

# Create log file and set permissions
RUN touch /var/log/app.log && chmod 666 /var/log/app.log

CMD ["python", "main.py"]