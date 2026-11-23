<template>
  <div class="chat-wrap" :class="{ embedded }">
    <aside class="sessions">
      <div class="sessions-head">
        <strong>{{ scope === 'all' ? '全部会话' : '我的会话' }}</strong>
        <el-button v-if="!readonly" type="primary" size="small" @click="newSession">新会话</el-button>
      </div>
      <div v-if="!sessions.length" class="empty-side">还没有会话</div>
      <div
        v-for="item in sessions"
        :key="item.id"
        class="session-item"
        :class="{ active: item.id === currentId }"
        @click="openSession(item.id)"
      >
        <div>
          <b>{{ item.title }}</b>
          <p v-if="scope === 'all'">{{ item.nickname }} · {{ item.username }}</p>
          <span>{{ item.update_time }}</span>
        </div>
        <el-icon v-if="!readonly || scope === 'all'" @click.stop="removeSession(item.id)"><Delete /></el-icon>
      </div>
    </aside>
    <section class="dialog">
      <div ref="scroller" class="messages">
        <div v-if="!messages.length" class="welcome">
          <img src="@/assets/logos/ai.svg" alt="" />
          <h3>你好，我是智能电商客服</h3>
          <p>可以咨询优惠、积分、退货和物流，也可以查订单、识别图片或升级工单。</p>
        </div>
        <div v-for="(item, index) in messages" :key="index" class="bubble-row" :class="item.role">
          <div class="bubble">
            <div v-if="item.role === 'assistant'" class="meta">
              <el-tag v-if="item.agent_name" size="small" effect="dark">{{ item.agent_name }}</el-tag>
              <el-tag v-if="item.intent" size="small" type="warning">{{ intentMap[item.intent] || item.intent }}</el-tag>
            </div>
            <div v-if="item.images?.length" class="pics">
              <el-image v-for="url in item.images" :key="url" :src="url" :preview-src-list="item.images" fit="cover" />
            </div>
            <div v-if="item.waiting" class="typing">
              <span>{{ waitText }}</span>
              <span class="dots" aria-hidden="true"><i></i><i></i><i></i></span>
            </div>
            <div v-else-if="item.role === 'assistant'" class="md" v-html="render(item.content)"></div>
            <div v-else class="text">{{ item.content }}</div>
            <div v-if="item.sources?.length" class="sources">
              参考：
              <span v-for="source in item.sources" :key="source.title">{{ source.category }} / {{ source.title }}</span>
            </div>
          </div>
        </div>
      </div>
      <div v-if="!readonly" class="composer">
        <div class="quick">
          <el-button v-for="item in quicks" :key="item" size="small" round @click="send(item)">{{ item }}</el-button>
        </div>
        <div v-if="pending.length" class="pending">
          <div v-for="(item, index) in pending" :key="item.url" class="pending-item">
            <el-image :src="item.url" fit="cover" />
            <el-icon @click="pending.splice(index, 1)"><Close /></el-icon>
          </div>
        </div>
        <div class="input-row">
          <el-upload :show-file-list="false" accept="image/*" :http-request="onImage">
            <el-button circle :icon="Picture" />
          </el-upload>
          <el-input v-model="input" type="textarea" :rows="2" resize="none" placeholder="请输入问题，可同时上传商品或包裹图片" @keydown.enter.exact.prevent="send()" />
          <el-button type="primary" class="send" :loading="sending" @click="send()">发送</el-button>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { nextTick, onMounted, onUnmounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Picture } from '@element-plus/icons-vue'
import MarkdownIt from 'markdown-it'
import { createSession, deleteSession, getMessages, getSessions, uploadImage } from '@/api'
import { useUserStore } from '@/stores/user'
import { intentMap } from '@/utils/options'

const props = defineProps({
  scope: { type: String, default: 'mine' },
  readonly: { type: Boolean, default: false },
  embedded: { type: Boolean, default: false },
})

