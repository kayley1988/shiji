<template>
  <div class="galaxy-page">
    <!-- 3D 画布容器 -->
    <div ref="canvasHost" class="canvas-host"></div>

    <!-- 加载遮罩 -->
    <div v-if="loading" class="g-loading">
      <div class="g-loading-title">诗 云</div>
      <div class="g-loading-sub">正在点亮 {{ totalPoems }} 首诗 · {{ totalPoets }} 位诗人…</div>
    </div>
    <div v-if="loadError" class="g-loading err">
      <div>星图加载失败</div>
      <div class="g-loading-sub">{{ loadError }}</div>
    </div>

    <!-- 顶栏 -->
    <div class="g-topbar">
      <div class="g-back" @click="$router.push('/')">← 返回</div>
      <div class="g-title">诗云 · 星图</div>
      <div class="g-searchwrap">
        <input
          v-model="keyword"
          class="g-search"
          type="text"
          placeholder="搜索诗人 / 朝代…"
          @input="onSearch"
          @keydown="onSearchKey"
        />
        <div v-if="suggests.length" class="g-suggest">
          <div
            v-for="(p, i) in suggests"
            :key="p.id"
            class="g-suggest-item"
            :class="{ active: i === sugIdx }"
            @click="chooseSuggest(p)"
          >
            {{ p.name }}<span class="meta">{{ p.dynasty }} · {{ p.count }} 首</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 左下角图例 -->
    <div class="g-legend">
      <div v-for="d in legend" :key="d.key" class="row">
        <span class="dot" :style="{ background: d.color }"></span>
        <span class="name">{{ d.key }}</span>
        <span class="desc">{{ d.count }} 位诗人</span>
      </div>
    </div>

    <!-- 右下角操作开关 -->
    <div class="g-tools">
      <div class="tool" :class="{ on: labelsOn }" @click="toggleLabels">星名</div>
      <div class="tool" @click="resetView">复位</div>
    </div>

    <!-- 底部操作提示 -->
    <div class="g-hint">拖拽旋转 · 滚轮缩放 · WASD 穿越 · 点击星辰读诗</div>

    <!-- 悬停提示 -->
    <div ref="hoverTip" class="g-hover"></div>

    <!-- 右侧诗人面板 -->
    <div class="g-panel" :class="{ open: !!selected }">
      <div class="panel-close" @click="closePanel">×</div>
      <div class="panel-name">{{ selected?.name }}</div>
      <div class="panel-dyn" :style="{ background: dynColorOf(selected?.dynasty) }">
        {{ selected?.dynasty }} · 存诗 {{ selected?.count }} 首
      </div>
      <div class="panel-poems">
        <div v-if="poemsLoading" class="panel-tip">正在取诗…</div>
        <div v-else-if="!authorPoems.length" class="panel-tip">暂无已审核诗句</div>
        <div v-for="(pm, i) in authorPoems" :key="i" class="poem">
          <div class="pt">{{ pm.title }}</div>
          <div class="pc">
            <div v-for="(ln, j) in pm.lines" :key="j">{{ ln }}</div>
            <div v-if="!pm.lines.length" class="no-lines">暂无已审核诗句</div>
          </div>
        </div>
        <div v-if="authorTotal > authorPoems.length" class="panel-tip">
          共 {{ authorTotal }} 首 · 已展示前 {{ authorPoems.length }} 首
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import * as THREE from 'three'
import { OrbitControls } from 'three/addons/controls/OrbitControls.js'
import { api } from '../api'

// ---------- 类型 ----------
interface GalaxyPoet {
  id: string
  name: string
  dynasty: string
  count: number
}
interface AuthorPoem {
  title: string
  lines: string[]
  open?: boolean
}

// ---------- 暗夜鎏金配色 ----------
const BG = 0x14161b            // 玄夜
const GOLD = 0xd4af37          // 鎏金
const DYN_COLORS: Record<string, string> = {
  '唐': '#D4AF37',             // 鎏金
  '宋': '#6FB3A8',             // 青瓷
  '元': '#C4756B',             // 绛陶
  '未知': '#8B8FA3'
}
// 朝代 → 时间带（内圈→外圈）
const DYN_T: Record<string, [number, number]> = {
  '唐': [0.08, 0.45],
  '宋': [0.5, 0.72],
  '元': [0.76, 0.98]
}
const ARMS = 3, TURNS = 2.4, INNER_R = 70, OUTER_R = 300, V_SPREAD = 130

