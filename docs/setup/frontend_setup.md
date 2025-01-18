# Frontend Setup Instructions

## Prerequisites
- Node.js 16+ 
- npm or yarn
- Modern web browser

## Installation Steps

1. Clone the repository:
```bash
git clone [repository-url]
cd pronto-rag-assistant-ui
```

2. Install dependencies:
```bash
# Using npm
npm install

# Using yarn
yarn install
```

3. Configure environment:
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
# Set API_URL to your backend URL
```

4. Start development server:
```bash
# Using npm
npm run dev

# Using yarn
yarn dev
```

5. Access the application:
- Open browser to http://localhost:3000
- Default credentials (if required) will be in .env.example

## Development Setup

### IDE Configuration
- Install recommended extensions:
  - ESLint
  - Prettier
  - TypeScript and JavaScript Language Features

### Available Scripts
```bash
# Start development server
npm run dev

# Build for production
npm run build

# Run tests
npm test

# Lint code
npm run lint
```

### Project Structure
```
src/
├── components/     # UI components
├── hooks/         # Custom React hooks
├── lib/           # Utility functions
├── styles/        # CSS styles
└── App.tsx        # Main application
```

## Troubleshooting

### Common Issues

1. Port already in use:
```bash
# Kill process on port 3000
lsof -i :3000
kill -9 [PID]
```

2. Dependencies issues:
```bash
# Clear npm cache
npm cache clean --force
rm -rf node_modules
npm install
```

3. Build errors:
```bash
# Check TypeScript errors
npm run type-check

# Fix linting issues
npm run lint --fix
```

## Production Deployment

1. Build the application:
```bash
npm run build
```

2. Serve production build:
```bash
npm run start
```

## Configuration Options

### Environment Variables
- `REACT_APP_API_URL`: Backend API URL
- `REACT_APP_API_KEY`: API authentication key
- `PORT`: Frontend server port (default: 3000)

### Feature Flags
Edit `.env` file to enable/disable features:
```
REACT_APP_ENABLE_TRAINING=true
REACT_APP_MAX_FILE_SIZE=1073741824  # 1GB
```

## Security Considerations

1. API Authentication:
   - Use environment variables for API keys
   - Never commit .env files
   - Use HTTPS in production

2. File Upload Security:
   - Size limit: 1GB
   - Allowed types: .4gl, .txt, .md
   - Content validation

## Performance Optimization

1. Development:
   - Enable React Fast Refresh
   - Use React.memo for expensive components
   - Implement code splitting

2. Production:
   - Enable compression
   - Use CDN for static assets
   - Implement caching strategies

## Monitoring

1. Error Tracking:
   - Check browser console
   - Monitor network requests
   - Review error boundaries

2. Performance Monitoring:
   - React DevTools
   - Network tab
   - Lighthouse reports
