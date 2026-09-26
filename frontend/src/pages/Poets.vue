<template>
  <div class="poets-page bg-xuanzhi">

    <!-- ═══ 列表态：诗人角色卡 ═══ -->
    <div v-if="mode === 'list'" class="poet-list">
      <p class="page-intro">选一位诗人对坐清谈，或邀几位同席雅集</p>

      <!-- 同席对谈入口 -->
      <div class="roundtable-entry animate-fadeUp" @click="enterGroup">
        <span class="roundtable-icon">🎭</span>
        <div class="roundtable-info">
          <span class="roundtable-title">同席雅集</span>
          <span class="roundtable-sub">邀多位诗人围坐：清谈或行飞花令</span>
        </div>
        <van-icon name="arrow" class="roundtable-arrow" />
      </div>

      <div class="poet-grid">
        <div
          v-for="(card, i) in cards"
          :key="card.id"
          class="poet-card animate-fadeUp"
          :style="{ animationDelay: `${i * 0.05}s` }"
          @click="enterChat(card)"
        >
          <div class="poet-avatar">{{ card.avatar }}</div>
          <div class="poet-info">
            <div class="poet-name-row">
              <span class="poet-name">{{ card.name }}</span>
              <span class="poet-title">{{ card.title }}</span>
            </div>
            <span class="poet-dynasty">{{ card.dynasty }}</span>
            <p class="poet-masterpiece">「{{ card.masterpieces?.[0]?.intro }}」</p>
          </div>
        </div>
      </div>

      <van-loading v-if="loadingCards" class="poet-loading" />
      <p v-if="!loadingCards && !cards.length" class="poet-empty">暂无诗人，稍后再来。</p>
    </div>

    <!-- ═══ 对话态：与诗人聊天 ═══ -->
    <div v-else-if="mode === 'chat'" class="chat-view">
      <div class="chat-header">
        <button class="chat-back" @click="backToList">
          <van-icon name="arrow-left" />
        </button>
        <div class="chat-poet-avatar">{{ currentCard.avatar }}</div>
        <div class="chat-poet-info">
          <span class="chat-poet-name">{{ currentCard.name }}</span>
          <span class="chat-poet-title">{{ currentCard.title }} · {{ currentCard.dynasty }}</span>
        </div>
      </div>

      <div ref="chatBodyRef" class="chat-body">
        <div
          v-for="(m, i) in messages"
          :key="i"
          class="msg-row"
          :class="m.role"
        >
          <div class="msg-bubble">
            <p class="msg-text">{{ m.content }}</p>
            <button
              v-if="m.role === 'assistant'"
              class="msg-speak"
              @click="speakMsg(m.content)"
            >
              <van-icon
                :name="(speakingNow === m.content && speakingState) ? 'stop-circle-o' : 'volume-o'"
              />
            </button>
          </div>
        </div>

        <div v-if="chatting" class="msg-row assistant">
          <div class="msg-bubble typing">正在斟酌词句…</div>
        </div>
      </div>

      <div class="chat-input-bar">
        <input
          v-model="draft"
          class="chat-input"
          placeholder="与 TA 说点什么…"
          :disabled="chatting"
          @keyup.enter="sendMessage"
        />
        <button
          class="chat-send"
          :disabled="!draft.trim() || chatting"
          @click="sendMessage"
        >发送</button>
      </div>
    </div>

    <!-- ═══ 群聊态：同席雅集（对谈 / 飞花令） ═══ -->
    <div v-else class="group-view">
      <div class="chat-header">
        <button class="chat-back" @click="backToList">
          <van-icon name="arrow-left" />
        </button>
        <div class="chat-poet-avatar group-header-avatar">🎭</div>
        <div class="chat-poet-info">
          <span class="chat-poet-name">同席雅集</span>
          <span class="chat-poet-title">邀君围坐，各抒胸臆</span>
        </div>
      </div>

      <div class="group-tabs">
        <button
          class="group-tab"
          :class="{ active: groupMode === 'talk' }"
          @click="switchGroupMode('talk')"
        >谈诗论道</button>
        <button
          class="group-tab"
          :class="{ active: groupMode === 'feihua' }"
          @click="switchGroupMode('feihua')"
        >飞花行令</button>
      </div>

      <!-- ── 对谈模式 ── -->
      <template v-if="groupMode === 'talk'">
        <div v-if="!groupStarted" class="group-setup">
          <p class="group-label">择入席诗人（2~4 位）</p>
          <div class="group-pick-grid">
            <div
              v-for="card in cards"
              :key="card.id"
              class="group-pick"
              :class="{ selected: groupSelected.includes(card.id) }"
              @click="togglePick(card.id)"
            >
              <span class="group-pick-avatar">{{ card.avatar }}</span>
              <span class="group-pick-name">{{ card.name }}</span>
              <van-icon v-if="groupSelected.includes(card.id)" name="success" class="group-pick-check" />
            </div>
          </div>

          <input
            v-model="groupTopic"
            class="chat-input group-topic"
            placeholder="拟一个话题，如：何为家国？人生几何？"
            @keyup.enter="startGroup"
          />
          <button
            class="chat-send group-start"
            :disabled="groupSelected.length < 2 || groupChatting"
            @click="startGroup"
          >
            {{ groupChatting ? '众人落座中…' : '开席' }}
          </button>
        </div>

        <div v-else ref="groupBodyRef" class="group-body">
          <p v-if="groupTopic" class="group-topic-tag">🎙 话题：{{ groupTopic }}</p>

          <div v-for="(m, i) in groupMessages" :key="i" class="group-msg">
            <div class="group-msg-head">
              <span class="group-msg-avatar">{{ m.avatar }}</span>
              <span class="group-msg-name">{{ m.poet_name }}</span>
              <span class="group-msg-dynasty">{{ m.dynasty }}</span>
              <button class="msg-speak" @click="speakGroupMsg(m)">
                <van-icon name="volume-o" />
              </button>
            </div>
            <div class="group-msg-bubble">
              <p class="msg-text">{{ m.content }}</p>
            </div>
          </div>

          <div v-if="groupChatting" class="msg-row assistant">
            <div class="msg-bubble typing">众人正在吟咏…</div>
          </div>

          <div v-if="!groupChatting && groupMessages.length" class="group-actions">
            <button class="chat-send" @click="anotherRound">再来一轮</button>
          </div>
        </div>
      </template>

      <!-- ── 飞花令模式 ── -->
      <template v-else>
        <div v-if="!feihuaStarted" class="group-setup">
          <p class="group-label">择入席诗人（2~4 位）</p>
          <div class="group-pick-grid">
            <div
              v-for="card in cards"
              :key="card.id"
              class="group-pick"
              :class="{ selected: groupSelected.includes(card.id) }"
              @click="togglePick(card.id)"
            >
              <span class="group-pick-avatar">{{ card.avatar }}</span>
              <span class="group-pick-name">{{ card.name }}</span>
              <van-icon v-if="groupSelected.includes(card.id)" name="success" class="group-pick-check" />
            </div>
          </div>

          <div class="feihua-keyword-box">
            <span class="feihua-keyword-label">令</span>
            <span class="feihua-keyword">{{ feihuaKeyword }}</span>
            <button class="feihua-shuffle" @click="shuffleKeyword">换令</button>
          </div>

          <button
            class="chat-send group-start"
            :disabled="groupSelected.length < 2 || feihuaChatting"
            @click="startFeihua"
          >
            {{ feihuaChatting ? '诗人行令中…' : '行令' }}
          </button>
        </div>

        <div v-else ref="feihuaBodyRef" class="group-body">
          <p class="group-topic-tag">🎯 令字：{{ feihuaKeyword }}</p>

          <div v-for="(m, i) in feihuaMessages" :key="i" class="feihua-msg">
            <div class="group-msg-head">
              <span class="group-msg-avatar">{{ m.avatar }}</span>
              <span class="group-msg-name">{{ m.poet_name }}</span>
              <span class="group-msg-dynasty">{{ m.dynasty }}</span>
              <button class="msg-speak" @click="speakFeihuaMsg(m)">
                <van-icon name="volume-o" />
              </button>
            </div>
            <div class="feihua-msg-body">
              <p v-if="m.comment" class="feihua-comment">{{ m.comment }}</p>
              <p v-if="m.line" class="feihua-line">「{{ m.line }}」</p>
              <p v-if="m.title" class="feihua-source">—— {{ m.poet_name }}《{{ m.title }}》</p>
            </div>
          </div>

          <div v-if="feihuaChatting" class="msg-row assistant">
            <div class="msg-bubble typing">诗人正在行令…</div>
          </div>

          <div v-if="!feihuaChatting && feihuaMessages.length" class="group-actions">
            <button class="chat-send ghost" @click="feihuaAgain(false)">再来一轮</button>
            <button class="chat-send" @click="feihuaAgain(true)">换令再战</button>
          </div>
        </div>
      </template>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted } from 'vue'