// ---------- 状态 ----------
const canvasHost = ref<HTMLDivElement>()
const hoverTip = ref<HTMLDivElement>()
const loading = ref(true)
const loadError = ref('')
const totalPoets = ref(0)
const totalPoems = ref(0)
const keyword = ref('')
const suggests = ref<GalaxyPoet[]>([])
const sugIdx = ref(-1)
const labelsOn = ref(false)
const selected = ref<GalaxyPoet | null>(null)
const authorPoems = ref<AuthorPoem[]>([])
const authorTotal = ref(0)
const poemsLoading = ref(false)
const legend = ref<{ key: string; color: string; count: number }[]>([])

let poets: GalaxyPoet[] = []
let scene: THREE.Scene | null = null
let camera: THREE.PerspectiveCamera | null = null
let renderer: THREE.WebGLRenderer | null = null
let controls: OrbitControls | null = null
let galaxy: THREE.Group | null = null
let rafId = 0
let disposed = false
const starObjs: { sprite: THREE.Sprite; poet: GalaxyPoet; baseSize: number; core?: THREE.Sprite; labelEl?: HTMLDivElement }[] = []
const labelEls: HTMLDivElement[] = []

// ---------- 工具 ----------
function hash(str: string): number {
  let h = 2166136261
  for (let i = 0; i < str.length; i++) { h ^= str.charCodeAt(i); h = Math.imul(h, 16777619) }
  return h >>> 0
}
const HMAX = 4294967295
function rand(seed: string): number { return hash(seed) / HMAX }

function dynColorOf(d?: string): string {
  return DYN_COLORS[d || '未知'] || DYN_COLORS['未知']
}
function dynToT(p: GalaxyPoet): number {
  const band = DYN_T[p.dynasty] || [0.2, 0.8]
  return band[0] + rand(p.id + 't') * (band[1] - band[0])
}
function placePoet(p: GalaxyPoet): THREE.Vector3 {
  const t = dynToT(p)
  const arm = hash(p.id) % ARMS
  const armOffset = (arm / ARMS) * Math.PI * 2
  const angle = t * TURNS * Math.PI * 2 + armOffset
  const radius = INNER_R + t * (OUTER_R - INNER_R)
  const jr = (rand(p.id + 'r') - 0.5) * 46
  const jy = (rand(p.id + 'y') - 0.5) * V_SPREAD * (0.4 + t * 0.6)
  const jz = (rand(p.id + 'z') - 0.5) * 46
  return new THREE.Vector3(
    Math.cos(angle) * radius + Math.cos(angle + 1.2) * jr,
    jy,
    Math.sin(angle) * radius + Math.sin(angle + 1.2) * jz
  )
}
function poetSize(count: number): number {
  return 4 + Math.min(7, Math.log2(count + 1) * 1.15)
}

function makeGlowTexture(): THREE.CanvasTexture {
  const c = document.createElement('canvas')
  c.width = c.height = 128
  const ctx = c.getContext('2d')!
  const g = ctx.createRadialGradient(64, 64, 0, 64, 64, 64)
  g.addColorStop(0.0, 'rgba(255,255,255,1)')
  g.addColorStop(0.18, 'rgba(255,255,255,0.92)')
  g.addColorStop(0.45, 'rgba(255,255,255,0.28)')
  g.addColorStop(1.0, 'rgba(255,255,255,0)')
  ctx.fillStyle = g
  ctx.fillRect(0, 0, 128, 128)
  const tex = new THREE.CanvasTexture(c)
  tex.colorSpace = THREE.SRGBColorSpace
  return tex
}
let GLOW: THREE.CanvasTexture

