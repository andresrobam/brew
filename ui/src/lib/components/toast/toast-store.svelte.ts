export const toasts: { [key: string]: ToastInfo & { id: string } } = $state({})

const timeouts: { [key: string]: number } = {}

const defaultTimeout = 1500

export function success(text: string) {
	newToast({ text, timeout: defaultTimeout, style: 'success' })
}

export function error(text: string) {
	newToast({ text, timeout: defaultTimeout, style: 'error' })
}

export function newToast(toast: ToastInfo) {
	const id = (Math.random() + 1).toString(36)
	if (toast.timeout != null) {
		timeouts[id] = setTimeout(() => removeToast(id), toast.timeout)
	}
	toasts[id] = { ...toast, id }
}

export function removeToast(id: string) {
	if (timeouts[id] != null) {
		clearTimeout(timeouts[id])
	}
	delete toasts[id]
}
