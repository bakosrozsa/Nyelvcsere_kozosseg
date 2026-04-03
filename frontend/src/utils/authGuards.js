export const shouldRedirectToLogin = ({ requiresAuth, isAuthenticated, redirectPath }) => {
  if (requiresAuth && !isAuthenticated) {
    return { name: 'Login', query: { redirect: redirectPath } }
  }
  return null
}

export const shouldRedirectFromAuthPages = ({ routeName, isAuthenticated }) => {
  if ((routeName === 'Login' || routeName === 'Register') && isAuthenticated) {
    return { name: 'Dashboard' }
  }
  return null
}
