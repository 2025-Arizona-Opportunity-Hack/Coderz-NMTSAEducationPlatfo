# NMTSA Learn - Deployment Guide

This guide covers deploying the NMTSA Learn frontend to various hosting platforms.

## 📋 Pre-Deployment Checklist

- [ ] All tests passing
- [ ] Environment variables configured
- [ ] Build command tested locally
- [ ] API backend is deployed and accessible
- [ ] Domain name configured (if applicable)
- [ ] SSL certificate ready (for custom domains)

## 🏗️ Building for Production

### 1. Install Dependencies

```bash
pnpm install
```

### 2. Set Environment Variables

Create `.env.production` file:

```env
VITE_API_BASE_URL=https://api.nmtsalearn.com/api
VITE_API_VERSION=v1
VITE_DEBUG=false
```

### 3. Build the Application

```bash
pnpm build
```

This creates an optimized production build in the `dist/` directory.

### 4. Test the Production Build

```bash
pnpm preview
```

Visit `http://localhost:4173` to test the production build locally.

## 🚀 Deployment Options

### Option 1: Vercel (Recommended)

Vercel provides the simplest deployment experience with automatic CI/CD.

#### Via Vercel CLI

1. **Install Vercel CLI**
```bash
npm install -g vercel
```

2. **Login to Vercel**
```bash
vercel login
```

3. **Deploy**
```bash
vercel --prod
```

#### Via Vercel Dashboard

1. Go to [vercel.com](https://vercel.com)
2. Click "Add New Project"
3. Import your GitHub repository
4. Configure:
   - Framework Preset: Vite
   - Build Command: `pnpm build`
   - Output Directory: `dist`
   - Install Command: `pnpm install`
5. Add Environment Variables:
   - `VITE_API_BASE_URL`
6. Click "Deploy"

#### vercel.json Configuration

The project includes a `vercel.json` file for SPA routing:

```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/" }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-XSS-Protection",
          "value": "1; mode=block"
        }
      ]
    }
  ]
}
```

### Option 2: Netlify

#### Via Netlify CLI

1. **Install Netlify CLI**
```bash
npm install -g netlify-cli
```

2. **Login to Netlify**
```bash
netlify login
```

3. **Deploy**
```bash
netlify deploy --prod --dir=dist
```

#### Via Netlify Dashboard

1. Go to [netlify.com](https://netlify.com)
2. Click "Add new site" → "Import an existing project"
3. Connect to your Git provider
4. Configure:
   - Build command: `pnpm build`
   - Publish directory: `dist`
5. Add Environment Variables
6. Click "Deploy"

#### netlify.toml Configuration

Create `netlify.toml`:

```toml
[build]
  command = "pnpm build"
  publish = "dist"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-Content-Type-Options = "nosniff"
    X-XSS-Protection = "1; mode=block"
    Referrer-Policy = "strict-origin-when-cross-origin"
```

### Option 3: AWS S3 + CloudFront

#### Prerequisites
- AWS Account
- AWS CLI configured
- S3 bucket created
- CloudFront distribution set up

#### Deploy to S3

1. **Build the application**
```bash
pnpm build
```

2. **Sync to S3**
```bash
aws s3 sync dist/ s3://your-bucket-name --delete
```

3. **Invalidate CloudFront cache**
```bash
aws cloudfront create-invalidation --distribution-id YOUR_DIST_ID --paths "/*"
```

#### S3 Bucket Configuration

1. Enable static website hosting
2. Set index document: `index.html`
3. Set error document: `index.html` (for SPA routing)
4. Configure bucket policy for public read access

#### CloudFront Configuration

1. Create distribution with S3 origin
2. Configure custom error pages:
   - 403 → `/index.html` (200)
   - 404 → `/index.html` (200)
3. Enable HTTPS
4. Add custom domain (optional)

### Option 4: Docker + Any Cloud Provider

#### Dockerfile

Create `Dockerfile`:

```dockerfile
# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# Install pnpm
RUN npm install -g pnpm

# Copy package files
COPY package.json pnpm-lock.yaml ./

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy source code
COPY . .

# Build application
RUN pnpm build

# Production stage
FROM nginx:alpine

# Copy built files from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

#### nginx.conf

Create `nginx.conf`:

```nginx
server {
    listen 80;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml text/javascript;

    # Security headers
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # SPA routing
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

#### Build and Run

```bash
# Build image
docker build -t nmtsa-learn-frontend .

# Run container
docker run -p 80:80 nmtsa-learn-frontend
```

#### Deploy to Cloud

**AWS ECS/Fargate**
1. Push image to ECR
2. Create ECS task definition
3. Deploy to ECS service

**Google Cloud Run**
```bash
gcloud run deploy nmtsa-learn --image gcr.io/project-id/nmtsa-learn-frontend
```

**Azure Container Instances**
```bash
az container create --resource-group myResourceGroup --name nmtsa-learn --image myregistry.azurecr.io/nmtsa-learn-frontend
```

## 🔧 Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_API_BASE_URL` | Backend API base URL | `https://api.nmtsalearn.com/api` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_VERSION` | API version | `v1` |
| `VITE_DEBUG` | Enable debug mode | `false` |

## 🔐 Security Considerations

### HTTPS
- **Always use HTTPS in production**
- Configure SSL certificates
- Redirect HTTP to HTTPS

### Content Security Policy

Add CSP headers in your hosting configuration:

```
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:;
```

### Environment Variables
- Never commit `.env` files
- Use platform-specific secret management
- Rotate API keys regularly

## 📊 Monitoring

### Error Tracking

Integrate error tracking service (e.g., Sentry):

```typescript
import * as Sentry from "@sentry/react";

Sentry.init({
  dsn: "YOUR_SENTRY_DSN",
  environment: import.meta.env.MODE,
  tracesSampleRate: 1.0,
});
```

### Analytics

Add analytics (e.g., Google Analytics):

```html
<!-- Add to index.html -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

## 🔄 CI/CD Pipeline

### GitHub Actions Example

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - uses: pnpm/action-setup@v2
        with:
          version: 8
      
      - name: Install dependencies
        run: pnpm install
      
      - name: Build
        run: pnpm build
        env:
          VITE_API_BASE_URL: ${{ secrets.API_BASE_URL }}
      
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.ORG_ID }}
          vercel-project-id: ${{ secrets.PROJECT_ID }}
          vercel-args: '--prod'
          working-directory: ./
```

## 🧪 Post-Deployment Verification

After deployment, verify:

- [ ] Application loads correctly
- [ ] All pages are accessible
- [ ] API calls work correctly
- [ ] Authentication functions properly
- [ ] Images and assets load
- [ ] SSL certificate is valid
- [ ] DNS resolves correctly
- [ ] Mobile responsive design works
- [ ] Performance metrics are acceptable
- [ ] Error tracking is working
- [ ] Analytics are recording

## 🔧 Rollback Strategy

### Vercel
```bash
vercel rollback
```

### Git-based Deployments
```bash
git revert HEAD
git push origin main
```

### Docker
```bash
# Deploy previous version
docker run -p 80:80 nmtsa-learn-frontend:previous-tag
```

## 📞 Support

For deployment issues:
- Check logs in hosting platform dashboard
- Verify environment variables
- Test API connectivity
- Review DNS configuration
- Check SSL certificates

---

**Last Updated**: January 2025
