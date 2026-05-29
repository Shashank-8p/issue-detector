# Layer 1: Start with a lightweight Linux image
FROM python:3.11-slim

# Layer 1.5: Force Python to stream logs instantly to the GitHub Actions console
ENV PYTHONUNBUFFERED=1

# Layer 2: Set the internal working directory
WORKDIR /app

# Layer 3: Copy the dependencies
COPY requirements.txt .

# Layer 4: Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Layer 5: Copy the production script ONLY (dummy JSON removed)
COPY main.py .

# Layer 6: Execute the script
CMD ["python", "main.py"]