# Deploy LUCA on the existing Render service

LUCA is configured for:

- Render web hosting;
- PostgreSQL through `DATABASE_URL`;
- Cloudinary uploads through `CLOUDINARY_URL`;
- WhiteNoise static assets;
- automatic migrations and production checks during each build.

## Update the current deployment

You do not need to create a new Render service or database. In the existing web service, confirm these environment variables:

```text
DATABASE_URL=<existing Render PostgreSQL internal URL>
CLOUDINARY_URL=cloudinary://<api-key>:<api-secret>@<cloud-name>
DJANGO_SECRET_KEY=<existing strong secret>
DJANGO_DEBUG=false
```

Render automatically supplies `RENDER_EXTERNAL_HOSTNAME`, which the app adds to Django's allowed hosts and CSRF origins. If the service uses a custom domain, also set:

```text
DJANGO_ALLOWED_HOSTS=your-domain.example.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://your-domain.example.com
```

Set the existing Render service commands to:

Build command:

```sh
bash build.sh
```

Start command:

```sh
gunicorn luca.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --access-logfile - --error-logfile -
```

Health check path:

```text
/health/
```

Push the changes to the branch connected to Render. The build installs dependencies, collects static assets, applies all pending PostgreSQL migrations, and runs Django's deployment checks. Existing PostgreSQL data is preserved.

## New Blueprint deployment

`render.yaml` is also available for a new Blueprint deployment. It provisions a Render PostgreSQL database and asks for the secret `CLOUDINARY_URL` during initial setup. Do not apply the Blueprint to replace the current service unless a separate deployment is intended.

## Media behavior

The app's Cloudinary fields store these uploads:

- profile photos;
- event posters;
- gallery images and videos;
- payment screenshots;
- the shared QR image.

Local development continues to use the local `media/` folder when `CLOUDINARY_URL` is absent.

## Verify after deployment

1. Open `/health/` and confirm it returns `{"status": "ok"}`.
2. Sign in with the existing PostgreSQL-backed account.
3. Upload a profile photo and confirm its URL uses `res.cloudinary.com`.
4. Upload the shared QR and a gallery image/video.
5. Redeploy once and confirm all uploaded media still appears.