const store = useUserStore()
const md = new MarkdownIt({ breaks: true, linkify: true })
const sessions = ref([])
const messages = ref([])
const currentId = ref(null)
const input = ref('')
const pending = ref([])
const sending = ref(false)
const scroller = ref()
const quicks = ['退货政策是怎样的？', '积分怎么获取和使用？', '帮我查一下最近的订单', '快递一般几天能到？', '商品破损了怎么办？']
const waitPhrases = ['正在理解您的问题', '正在查找相关信息', '马上为您整理回复']
const waitText = ref(waitPhrases[0])
let waitTimer = 0

/** 渲染 Markdown */
function render(content) {
  return md.render(content || '')
}

/** 开始展示等待提示，并轮换友好文案 */
function startWaitHint() {
  let index = 0
  waitText.value = waitPhrases[0]
  window.clearInterval(waitTimer)
  waitTimer = window.setInterval(() => {
    index = (index + 1) % waitPhrases.length
    waitText.value = waitPhrases[index]
  }, 1600)
}

/** 结束等待提示 */
function stopWaitHint(assistant) {
  if (assistant) assistant.waiting = false
  window.clearInterval(waitTimer)
  waitTimer = 0
}

/** 滚动到最新消息 */
async function scrollBottom() {
  await nextTick()
  if (scroller.value) scroller.value.scrollTop = scroller.value.scrollHeight
}

/** 加载会话列表 */
async function loadSessions() {
  const res = await getSessions(props.scope)
  sessions.value = res.data || []
}

/** 打开会话 */
async function openSession(id) {
  currentId.value = id
  const res = await getMessages(id)
  messages.value = res.data || []
  scrollBottom()
}

/** 新建会话 */
async function newSession() {
  const res = await createSession()
  currentId.value = res.data.id
  messages.value = []
  await loadSessions()
}

/** 删除会话 */
async function removeSession(id) {
  await ElMessageBox.confirm('确定删除该会话吗？', '提示', { type: 'warning' })
  await deleteSession(id)
  if (currentId.value === id) {
    currentId.value = null
    messages.value = []
  }
  await loadSessions()
}

/** 上传聊天图片 */
async function onImage(option) {
  if (pending.value.length >= 3) {
    ElMessage.warning('最多上传3张图片')
    return
  }
  const res = await uploadImage(option.file, 'chat')
  pending.value.push({ url: res.data.url })
}

/** 发送消息并读取流式回复 */
async function send(text) {
  const content = (text ?? input.value).trim()
  const images = pending.value.map((item) => item.url)
  if ((!content && !images.length) || sending.value || props.readonly) return
  if (!currentId.value) await newSession()
  messages.value.push({ role: 'user', content, images: [...images], sources: [] })
  const assistant = reactive({
    role: 'assistant',
    content: '',
    images: [],
    intent: '',
    agent_name: '',
    sources: [],
    waiting: true,
  })
  messages.value.push(assistant)
  input.value = ''
  pending.value = []
  sending.value = true
  startWaitHint()
  scrollBottom()
  try {
    const response = await fetch(`/api/chat/sessions/${currentId.value}/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${store.token}`,
      },
      body: JSON.stringify({ content, image_urls: images }),
    })
    if (!response.ok) {
      const body = await response.json().catch(() => ({}))
      throw new Error(body.msg || '发送失败')
    }
    const reader = response.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let buffer = ''
    while (true) {
      const { value, done } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const parts = buffer.split('\n\n')
      buffer = parts.pop() || ''
      for (const part of parts) {
        const line = part.split('\n').find((item) => item.startsWith('data:'))
        if (!line) continue
        const event = JSON.parse(line.slice(5).trim())
        if (event.type === 'delta' && event.content) {
          stopWaitHint(assistant)
          assistant.content += event.content
        }
        if (event.type === 'intent') assistant.intent = event.intent
        if (event.type === 'agent') assistant.agent_name = event.agent
        if (event.type === 'sources') assistant.sources = event.sources || []
        if (event.type === 'done') {
          stopWaitHint(assistant)
          if (event.answer) assistant.content = event.answer
          assistant.intent = event.intent || assistant.intent
          assistant.agent_name = event.agent || assistant.agent_name
          assistant.sources = event.sources || assistant.sources
        }
        if (event.type === 'error') {
          stopWaitHint(assistant)
          assistant.content = assistant.content || event.message
          ElMessage.error(event.message)
        }
        scrollBottom()
      }
    }
    await loadSessions()
  } catch (error) {
    stopWaitHint(assistant)
    assistant.content = assistant.content || error.message
    ElMessage.error(error.message || '发送失败')
  } finally {
    stopWaitHint(assistant)
    sending.value = false
    scrollBottom()
  }
}

