export interface User { id: number; username: string; email: string }
export interface Task { id: number; user_id: number; title: string; descricao: string | null; concluida: boolean }
export interface TaskInput { title: string; descricao: string | null; concluida: boolean }

const base = import.meta.env.VITE_API_URL ?? (import.meta.env.DEV ? '/api' : '');
const storageKey = 'fluxo.session';
let token = sessionStorage.getItem(storageKey);

export class ApiError extends Error {
  constructor(message: string, public status: number) { super(message); }
}

export function setToken(value: string | null): void {
  token = value;
  if (value) sessionStorage.setItem(storageKey, value);
  else sessionStorage.removeItem(storageKey);
}
export const hasSession = (): boolean => Boolean(token);

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${base}${path}`, {
      ...options,
      headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}), ...options.headers },
    });
  } catch {
    throw new ApiError('Não foi possível conectar. Confira se a API está em execução.', 0);
  }
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    const detail = payload.detail;
    const message = typeof detail === 'string' ? detail : Array.isArray(detail)
      ? detail.map((error: { loc?: string[]; msg?: string }) => `${error.loc?.slice(1).join('.') ?? 'Campo'}: ${error.msg ?? 'valor inválido'}`).join(' · ')
      : 'Não foi possível concluir a ação. Tente novamente.';
    throw new ApiError(message, response.status);
  }
  return response.status === 204 ? undefined as T : response.json();
}

export const api = {
  async login(email: string, password: string): Promise<void> {
    const data = await request<{ access_token: string }>('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) });
    setToken(data.access_token);
  },
  register: (username: string, email: string, password: string) => request<User>('/users/', { method: 'POST', body: JSON.stringify({ username, email, password }) }),
  async me(): Promise<User> {
    const users = await request<User[]>('/users/');
    if (!users[0]) throw new ApiError('Conta não encontrada.', 401);
    return users[0];
  },
  async tasks(): Promise<Task[]> {
    const tasks: Task[] = [];
    for (let offset = 0; ; offset += 100) {
      const page = await request<Task[]>(`/tasks/?offset=${offset}&limit=100`);
      tasks.push(...page);
      if (page.length < 100) return tasks;
    }
  },
  create: (data: TaskInput) => request<Task>('/tasks/', { method: 'POST', body: JSON.stringify(data) }),
  update: (id: number, data: Partial<TaskInput>) => request<Task>(`/tasks/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  remove: (id: number) => request<void>(`/tasks/${id}`, { method: 'DELETE' }),
};
