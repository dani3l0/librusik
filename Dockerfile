FROM python:3.13-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# non-root user
RUN adduser -D librusik && \
    chown -R librusik:librusik /app

USER librusik

CMD ["python", "librusik.py", "--skip-wizard"]