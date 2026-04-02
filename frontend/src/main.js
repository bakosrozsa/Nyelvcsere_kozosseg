import { createApp } from 'vue'
import axios from 'axios'
import './style.css'
import App from './App.vue'
import router from './router'

const AUTH_LOGOUT_EVENT = 'auth:logout'

let logoutInProgress = false

const forceLogoutOnUnauthorized = () => {
	const hasStoredToken = !!(localStorage.getItem('token') || localStorage.getItem('access_token'))
	if (!hasStoredToken || logoutInProgress) {
		return
	}

	logoutInProgress = true
	localStorage.removeItem('token')
	localStorage.removeItem('access_token')
	window.dispatchEvent(new CustomEvent(AUTH_LOGOUT_EVENT, { detail: { reason: 'unauthorized' } }))

	if (router.currentRoute.value.name !== 'Login') {
		router.push({ name: 'Login' }).finally(() => {
			logoutInProgress = false
		})
		return
	}

	logoutInProgress = false
}

const nativeFetch = window.fetch.bind(window)
window.fetch = async (input, init) => {
	const response = await nativeFetch(input, init)
	if (response.status === 401) {
		forceLogoutOnUnauthorized()
	}
	return response
}

axios.interceptors.response.use(
	(response) => response,
	(error) => {
		if (error?.response?.status === 401) {
			forceLogoutOnUnauthorized()
		}
		return Promise.reject(error)
	}
)

const app = createApp(App)

app.use(router)
app.mount('#app')
