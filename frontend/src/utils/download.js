import axios from 'axios'

const TOKEN_KEY = 'token'

export function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

export async function downloadExport(url, params, defaultFilename) {
  const token = localStorage.getItem(TOKEN_KEY)
  const response = await axios.get(url, {
    params,
    responseType: 'blob',
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  })

  // ✅ 先拿到headers，再做json错误判断
  const disposition = response.headers['content-disposition']
  const blob = response.data

  // 后端报错时返回json blob，没有content‑disposition
  if (blob.type?.includes('application/json') && !disposition) {
    const text = await blob.text()
    const payload = JSON.parse(text)
    throw new Error(payload.message || '导出失败')
  }

  let filename = defaultFilename
  if (disposition) {
    const match = disposition.match(/filename[*]?=(?:UTF-8''|"?)([^";]+)/i)
    if (match?.[1]) {
      filename = decodeURIComponent(match[1].replace(/"/g, ''))
    }
  }

  downloadBlob(blob, filename)
}