import { api } from '../api'
import { speak, stop, speaking } from '../composables/useSpeech'

interface Masterpiece { title: string; intro: string }
interface PoetCard {
  id: string
  name: string
  dynasty: string
  title: string
  avatar: string
  first_message: string
  masterpieces: Masterpiece[]
  voice: { rate: number; pitch: number }
}
interface GroupMsg {
  poet_id: string
  poet_name: string
  avatar: string
  dynasty: string
  voice: { rate: number; pitch: number }
  content: string
}
interface FeihuaMsg {
  poet_id: string
  poet_name: string
  avatar: string
  dynasty: string
  voice: { rate: number; pitch: number }
  line: string
  title: string
  comment: string
}

type ViewMode = 'list' | 'chat' | 'group'
type GroupMode = 'talk' | 'feihua'

const mode = ref<ViewMode>('list')
const cards = ref<PoetCard[]>([])
const loadingCards = ref(false)
const currentCard = ref<PoetCard | null>(null)
const messages = ref<{ role: 'user' | 'assistant'; content: string }[]>([])
const draft = ref('')
const chatting = ref(false)
const chatBodyRef = ref<HTMLElement | null>(null)
const speakingNow = ref('')
const speakingState = ref(false)

// 群聊（对谈）
const groupMode = ref<GroupMode>('talk')
const groupSelected = ref<string[]>([])
const groupTopic = ref('')
const groupMessages = ref<GroupMsg[]>([])
const groupChatting = ref(false)
const groupStarted = ref(false)
const groupBodyRef = ref<HTMLElement | null>(null)

