<template>
  <div class="notes-page" :class="themeClass">
    <!-- 顶部 -->
    <div class="notes-header">
      <van-icon name="arrow-left" class="back-btn" @click="$router.back()" />
      <span class="notes-title">私人诗摘</span>
      <van-icon name="plus" class="add-btn" @click="openAdd" />
    </div>

    <!-- 空状态 -->
    <div v-if="!loading && notes.length === 0" class="notes-empty">
      <div class="empty-icon">📜</div>
      <p class="empty-title">还没有诗摘</p>
      <p class="empty-hint">收藏触动你的诗句，写下你的感悟</p>
      <van-button size="small" round type="default" @click="openAdd">添加第一条</van-button>
    </div>

    <!-- 诗摘列表 -->
    <div v-else class="notes-list">
      <div
        v-for="n in notes"
        :key="n.id"
        class="note-card"
        @click="openDetail(n)"
      >
        <div class="note-line">「{{ n.line_text }}」</div>
        <div class="note-source">
          <span>{{ n.poem_title }}</span>
          <span class="note-poet">· {{ n.poet_name }}</span>
        </div>
        <div v-if="n.note" class="note-text">{{ n.note }}</div>
        <div class="note-footer">
          <span class="note-mood" :class="`mood-${n.mood_tag}`">{{ n.mood_tag }}</span>
          <span class="note-date">{{ formatDate(n.created_at) }}</span>
        </div>
      </div>
    </div>

    <!-- 加载态 -->
    <div v-if="loading" class="notes-loading">
      <van-loading size="32px">加载中...</van-loading>
    </div>

    <!-- 新增/编辑弹窗 -->
    <van-popup v-model="showEditor" position="bottom" round :style="{ maxHeight: '92vh' }">
      <div class="editor-wrap">
        <div class="editor-title">{{ editingNote ? '编辑诗摘' : '新建诗摘' }}</div>

        <!-- 诗句 -->
        <van-field
          v-model="form.line_text"
          label="诗句"
          placeholder="写下触动你的那句诗"
          :rules="[{ required: true, message: '请输入诗句' }]"
        />

        <!-- 诗题 -->
        <van-field
          v-model="form.poem_title"
          label="诗题"
          placeholder="诗的题目"
        />

        <!-- 作者 -->
        <van-field
          v-model="form.poet_name"
          label="作者"
          placeholder="诗人名"
        />

        <!-- 心情标签 -->
        <div class="editor-mood">
          <div class="field-label">此刻心情</div>
          <div class="mood-tags">
            <span
              v-for="m in moodOptions"
              :key="m"
              class="mood-tag"
              :class="{ active: form.mood_tag === m }"
              @click="form.mood_tag = m"
            >{{ m }}</span>
          </div>
        </div>

        <!-- 感悟 -->
        <van-field
          v-model="form.note"
          label="感悟"
          type="textarea"
          rows="3"
          autosize
          placeholder="记录此刻的心情..."
          maxlength="200"
          show-word-limit
        />

        <!-- 操作 -->
        <div class="editor-actions">
          <van-button v-if="editingNote" type="danger" plain round @click="handleDelete">删除</van-button>
          <van-button type="primary" round @click="handleSave">{{ editingNote ? '保存' : '添加' }}</van-button>
        </div>
      </div>
    </van-popup>

    <!-- 详情弹窗 -->
    <van-popup v-model="showDetail" position="center" round style="width: 90%; max-width: 400px;">
      <div v-if="detailNote" class="detail-wrap">
        <div class="detail-line">「{{ detailNote.line_text }}」</div>
        <div class="detail-meta">
          《{{ detailNote.poem_title }}》· {{ detailNote.poet_name }}
        </div>
        <div v-if="detailNote.note" class="detail-note">{{ detailNote.note }}</div>
        <div class="detail-footer">
          <span class="note-mood" :class="`mood-${detailNote.mood_tag}`">{{ detailNote.mood_tag }}</span>
          <span class="note-date">{{ formatDate(detailNote.created_at) }}</span>
        </div>
        <div class="detail-actions">
          <van-button size="small" round @click="speakNote">朗读</van-button>
          <van-button size="small" round @click="copyNote">复制</van-button>
          <van-button size="small" round type="primary" @click="editNote(detailNote)">编辑</van-button>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { showToast, showConfirmDialog } from 'vant'
