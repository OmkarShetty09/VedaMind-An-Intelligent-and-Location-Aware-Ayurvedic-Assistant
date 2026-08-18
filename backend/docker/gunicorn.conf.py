import multiprocessing

bind = "0.0.0.0:8000"
workers = (multiprocessing.cpu_count() * 2) + 1
timeout = 90  # aligned with the RAG stream budget
graceful_timeout = 30
accesslog = "-"
errorlog = "-"