// ---------- 场景构建 ----------
function buildStarfield() {
  if (!scene) return
  const N = 4500
  const geo = new THREE.BufferGeometry()
  const pos = new Float32Array(N * 3)
  const col = new Float32Array(N * 3)
  const c = new THREE.Color()
  for (let i = 0; i < N; i++) {
    const r = 900 + Math.random() * 2200
    const th = Math.random() * Math.PI * 2
    const ph = Math.acos(2 * Math.random() - 1)
    pos[i * 3] = r * Math.sin(ph) * Math.cos(th)
    pos[i * 3 + 1] = r * Math.cos(ph) * 0.6
    pos[i * 3 + 2] = r * Math.sin(ph) * Math.sin(th)
    // 暖金色星尘，贴合鎏金主题
    c.setHSL(0.09 + Math.random() * 0.06, 0.45, 0.55 + Math.random() * 0.3)
    col[i * 3] = c.r; col[i * 3 + 1] = c.g; col[i * 3 + 2] = c.b
  }
  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3))
  geo.setAttribute('color', new THREE.BufferAttribute(col, 3))
  const mat = new THREE.PointsMaterial({
    size: 2.2, sizeAttenuation: true, vertexColors: true,
    transparent: true, opacity: 0.8, depthWrite: false, blending: THREE.AdditiveBlending
  })
  scene.add(new THREE.Points(geo, mat))
}

function buildCoreGlow() {
  if (!scene || !galaxy) return
  const sp = new THREE.Sprite(new THREE.SpriteMaterial({
    map: GLOW, color: GOLD, transparent: true, opacity: 0.4,
    depthWrite: false, blending: THREE.AdditiveBlending
  }))
  sp.scale.set(150, 150, 1)
  galaxy.add(sp)
}

function addStar(p: GalaxyPoet) {
  if (!galaxy) return
  const pos = placePoet(p)
  const color = new THREE.Color(dynColorOf(p.dynasty))
  const size = poetSize(p.count)
  const mat = new THREE.SpriteMaterial({
    map: GLOW, color, transparent: true, opacity: 0.95,
    depthWrite: false, blending: THREE.AdditiveBlending
  })
  const sp = new THREE.Sprite(mat)
  sp.position.copy(pos)
  sp.scale.set(size, size, 1)
  sp.userData = { poet: p, baseSize: size }
  galaxy.add(sp)
  const obj: { sprite: THREE.Sprite; poet: GalaxyPoet; baseSize: number; core?: THREE.Sprite; labelEl?: HTMLDivElement } = { sprite: sp, poet: p, baseSize: size }
  if (p.count >= 400) {
    const core = new THREE.Sprite(new THREE.SpriteMaterial({
      map: GLOW, color: 0xfff6dd, transparent: true, opacity: 0.9,
      depthWrite: false, blending: THREE.AdditiveBlending
    }))
    core.scale.set(size * 0.42, size * 0.42, 1)
    core.position.copy(pos)
    galaxy.add(core)
    obj.core = core
  }
  starObjs.push(obj)
}

function buildLegend() {
  const cnt: Record<string, number> = {}
  poets.forEach(p => { cnt[p.dynasty] = (cnt[p.dynasty] || 0) + 1 })
  legend.value = ['唐', '宋', '元'].map(k => ({
    key: k, color: DYN_COLORS[k], count: cnt[k] || 0
  }))
}

// ---------- 交互 ----------
const raycaster = new THREE.Raycaster()
const pointer = new THREE.Vector2()
let fly: { camTo: THREE.Vector3; tgtTo: THREE.Vector3 } | null = null
const keys: Record<string, boolean> = {}

