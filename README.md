[![Español](https://img.shields.io/badge/Read-in%20Spanish-red?style=for-the-badge)](./README-ESP.md)
# Content Batching Engine

**Turn one video into a complete omnichannel content campaign in minutes.**

Content Batching Engine is an AI-powered automation system that transforms a single short video into ready-to-publish content across multiple platforms. Upload a video to Google Drive, and the system automatically generates: one Twitter thread, one LinkedIn post, and three Reels scripts—all optimized for each platform's unique format and audience.

The entire workflow happens automatically. Clients receive a Telegram message with the generated content and a simple "Approve" button. When approved, the content is ready for scheduling. No more manual repurposing, no more switching between platforms, no more wasted time.

This is the ultimate tool for content agencies, creators, and businesses that need to maintain a consistent presence across all major social platforms without the manual effort.

---

## Tech Stack

- **API Framework**: FastAPI (Python)
- **Task Queue**: Celery with Redis broker
- **Database**: PostgreSQL with SQLAlchemy async
- **AI Services**: 
  - OpenAI Whisper (audio transcription)
  - Google Gemini 1.5 Flash (content generation)
- **Cloud Storage**: Google Drive API
- **Messaging**: Telegram Bot API
- **Media Processing**: FFmpeg
- **Containerization**: Docker & Docker Compose

---

## The Why

Content creators and agencies face a fundamental problem: creating quality content for multiple platforms is incredibly time-consuming. A single video could become a Twitter thread, a LinkedIn post, and multiple Reels—but manually repurposing content takes hours of work.

This inefficiency creates a bottleneck:

- **Time wasted**: Repurposing one video manually takes 1-2 hours minimum
- **Inconsistency**: Many creators end up focusing on only one or two platforms
- **Scalability limits**: Agencies can't take on more clients because content creation doesn't scale
- **Client delays**: Manual approval processes add more friction

The Content Batching Engine solves this by automating the entire repurposing workflow. The system takes a video, transcribes it, and uses AI to generate platform-specific content that actually works—not generic filler, but optimized posts that match each platform's best practices.

**Why it's efficient:**

1. **Zero manual transcription**: Whisper handles audio-to-text with high accuracy
2. **Intelligent generation**: Gemini creates platform-specific content that sounds natural, not AI-generated
3. **Built-in approval workflow**: Clients approve via Telegram—no email back-and-forth, no dashboard login required
4. **Automatic retry logic**: Failed jobs are automatically retried with exponential backoff
5. **Complete audit trail**: Every job's status, transcription, and generated content is stored in PostgreSQL

The result: what used to take hours now takes minutes, and the system scales effortlessly with your client base.

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              CONTENT BATCHING ENGINE                                 │
└─────────────────────────────────────────────────────────────────────────────────────┘

                                    ┌──────────────────┐
                                    │   GOOGLE DRIVE   │
                                    │  (Video Upload)  │
                                    └────────┬─────────┘
                                             │
                                             │ 1. Download video
                                             ▼
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                                    WORKER                                            │
│  ┌─────────────┐    ┌──────────────┐    ┌──────────────┐    ┌────────────────────┐   │
│  │   PENDING   │───▶│  PROCESSING  │───▶│  COMPLETED   │───▶│  APPROVED/REJECTED │   │
│  └─────────────┘    └──────────────┘    └──────────────┘    └────────────────────┘   │
│        │                  │                   │                      │               │
│        ▼                  ▼                   ▼                      ▼               │
│  ┌──────────┐      ┌────────────┐      ┌──────────────┐       ┌───────────────┐      │
│  │  Celery  │      │   FFmpeg   │      │   Database   │       │    Telegram   │      │
│  │   Queue  │      │  (Audio)   │      │  (PostgreSQL)│       │    (Notify)   │      │
│  └──────────┘      └────────────┘      └──────────────┘       └───────────────┘      │
│        │                  │                   │                      │               │
│        │                  │                   │                      │               │
│        ▼                  ▼                   ▼                      ▼               │
│  ┌──────────┐      ┌────────────┐      ┌──────────────┐       ┌───────────────┐      │
│  │  Redis   │      │  Whisper   │      │  JSON Store  │       │  Approval     │      │
│  │ (Broker) │      │ (Transcript)│     │  (Content)   │       │  Buttons      │      │
│  └──────────┘      └────────────┘      └──────────────┘       └───────────────┘      │
│                           │                                     │                    │
│                           │ 2. Extract audio                    │                    │
│                           ▼                                     │                    │
│                    ┌────────────┐                               │                    │
│                    │   OpenAI   │                               │                    │
│                    │  Whisper-1 │                               │                    │
│                    └────────────┘                               │                    │
│                           │ 3. Transcription                    │                    │
│                           ▼                                     │                    │
│                    ┌────────────┐         5. Save to DB         │                    │
│                    │   Gemini   │───────────────────────────────┤                    │
│                    │  1.5 Flash │                               │                    │
│                    └────────────┘         6. Send to Telegram   │                    │
│                           │                                     │                    │
│                           │ 4. Generate content                 │                    │
│                           ▼                                     │                    │
│                    ┌─────────────────────────────────────────┐  │                    │
│                    │           OUTPUT CONTENT                │  │                    │
│                    │  ┌────────────────────────────────────┐ │  │                    │
│                    │  │ 🐦 Twitter Thread (3 tweets)       │ │  │                    │
│                    │  │ 💼 LinkedIn Post                   │ │  │                    │
│                    │  │ 🎬 Reels Scripts (3 x 30-60s)      │ │  │                    │
│                    │  └────────────────────────────────────┘ │                       │
│                    └─────────────────────────────────────────┘                       │
└──────────────────────────────────────────────────────────────────────────────────────┘
                                              │
                                              │ 7. Client clicks Approve
                                              ▼
                                    ┌──────────────────┐
                                    │   READY FOR      │
                                    │   SCHEDULING     │
                                    └──────────────────┘
```

**Step-by-Step Flow:**

1. **Video Upload**: Client uploads a video to a configured Google Drive folder
2. **Job Creation**: API receives the Drive file ID, creates a job in PostgreSQL with status `PENDING`
3. **Queue Processing**: Celery picks up the job from Redis, status changes to `PROCESSING`
4. **Download**: Worker downloads the video from Google Drive to temp storage
5. **Audio Extraction**: FFmpeg extracts audio from the video
6. **Transcription**: OpenAI Whisper transcribes the audio to text
7. **Content Generation**: Gemini receives the transcription and generates:
   - 3-tweet Twitter thread
   - LinkedIn post
   - 3 Reels scripts with duration estimates
8. **Database Save**: All content (transcription + generated) saved to PostgreSQL
9. **Telegram Notification**: Client receives formatted message with preview and Approve/Reject buttons
10. **Approval**: Client clicks "Approve" via Telegram, status changes to `APPROVED`, content is ready for scheduling

---

## Setup & Installation

### Prerequisites

- Docker & Docker Compose
- FFmpeg (installed on the host for audio extraction)
- API keys for:
  - Google Cloud (service account with Drive access)
  - OpenAI (for Whisper)
  - Google AI Studio (for Gemini)
  - Telegram Bot

### Environment Configuration

Copy the example environment file and configure your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your values:

```env
# Database
POSTGRES_PASSWORD=your_secure_password_here

# Redis
REDIS_URL=redis://redis:6379/0

# Google Drive
# Create a service account in Google Cloud Console:
# 1. Go to IAM & Admin > Service Accounts
# 2. Create a service account with "Drive API" scope
# 3. Generate a JSON key
# 4. Copy the entire JSON content here (single quotes required)
GOOGLE_DRIVE_CREDENTIALS_JSON='{"type":"service_account","project_id":...}'
# Share your input folder with the service account email
GOOGLE_DRIVE_FOLDER_ID=your_folder_id_from_url

# OpenAI (for Whisper transcription)
OPENAI_API_KEY=sk-...

# Gemini (for content generation)
# Get your API key from: https://aistudio.google.com/app/apikey
GEMINI_API_KEY=...

# Telegram
# 1. Create a bot via @BotFather on Telegram
# 2. Get your chat ID via @userinfobot
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_ADMIN_CHAT_ID=your_numeric_chat_id

# App Settings
APP_HOST=0.0.0.0
APP_PORT=8000

# Celery Timeouts (in seconds)
CELERY_TASK_SOFT_TIME_LIMIT=300
CELERY_TASK_TIME_LIMIT=360
```

### Google Drive Setup

1. **Create a Google Cloud Project**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project

2. **Enable APIs**:
   - Enable Google Drive API
   - Enable Google Sheets API (optional)

3. **Create Service Account**:
   - Go to IAM & Admin > Service Accounts
   - Create a service account
   - Download the JSON key file

4. **Share Folder**:
   - Create a folder in Google Drive for input videos
   - Share the folder with the service account email (found in the JSON key)
   - Copy the folder ID from the URL (the long string after `/folders/`)

### Telegram Setup

1. **Create a Bot**:
   - Open Telegram and search for @BotFather
   - Send `/newbot` and follow instructions
   - Copy the bot token

2. **Get Your Chat ID**:
   - Search for @userinfobot
   - Send `/start`
   - Copy your numeric chat ID

3. **Configure Webhook**:
   - After starting the containers, set up the webhook:
   ```bash
   curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
     -d "url=https://your-domain.com/api/v1/telegram/webhook"
   ```
   - For local development, use a tool like ngrok to expose your localhost

---

## Deployment

### Quick Start (Development)

```bash
# Build and start all services
docker-compose up -d

# Check logs
docker-compose logs -f

# The API will be available at http://localhost:8000
# API docs: http://localhost:8000/docs
```

### Production Deployment

1. **Configure environment**:
   - Update `POSTGRES_PASSWORD` with a strong password
   - Set `APP_HOST=0.0.0.0` or your production domain
   - Configure proper `REDIS_URL` if using external Redis

2. **Set up a production webhook**:
   ```bash
   curl -X POST "https://api.telegram.org/bot<TOKEN>/setWebhook" \
     -d "url=https://your-production-domain.com/api/v1/telegram/webhook"
   ```

3. **Use a reverse proxy** (nginx, Traefik, etc.) for SSL termination

4. **Database migrations**:
   The database tables are created automatically on startup via SQLAlchemy's `create_all`.

---

## API Usage

### Create a New Job

```bash
curl -X POST "http://localhost:8000/api/v1/jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "drive_file_id": "1abc123def456ghi789jkl",
    "telegram_chat_id": 123456789
  }'
```

Response:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "drive_file_id": "1abc123def456ghi789jkl",
  "status": "PENDING",
  "transcription": null,
  "generated_content": null,
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Get Job Status

```bash
curl "http://localhost:8000/api/v1/jobs/550e8400-e29b-41d4-a716-446655440000"
```

### List All Jobs

```bash
curl "http://localhost:8000/api/v1/jobs?limit=20&status_filter=PENDING"
```

### Retry a Failed Job

```bash
curl -X POST "http://localhost:8000/api/v1/jobs/550e8400-e29b-41d4-a716-446655440000/retry"
```

---

## System Requirements

### Hardware

- **Minimum**: 2 CPU cores, 4GB RAM
- **Recommended**: 4+ CPU cores, 8GB RAM
- **Storage**: At least 5GB for temporary video files (cleaned up automatically)

### Software

- Docker 20.10+
- Docker Compose 2.0+
- FFmpeg (automatically installed in containers)

### Network

- Outbound HTTPS to:
  - `api.openai.com` (Whisper)
  - `generativelanguage.googleapis.com` (Gemini)
  - `api.telegram.org` (Bot API)
  - `googleapis.com` (Drive API)

---

## Project Structure

```
content-batching-engine/
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── content.py      # Job management endpoints
│   │       └── telegram.py     # Telegram webhook handler
│   ├── models/
│   │   └── content.py         # SQLAlchemy models
│   ├── schemas/
│   │   └── content.py         # Pydantic schemas
│   ├── services/
│   │   ├── ai/
│   │   │   ├── gemini.py      # Content generation
│   │   │   └── whisper.py     # Audio transcription
│   │   ├── drive.py           # Google Drive integration
│   │   ├── media.py           # FFmpeg audio extraction
│   │   └── telegram.py       # Telegram notifications
│   ├── config.py              # Settings management
│   ├── database.py            # Database connection
│   └── main.py                # FastAPI app
├── workers/
│   ├── celery_app.py         # Celery configuration
│   └── tasks.py              # Background job tasks
├── alembic/                   # Database migrations
├── docker-compose.yml         # Container orchestration
├── Dockerfile.api             # API image
├── Dockerfile.worker          # Worker image
└── requirements.txt          # Python dependencies
```

---

## Troubleshooting

### Job fails with "Audio file too large"

The audio file exceeds 25MB (Whisper limit). Solution: Use a shorter video or split it into smaller clips.

### Telegram webhook not receiving updates

- Verify the webhook is set: `https://api.telegram.org/bot<TOKEN>/getWebhookInfo`
- Ensure your server is accessible (use ngrok for local development)
- Check logs: `docker-compose logs worker`

### Google Drive download fails

- Verify the service account has access to the file/folder
- Check the `GOOGLE_DRIVE_CREDENTIALS_JSON` format (must be valid JSON with single quotes around the entire string in .env)

### Transcription is empty or poor quality

- Ensure the video has clear audio
- Consider adjusting the language parameter in `whisper.py` (currently set to Spanish)

---

## License

MIT License - See LICENSE file for details.
