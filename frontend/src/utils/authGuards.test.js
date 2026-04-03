import { describe, expect, it } from 'vitest'

import { shouldRedirectFromAuthPages, shouldRedirectToLogin } from './authGuards'

describe('authGuards', () => {
  it('redirects guests away from protected routes', () => {
    const result = shouldRedirectToLogin({
      requiresAuth: true,
      isAuthenticated: false,
      redirectPath: '/sessions',
    })

    expect(result).toEqual({ name: 'Login', query: { redirect: '/sessions' } })
  })

  it('does not redirect when route is public', () => {
    const result = shouldRedirectToLogin({
      requiresAuth: false,
      isAuthenticated: false,
      redirectPath: '/',
    })

    expect(result).toBeNull()
  })

  it('redirects authenticated users away from login/register', () => {
    const result = shouldRedirectFromAuthPages({
      routeName: 'Login',
      isAuthenticated: true,
    })

    expect(result).toEqual({ name: 'Dashboard' })
  })

  it('allows navigation for authenticated users on protected routes', () => {
    const result = shouldRedirectToLogin({
      requiresAuth: true,
      isAuthenticated: true,
      redirectPath: '/dashboard',
    })

    expect(result).toBeNull()
  })
})
