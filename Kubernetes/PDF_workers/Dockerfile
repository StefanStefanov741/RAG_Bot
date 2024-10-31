FROM python:3.9-slim

WORKDIR /app
COPY Kubernetes/PDF_workers/pdf_worker.py /app
COPY Preprocessing /app/Preprocessing

RUN pip install flask  pika pdfminer.six unstructured unstructured-ingest[remote]

EXPOSE 5001
CMD ["python", "pdf_worker.py"]
