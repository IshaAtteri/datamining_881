FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y unzip && rm -rf /var/lib/apt/lists/*

COPY requirements-serving.txt .
RUN pip install --no-cache-dir -r requirements-serving.txt

COPY . .

# Extract .npy from split zip parts
RUN cat xplot_embeddings_full_data.zip.001 xplot_embeddings_full_data.zip.002 \
    > xplot_embeddings_full_data.zip \
    && unzip -o xplot_embeddings_full_data.zip \
    && rm xplot_embeddings_full_data.zip

EXPOSE 8000
CMD ["uvicorn", "model_server:app", "--host", "0.0.0.0", "--port", "8000"]