// 群聊（飞花令）
const feihuaKeyword = ref('月')
const feihuaKeywords = ref<string[]>([])
const feihuaMessages = ref<FeihuaMsg[]>([])
const feihuaChatting = ref(false)
const feihuaStarted = ref(false)
const feihuaExclude = ref<string[]>([])
const feihuaBodyRef = ref<HTMLElement | null>(null)

onMounted(async () => {
  loadingCards.value = true
  try {
    const res = await api.getPoetCards()
    cards.value = res.data.data?.cards || []
  } catch {
    cards.value = []
  } finally {
    loadingCards.value = false
  }

  // 预取飞花令关键字池（70 字），随机一个初始令字
  try {
    const kres = await api.getPracticeKeywords()
    const kws = kres.data.data?.keywords || []
    if (kws.length) {
      feihuaKeywords.value = kws
      feihuaKeyword.value = kws[Math.floor(Math.random() * kws.length)]
    }
  } catch {
    // 忽略，保留默认「月」
  }
})

function enterChat(card: PoetCard) {
  mode.value = 'chat'
  currentCard.value = card
  messages.value = [{ role: 'assistant', content: card.first_message }]
  draft.value = ''
  scrollToBottom()
}

function enterGroup() {
  mode.value = 'group'
  groupMode.value = 'talk'
  groupSelected.value = []
  groupTopic.value = ''
  groupMessages.value = []
  groupStarted.value = false
  groupChatting.value = false
  feihuaMessages.value = []
  feihuaStarted.value = false
  feihuaChatting.value = false
  feihuaExclude.value = []
}

function switchGroupMode(m: GroupMode) {
  groupMode.value = m
}

