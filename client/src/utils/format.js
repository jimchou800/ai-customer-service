import dayjs from 'dayjs'

/** 日期时间显示为 2026-11-02 17:25:17 */
export function formatDateTime(value) {
  if (!value) return ''
  const time = dayjs(value)
  return time.isValid() ? time.format('YYYY-MM-DD HH:mm:ss') : String(value)
}

/** 日期显示为 2026-11-02 */
export function formatDate(value) {
  if (!value) return ''
  const time = dayjs(value)
  return time.isValid() ? time.format('YYYY-MM-DD') : String(value).slice(0, 10)
}
