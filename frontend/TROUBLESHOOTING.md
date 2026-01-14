# Vercel Deployment Troubleshooting Guide

## Common Issues and Solutions

### 1. Environment Variables
**Problem**: API calls failing in production
**Solution**:
- Ensure `NEXT_PUBLIC_API_URL` is set in Vercel dashboard
- Go to: Vercel Dashboard → Your Project → Settings → Environment Variables
- Add: `NEXT_PUBLIC_API_URL` with value pointing to your backend API

### 2. Backend API Accessibility
**Problem**: Frontend can't connect to backend
**Solution**:
- Make sure your backend API is deployed and publicly accessible
- If using localhost in development, update to your actual backend URL for production
- Example: Change from `http://localhost:7860` to `https://your-backend.vercel.app` or your actual backend URL

### 3. Build Errors
**Problem**: Deployment fails during build process
**Solution**:
- Check that all dependencies are properly specified in package.json
- Ensure no development-only dependencies are required for runtime
- Verify that your Next.js app builds locally with `npm run build`

### 4. Redirect/Router Issues
**Problem**: Page redirects not working properly
**Solution**:
- Ensure client-side navigation is properly handled
- Check that authentication state is properly managed in deployed environment

## Steps to Deploy Successfully

1. **Prepare your backend**:
   - Deploy your backend API to a publicly accessible URL
   - Note the API URL for the next step

2. **Configure Vercel environment variables**:
   - Go to your Vercel project dashboard
   - Navigate to Settings → Environment Variables
   - Add `NEXT_PUBLIC_API_URL` with your backend API URL

3. **Redeploy**:
   - Trigger a new deployment in Vercel
   - Check the build logs for any errors

## Testing Your Deployment

After deployment:
1. Visit your Vercel URL
2. Check browser console for any API connection errors
3. Verify that authentication flows work properly
4. Test that API calls to your backend are successful

## Additional Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Next.js Deployment Guide](https://nextjs.org/docs/deployment)
- [Environment Variables Guide](https://vercel.com/docs/concepts/projects/environment-variables)