# Email Trigger App - Frontend

A modern React frontend for the Email Trigger application with OAuth authentication and email management.

## Features

- 🔐 **OAuth Login** - One-click Gmail/Outlook authentication
- 📧 **Email Dashboard** - View recent emails from all connected accounts
- ⚡ **Trigger Management** - Create and manage email processing rules
- 📱 **Responsive Design** - Works on desktop and mobile
- 🎨 **Modern UI** - Clean design with Tailwind CSS

## Quick Start

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start development server:**
   ```bash
   npm run dev
   ```

3. **Or with Docker:**
   ```bash
   docker-compose up frontend
   ```

The frontend will be available at http://localhost:3000

## Components

- **LoginCard** - OAuth provider selection and authentication
- **EmailDashboard** - Main application interface
- **EmailList** - Display emails from all providers
- **TriggerManager** - Create and manage email triggers

## Configuration

The app connects to the backend API at `http://localhost:8000` by default. This can be configured in `vite.config.js`.

## Building for Production

```bash
npm run build
```

Built files will be in the `dist/` directory.

## Technologies

- **React 18** - Modern React with hooks
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **Lucide React** - Beautiful icons
- **React Hot Toast** - Elegant notifications
- **Axios** - HTTP client for API calls
- **Date-fns** - Date utilities