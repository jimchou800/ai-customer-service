import request from '@/utils/request'

/** 登录 */
export function login(data) {
  return request.post('/api/auth/login', data)
}

/** 注册 */
export function register(data) {
  return request.post('/api/auth/register', data)
}

/** 当前用户 */
export function getMe() {
  return request.get('/api/auth/me')
}

/** 修改个人资料 */
export function updateProfile(data) {
  return request.put('/api/profile', data)
}

/** 上传头像 */
export function uploadAvatar(file) {
  const form = new FormData()
  form.append('file', file)
  return request.post('/api/profile/avatar', form)
}

/** 修改密码 */
export function updatePassword(data) {
  return request.put('/api/profile/password', data)
}

/** 控制台统计 */
export function getOverview() {
  return request.get('/api/dashboard/overview')
}

/** 上传图片 */
export function uploadImage(file, folder) {
  const form = new FormData()
  form.append('file', file)
  form.append('folder', folder)
  return request.post('/api/upload/image', form)
}

export function getProducts(params) {
  return request.get('/api/products', { params })
}

export function saveProduct(data, id) {
  return id ? request.put(`/api/products/${id}`, data) : request.post('/api/products', data)
}

export function deleteProduct(id) {
  return request.delete(`/api/products/${id}`)
}

export function getOrders(params) {
  return request.get('/api/orders', { params })
}

export function shipOrder(id, data) {
  return request.put(`/api/orders/${id}/ship`, data)
}

export function updateOrderStatus(id, status) {
  return request.put(`/api/orders/${id}/status`, { status })
}

export function getKnowledge(params) {
  return request.get('/api/knowledge', { params })
}

export function saveKnowledge(data, id) {
  return id ? request.put(`/api/knowledge/${id}`, data) : request.post('/api/knowledge', data)
}

export function deleteKnowledge(id) {
  return request.delete(`/api/knowledge/${id}`)
}

export function uploadKnowledgeFile(file) {
  const form = new FormData()
  form.append('file', file)
  return request.post('/api/knowledge/upload', form)
}

export function vectorizeKnowledge(id) {
  return request.post(`/api/knowledge/${id}/vectorize`)
}

export function rebuildKnowledge() {
  return request.post('/api/knowledge/rebuild')
}

export function searchKnowledge(data) {
  return request.post('/api/knowledge/search', data)
}

export function getTickets(params) {
  return request.get('/api/tickets', { params })
}

export function handleTicket(id, data) {
  return request.put(`/api/tickets/${id}`, data)
}

export function getUsers(params) {
  return request.get('/api/users', { params })
}

export function saveUser(data, id) {
  return id ? request.put(`/api/users/${id}`, data) : request.post('/api/users', data)
}

export function resetUserPassword(id) {
  return request.put(`/api/users/${id}/reset-password`)
}

export function deleteUser(id) {
  return request.delete(`/api/users/${id}`)
}

export function getSessions(scope = 'mine') {
  return request.get('/api/chat/sessions', { params: { scope } })
}

export function createSession() {
  return request.post('/api/chat/sessions')
}

export function deleteSession(id) {
  return request.delete(`/api/chat/sessions/${id}`)
}

export function getMessages(id) {
  return request.get(`/api/chat/sessions/${id}/messages`)
}
