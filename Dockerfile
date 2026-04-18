
FROM python:3.11-slim as builder

RUN pip install uv

# Configure UV for container environment
ENV UV_SYSTEM_PYTHON=1 UV_COMPILE_BYTECODE=1


WORKDIR /app


COPY requirements.txt .


RUN uv pip install -r requirements.txt


FROM gcr.io/distroless/python3-debian12

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11/site-packages /app/packages


COPY . .

ENV PYTHONPATH /app/packages


ENTRYPOINT ["python"]
CMD ["main.py"]
