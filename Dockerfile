FROM python:3.10-slim

WORKDIR /app

# Install only Python deps
COPY req.txt .
RUN pip install --no-cache-dir -r req.txt

COPY . .

RUN mkdir -p uploads output_logs sample_inputs


EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