import { api } from '../api'
import { useTheme } from '../composables/useTheme'
import { useSpeech } from '../composables/useSpeech'

const { currentTheme } = useTheme()
const { speak } = useSpeech()

const themeClass = computed(() => `theme-${currentTheme.value}`)

const notes = ref<any[]>([])
const loading = ref(false)
const showEditor = ref(false)
const showDetail = ref(false)
const editingNote = ref<any>(null)
const detailNote = ref<any>(null)

const form = ref({
  poem_id: '',
  line_text: '',
  poem_title: '',
  poet_name: '',
  note: '',
  mood_tag: '平静',
})

const moodOptions = ['欢喜', '忧愁', '平静', '迷茫', '感怀', '思念', '闲适']

async function fetchNotes() {
  loading.value = true
  try {
    const res = await api.getPoemNotes()
    notes.value = res.data.data.notes || []
  } catch (e) {
    showToast('加载失败，请重试')
  } finally {
    loading.value = false
  }
}

function openAdd() {
  editingNote.value = null
  form.value = { poem_id: '', line_text: '', poem_title: '', poet_name: '', note: '', mood_tag: '平静' }
  showEditor.value = true
}

function openDetail(n: any) {
  detailNote.value = n
  showDetail.value = true
}

function editNote(n: any) {
  detailNote.value = null
  showDetail.value = false
  editingNote.value = n
  form.value = { ...n, poem_id: n.poem_id || '' }
  showEditor.value = true
}

async function handleSave() {
  if (!form.value.line_text.trim()) {
    showToast('请输入诗句')
    return
  }
  try {
    if (editingNote.value) {
      await api.updatePoemNote(editingNote.value.id, {
        note: form.value.note,
        mood_tag: form.value.mood_tag,
      })
      showToast('已保存')
    } else {
      await api.addPoemNote(form.value)
      showToast('已添加')
    }
    showEditor.value = false
    fetchNotes()
  } catch (e) {
    showToast(editingNote.value ? '保存失败' : '添加失败')
  }
}

async function handleDelete() {
  if (!editingNote.value) return
  try {
    await showConfirmDialog({ title: '确认删除', message: '删除后不可恢复，确定删除吗？' })
    await api.deletePoemNote(editingNote.value.id)
    showToast('已删除')
    showEditor.value = false
    fetchNotes()
  } catch {
    // 用户取消
  }
}

async function speakNote() {
  if (!detailNote.value) return
  await speak(`「${detailNote.value.line_text}」。出自《${detailNote.value.poem_title}》。${detailNote.value.note || ''}`)
}

function copyNote() {
  if (!detailNote.value) return
  const text = `「${detailNote.value.line_text}」—— ${detailNote.value.poet_name}《${detailNote.value.poem_title}》\n${detailNote.value.note || ''}`
  navigator.clipboard.writeText(text).then(() => showToast('已复制'))
}

function formatDate(d: string) {
  if (!d) return ''
  return d.slice(0, 10).replace(/-/g, '月').replace(/(\d+)月(\d+)月/, '$1年$2') || d.slice(0, 10)
}

onMounted(fetchNotes)
</script>

<style scoped>
.notes-page {
  min-height: 100vh;
  padding-bottom: 40px;
  background: var(--parchment);
}

.notes-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  border-bottom: 1px solid var(--ink-light);
  background: var(--parchment);
}
.back-btn { font-size: 22px; cursor: pointer; }
.notes-title { font-family: var(--font-display); font-size: 18px; }
.add-btn { font-size: 22px; margin-left: auto; cursor: pointer; color: var(--cinnabar); }

