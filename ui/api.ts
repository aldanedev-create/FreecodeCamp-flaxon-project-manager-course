import type { Session } from './types';

let session: Session | null = null;
export async function loadSession(): Promise<Session> {
    const response = await fetch('/api/auth/session', { credentials: 'same-origin' });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error?.message || 'Could not load your session.');
    session = payload.data;
    return session!;
}

export async function api<T>(path: string, method = 'GET', body?: unknown): Promise<T> {
    if (!session) await loadSession();
    const response = await fetch(path, {
        method,
        credentials: 'same-origin',
        headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': session!.csrf },
        body: body === undefined ? undefined : JSON.stringify(body),
    });
    const payload = await response.json();
    if (!response.ok) {
        if (response.status === 401 || response.status === 403) session = null;
        throw new Error(payload.error?.message || 'The request failed. Please try again.');
    }
    if (path.startsWith('/api/auth/')) session = payload.data;
    return payload.data as T;
}