function setPointer(e: PointerEvent) {
  pointer.x = (e.clientX / innerWidth) * 2 - 1
  pointer.y = -(e.clientY / innerHeight) * 2 + 1
}
function pick(): THREE.Sprite | null {
  if (!camera) return null
  raycaster.setFromCamera(pointer, camera)
  const hits = raycaster.intersectObjects(starObjs.map(o => o.sprite), false)
  return hits.length ? (hits[0].object as THREE.Sprite) : null
}
function onPointerMove(e: PointerEvent) {
  if (!renderer || !hoverTip.value) return
  setPointer(e)
  const obj = pick()
  if (obj) {
    renderer.domElement.style.cursor = 'pointer'
    const p = obj.userData.poet as GalaxyPoet
    hoverTip.value.textContent = `${p.name} · ${p.dynasty} · ${p.count} 首`
    hoverTip.value.style.left = e.clientX + 'px'
    hoverTip.value.style.top = e.clientY + 'px'
    hoverTip.value.style.display = 'block'
  } else {
    renderer.domElement.style.cursor = 'grab'
    hoverTip.value.style.display = 'none'
  }
}
function onClick() {
  const obj = pick()
  if (obj) openPoet(obj.userData.poet as GalaxyPoet, obj)
}

async function openPoet(p: GalaxyPoet, sprite: THREE.Sprite) {
  selected.value = p
  authorPoems.value = []
  authorTotal.value = 0
  poemsLoading.value = true
  focusOn(sprite)
  try {
    const res: any = await api.getGalaxyAuthorPoems(p.id)
    if (selected.value && selected.value.id === p.id) {
      authorPoems.value = (res.data?.poems || []) as AuthorPoem[]
      authorTotal.value = res.data?.total || 0
    }
  } catch {
    authorPoems.value = []
  } finally {
    poemsLoading.value = false
  }
}
function closePanel() { selected.value = null; authorPoems.value = []; authorTotal.value = 0 }

function focusOn(sprite: THREE.Sprite) {
  if (!camera) return
  const world = sprite.getWorldPosition(new THREE.Vector3())
  const dir = world.clone().normalize()
  const camTo = world.clone().add(dir.multiplyScalar(46)).add(new THREE.Vector3(0, 14, 0))
  fly = { camTo, tgtTo: world.clone() }
}

// ---------- 搜索 ----------
function onSearch() {
  const q = keyword.value.trim()
  if (!q) { suggests.value = []; sugIdx.value = -1; return }
  suggests.value = poets
    .filter(p => p.name.includes(q) || p.dynasty.includes(q))
    .slice(0, 12)
  sugIdx.value = -1
}
function onSearchKey(e: KeyboardEvent) {
  if (e.key === 'ArrowDown') sugIdx.value = Math.min(sugIdx.value + 1, suggests.value.length - 1)
  else if (e.key === 'ArrowUp') sugIdx.value = Math.max(sugIdx.value - 1, 0)
  else if (e.key === 'Enter') {
    const p = suggests.value[sugIdx.value >= 0 ? sugIdx.value : 0]
    if (p) chooseSuggest(p)
  }
}
function chooseSuggest(p: GalaxyPoet) {
  keyword.value = p.name
  suggests.value = []
  const o = starObjs.find(x => x.poet.id === p.id)
  if (o) openPoet(p, o.sprite)
}

// ---------- 标签 ----------
function toggleLabels() {
  labelsOn.value = !labelsOn.value
  if (labelsOn.value) ensureLabelEls()
  else labelEls.forEach(l => { l.style.display = 'none' })
}
function resetView() {
  fly = { camTo: new THREE.Vector3(0, 180, 620), tgtTo: new THREE.Vector3(0, 0, 0) }
  closePanel()
}
function ensureLabelEls() {
  if (labelEls.length) {
    labelEls.forEach(l => { l.style.display = 'block' })
    return
  }
  starObjs.forEach(o => {
    if (o.poet.count < 200) return   // 只给巨星贴名
    const el = document.createElement('div')
    el.className = 'g-plabel'
    el.textContent = o.poet.name
    el.style.color = dynColorOf(o.poet.dynasty)
    document.body.appendChild(el)
    o.labelEl = el
    labelEls.push(el)
  })
}
function updateLabels() {
  if (!labelsOn.value || !camera) return
  const cam = camera
  const v = new THREE.Vector3()
  starObjs.forEach(o => {
    if (!o.labelEl) return
    o.sprite.getWorldPosition(v)
    v.project(cam)
    const inFront = v.z < 1
    if (inFront && v.x > -1.1 && v.x < 1.1 && v.y > -1.1 && v.y < 1.1) {
      o.labelEl.style.display = 'block'
      o.labelEl.style.left = (v.x * 0.5 + 0.5) * innerWidth + 'px'
      o.labelEl.style.top = (-v.y * 0.5 + 0.5) * innerHeight + 'px'
    } else o.labelEl.style.display = 'none'
  })
}

