export const formatIndicatorName = (name) => {
  if (!name) return ''
  let formatted = name
    .replace(/-/g, ' ')
    .replace(/\b\d{1,3}(?=(\d{3})+(?!\d))/g, '$&,')
    .replace(/by country/gi, '')
    .replace(/worldbank/gi, '')
    .replace(/unodc/gi, '')
    .trim()
    .split(/\s+/)
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ')

  formatted = formatted
    .replace(/Children Aged 5 17 Years Engaged In Labor/gi, 'Children Aged 5 to 17 Years Engaged in Labor')
    .replace(/Researchers In Rd Per Million People/gi, 'Researchers In R&D Per Million People')
    .replace(/Children Per Woman Un/gi, 'Children Per Woman')
    .replace(/Pm25 Air Pollution/gi, 'PM2.5 Air Pollution (Fine Particulate Matter)')
    .replace(/\bGdp\b/gi, 'GDP')
    .replace(/\bHdi\b/gi, 'HDI')
    .replace(/\bCo2\b/gi, 'CO₂')

  return formatted.trim()
}

export const COLOR_PALETTE = [
  '#fef08a',
  '#fde047',
  '#facc15',
  '#fbbf24',
  '#fb923c',
  '#f97316',
  '#ea580c',
  '#dc2626',
  '#991b1b'
]

export function getColorForValue(value, bounds) {
  if (value == null) return '#1e293b'
  const { min, max } = bounds
  const ratio = max === min ? 0.5 : (value - min) / (max - min)
  const idx = Math.min(Math.floor(ratio * COLOR_PALETTE.length), COLOR_PALETTE.length - 1)
  return COLOR_PALETTE[idx]
}

export const getFeatureStyle = (feature, bounds) => {
  const hasValue = feature.properties.value != null
  return {
    fillColor: getColorForValue(feature.properties.value, bounds),
    weight: 0.8,
    opacity: 1,
    color: hasValue ? '#0f172a' : '#334155',
    fillOpacity: hasValue ? 0.82 : 0.45
  }
}

const escapeHtml = (str) =>
  String(str ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')

export const bindFeatureInteractions = (feature, layer) => {
  const val = feature.properties.value
  const safeName = escapeHtml(feature.properties.name)
  const formattedVal =
    val == null
      ? 'No data'
      : Number(val).toLocaleString('en-US', {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2
        })
  const tooltipHtml = `<div class="map-tooltip-inner"><span class="map-tooltip-country">${safeName}</span><span class="map-tooltip-value">${formattedVal}</span></div>`
  layer.bindTooltip(tooltipHtml, { sticky: true, className: 'dark-slate-tooltip' })
  layer.on({
    mouseover: (e) =>
      e.target.setStyle({
        weight: 2.2,
        color: '#38bdf8',
        fillOpacity: val == null ? 0.6 : 0.95
      }),
    mouseout: (e) =>
      e.target.setStyle({
        weight: 0.8,
        color: val != null ? '#0f172a' : '#334155',
        fillOpacity: val != null ? 0.82 : 0.45
      })
  })
}

export function mergeGeojsonWithData(geojson, dataRows) {
  if (!geojson) return null
  if (!dataRows || dataRows.length === 0) {
    const clone = JSON.parse(JSON.stringify(geojson))
    clone.features.forEach((f) => (f.properties.value = null))
    return clone
  }
  const valueMap = new Map(dataRows.map((row) => [row.iso_a3, row.value]))
  const clone = JSON.parse(JSON.stringify(geojson))
  clone.features.forEach((f) => {
    f.properties.value = valueMap.get(f.properties.iso_a3) ?? null
  })
  return clone
}

export function getSliderTrackStyle(fromYear, toYear, minYear, maxYear) {
  if (!minYear || !maxYear || minYear === maxYear) return { background: '#38bdf8' }
  const startPct = ((fromYear - minYear) / (maxYear - minYear)) * 100
  const endPct = ((toYear - minYear) / (maxYear - minYear)) * 100
  if (isNaN(startPct) || isNaN(endPct)) return { background: '#334155' }
  return {
    background: `linear-gradient(to right, #334155 ${startPct}%, #38bdf8 ${startPct}%, #3b82f6 ${endPct}%, #334155 ${endPct}%)`
  }
}

export function computeValueBounds(dataRows) {
  const validValues = dataRows.map((r) => r.value).filter((v) => v != null)
  if (validValues.length === 0) return { min: 0, max: 1 }
  const min = Math.min(...validValues)
  const max = Math.max(...validValues)
  return { min, max: min === max ? min + 1 : max }
}

export function debounce(fn, delay = 400) {
  let timer
  const debounced = (...args) => {
    clearTimeout(timer)
    timer = setTimeout(() => fn(...args), delay)
  }
  debounced.cancel = () => clearTimeout(timer)
  return debounced
}

export function toggleSortOrder(currentSort, column) {
  const [col, dir] = currentSort.split('_')
  return col === column ? `${column}_${dir === 'asc' ? 'desc' : 'asc'}` : `${column}_asc`
}

export function downloadCsv(rows, indicatorName, fromYear, toYear) {
  if (!rows || rows.length === 0) {
    alert('No data available to download.')
    return
  }
  const headers = ['Country', 'Average Value']
  const csvRows = rows.map((r) => {
    const country = `"${r.name.replace(/"/g, '""')}"`
    const val = r.value == null ? 'N/A' : parseFloat(r.value).toFixed(2)
    return [country, val].join(',')
  })
  const csvContent = [headers.join(','), ...csvRows].join('\n')
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  const filename = `${indicatorName.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_${fromYear}-${toYear}.csv`
  link.setAttribute('download', filename)
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}
