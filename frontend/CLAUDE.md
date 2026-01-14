# Frontend Implementation Guidance

## Technology Stack

- **Framework**: Next.js 16+ (App Router)
- **Language**: TypeScript
- **Authentication**: Better Auth with JWT strategy
- **Data Fetching**: TanStack React Query (React Query v5)
- **Styling**: CSS Modules / Tailwind CSS (to be determined)

## Project Structure

```
frontend/
├── src/
│   ├── app/                 # Next.js App Router pages
│   │   ├── layout.tsx       # Root layout with Better Auth provider
│   │   ├── page.tsx         # Landing page with auth redirect
│   │   ├── login/page.tsx   # Login page
│   │   ├── signup/page.tsx  # Signup page
│   │   └── tasks/
│   │       ├── page.tsx     # Task list page
│   │       └── [id]/page.tsx # Task edit page
│   ├── components/          # Reusable React components
│   │   ├── AuthGuard.tsx    # Protected route wrapper
│   │   ├── TaskList.tsx     # Task list component
│   │   ├── TaskItem.tsx     # Individual task display
│   │   └── TaskForm.tsx     # Create/edit task form
│   ├── lib/
│   │   ├── auth.ts          # Better Auth configuration
│   │   └── api.ts           # API client with JWT attachment
│   └── types/
│       └── task.ts          # TypeScript interfaces
├── public/                  # Static assets
├── package.json             # Node dependencies
└── .env.local               # Environment variables (gitignored)
```

## Key Principles

### 1. JWT Token Management (CRITICAL)

**Token Attachment**:
- Extract JWT from Better Auth session on EVERY API request
- Attach token to Authorization header: `Bearer <token>`
- NEVER send user_id in request body or rely on path parameters for security

**Example**:
```typescript
// lib/api.ts
export async function apiRequest<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const token = await getAuthToken(); // Better Auth session

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
      ...options?.headers,
    },
  });

  if (response.status === 401) {
    // Token invalid/expired - redirect to login
    clearSession();
    router.push('/login');
    throw new Error('Unauthorized');
  }

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Request failed');
  }

  return response.json();
}
```

### 2. Protected Routes

**AuthGuard Pattern**:
```typescript
// components/AuthGuard.tsx
export function AuthGuard({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth(); // Better Auth hook

  if (loading) return <LoadingSpinner />;

  if (!user) {
    redirect('/login');
    return null;
  }

  return <>{children}</>;
}

// Usage in app/tasks/page.tsx
export default function TasksPage() {
  return (
    <AuthGuard>
      <TaskList />
    </AuthGuard>
  );
}
```

### 3. React Query for Data Fetching

**Query Pattern** (GET requests):
```typescript
// Fetch tasks
const { data: tasks, isLoading, error } = useQuery({
  queryKey: ['tasks'],
  queryFn: () => apiRequest<Task[]>('/api/{user_id}/tasks'),
  staleTime: 5000, // 5 seconds
});
```

**Mutation Pattern** (POST/PUT/PATCH/DELETE):
```typescript
// Create task
const createMutation = useMutation({
  mutationFn: (newTask: TaskCreate) =>
    apiRequest('/api/{user_id}/tasks', {
      method: 'POST',
      body: JSON.stringify(newTask),
    }),
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['tasks'] }); // Refetch list
    toast.success('Task created!');
  },
  onError: (error) => {
    toast.error(error.message);
  },
});
```

### 4. Form Validation

**Client-Side Validation**:
```typescript
// Validate before submission
const handleSubmit = (e: React.FormEvent) => {
  e.preventDefault();

  if (!title.trim()) {
    setError('Title is required');
    return;
  }

  if (title.length > 255) {
    setError('Title must be 255 characters or less');
    return;
  }

  if (description && description.length > 2000) {
    setError('Description must be 2000 characters or less');
    return;
  }

  createMutation.mutate({ title, description });
};
```

### 5. Error Handling