function togglePick(id: string) {
  if (groupSelected.value.includes(id)) {
    groupSelected.value = groupSelected.value.filter(x => x !== id)
  } else if (groupSelected.value.length < 4) {
    groupSelected.value.push(id)
  }
}

function backToList() {
  stop()
  speakingNow.value = ''
  speakingState.value = false
  mode.value = 'list'
  currentCard.value = null
  messages.value = []
  draft.value = ''
  groupSelected.value = []
  groupTopic.value = ''
  groupMessages.value = []
  groupStarted.value = false
  groupChatting.value = false
  feihuaMessages.value = []
  feihuaStarted.value = false
  feihuaChatting.value = false
  feihuaExclude.value = []
}

async function sendMessage() {
  const text = draft.value.trim()
  if (!text || chatting.value || !currentCard.value) return
  messages.value.push({ role: 'user', content: text })
  draft.value = ''
  chatting.value = true
  scrollToBottom()
  try {
    const res = await api.poetChat({
      poet_id: currentCard.value.id,
      messages: messages.value.map(m => ({ role: m.role, content: m.content })),
    })
    const reply = res.data.data?.reply || '（诗人沉默不语）'
    messages.value.push({ role: 'assistant', content: reply })
  } catch {
    messages.value.push({ role: 'assistant', content: '（诗人暂时走神了，稍后再试）' })
  } finally {
    chatting.value = false
    scrollToBottom()
  }
}

async function startGroup() {
  if (groupSelected.value.length < 2 || groupChatting.value) return
  groupChatting.value = true
  try {
    const res = await api.poetRoundtable({
      poet_ids: groupSelected.value,
      topic: groupTopic.value.trim(),
      rounds: 1,
    })
    const msgs = res.data.data?.messages || []
    groupMessages.value = [...groupMessages.value, ...msgs]
    groupStarted.value = true
  } catch {
    groupStarted.value = true
  } finally {
    groupChatting.value = false
    scrollGroupBottom()
  }
}

async function anotherRound() {
  if (groupChatting.value) return
  groupChatting.value = true
  try {
    const res = await api.poetRoundtable({
      poet_ids: groupSelected.value,
      topic: groupTopic.value.trim(),
      rounds: 1,
      history: groupMessages.value.map(m => ({ poet_name: m.poet_name, content: m.content })),
    })
    const msgs = res.data.data?.messages || []
    groupMessages.value = [...groupMessages.value, ...msgs]
  } catch {
    // 忽略
  } finally {
    groupChatting.value = false
    scrollGroupBottom()
  }
}

function shuffleKeyword() {
  if (feihuaKeywords.value.length < 2) {
    feihuaKeyword.value = '月'
    return
  }
  let k = feihuaKeyword.value
  while (k === feihuaKeyword.value) {
    k = feihuaKeywords.value[Math.floor(Math.random() * feihuaKeywords.value.length)]
  }
  feihuaKeyword.value = k
}

async function startFeihua() {
  if (groupSelected.value.length < 2 || feihuaChatting.value) return
  feihuaChatting.value = true
  try {
    const res = await api.poetFeihualing({
      poet_ids: groupSelected.value,
      keyword: feihuaKeyword.value,
      exclude_lines: feihuaExclude.value,
    })
    const msgs = res.data.data?.messages || []
    feihuaMessages.value = [...feihuaMessages.value, ...msgs]
    msgs.forEach((m: FeihuaMsg) => {
      if (m.title && m.line) feihuaExclude.value.push(m.title + '|' + m.line)
    })
    feihuaStarted.value = true
  } catch {
    feihuaStarted.value = true
  } finally {
    feihuaChatting.value = false
    scrollFeihuaBottom()
  }
}

async function feihuaAgain(newKeyword: boolean) {
  if (feihuaChatting.value) return
  if (newKeyword) {
    feihuaMessages.value = []
    feihuaExclude.value = []
    shuffleKeyword()
  }
  await startFeihua()
}

