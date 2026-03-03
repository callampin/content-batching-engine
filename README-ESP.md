[![English](https://img.shields.io/badge/Read-in%20English-blue?style=for-the-badge)](./README.md)
# Content Batching Engine

**Convierte un video en una campaña de contenido omnicanal completa en minutos.**

Content Batching Engine es un sistema de automatización impulsado por IA que transforma un solo video corto en contenido listo para publicar en múltiples plataformas. Sube un video a Google Drive y el sistema automáticamente genera: un hilo de Twitter, una publicación de LinkedIn y tres guiones para Reels, todos optimizados para el formato y audiencia únicos de cada plataforma.

Todo el flujo de trabajo ocurre automáticamente. Los clientes reciben un mensaje de Telegram con el contenido generado y un simple botón de "Aprobar". Cuando se aprueba, el contenido está listo para programar. No más reproducción manual, no más cambiar entre plataformas, no más tiempo desperdiciado.

Esta es la herramienta definitiva para agencias de contenido, creadores y empresas que necesitan mantener una presencia consistente en todas las principales plataformas sociales sin el esfuerzo manual.

---

## Stack Tecnológico

- **Framework de API**: FastAPI (Python)
- **Cola de Tareas**: Celery con broker Redis
- **Base de Datos**: PostgreSQL con SQLAlchemy async
- **Servicios de IA**: 
  - OpenAI Whisper (transcripción de audio)
  - Google Gemini 1.5 Flash (generación de contenido)
- **Almacenamiento en la Nube**: Google Drive API
- **Mensajería**: Telegram Bot API
- **Procesamiento de Medios**: FFmpeg
- **Contenedores**: Docker & Docker Compose

---

## El Porqué

Los creadores de contenido y las agencias enfrentan un problema fundamental: crear contenido de calidad para múltiples plataformas consume una cantidad increíble de tiempo. Un solo video podría convertirse en un hilo de Twitter, una publicación de LinkedIn y múltiples Reels, pero reproducir manualmente el contenido toma horas de trabajo.

Esta ineficiencia crea un cuello de botella:

- **Tiempo desperdiciado**: Reproducir un video manualmente toma un mínimo de 1-2 horas
- **Inconsistencia**: Muchos creadores terminan enfocándose solo en una o dos plataformas
- **Límites de escalabilidad**: Las agencias no pueden tomar más clientes porque la creación de contenido no escala
- **Retrasos con clientes**: Los procesos de aprobación manual agregan más fricción

El Content Batching Engine resuelve esto automatizando todo el flujo de trabajo de reproducción. El sistema toma un video, lo transcribe y usa IA para generar contenido específico para cada plataforma que realmente funciona, no relleno genérico, sino publicaciones optimizadas que coinciden con las mejores prácticas de cada plataforma.

**Por qué es eficiente:**

1. **Transcripción cero manual**: Whisper maneja audio a texto con alta precisión
2. **Generación inteligente**: Gemini crea contenido específico para cada plataforma que suena natural, no generado por IA
3. **Flujo de aprobación integrado**: Los clientes aprueban vía Telegram, no hay ida y vuelta de emails, no se requiere iniciar sesión en un panel
4. **Lógica de reintento automático**: Los trabajos fallidos se reintentan automáticamente con retroceso exponencial
5. **Registro de auditoría completo**: El estado de cada trabajo, la transcripción y el contenido generado se almacenan en PostgreSQL

El resultado: lo que solía tomar horas ahora toma minutos, y el sistema escala sin esfuerzo con tu base de clientes.

---

## Diagrama de Flujo de Datos

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              CONTENT BATCHING ENGINE                                 │
└─────────────────────────────────────────────────────────────────────────────────────┘

                                    ┌──────────────────┐
                                    │   GOOGLE DRIVE   │
                                    │  (Subir Video)   │
                                    └────────┬─────────┘
                                             │
                                             │ 1. Descargar video
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
│                           │ 2. Extraer audio                    │                    │
│                           ▼                                     │                    │
│                    ┌────────────┐                               │                    │
│                    │   OpenAI   │                               │                    │
│                    │  Whisper-1 │                               │                    │
│                    └────────────┘                               │                    │
│                           │ 3. Transcripción                    │                    │
│                           ▼                                     │                    │
│                    ┌────────────┐         5. Guardar en BD      │                    │
│                    │   Gemini   │───────────────────────────────┤                    │
│                    │  1.5 Flash │                               │                    │
│                    └────────────┘         6. Enviar a Telegram  │                    │
│                           │                                     │                    │
│                           │ 4. Generar contenido                │                    │
│                           ▼                                     │                    │
│                    ┌─────────────────────────────────────────┐  │                    │
│                    │           OUTPUT CONTENT                │  │                    │
│                    │  ┌────────────────────────────────────┐ │  │                    │
│                    │  │ 🐦 Hilo de Twitter (3 tweets)      │ │  │                    │
│                    │  │ 💼 Publicación de LinkedIn         │ │  │                    │
│                    │  │ 🎬 Guiones de Reels (3 x 30-60s)   │ │  │                    │
│                    │  └────────────────────────────────────┘ │                       │
│                    └─────────────────────────────────────────┘                       │
└──────────────────────────────────────────────────────────────────────────────────────┘
                                              │
                                              │ 7. Cliente hace clic en Aprobar
                                              ▼
                                    ┌──────────────────┐
                                    │   LISTO PARA     │
                                    │   PROGRAMAR      │
                                    └──────────────────┘
```

**Flujo Paso a Paso:**

1. **Subir Video**: El cliente sube un video a una carpeta de Google Drive configurada
2. **Creación de Trabajo**: La API recibe el ID del archivo de Drive, crea un trabajo en PostgreSQL con estado `PENDING`
3. **Procesamiento de Cola**: Celery selecciona el trabajo de Redis, el estado cambia a `PROCESSING`
4. **Descarga**: El worker descarga el video de Google Drive al almacenamiento temporal
5. **Extracción de Audio**: FFmpeg extrae el audio del video
6. **Transcripción**: OpenAI Whisper transcribe el audio a texto
7. **Generación de Contenido**: Gemini recibe la transcripción y genera:
   - Hilo de Twitter de 3 tweets
   - Publicación de LinkedIn
   - 3 guiones de Reels con estimaciones de duración
8. **Guardar en Base de Datos**: Todo el contenido (transcripción + generado) se guarda en PostgreSQL
9. **Notificación de Telegram**: El cliente recibe un mensaje formateado con vista previa y botones de Aprobar/Rechazar
10. **Aprobación**: El cliente hace clic en "Aprobar" vía Telegram, el estado cambia a `APPROVED`, el contenido está listo para programar

---

## Configuración e Instalación

### Prerrequisitos

- Docker & Docker Compose
- FFmpeg (instalado en el host para extracción de audio)
- Claves API para:
  - Google Cloud (cuenta de servicio con acceso a Drive)
  - OpenAI (para Whisper)
  - Google AI Studio (para Gemini)
  - Telegram Bot

### Configuración del Entorno

Copia el archivo de entorno de ejemplo y configura tus credenciales:

```bash
cp .env.example .env
```

Edita `.env` con tus valores:

```env
# Base de Datos
POSTGRES_PASSWORD=tu_contraseña_segura_aquí

# Redis
REDIS_URL=redis://redis:6379/0

# Google Drive
# Crea una cuenta de servicio en Google Cloud Console:
# 1. Ve a IAM & Admin > Cuentas de Servicio
# 2. Crea una cuenta de servicio con el alcance "Drive API"
# 3. Genera una clave JSON
# 4. Copia todo el contenido JSON aquí (se requieren comillas simples)
GOOGLE_DRIVE_CREDENTIALS_JSON='{"type":"service_account","project_id":...}'
# Comparte tu carpeta de entrada con el email de la cuenta de servicio
GOOGLE_DRIVE_FOLDER_ID=tu_folder_id_desde_la_url

# OpenAI (para transcripción Whisper)
OPENAI_API_KEY=sk-...

# Gemini (para generación de contenido)
# Obtén tu clave API de: https://aistudio.google.com/app/apikey
GEMINI_API_KEY=...

# Telegram
# 1. Crea un bot vía @BotFather en Telegram
# 2. Obtén tu chat ID vía @userinfobot
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_ADMIN_CHAT_ID=tu_chat_id_numérico

# Configuración de la App
APP_HOST=0.0.0.0
APP_PORT=8000

# Tiempos de Celery (en segundos)
CELERY_TASK_SOFT_TIME_LIMIT=300
CELERY_TASK_TIME_LIMIT=360
```

### Configuración de Google Drive

1. **Crear un Proyecto de Google Cloud**:
   - Ve a [Google Cloud Console](https://console.cloud.google.com/)
   - Crea un nuevo proyecto

2. **Habilitar APIs**:
   - Habilita Google Drive API
   - Habilita Google Sheets API (opcional)

3. **Crear Cuenta de Servicio**:
   - Ve a IAM & Admin > Cuentas de Servicio
   - Crea una cuenta de servicio
   - Descarga el archivo de clave JSON

4. **Compartir Carpeta**:
   - Crea una carpeta en Google Drive para videos de entrada
   - Comparte la carpeta con el email de la cuenta de servicio (encontrado en la clave JSON)
   - Copia el ID de la carpeta de la URL (la cadena larga después de `/folders/`)

### Configuración de Telegram

1. **Crear un Bot**:
   - Abre Telegram y busca @BotFather
   - Envía `/newbot` y sigue las instrucciones
   - Copia el token del bot

2. **Obtener Tu Chat ID**:
   - Busca @userinfobot
   - Envía `/start`
   - Copia tu chat ID numérico

3. **Configurar Webhook**:
   - Después de iniciar los contenedores, configura el webhook:
   ```bash
   curl -X POST "https://api.telegram.org/bot<TU_BOT_TOKEN>/setWebhook" \
     -d "url=https://tu-dominio.com/api/v1/telegram/webhook"
   ```
   - Para desarrollo local, usa una herramienta como ngrok para exponer tu localhost

---

## Despliegue

### Inicio Rápido (Desarrollo)

```bash
# Construir e iniciar todos los servicios
docker-compose up -d

# Ver registros
docker-compose logs -f

# La API estará disponible en http://localhost:8000
# Documentación de la API: http://localhost:8000/docs
```

### Despliegue en Producción

1. **Configurar entorno**:
   - Actualiza `POSTGRES_PASSWORD` con una contraseña segura
   - Configura `APP_HOST=0.0.0.0` o tu dominio de producción
   - Configura `REDIS_URL` apropiado si usas Redis externo

2. **Configurar un webhook de producción**:
   ```bash
   curl -X POST "https://api.telegram.org/bot<TOKEN>/setWebhook" \
     -d "url=https://tu-dominio-de-produccion.com/api/v1/telegram/webhook"
   ```

3. **Usa un proxy reverso** (nginx, Traefik, etc.) para terminación SSL

4. **Migraciones de base de datos**:
   Las tablas de la base de datos se crean automáticamente al inicio mediante `create_all` de SQLAlchemy.

---

## Uso de la API

### Crear un Nuevo Trabajo

```bash
curl -X POST "http://localhost:8000/api/v1/jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "drive_file_id": "1abc123def456ghi789jkl",
    "telegram_chat_id": 123456789
  }'
```

Respuesta:
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

### Obtener Estado del Trabajo

```bash
curl "http://localhost:8000/api/v1/jobs/550e8400-e29b-41d4-a716-446655440000"
```

### Listar Todos los Trabajos

```bash
curl "http://localhost:8000/api/v1/jobs?limit=20&status_filter=PENDING"
```

### Reintentar un Trabajo Fallido

```bash
curl -X POST "http://localhost:8000/api/v1/jobs/550e8400-e29b-41d4-a716-446655440000/retry"
```

---

## Requisitos del Sistema

### Hardware

- **Mínimo**: 2 núcleos de CPU, 4GB de RAM
- **Recomendado**: 4+ núcleos de CPU, 8GB de RAM
- **Almacenamiento**: Al menos 5GB para archivos de video temporales (se limpian automáticamente)

### Software

- Docker 20.10+
- Docker Compose 2.0+
- FFmpeg (instalado automáticamente en los contenedores)

### Red

- Salida HTTPS a:
  - `api.openai.com` (Whisper)
  - `generativelanguage.googleapis.com` (Gemini)
  - `api.telegram.org` (Bot API)
  - `googleapis.com` (Drive API)

---

## Estructura del Proyecto

```
content-batching-engine/
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── content.py      # Endpoints de gestión de trabajos
│   │       └── telegram.py     # Handler del webhook de Telegram
│   ├── models/
│   │   └── content.py         # Modelos de SQLAlchemy
│   ├── schemas/
│   │   └── content.py         # Esquemas de Pydantic
│   ├── services/
│   │   ├── ai/
│   │   │   ├── gemini.py      # Generación de contenido
│   │   │   └── whisper.py     # Transcripción de audio
│   │   ├── drive.py           # Integración con Google Drive
│   │   ├── media.py           # Extracción de audio con FFmpeg
│   │   └── telegram.py        # Notificaciones de Telegram
│   ├── config.py              # Gestión de configuraciones
│   ├── database.py            # Conexión a la base de datos
│   └── main.py                # Aplicación FastAPI
├── workers/
│   ├── celery_app.py         # Configuración de Celery
│   └── tasks.py              # Tareas de trabajo en segundo plano
├── alembic/                   # Migraciones de base de datos
├── docker-compose.yml         # Orquestación de contenedores
├── Dockerfile.api             # Imagen de la API
├── Dockerfile.worker          # Imagen del worker
└── requirements.txt          # Dependencias de Python
```

---

## Solución de Problemas

### El trabajo falla con "Audio file too large"

El archivo de audio excede los 25MB (límite de Whisper). Solución: Usa un video más corto o divídelo en clips más pequeños.

### El webhook de Telegram no recibe actualizaciones

- Verifica que el webhook esté configurado: `https://api.telegram.org/bot<TOKEN>/getWebhookInfo`
- Asegúrate de que tu servidor sea accesible (usa ngrok para desarrollo local)
- Verifica los registros: `docker-compose logs worker`

### La descarga de Google Drive falla

- Verifica que la cuenta de servicio tenga acceso al archivo/carpeta
- Verifica el formato de `GOOGLE_DRIVE_CREDENTIALS_JSON` (debe ser JSON válido con comillas simples alrededor de toda la cadena en .env)

### La transcripción está vacía o es de mala calidad

- Asegúrate de que el video tenga audio claro
- Considera ajustar el parámetro de idioma en `whisper.py` (actualmente configurado en español)

---

## Licencia

Licencia MIT - Ver archivo LICENSE para más detalles.
