
# 🖼️ Image Processing API (Django + Celery + MinIO + Railway)

A scalable asynchronous **image processing service** built with:

* **Django REST Framework** (API backend)
* **Celery** (async task processing)
* **Redis** (Celery message broker)
* **MinIO (S3-compatible storage)** (secure media storage)
* **Railway** (deployment platform)

This API allows clients to upload an image and automatically generates:

* **Original file** (stored immediately)
* **Resized image** (1024×1024)
* **Compressed image** (JPEG 60% quality)
* **Thumbnail** (300×300)

All images are stored in S3 buckets, and a callback endpoint provides **secure presigned URLs** for accessing processed images.

---

## 🚀 Features

### ✔ Image Upload

Users upload an image via `/upload/`. The API immediately stores the original file in MinIO and triggers an asynchronous processing task.

### ✔ Asynchronous Image Processing

Celery handles:

* resizing
* compression
* thumbnail generation

Processing runs in the background so uploads stay fast.

### ✔ Secure S3 File Storage (MinIO)

Uploaded and processed files are stored using MinIO with:

* private ACL
* presigned URLs for access
* clean folder structure:

  ```
  uploads/originals/
  uploads/resized/
  uploads/compressed/
  uploads/thumbnails/
  ```

### ✔ Status Tracking

Each upload is stored in the database with a state machine:

* `pending`
* `processing`
* `completed`
* `failed`

Clients can poll `/upload/<id>/` to get latest results.

### ✔ Works for Local Dev & Railway Deployment

Supports:

* Local MinIO instance via Docker Compose
* Railway-provided MinIO object storage in production
* Dynamic S3_BASE_URL switching

---

## 📂 Project Structure

```
project/
│── core/
│   └── settings.py
│
│── uploads/
│   ├── models.py
│   ├── serializers.py
│   ├── tasks.py
│   └── utils/
│       └── storage.py
│
│── Dockerfile
│── docker-compose.yml
│── requirements.txt
│── README.md
```

---

## ⚙️ How It Works

### 1️⃣ Upload Endpoint

Client uploads an image → original file saved to S3 → Celery task started.

**Example Response**

```json
{
  "id": "f1540e82-224f-482f-8f46-a7877670fedc",
  "status": "pending",
  "original": "https://<presigned-url>"
}
```

---

### 2️⃣ Background Processing

Celery loads the original file → performs:

* resize
* compress
* thumbnail

Then uploads each processed version back to S3.

---

### 3️⃣ Result Endpoint

Client hits:

```
GET /uploads/<id>/
```

API returns:

```json
{
  "id": "f1540e82-224f-482f-8f46-a7877670fedc",
  "status": "completed",
  "original": "https://<presigned-url>",
  "resized": "https://<presigned-url>",
  "compressed": "https://<presigned-url>",
  "thumbnail": "https://<presigned-url>"
}
```

All URLs are **temporary secure presigned URLs**, valid for 1 hour.

---

## 🔧 Key Components

### 🗂 Django Model (`Upload`)

Stores image URLs and processing status.

### 🛠 Celery Task (`process_image`)

Responsible for resizing, compressing, and thumbnail generation using Pillow.

### 📦 Storage Utility (`storage.py`)

Handles:

* uploading files to S3 (MinIO)
* generating presigned URLs
* initializing boto3 client

### 🎛 Serializer (`UploadSerializer`)

Generates presigned URLs on-demand.

---

## 🐳 Docker Setup (Local Development)

Local development uses MinIO + Redis via Docker Compose.

`docker-compose.yml`:

* `web` → Django + Gunicorn
* `celery` → Celery worker
* `redis` → message broker
* `minio` → S3-compatible storage

Run locally:

```
docker-compose up --build
```

MinIO console:

```
http://localhost:9001
```

---

## ☁️ Deployment on Railway

Production environment uses:

* Railway Django container
* Railway Redis
* Railway MinIO object storage

Environment variables required:

```
S3_ENDPOINT_URL=https://storage.railway.app
S3_ACCESS_KEY=<railway-minio-access-key>
S3_SECRET_KEY=<railway-minio-secret>
S3_BUCKET_NAME=uploads
S3_BASE_URL=https://storage.railway.app/uploads
```

Recommended:

```
DEBUG=False
```

---


## 🧪 Testing the API

### 1. Upload an Image

```bash
curl -X POST http://localhost:8000/uploads/ \
  -F "file=@/path/to/image.jpg"
```

### 2. Poll the Status

```bash
curl http://localhost:8000/uploads/<id>/
```

When `status = completed`, URLs will begin working.

---

## 🛠 Technologies Used

| Component        | Tool                  |
| ---------------- | --------------------- |
| Backend          | Django REST Framework |
| Async Worker     | Celery                |
| Message Broker   | Redis                 |
| Storage          | MinIO (S3)            |
| Image Processing | Pillow                |
| Deployment       | Railway               |
| Presigned URLs   | boto3                 |

---

## 🧩 Known Challenges Solved

✔ Issue: Images were unreadable (0 bytes)
→ Fix: Reset `BytesIO` pointer using `.seek(0)` before uploading.

✔ Issue: Processed files returned “AccessDenied”
→ Fix: Correct S3 key extraction + presigned URL generation.

✔ Issue: MinIO public URLs not working in production
→ Fix: Use Railway MinIO endpoint as `S3_BASE_URL`.

✔ Issue: File paths wrong for presigned URLs
→ Fix: Extract object keys from stored URLs.

---

## 📌 Future Improvements

* Webhook callback instead of polling
* Support for PNG / GIF / WEBP output
* Multiple file uploads
* Image moderation (NSFW detection)
* Queue monitoring dashboard

---

## 🙌 Author

**Favour Adebose**
Backend Developer — Django • Celery • DevOps • Cloud
GitHub: [https://github.com/temmy669](https://github.com/temmy669)