/* 空状态 */
.notes-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 80px 20px;
  text-align: center;
}
.empty-icon { font-size: 64px; }
.empty-title { font-family: var(--font-display); font-size: 18px; color: var(--ink); }
.empty-hint { font-size: 13px; color: var(--ink-light); }

/* 列表 */
.notes-list {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.note-card {
  background: var(--card-bg);
  border: 1px solid var(--ink-faint);
  border-radius: 12px;
  padding: 16px;
  cursor: pointer;
  transition: transform 0.2s;
}
.note-card:hover { transform: translateY(-2px); }
.note-line {
  font-family: var(--font-display);
  font-size: 17px;
  color: var(--ink);
  margin-bottom: 8px;
}
.note-source {
  font-size: 12px;
  color: var(--ink-light);
  margin-bottom: 8px;
}
.note-poet { color: var(--ink-faint); }
.note-text {
  font-size: 13px;
  color: var(--ink);
  line-height: 1.6;
  background: rgba(139, 90, 43, 0.05);
  border-radius: 6px;
  padding: 8px 10px;
  margin-bottom: 8px;
}
.note-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.note-mood {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 10px;
  background: var(--card-bg);
  border: 1px solid var(--ink-faint);
  color: var(--ink-light);
}
.note-mood.mood-欢喜 { background: rgba(180, 60, 50, 0.08); border-color: var(--cinnabar); color: var(--cinnabar); }
.note-mood.mood-平静 { background: rgba(61, 107, 74, 0.08); border-color: var(--jade); color: var(--jade); }
.note-mood.mood-忧愁 { background: rgba(100, 100, 160, 0.08); border-color: #6464a0; color: #6464a0; }
.note-mood.mood-迷茫 { background: rgba(160, 130, 80, 0.08); border-color: var(--gold); color: var(--gold); }
.note-date { font-size: 11px; color: var(--ink-faint); }

.notes-loading { display: flex; justify-content: center; padding: 40px; }

/* 编辑弹窗 */
.editor-wrap {
  padding: 20px 16px 36px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-height: 80vh;
  overflow-y: auto;
}
.editor-title {
  font-family: var(--font-display);
  font-size: 18px;
  text-align: center;
  margin-bottom: 12px;
}
.editor-mood { padding: 12px 16px; }
.field-label { font-size: 14px; color: var(--ink); margin-bottom: 8px; }
.mood-tags { display: flex; gap: 8px; flex-wrap: wrap; }
.mood-tag {
  padding: 4px 12px;
  border-radius: 14px;
  font-size: 13px;
  background: var(--card-bg);
  border: 1px solid var(--ink-faint);
  cursor: pointer;
  color: var(--ink-light);
  transition: all 0.2s;
}
.mood-tag.active {
  background: rgba(180, 60, 50, 0.08);
  border-color: var(--cinnabar);
  color: var(--cinnabar);
}
.editor-actions { display: flex; gap: 12px; padding: 12px 16px 0; }
.editor-actions > * { flex: 1; }

/* 详情弹窗 */
.detail-wrap {
  padding: 28px 24px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  align-items: center;
}
.detail-line {
  font-family: var(--font-display);
  font-size: 20px;
  color: var(--ink);
  text-align: center;
  line-height: 1.6;
}
.detail-meta { font-size: 13px; color: var(--ink-light); }
.detail-note {
  font-size: 14px;
  color: var(--ink);
  line-height: 1.8;
  text-align: center;
  background: rgba(139, 90, 43, 0.05);
  border-radius: 8px;
  padding: 12px 16px;
  width: 100%;
}
.detail-footer { display: flex; gap: 12px; align-items: center; }
.detail-actions { display: flex; gap: 10px; width: 100%; }
.detail-actions > * { flex: 1; }
</style>
