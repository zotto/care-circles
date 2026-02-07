# Care Circles - Frontend Application

A modern, enterprise-grade Vue.js application for AI-assisted care coordination.

## 🎯 Overview

The Care Circles frontend provides an intuitive, single-page workflow for organizing care support. Users describe their caregiving situation, and AI agents analyze the needs and generate a personalized care plan—all within one seamless interface.

## ✨ Key Features

- **Unified Workflow** - Complete care coordination on a single page
- **Real-Time Updates** - Live status tracking with automatic polling
- **Intelligent AI Processing** - Multi-step agent pipeline visible to users
- **Inline Task Editing** - Modify tasks directly without separate forms
- **Professional Design** - Enterprise-ready UI with subtle animations
- **Fully Responsive** - Optimized for desktop, tablet, and mobile
- **Type-Safe** - Complete TypeScript coverage

## 🚀 Quick Start

### Prerequisites

- Node.js 16+ or 18+
- Yarn or npm
- Backend API running on `http://localhost:8000`

### Installation

```bash
# Install dependencies
yarn install

# Start development server
yarn dev
```

The app will be available at `http://localhost:5173`

### Build for Production

```bash
yarn build
```

The build output in `dist/` is suitable for deployment to S3 + CloudFront (or any static host). Assets in `public/` are copied to the root unchanged, so after deploy you get stable URLs:

- **Logo (e.g. for Supabase magic link email):** `https://<your-cloudfront-domain>/logo.png`  
  Use in your email template as: `<img src="https://<your-cloudfront-domain>/logo.png" alt="Care Circles" />`

### Preview Production Build

```bash
yarn preview
```

## 🏗️ Architecture

### Tech Stack

- **Vue 3** - Progressive JavaScript framework
- **TypeScript** - Type-safe development
- **Pinia** - State management
- **Vue Router** - Client-side routing
- **Axios** - HTTP client
- **Vite** - Lightning-fast build tool

### Project Structure

```
src/
├── components/
│   ├── atoms/          # Basic UI components (buttons, inputs, badges)
│   └── organisms/      # Complex components (forms, panels)
├── views/              # Page-level components
├── stores/             # Pinia state management
├── services/           # API service layer
├── types/              # TypeScript definitions
├── constants/          # Configuration constants
├── composables/        # Reusable composition functions
└── router/             # Route definitions
```

## 📱 User Experience

### The Workflow

1. **Describe Situation** (Step 1)
   - User fills out care request form
   - Minimum 50 characters required
   - Optional constraints and boundaries

2. **AI Analysis** (Step 2)
   - Real-time processing visualization
   - Three sub-steps with progress indicators
   - Automatic polling every 2 seconds
   - Manual refresh option

3. **Review & Approve** (Step 3)
   - Grid of editable task cards
   - Inline editing of all fields
   - Priority-based color coding
   - Approve entire care plan

### Design Philosophy

- **Progressive Disclosure** - Information appears when relevant
- **Clear Visual Hierarchy** - Easy to scan and understand
- **Contextual Actions** - Buttons appear at the right moment
- **Error Recovery** - Clear error states with actionable solutions
- **Smooth Transitions** - Professional animations throughout

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```bash
# API Configuration
VITE_API_BASE_URL=http://localhost:8000/api

# Environment
VITE_ENV=development
```

### API Endpoints Used

- `POST /api/care-requests` - Submit care request
- `GET /api/care-requests/{id}` - Get care request details
- `GET /api/jobs/{id}` - Poll job status
- `GET /api/jobs` - List all jobs (debugging)

## 🎨 Design System

### Color Palette

- **Primary** - Indigo (`#4f46e5`) - Trustworthy
- **Secondary** - Pink (`#ec4899`) - Caring
- **Accent** - Teal (`#14b8a6`) - Calming
- **Success** - Green (`#10b981`)
- **Warning** - Orange (`#f59e0b`)
- **Danger** - Red (`#ef4444`)

### Typography

- **Font Family** - Inter (system fallback)
- **Scale** - 12px to 44px (responsive)
- **Weights** - 400 (normal), 500 (medium), 600 (semibold), 700 (bold)

### Spacing System

- **xs** - 4px
- **sm** - 8px
- **md** - 16px
- **lg** - 24px
- **xl** - 32px
- **2xl** - 48px
- **3xl** - 64px

## 🔌 API Integration

### Service Layer

All API calls go through a centralized service:

```typescript
import { api } from '@/services/api';

// Create care request
const response = await api.createCareRequest({
  narrative: "Description...",
  constraints: "Constraints...",
  boundaries: "Boundaries..."
});

// Get job status
const status = await api.getJobStatus(jobId);
```

### State Management

The Pinia store handles all application state:

```typescript
import { useCareStore } from '@/stores/careStore';

const careStore = useCareStore();

// Create care request (starts polling automatically)
await careStore.createCareRequest(narrative, constraints, boundaries);

// Access state
const tasks = careStore.tasks;
const isLoading = careStore.isLoading;
const error = careStore.error;

// Update task
careStore.updateTask(taskId, { title: "New Title" });

// Delete task
careStore.deleteTask(taskId);
```

## 📊 Performance

### Bundle Size

- **JavaScript** - 164KB (gzipped: 63KB)
- **CSS** - 36KB (gzipped: 6KB)
- **Total** - ~200KB (gzipped: ~69KB)

### Metrics

- **First Paint** - <1s
- **Time to Interactive** - <2s
- **Lighthouse Score** - 95+ (Performance, Accessibility, Best Practices)

## 🧪 Development

### Code Quality

```bash
# Type checking
yarn vue-tsc

# Build (includes type checking)
yarn build
```

### Best Practices

- **TypeScript Strict Mode** - Enabled
- **Composition API** - Preferred over Options API
- **Single File Components** - `.vue` files with `<script setup>`
- **Scoped Styles** - Component-level CSS
- **Semantic HTML** - Accessibility-first markup

## 📚 Key Components

### UnifiedWorkflowView
The main page component that orchestrates the entire workflow.

**Features:**
- Three-step progressive interface
- Real-time status updates
- Task management
- Approval workflow

### CareRequestForm
Form for submitting care requests.

**Features:**
- Character count validation
- Optional expandable fields
- Smooth animations
- Error handling

### TaskReviewPanel (deprecated - integrated into UnifiedWorkflowView)
Task management interface.

**Features:**
- Grid layout
- Inline editing
- Priority badges
- Category selection

## 🌐 Browser Support

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

## 📖 Documentation

- **Integration Guide** - `INTEGRATION.md`
- **Unified Workflow** - `UNIFIED-WORKFLOW.md`
- **Integration Summary** - `INTEGRATION-SUMMARY.md`

## 🤝 Contributing

1. Follow the existing code style
2. Use TypeScript for all new code
3. Test on multiple browsers
4. Ensure build succeeds before committing
5. Write meaningful commit messages

## 📝 License

[Your License Here]

## 🎯 Next Steps

### Potential Enhancements

- [ ] WebSocket support (replace polling)
- [ ] Task drag-and-drop reordering
- [ ] Bulk task operations
- [ ] Export to PDF
- [ ] Dark mode
- [ ] Keyboard shortcuts
- [ ] Undo/redo
- [ ] Collaborative editing
- [ ] Mobile app (React Native)

---

**Built with ❤️ for Care Circles**
