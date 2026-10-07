export interface User { id: number; name: string; email: string; }
export interface Project { id: number; owner_id: number; name: string; description: string; }
export type TaskStatus = 'todo' | 'doing' | 'done';
export interface Task { id: number; project_id: number; title: string; status: TaskStatus; due_date: string | null; }
export interface Session { user: User | null; csrf: string; }
export interface Article { id: string; title: string; slug: string; summary: string; body?: string; }