**Response Status Handling**:
```typescript
// 401 Unauthorized → Redirect to login
if (response.status === 401) {
  clearSession();
  router.push('/login');
}

// 403 Forbidden → Show access denied message
if (response.status === 403) {
  toast.error('Access denied');
}

// 404 Not Found → Show not found message
if (response.status === 404) {
  toast.error('Task not found');
}

// Network error → Show retry option
catch (error) {
  toast.error('Network error. Please try again.');
}
```

### 6. Loading States

**UI Feedback**:
```typescript
// Loading skeleton during fetch
{isLoading && <TaskListSkeleton />}

// Disabled inputs during submission
<button disabled={createMutation.isPending}>
  {createMutation.isPending ? 'Creating...' : 'Create Task'}
</button>

// Optimistic updates for instant feedback
const toggleMutation = useMutation({
  mutationFn: (taskId: number) =>
    apiRequest(`/api/{user_id}/tasks/${taskId}/complete`, {
      method: 'PATCH',
      body: JSON.stringify({ completed: !task.completed }),
    }),
  onMutate: async (taskId) => {
    // Optimistically update UI before server responds
    await queryClient.cancelQueries({ queryKey: ['tasks'] });
    const previous = queryClient.getQueryData(['tasks']);
    queryClient.setQueryData(['tasks'], (old: Task[]) =>
      old.map(t => t.id === taskId ? { ...t, completed: !t.completed } : t)
    );
    return { previous };
  },
  onError: (err, variables, context) => {
    // Rollback on error
    queryClient.setQueryData(['tasks'], context?.previous);
  },
});
```

### 7. Responsive Design

**Mobile-First Approach**:
- Base styles for mobile (375x667)
- Media queries for desktop (1920x1080)
- Touch-friendly targets (minimum 44x44px)
- Accessible color contrast

## Implementation Checklist

### Authentication
- [ ] Better Auth configured with JWT strategy
- [ ] Signup page with email/password validation
- [ ] Login page with error handling
- [ ] Session persistence across refreshes
- [ ] Logout functionality
- [ ] Protected route guards

### Task Management UI
- [ ] Task list page with loading/empty states
- [ ] Create task form with validation
- [ ] Task item with completion checkbox
- [ ] Edit task page/modal
- [ ] Delete task with confirmation dialog
- [ ] Responsive layout (mobile + desktop)

### API Integration
- [ ] API client with JWT attachment
- [ ] 401 handling (redirect to login)
- [ ] 403 handling (access denied message)
- [ ] Error messages displayed to user
- [ ] Loading indicators during operations
- [ ] Toast notifications for feedback

### React Query
- [ ] Query setup for fetching tasks
- [ ] Mutations for create/update/delete/toggle
- [ ] Cache invalidation after mutations
- [ ] Optimistic updates for instant feedback
- [ ] Error handling with rollback

## Common Pitfalls to Avoid

1. ❌ Not attaching JWT token to API requests
2. ❌ Allowing unauthenticated users to access protected pages
3. ❌ Not handling 401 responses (token expiration)
4. ❌ Missing loading states during async operations
5. ❌ Not validating form inputs on client side
6. ❌ Forgetting to invalidate cache after mutations
7. ❌ Hardcoding API URLs instead of using environment variables
8. ❌ Not providing visual feedback for completed tasks

## Running the Frontend

### Development
```bash
cd frontend
npm install
npm run dev
```

App runs at http://localhost:3000

### Environment Setup
Create `.env.local` from `.env.local.example`:
```env
BETTER_AUTH_SECRET=<same-as-backend>
NEXT_PUBLIC_API_URL=http://localhost:7860
```

## Reference Documents

- Specification: `@specs/001-fullstack-todo-app/spec.md`
- Implementation Plan: `@specs/001-fullstack-todo-app/plan.md`
- API Contract: `@specs/001-fullstack-todo-app/contracts/api-spec.yaml`
- Research Decisions: `@specs/001-fullstack-todo-app/research.md`
- Quickstart Guide: `@specs/001-fullstack-todo-app/quickstart.md`
