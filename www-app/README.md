# Care Circles Web Application

A modern, Vue 3-based web application for AI-assisted caregiving coordination with sophisticated animations and enterprise-grade architecture.

## ✨ Features

### Design & UX
- 🎨 **Modern Design System**: Comprehensive design tokens with warm, caring color palette
- 🌊 **Scroll Animations**: Smooth reveal animations as content enters viewport
- ✨ **Micro-interactions**: Hover effects, transitions, and loading states
- 🎭 **Glassmorphism**: Modern glass effects with backdrop blur
- 📱 **Fully Responsive**: Mobile-first design with breakpoints
- ♿ **Accessible**: ARIA attributes, keyboard navigation, focus management

### Technical Excellence
- ⚡ **Vue 3 Composition API**: Modern, performant component architecture
- 🔷 **TypeScript**: Full type safety across the application
- 🏪 **Pinia State Management**: Reactive, type-safe state
- 🎯 **Atomic Design**: Components organized from atoms to organisms
- 🎬 **Advanced Animations**: CSS keyframes, transitions, and Vue transitions
- 📦 **Zero Duplication**: Reusable, composable components

## Architecture

```
www-app/
├── src/
│   ├── components/
│   │   ├── atoms/           # Basic building blocks
│   │   │   ├── BaseButton.vue      # Enhanced with gradient backgrounds
│   │   │   ├── BaseTextArea.vue    # Auto-resize, character count
│   │   │   ├── BaseCard.vue        # Elevated variants with shadows
│   │   │   ├── BaseInput.vue       # Form input with validation states
│   │   │   ├── BaseBadge.vue       # Status indicators
│   │   │   └── BaseSkeleton.vue    # Loading placeholders
│   │   │
│   │   └── organisms/       # Complex components
│   │       ├── AppHeader.vue       # Sticky header with glassmorphism
│   │       ├── AppFooter.vue       # Footer with links
│   │       └── CareRequestForm.vue # Main form with animations
│   │
│   ├── views/
│   │   └── PlanView.vue     # Landing page with scroll reveals
│   │
│   ├── stores/
│   │   └── careStore.ts     # Pinia store for care requests
│   │
│   ├── composables/
│   │   └── useAnimations.ts # Reusable animation hooks
│   │
│   ├── types/
│   │   └── index.ts         # TypeScript definitions
│   │
│   ├── constants/
│   │   └── index.ts         # Centralized constants (no magic numbers!)
│   │
│   ├── router/
│   │   └── index.ts         # Vue Router configuration
│   │
│   └── style.css           # Global styles & design tokens
│
├── index.html
├── vite.config.ts
└── package.json
```

### Design Tokens

The application uses CSS custom properties for:
- **Colors**: Primary (indigo), Secondary (pink), Accent (teal), Semantic colors
- **Typography**: Inter font family, consistent sizing scale
- **Spacing**: 8px base unit with consistent scale
- **Shadows**: Elevation system with colored shadows
- **Transitions**: Consistent animation timing (150ms, 200ms, 300ms)
- **Gradients**: Smooth color transitions for backgrounds and text

### Animation System

**Scroll Reveal Animations**
- Elements fade in and slide up as they enter viewport
- Staggered animations for lists and grids
- Threshold-based triggering using Intersection Observer

**Micro-interactions**
- Button hover lift effect with colored shadows
- Card hover with border animation
- Loading spinners with smooth rotation
- Success state with checkmark draw animation

**Page Transitions**
- Smooth fade and scale effects
- Vue transition components for dynamic content
- Parallax background elements

### Constants System

All magic numbers are centralized in `constants/index.ts`:

```typescript
VALIDATION: {
  NARRATIVE_MIN_LENGTH: 50,
  NARRATIVE_MAX_LENGTH: 2000,
  // ...
}

ANIMATION: {
  FAST: 150,
  BASE: 200,
  SLOW: 300,
  // ...
}

SCROLL: {
  REVEAL_THRESHOLD: 0.1,
  PARALLAX_SPEED: 0.5,
  // ...
}
```

### Component Philosophy

- **Atomic Design**: Components are organized from atomic (Button) to organisms (CareRequestForm)
- **No Duplication**: Reusable components with props for customization
- **Type-Safe**: Full TypeScript support throughout
- **Accessible**: ARIA attributes, keyboard navigation, focus management
- **Responsive**: Mobile-first design with breakpoints
- **Performant**: Optimized animations, lazy loading, efficient renders

## Tech Stack

- **Vue 3** (Composition API)
- **TypeScript**
- **Pinia** (State Management)
- **Vue Router** (Routing)
- **Vite** (Build Tool)

## Getting Started

### Prerequisites

- Node.js 18+ and Yarn

### Installation

```bash
cd www-app
yarn install
```

### Development

```bash
yarn dev
```

Visit `http://localhost:5173`

### Build

```bash
yarn build
```

### Type Check

```bash
yarn build
```

## Features

### Current (v1)

- ✅ Modern, caring design system
- ✅ Care request form with validation
- ✅ Optional constraints and boundaries fields
- ✅ Success state after submission
- ✅ Responsive design
- ✅ Type-safe state management
- ✅ Atomic component library

### Future

- [ ] Authentication (Supabase Auth)
- [ ] Review packet approval flow
- [ ] Task list view for helpers
- [ ] Real-time updates
- [ ] Backend API integration

## Component Documentation

### Atoms

