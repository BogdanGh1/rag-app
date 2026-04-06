import type { MeResponse, TokenResponse } from '../types/api'
import { apiClient } from './client'

export async function login(username: string, password: string): Promise<TokenResponse> {
  const params = new URLSearchParams({ username, password })
  const { data } = await apiClient.post<TokenResponse>('/auth/login', params, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
  return data
}

export async function register(
  username: string,
  email: string,
  password: string,
): Promise<TokenResponse> {
  const { data } = await apiClient.post<TokenResponse>('/auth/register', {
    username,
    email,
    password,
  })
  return data
}

export async function getMe(): Promise<MeResponse> {
  const { data } = await apiClient.get<MeResponse>('/auth/me')
  return data
}