onMounted(async () => {
  await loadSessions()
  if (sessions.value.length) openSession(sessions.value[0].id)
})

onUnmounted(() => stopWaitHint())
</script>

<style scoped>
.chat-wrap {
  height: calc(100vh - 112px);
  display: flex;
  gap: 16px;
}

.chat-wrap.embedded {
  height: calc(100vh - 176px);
}

.sessions,
.dialog {
  background: #fff;
  border-radius: 18px;
  box-shadow: 0 10px 30px rgba(73, 68, 140, 0.06);
}

.sessions {
  width: 280px;
  flex: 0 0 280px;
  padding: 14px;
  overflow: auto;
}

.sessions-head,
.session-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.session-item {
  gap: 8px;
  margin-top: 8px;
  padding: 10px 12px;
  border-radius: 12px;
  cursor: pointer;
}

.session-item.active,
.session-item:hover {
  background: #f4f1ff;
}

.session-item b,
.session-item p,
.session-item span {
  display: block;
}

.session-item p,
.session-item span,
.empty-side {
  color: #8a90a6;
  font-size: 12px;
  margin: 4px 0 0;
}

.dialog {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.messages {
  flex: 1;
  overflow: auto;
  padding: 22px;
}

.welcome {
  text-align: center;
  color: #6d7388;
  margin-top: 48px;
}

.welcome img {
  width: 72px;
  height: 72px;
}

.bubble-row {
  display: flex;
  margin-bottom: 16px;
}

.bubble-row.user {
  justify-content: flex-end;
}

.bubble {
  max-width: 76%;
  padding: 12px 14px;
  border-radius: 16px;
  background: #f5f7fb;
}

.user .bubble {
  background: linear-gradient(135deg, #6d5efc, #8d7bff);
  color: #fff;
}

.meta {
  display: flex;
  gap: 6px;
  margin-bottom: 8px;
}

.text {
  white-space: pre-wrap;
  line-height: 1.6;
}

.typing {
  display: flex;
  align-items: center;
  gap: 8px;
  min-height: 24px;
  color: #6d7388;
  line-height: 1.6;
}

.dots {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.dots i {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #6d5efc;
  animation: typing-bounce 1.2s infinite ease-in-out;
}

.dots i:nth-child(2) {
  animation-delay: 0.15s;
}

.dots i:nth-child(3) {
  animation-delay: 0.3s;
}

@keyframes typing-bounce {
  0%,
  80%,
  100% {
    transform: translateY(0);
    opacity: 0.35;
  }

  40% {
    transform: translateY(-4px);
    opacity: 1;
  }
}

.md :deep(p) {
  margin: 0 0 8px;
  line-height: 1.7;
}

.pics,
.pending {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.pics :deep(.el-image),
.pending-item {
  width: 92px;
  height: 92px;
  border-radius: 10px;
  overflow: hidden;
}

.pending-item {
  position: relative;
}

.pending-item .el-icon {
  position: absolute;
  top: 4px;
  right: 4px;
  color: #fff;
  background: rgba(0, 0, 0, 0.45);
  border-radius: 50%;
  cursor: pointer;
}

.sources {
  margin-top: 8px;
  color: #6d5efc;
  font-size: 12px;
}

.sources span {
  margin-right: 8px;
}

.composer {
  border-top: 1px solid #f0f2f8;
  padding: 12px 14px 14px;
}

.quick {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 10px;
}

.input-row {
  display: flex;
  gap: 10px;
  align-items: flex-end;
}

.input-row .el-textarea {
  flex: 1;
}

.send {
  height: 52px;
  width: 88px;
  border: none;
  background: linear-gradient(90deg, #6d5efc, #ff5d8f);
}
</style>
