
FROM python:3.9-slim as builder

RUN pip install uv

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


CMD ["python", "main.py"]