// ---------- 键盘 ----------
function onKeyDown(e: KeyboardEvent) {
  const tag = (e.target as HTMLElement)?.tagName
  if (tag === 'INPUT' || tag === 'TEXTAREA') return
  keys[e.key.toLowerCase()] = true
}
function onKeyUp(e: KeyboardEvent) { keys[e.key.toLowerCase()] = false }
function onResize() {
  if (!camera || !renderer) return
  camera.aspect = innerWidth / innerHeight
  camera.updateProjectionMatrix()
  renderer.setSize(innerWidth, innerHeight)
}

// ---------- 主循环 ----------
const tmpF = new THREE.Vector3(), tmpR = new THREE.Vector3(), tmpU = new THREE.Vector3(0, 1, 0)
const clock = new THREE.Clock()
function animate() {
  if (disposed) return
  rafId = requestAnimationFrame(animate)
  const dt = Math.min(clock.getDelta(), 0.05)
  if (!fly && galaxy) galaxy.rotation.y += dt * 0.012
  if (fly && camera && controls) {
    camera.position.lerp(fly.camTo, 0.06)
    controls.target.lerp(fly.tgtTo, 0.06)
    if (camera.position.distanceTo(fly.camTo) < 2) fly = null
  }
  // WASD 穿行
  const typing = document.activeElement && document.activeElement.tagName === 'INPUT'
  if (!typing && camera && controls && (keys['w'] || keys['s'] || keys['a'] || keys['d'])) {
    camera.getWorldDirection(tmpF).normalize()
    tmpR.crossVectors(tmpF, tmpU).normalize()
    const sp = 90 * dt
    const mv = new THREE.Vector3()
    if (keys['w']) mv.add(tmpF)
    if (keys['s']) mv.sub(tmpF)
    if (keys['d']) mv.add(tmpR)
    if (keys['a']) mv.sub(tmpR)
    if (mv.lengthSq() > 0) {
      mv.normalize().multiplyScalar(sp)
      camera.position.add(mv)
      controls.target.add(mv)
      fly = null
    }
  }
  // 悬停星脉动
  const tms = performance.now() * 0.003
  starObjs.forEach(o => {
    const s = o.baseSize * (1 + 0.06 * Math.sin(tms + (hash(o.poet.id) % 6)))
    o.sprite.scale.set(s, s, 1)
  })
  if (controls) controls.update()
  updateLabels()
  if (renderer && scene && camera) renderer.render(scene, camera)
}

// ---------- 初始化 ----------
async function init() {
  // 取数据
  try {
    const res: any = await api.getGalaxyPoets()
    poets = res.data?.poets || []
    totalPoets.value = res.data?.total_poets || 0
    totalPoems.value = res.data?.total_poems || 0
  } catch (e: any) {
    loadError.value = e?.message || '接口异常'
    loading.value = false
    return
  }
  if (!poets.length) {
    loadError.value = '库中没有诗人数据'
    loading.value = false
    return
  }

  GLOW = makeGlowTexture()
  scene = new THREE.Scene()
  scene.fog = new THREE.FogExp2(BG, 0.0011)
  galaxy = new THREE.Group()
  scene.add(galaxy)

  camera = new THREE.PerspectiveCamera(58, innerWidth / innerHeight, 0.5, 6000)
  camera.position.set(0, 520, 1300)

  renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' })
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2))
  renderer.setSize(innerWidth, innerHeight)
  renderer.setClearColor(BG, 1)
  canvasHost.value?.appendChild(renderer.domElement)

  controls = new OrbitControls(camera, renderer.domElement)
  controls.enableDamping = true
  controls.dampingFactor = 0.08
  controls.rotateSpeed = 0.5
  controls.minDistance = 6
  controls.maxDistance = 1600

  buildStarfield()
  buildCoreGlow()
  poets.forEach(addStar)
  buildLegend()

  window.addEventListener('resize', onResize)
  renderer.domElement.addEventListener('pointermove', onPointerMove)
  renderer.domElement.addEventListener('click', onClick)
  window.addEventListener('keydown', onKeyDown)
  window.addEventListener('keyup', onKeyUp)

  // 开场飞入
  fly = { camTo: new THREE.Vector3(0, 180, 620), tgtTo: new THREE.Vector3(0, 0, 0) }

  loading.value = false
  animate()
}

