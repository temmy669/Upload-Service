
# Image Processing API (Django + Celery + MinIO)

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

All images are stored in S3 buckets, and a callback endpoint for accessing processed images.

---

##  Features

### Image Upload

Users upload an image via `/upload/`. The API immediately stores the original file in MinIO and triggers an asynchronous processing task.

### Asynchronous Image Processing

Celery handles:

* resizing
* compression
* thumbnail generation

Processing runs in the background so uploads stay fast.

### Secure S3 File Storage (MinIO)

Uploaded and processed files are stored using MinIO with:

* clean folder structure:

  ```
  uploads/originals/
  uploads/resized/
  uploads/compressed/
  uploads/thumbnails/
  ```

### Status Tracking

Each upload is stored in the database with a state machine:

* `pending`
* `processing`
* `completed`
* `failed`

Clients can poll `/upload/<id>/results/` to get latest results.

### Works for Local Dev & Railway Deployment

Supports:

* Local MinIO instance via Docker Compose
* Railway-provided MinIO object storage in production
* Dynamic S3_BASE_URL switching

---

## Project Structure

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

##  How It Works

### 1️ Upload Endpoint

Client uploads an image → original file saved to S3 → Celery task started.

**Example Response**

```json
{
  "id": "f1540e82-224f-482f-8f46-a7877670fedc",
  "status": "pending",
}
```

---

### 2️ Background Processing

Celery loads the original file → performs:

* resize
* compress
* thumbnail

Then uploads each processed version back to S3.

---

### 3️ Result Endpoint

Client hits:

```
GET /uploads/<id>/result
```
```json
{
  "id": "f1540e82-224f-482f-8f46-a7877670fedc",
  "original": "https://<presigned-url>",
  "resized": "https://<presigned-url>",
  "compressed": "https://<presigned-url>",
  "thumbnail": "https://<presigned-url>"
}
```

----

## Key Components

###  Django Model (`Upload`)

Stores image URLs and processing status.

###  Celery Task (`process_image`)

Responsible for resizing, compressing, and thumbnail generation using Pillow.

### Storage Utility (`storage.py`)

Handles:

* uploading files to S3 (MinIO)
* generating presigned URLs
* initializing boto3 client


---

## Docker Setup (Local Development)

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


---

##  Deployment on Railway

Production environment uses:

* Railway Django container
* Railway Redis
* Railway MinIO object storage

The Celery worker is deployed as a separate service from the main Django application, though it resides in the same repository. This separation ensures that background task processing (e.g., image uploads and processing) does not block or slow down the web server. It also allows independent scaling of the worker based on task load.

Environment variables required:

```
S3_ENDPOINT_URL="<s3-base-url>/uploads"
S3_ACCESS_KEY=<railway-minio-access-key>
S3_SECRET_KEY=<railway-minio-secret>
S3_BUCKET_NAME=uploads
S3_BASE_URL="<s3-base-url>"
```

Recommended:

```
DEBUG=False
```

---


## Testing the API

## Using Curl

### 1. Upload an Image

```bash
curl https://lucid-fulfillment-production.up.railway.app/uploads/ \
  -F "file=@/path/to/image.jpg"
```

### 2. Poll the Status

```bash
curl https://lucid-fulfillment-production.up.railway.app/uploads/<id>/status
```

### 3. Poll the Results

```bash
curl https://lucid-fulfillment-production.up.railway.app/uploads/<id>/results
``` 

When `status = completed`, URLs will begin working.

## Testing via Postman

same testing process only diffence is UI and the option to select a file directly to upload without directly using curl

## Test /upload/ (POST)

Open Postman → New Request → POST

```
   https://lucid-fulfillment-production.up.railway.app/upload/ ```
```

Under Body → select form-data

Key: file → Type: File → select an image from your computer

Click Send

Response should look like:

``` bash
{
  "id": "3f7d1b9e-4c5b-4f0f-bd2d-9e4c4f6d9a11",
  "status": "pending"
}
```

## Test /upload/{id}/status/ (GET)

New Request → GET

URL:
``` bash
https://lucid-fulfillment-production.up.railway.app/upload/<id>/status/
```

Replace `id` with the id returned from /upload/.

Click Send

Response should look like:

``` bash
    {
  "id": "3f7d1b9e-4c5b-4f0f-bd2d-9e4c4f6d9a11",
  "status": "completed" #if the upload and processing was successful
}

```

## Test /upload/{id}/result/ (GET)

New Request → GET

URL:
``` bash
https://lucid-fulfillment-production.up.railway.app/upload/<id>/result/
```


Click Send

Response should look like:

``` bash
{
    "id": "3f7d1b9e-4c5b-4f0f-bd2d-9e4c4f6d9a11",
    "original": "https://<bucket-url>/uploads/originals/abcd1234.jpg",
    "resized": "https://<bucket-url>/uploads/resized/abcd1234.jpg",
    "compressed": "https://<bucket-url>/uploads/compressed/abcd1234.jpg",
    "thumbnail": "https://<bucket-url>/uploads/thumbnail/abcd1234.jpg"
}
```



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

##  Known Challenges Solved

✔ Issue: Images were unreadable (0 bytes)
→ Fix: Reset `BytesIO` pointer using `.seek(0)` before uploading.

✔ Issue: MinIO public URLs not working in production
→ Fix: Use Railway MinIO endpoint as `S3_BASE_URL`.

---

## Future Improvements

* Webhook callback instead of polling
* Support for PNG / GIF / WEBP output
* Multiple file uploads
* Image moderation (NSFW detection)
* Queue monitoring dashboard

---

## Author

**Favour Adebose**
Backend Developer — Django • Celery • DevOps • Cloud
GitHub: [https://github.com/temmy669](https://github.com/temmy669)
