const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://qol-api-service-450135571603.us-central1.run.app/api/v1'

async function fetchFromApi(endpoint, resourceName, params = {}, options = {}) {
  try {
    let url = `${API_BASE_URL}/${endpoint}`
    if (Object.keys(params).length > 0) {
      url += `?${new URLSearchParams(params).toString()}`
    }
    const response = await fetch(url, options)
    if (!response.ok) {
      throw new Error(`Error with ${resourceName}: ${response.statusText}`)
    }
    return await response.json()
  } catch (err) {
    if (err?.name === 'AbortError') {
      throw err
    }
    console.error(`Error fetching ${resourceName}:`, err)
    throw err
  }
}

export const fetchIndicators = (options) => fetchFromApi('metadata/indicators', 'indicators', {}, options)
export const fetchYears = (indicator, options) => fetchFromApi('metadata/years', 'years', { indicator }, options)
export const fetchWorldGeometry = (options) => fetchFromApi('metadata/world-geometry', 'world geometry', {}, options)
export const fetchIndicatorData = (indicator_name, start_year, end_year, sort_by, options) =>
  fetchFromApi('data/', 'data', { indicator_name, start_year, end_year, sort_by }, options)