onMounted(init)

onBeforeUnmount(() => {
  disposed = true
  cancelAnimationFrame(rafId)
  window.removeEventListener('resize', onResize)
  window.removeEventListener('keydown', onKeyDown)
  window.removeEventListener('keyup', onKeyUp)
  labelEls.forEach(l => l.remove())
  if (renderer) {
    renderer.domElement.removeEventListener('pointermove', onPointerMove)
    renderer.domElement.removeEventListener('click', onClick)
    renderer.dispose()
    renderer.domElement.remove()
  }
  GLOW?.dispose()
})
</script>

<style scoped>
.galaxy-page {
  position: fixed;
  inset: 0;
  background: var(--paper, #14161B);
  overflow: hidden;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
}
.canvas-host { position: absolute; inset: 0; }
.canvas-host :deep(canvas) { display: block; }

/* 加载遮罩 */
.g-loading {
  position: absolute; inset: 0; z-index: 30;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  background: var(--paper, #14161B);
}
.g-loading.err { background: rgba(20, 22, 27, 0.9); }
.g-loading-title {
  font-size: 34px; letter-spacing: 14px; font-weight: 700;
  color: var(--cinnabar, #D4AF37);
  text-shadow: 0 0 24px rgba(212, 175, 55, 0.45);
}
.g-loading-sub { margin-top: 14px; font-size: 13px; color: var(--ink-light, #ABA694); }

/* 顶栏 */
.g-topbar {
  position: absolute; top: 0; left: 0; right: 0; z-index: 20;
  display: flex; align-items: center; gap: 16px;
  padding: 14px 20px;
  background: linear-gradient(to bottom, rgba(20, 22, 27, 0.9), rgba(20, 22, 27, 0));
}
.g-back {
  padding: 6px 14px; border-radius: 18px; font-size: 13px;
  color: var(--ink, #D9D4C5);
  background: var(--card, #1E222B);
  border: 1px solid rgba(212, 175, 55, 0.35);
  cursor: pointer; user-select: none;
  transition: border-color 0.2s, color 0.2s;
}
.g-back:hover { border-color: var(--cinnabar, #D4AF37); color: var(--cinnabar-light, #E9CB6B); }
.g-title {
  font-size: 17px; font-weight: 700; letter-spacing: 6px;
  color: var(--cinnabar, #D4AF37);
}
.g-searchwrap { position: relative; margin-left: auto; }
.g-search {
  width: 220px; padding: 7px 14px; border-radius: 18px;
  background: var(--card, #1E222B);
  border: 1px solid rgba(212, 175, 55, 0.35);
  color: var(--ink, #D9D4C5); font-size: 13px; outline: none;
}
.g-search::placeholder { color: var(--ink-mist, #847F6E); }
.g-search:focus { border-color: var(--cinnabar, #D4AF37); }
.g-suggest {
  position: absolute; top: 40px; right: 0; width: 260px; max-height: 320px; overflow-y: auto;
  background: var(--card, #1E222B);
  border: 1px solid rgba(212, 175, 55, 0.35);
  border-radius: 10px; z-index: 25;
}
.g-suggest-item {
  padding: 8px 14px; font-size: 13px; color: var(--ink, #D9D4C5); cursor: pointer;
}
.g-suggest-item:hover, .g-suggest-item.active { background: var(--card-hover, #252A35); color: var(--cinnabar-light, #E9CB6B); }
.g-suggest-item .meta { float: right; font-size: 11px; color: var(--ink-mist, #847F6E); }

/* 图例 */
.g-legend {
  position: absolute; left: 20px; bottom: 52px; z-index: 20;
  display: flex; flex-direction: column; gap: 6px;
  padding: 12px 16px;
  background: rgba(30, 34, 43, 0.85);
  border: 1px solid rgba(212, 175, 55, 0.25);
  border-radius: 12px; backdrop-filter: blur(6px);
}
.g-legend .row { display: flex; align-items: center; gap: 8px; font-size: 12px; color: var(--ink, #D9D4C5); }
.g-legend .dot { width: 9px; height: 9px; border-radius: 50%; box-shadow: 0 0 8px currentColor; }
.g-legend .desc { color: var(--ink-mist, #847F6E); }

/* 工具开关 */
.g-tools {
  position: absolute; right: 20px; bottom: 52px; z-index: 20;
  display: flex; gap: 8px;
}
.g-tools .tool {
  padding: 6px 14px; border-radius: 16px; font-size: 12px;
  color: var(--ink-light, #ABA694);
  background: rgba(30, 34, 43, 0.85);
  border: 1px solid rgba(212, 175, 55, 0.25);
  cursor: pointer; user-select: none;
}
.g-tools .tool.on, .g-tools .tool:hover {
  color: var(--cinnabar, #D4AF37);
  border-color: var(--cinnabar, #D4AF37);
}

/* 底部提示 */
.g-hint {
  position: absolute; bottom: 14px; left: 0; right: 0; z-index: 20;
  text-align: center; font-size: 11px; letter-spacing: 2px;
  color: var(--ink-mist, #847F6E);
}

/* 悬停提示 */
.g-hover {
  position: fixed; z-index: 40; display: none;
  transform: translate(12px, -50%);
  padding: 5px 12px; border-radius: 8px;
  font-size: 12px; white-space: nowrap; pointer-events: none;
  color: var(--cinnabar-light, #E9CB6B);
  background: rgba(20, 22, 27, 0.92);
  border: 1px solid rgba(212, 175, 55, 0.45);
}

/* 诗人面板 */
.g-panel {
  position: absolute; top: 0; right: -380px; bottom: 0; z-index: 20;
  width: 340px; padding: 56px 22px 22px;
  background: rgba(25, 28, 35, 0.96);
  border-left: 1px solid rgba(212, 175, 55, 0.35);
  transition: right 0.35s ease;
  overflow-y: auto;
}
.g-panel.open { right: 0; }
.panel-close {
  position: absolute; top: 14px; right: 16px;
  width: 28px; height: 28px; line-height: 26px; text-align: center;
  border-radius: 50%; font-size: 18px; cursor: pointer;
  color: var(--ink-light, #ABA694);
  border: 1px solid rgba(212, 175, 55, 0.3);
}
.panel-close:hover { color: var(--cinnabar, #D4AF37); }
.panel-name { font-size: 26px; font-weight: 700; color: var(--ink-dark, #F2ECDA); }
.panel-dyn {
  display: inline-block; margin-top: 8px; padding: 3px 12px;
  border-radius: 12px; font-size: 12px; color: #14161B; font-weight: 600;
}
.panel-poems { margin-top: 18px; display: flex; flex-direction: column; gap: 10px; }
.panel-tip { font-size: 13px; color: var(--ink-mist, #847F6E); padding: 8px 0; }
.poem {
  padding: 10px 14px; border-radius: 10px;
  background: var(--card, #1E222B);
  border: 1px solid rgba(212, 175, 55, 0.18);
}
.poem .pt { font-size: 14px; font-weight: 600; color: var(--cinnabar-light, #E9CB6B); }
.poem .pc {
  margin-top: 8px;
  font-size: 13px; line-height: 2.0; color: var(--ink, #D9D4C5);
}
.poem .pc .no-lines { color: var(--ink-mist, #847F6E); font-size: 12px; }

/* 星名标签（非 scoped，动态创建） */
.g-plabel {
  position: fixed; z-index: 15; display: none;
  transform: translate(-50%, -140%);
  font-size: 12px; font-weight: 600; pointer-events: none;
  text-shadow: 0 0 6px rgba(0, 0, 0, 0.9), 0 0 12px rgba(0, 0, 0, 0.7);
}
</style>
