const BASE_API_URL = '/api'

type QueryParams = {
    [key: string]: string | number | boolean
}

function getUrlWithParams(endpoint: string, params: QueryParams): string {
    const stringParams: Record<string, string> = {}
    Object.entries(params).forEach(([key, value]) => stringParams[key] = value.toString())
    return BASE_API_URL + endpoint + '?' + new URLSearchParams(stringParams)
}

export async function getJson<ReturnType>(endpoint: string): Promise<ReturnType> {
    return await fetch(BASE_API_URL+endpoint)
    .then(response => {
        return response.json() as ReturnType
    })
}

export async function putWithParams(endpoint: string, params: QueryParams): Promise<void> {
    await fetch(getUrlWithParams(endpoint, params), {method: 'PUT'})
}