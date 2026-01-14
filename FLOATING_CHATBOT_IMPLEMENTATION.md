# Floating AI Chatbot Feature

## Overview
This feature adds a floating AI chatbot button to the Todo app that appears on all authenticated pages except login and signup pages.

## Implementation Details

### Components
- `FloatingChatButton.tsx`: The main component that renders the floating button and modal
- Located in `src/components/FloatingChatButton.tsx`

### Layout Structure
- The authenticated routes are now organized under `/authenticated/*`
- The `AuthenticatedRootLayout` wraps all authenticated routes
- The floating chat button is conditionally rendered based on the current route

### Functionality
- The floating button appears on the bottom-right corner of all authenticated pages
- The button is hidden on `/login` and `/signup` pages
- Clicking the button opens a modal with the existing chat component
- The modal can be closed by:
  - Clicking the close (X) button
  - Clicking on the backdrop/background
  - The modal prevents closing when clicking inside the chat component

### Responsive Design
- The button position adjusts for different screen sizes
- The modal is responsive and adapts to mobile, tablet, and desktop views
- Uses Tailwind CSS utility classes for responsive behavior

### Technical Notes
- Uses Next.js App Router with client-side route detection
- Implements dynamic import for the chat component to avoid SSR issues
- Leverages the existing `chat.jsx` component from the pages directory
- Includes proper accessibility attributes (aria-label)