function speakMsg(content: string) {
  if (speaking.value && speakingNow.value === content) {
    stop()
    speakingNow.value = ''
    speakingState.value = false
    return
  }
  speakingNow.value = content
  speakingState.value = true
  speak(content, currentCard.value?.voice)
  setTimeout(() => {
    if (!speaking.value) {
      speakingState.value = false
    }
  }, 1000)
}

function speakGroupMsg(m: GroupMsg) {
  if (speaking.value && speakingNow.value === m.content) {
    stop()
    speakingNow.value = ''
    speakingState.value = false
    return
  }
  speakingNow.value = m.content
  speakingState.value = true
  speak(m.content, m.voice)
  setTimeout(() => {
    if (!speaking.value) {
      speakingState.value = false
    }
  }, 1000)
}

function speakFeihuaMsg(m: FeihuaMsg) {
  const text = [m.comment, m.line].filter(Boolean).join('。')
  if (!text) return
  if (speaking.value && speakingNow.value === text) {
    stop()
    speakingNow.value = ''
    speakingState.value = false
    return
  }
  speakingNow.value = text
  speakingState.value = true
  speak(text, m.voice)
  setTimeout(() => {
    if (!speaking.value) {
      speakingState.value = false
    }
  }, 1000)
}

function scrollToBottom() {
  nextTick(() => {
    chatBodyRef.value?.scrollTo({ top: chatBodyRef.value.scrollHeight, behavior: 'smooth' })
  })
}

function scrollGroupBottom() {
  nextTick(() => {
    groupBodyRef.value?.scrollTo({ top: groupBodyRef.value.scrollHeight, behavior: 'smooth' })
  })
}

function scrollFeihuaBottom() {
  nextTick(() => {
    feihuaBodyRef.value?.scrollTo({ top: feihuaBodyRef.value.scrollHeight, behavior: 'smooth' })
  })
}
</script>

<style scoped>
.poets-page { min-height: 100vh; padding-bottom: 30px; }

