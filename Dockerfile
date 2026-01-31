
FROM python:3.9-slim as builder

RUN pip install uv

# Install psycopg2 system dependencies
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# Configure UV for container environment
ENV UV_SYSTEM_PYTHON=1 UV_COMPILE_BYTECODE=1


WORKDIR /app


COPY requirements.txt .


RUN uv pip install -r requirements.txt


FROM gcr.io/distroless/python3-debian11


WORKDIR /app


COPY --from=builder /usr/local/lib/python3.9/site-packages /app/packages


COPY . .

ENV PYTHONPATH /app/packages


CMD ["main.py"]