**BaseButton**
- Props: `variant`, `size`, `loading`, `disabled`, `fullWidth`
- Variants: primary (gradient), secondary (gradient), outline, ghost, danger
- Features: Loading spinner, gradient backgrounds, lift animation, colored shadows
- Accessibility: Focus states, disabled states, ARIA attributes

**BaseTextArea**
- Props: `modelValue`, `label`, `placeholder`, `rows`, `maxLength`, `showCharCount`
- Features: Auto-resize, character count, validation states, focus animation
- Validation: Real-time error display, hint text support

**BaseCard**
- Props: `title`, `variant`, `padding`, `hoverable`
- Variants: default, outlined, elevated
- Features: Slot-based content, hover effects, shadow elevations

**BaseInput**
- Props: `modelValue`, `type`, `placeholder`, `error`
- States: focused, error, disabled
- Features: Validation states, focus ring, smooth transitions

**BaseBadge**
- Props: `variant`, `size`, `outlined`
- Variants: All semantic colors (success, warning, error, info)
- Features: Outlined and filled variants, size variations

**BaseSkeleton**
- Props: `width`, `height`, `variant`, `animated`
- Variants: text, circular, rectangular
- Features: Shimmer animation, customizable dimensions

### Organisms

**AppHeader**
- Features: Sticky positioning, glassmorphism effect, backdrop blur
- Animations: Logo hover scale, brand lift effect, gradient border reveal
- Responsive: Collapsible tagline on mobile

**AppFooter**
- Layout: Flex-based responsive layout
- Content: Copyright, links, support information

**CareRequestForm**
- Main form for care request submission
- Features:
  - Narrative field (required, 50-2000 chars)
  - Optional constraints and boundaries fields
  - Collapsible optional sections with animation
  - Info card with hover effects
  - Form validation with error display
  - Submit button with loading state
- Animations: Smooth field reveals, info card border animation

### Views

**PlanView**
- Comprehensive landing page with multiple sections:
  - **Hero**: Animated badge, gradient title, trust indicators
  - **Form Section**: Care request form with scroll reveal
  - **Success State**: Animated checkmark, progress steps, ripple effect
  - **How It Works**: 4-step process with icons and stagger animation
  - **Social Proof**: Caring message with floating emoji
- Background: Animated floating circles with parallax
- Scroll: All sections use intersection observer for reveals

## Composables

### useAnimations.ts

**useScrollReveal(options)**
- Returns: `{ isVisible, elementRef }`
- Features: Intersection Observer-based scroll reveal
- Options: threshold, rootMargin, once (single trigger)
- Usage: Attach `elementRef` to element, watch `isVisible` for animations

**useScrollProgress()**
- Returns: `{ scrollProgress, scrollY }`
- Features: Real-time scroll position tracking
- Use case: Progress bars, scroll indicators

**useParallax(speed)**
- Returns: `{ parallaxStyle, parallaxRef }`
- Features: Parallax scrolling effect
- Usage: Apply `parallaxStyle` to create depth

**useMousePosition()**
- Returns: `{ x, y }`
- Features: Track mouse coordinates
- Use case: Interactive hover effects, cursor followers

**useStaggeredReveal(count, baseDelay)**
- Returns: `{ getDelay }`
- Features: Calculate staggered animation delays
- Use case: Sequential list animations

## State Management

### careStore (Pinia)

```typescript
// State
currentCareCircle: CareCircle | null
careRequests: CareRequest[]
activeJob: Job | null
isLoading: boolean
error: string | null

// Getters
hasActiveRequest: computed
latestRequest: computed

// Actions
createCareRequest(narrative, constraints?, boundaries?)
getCareRequest(id)
pollJobStatus(jobId)
clearError()
reset()
```

**API Integration Notes:**
- Currently uses mock implementations
- Ready for backend integration (TODO markers in code)
- Supports async operations with loading states
- Error handling with user-friendly messages

## Styling Approach

- **CSS Custom Properties**: All design tokens in `:root`
- **Scoped Styles**: Component-specific styles with Vue scoped attribute
- **No CSS Framework**: Custom, purpose-built styles for full control
- **Animation Library**: Built-in keyframes for common patterns
- **Utility Classes**: `.scroll-reveal`, `.gradient-text`, `.glass`, etc.
- **Performance**: Hardware-accelerated transforms, will-change hints
- **Accessibility**: Respects `prefers-reduced-motion`

### Global Animations Available

```css
/* Keyframe Animations */
fadeIn, fadeInUp, fadeInDown, fadeInLeft, fadeInRight
scaleIn, slideUp, shimmer, pulse, float, gradient

/* Utility Classes */
.animate-fadeIn, .animate-fadeInUp, .animate-scaleIn, .animate-float
.scroll-reveal, .scroll-reveal.is-visible
.glass, .gradient-text, .gradient-animated
.skeleton, .hover-lift
```

### Custom Scrollbar

- Styled for modern browsers
- Matches application color scheme
- Smooth hover transitions

## Type Safety

All domain entities match the backend specification:
- `CareRequest`
- `CareCircle`
- `CareTask`
- `ReviewPacket`
- `Job`
- `NeedsMap`

## API Integration (Future)

The store includes placeholders for API calls:

```typescript
// TODO: Replace mock with actual API
const response = await fetch('/api/care-requests', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(data)
});
```

## Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- ES2020+
- CSS Grid and Flexbox

## Contributing

When adding new components:

1. Follow atomic design principles
2. Add TypeScript types
3. Include ARIA attributes
4. Test responsive behavior
5. Use design tokens (no magic values)

---

Built with ❤️ for caregivers