/* ── 列表态 ── */
.poet-list { padding: 16px; }
.page-intro {
  font-family: var(--font-display);
  font-size: 14px; color: var(--stone);
  text-align: center; margin-bottom: 16px;
  letter-spacing: 0.05em;
}
.roundtable-entry {
  display: flex; align-items: center; gap: 12px;
  background: linear-gradient(135deg, rgba(190,63,53,0.08), rgba(190,63,53,0.02));
  border: 1px solid rgba(190,63,53,0.28);
  border-radius: var(--radius-md);
  padding: 14px 16px;
  margin-bottom: 16px;
  cursor: pointer;
  transition: all 0.2s var(--ease-out);
  box-shadow: var(--shadow-sm);
}
.roundtable-entry:hover {
  border-color: var(--cinnabar);
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}
.roundtable-icon { font-size: 30px; }
.roundtable-info { flex: 1; min-width: 0; }
.roundtable-title {
  display: block;
  font-family: var(--font-display);
  font-size: 17px; color: var(--cinnabar);
}
.roundtable-sub {
  display: block; font-size: 12px; color: var(--stone);
  margin-top: 2px;
}
.roundtable-arrow { color: var(--cinnabar); font-size: 16px; }
.poet-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}
.poet-card {
  display: flex; align-items: center; gap: 14px;
  background: #fff;
  border: 1px solid rgba(158,142,126,0.16);
  border-radius: var(--radius-md);
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s var(--ease-out);
  box-shadow: var(--shadow-sm);
}
.poet-card:hover {
  border-color: var(--cinnabar);
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}
.poet-avatar {
  width: 56px; height: 56px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  font-size: 32px;
  background: var(--parchment);
  border-radius: 50%;
  border: 1px solid rgba(158,142,126,0.2);
}
.poet-info { flex: 1; min-width: 0; }
.poet-name-row { display: flex; align-items: baseline; gap: 8px; }
.poet-name { font-family: var(--font-display); font-size: 18px; color: var(--ink); }
.poet-title { font-size: 12px; color: var(--gold); }
.poet-dynasty { font-size: 12px; color: var(--stone); display: block; margin-top: 2px; }
.poet-masterpiece {
  font-family: var(--font-serif); font-size: 13px; color: var(--ink-light);
  margin-top: 6px; line-height: 1.6;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.poet-loading { display: flex; justify-content: center; padding: 30px; }
.poet-empty { text-align: center; color: var(--stone); padding: 30px; font-size: 13px; }

/* ── 对话态 ── */
.chat-view { display: flex; flex-direction: column; height: calc(100vh - 60px); }
.chat-header {
  display: flex; align-items: center; gap: 12px;
  padding: 12px 16px;
  background: rgba(250,246,240,0.92);
  border-bottom: 1px solid rgba(158,142,126,0.15);
  position: sticky; top: 0; z-index: 10;
}
.chat-back {
  width: 34px; height: 34px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  background: none; border: none; color: var(--ink);
  font-size: 20px; cursor: pointer; border-radius: var(--radius-sm);
}
.chat-poet-avatar {
  width: 42px; height: 42px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  font-size: 24px;
  background: var(--parchment);
  border-radius: 50%;
  border: 1px solid rgba(158,142,126,0.2);
}
.group-header-avatar { font-size: 22px; }
.chat-poet-info { flex: 1; min-width: 0; }
.chat-poet-name { font-family: var(--font-display); font-size: 17px; color: var(--ink); }
.chat-poet-title { font-size: 12px; color: var(--stone); display: block; margin-top: 1px; }
.chat-body { flex: 1; overflow-y: auto; padding: 16px; }
.msg-row { display: flex; margin-bottom: 12px; }
.msg-row.user { justify-content: flex-end; }
.msg-row.assistant { justify-content: flex-start; }
.msg-bubble {
  max-width: 82%;
  padding: 10px 14px;
  border-radius: var(--radius-md);
  background: #fff;
  border: 1px solid rgba(158,142,126,0.14);
  box-shadow: var(--shadow-sm);
  position: relative;
}
.msg-row.user .msg-bubble {
  background: var(--cinnabar);
  color: #fff;
  border-color: var(--cinnabar);
}
.msg-row.user .msg-text { color: #fff; }
.msg-text {
  margin: 0; font-size: 14px; line-height: 1.7; color: var(--ink);
  white-space: pre-wrap; word-break: break-word;
}
.msg-speak {
  position: absolute; right: 6px; bottom: 6px;
  width: 24px; height: 24px;
  display: flex; align-items: center; justify-content: center;
  background: rgba(190,63,53,0.08); border: none; border-radius: 50%;
  color: var(--cinnabar); cursor: pointer; font-size: 13px;
}
.msg-speak:hover { background: rgba(190,63,53,0.16); }
.typing { color: var(--stone); font-size: 13px; padding: 8px 14px; }
.chat-input-bar {
  display: flex; gap: 10px; align-items: center;
  padding: 12px 16px;
  background: rgba(250,246,240,0.95);
  border-top: 1px solid rgba(158,142,126,0.15);
}
.chat-input {
  flex: 1;
  border: 1px solid rgba(158,142,126,0.2);
  border-radius: var(--radius-full);
  padding: 10px 16px;
  font-size: 14px; color: var(--ink);
  outline: none;
  background: #fff;
}
.chat-input:focus { border-color: var(--cinnabar); }
.chat-send {
  border: none;
  background: var(--cinnabar);
  color: #fff;
  border-radius: var(--radius-full);
  padding: 10px 20px;
  font-size: 14px; cursor: pointer;
  transition: opacity 0.2s;
}
.chat-send:disabled { opacity: 0.4; cursor: not-allowed; }

/* ── 群聊态 ── */
.group-view { display: flex; flex-direction: column; height: calc(100vh - 60px); }
.group-tabs {
  display: flex;
  padding: 8px 16px;
  gap: 8px;
  background: rgba(250,246,240,0.92);
  border-bottom: 1px solid rgba(158,142,126,0.15);
}
.group-tab {
  flex: 1;
  border: 1px solid rgba(158,142,126,0.18);
  background: #fff;
  color: var(--stone);
  border-radius: var(--radius-full);
  padding: 8px 0;
  font-size: 14px; cursor: pointer;
  transition: all 0.2s;
}
.group-tab.active {
  background: var(--cinnabar);
  color: #fff;
  border-color: var(--cinnabar);
}
.group-setup { flex: 1; overflow-y: auto; padding: 16px; }
.group-label {
  font-family: var(--font-display); font-size: 14px; color: var(--ink);
  margin-bottom: 12px;
}
.group-pick-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
  margin-bottom: 18px;
}
.group-pick {
  position: relative;
  display: flex; flex-direction: column; align-items: center; gap: 6px;
  padding: 12px 6px;
  background: #fff;
  border: 1px solid rgba(158,142,126,0.18);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s var(--ease-out);
}
.group-pick.selected {
  border-color: var(--cinnabar);
  background: rgba(190,63,53,0.05);
  box-shadow: var(--shadow-sm);
}
.group-pick-avatar { font-size: 26px; }
.group-pick-name { font-size: 13px; color: var(--ink); font-family: var(--font-display); }
.group-pick-check {
  position: absolute; top: 6px; right: 6px;
  color: var(--cinnabar); font-size: 15px;
}
.group-topic { width: 100%; margin-bottom: 14px; box-sizing: border-box; }
.group-start { width: 100%; padding: 12px; font-size: 15px; }

.group-body { flex: 1; overflow-y: auto; padding: 16px; }
.group-topic-tag {
  font-family: var(--font-display); font-size: 14px; color: var(--cinnabar);
  text-align: center; margin: 0 0 16px;
  padding: 8px 12px;
  background: rgba(190,63,53,0.06);
  border-radius: var(--radius-full);
}
.group-msg { margin-bottom: 16px; }
.group-msg-head {
  display: flex; align-items: center; gap: 8px;
  margin-bottom: 6px;
}
.group-msg-avatar {
  width: 32px; height: 32px;
  display: flex; align-items: center; justify-content: center;
  font-size: 18px;
  background: var(--parchment);
  border-radius: 50%;
  border: 1px solid rgba(158,142,126,0.2);
}
.group-msg-name { font-family: var(--font-display); font-size: 15px; color: var(--ink); }
.group-msg-dynasty { font-size: 12px; color: var(--stone); }
.group-msg .msg-speak { position: static; margin-left: auto; }
.group-msg-bubble {
  padding: 12px 14px;
  background: #fff;
  border: 1px solid rgba(158,142,126,0.14);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
}
.group-actions { display: flex; justify-content: center; padding: 8px 0 20px; gap: 10px; }
.chat-send.ghost {
  background: transparent;
  color: var(--cinnabar);
  border: 1px solid var(--cinnabar);
}

/* ── 飞花令 ── */
.feihua-keyword-box {
  display: flex; align-items: center; justify-content: center; gap: 14px;
  margin: 8px 0 20px;
}
.feihua-keyword-label {
  font-family: var(--font-display); font-size: 13px; color: var(--cinnabar);
  border: 1px solid var(--cinnabar);
  border-radius: 50%; width: 26px; height: 26px;
  display: flex; align-items: center; justify-content: center;
}
.feihua-keyword {
  font-family: var(--font-display); font-size: 44px; color: var(--cinnabar);
  line-height: 1;
}
.feihua-shuffle {
  border: 1px solid rgba(158,142,126,0.3);
  background: #fff; color: var(--stone);
  border-radius: var(--radius-full);
  padding: 6px 14px; font-size: 13px; cursor: pointer;
}
.feihua-msg { margin-bottom: 18px; }
.feihua-msg-body {
  padding: 12px 14px;
  background: #fff;
  border: 1px solid rgba(158,142,126,0.14);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
}
.feihua-comment { margin: 0 0 8px; font-size: 13px; color: var(--stone); line-height: 1.7; }
.feihua-line {
  margin: 0 0 4px;
  font-family: var(--font-serif); font-size: 17px; color: var(--ink);
  line-height: 1.8;
  background: rgba(190,63,53,0.06);
  padding: 6px 10px;
  border-radius: var(--radius-sm);
}
.feihua-source { margin: 0; font-size: 12px; color: var(--ink-light); text-align: right; }
</style>