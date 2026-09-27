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
    <div class="g-hint">拖拽平移 · 滚轮缩放 · 拉近显示更多星名 · 点击星辰读诗</div>

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
// 朝代泳道（横轴）：laneY 为纵轴位置，范围用于无年表作者的分布
const DYN_RANGES: Record<string, [number, number]> = {
  '唐': [618, 907],
  '宋': [960, 1279],
  '元': [1271, 1368]
}
const LANE_Y: Record<string, number> = { '唐': 95, '宋': 0, '元': -95 }
const X_LEFT = -440, X_RIGHT = 440        // 年代 600 → 1400 映射到横轴
const YEAR_MIN = 600, YEAR_MAX = 1400

// 名家年表（生年，近似）：有年表的按真实年代落位，无年表在朝代区间内抖动
const KNOWN_YEARS: Record<string, number> = {
  // 唐
  '骆宾王': 619, '王勃': 650, '杨炯': 650, '卢照邻': 634, '陈子昂': 661,
  '贺知章': 659, '张九龄': 678, '张若虚': 660, '王之涣': 688, '孟浩然': 689,
  '王昌龄': 698, '王维': 701, '李白': 701, '高适': 704, '崔颢': 704,
  '杜甫': 712, '岑参': 715, '钱起': 722, '刘长卿': 726, '韦应物': 737,
  '卢纶': 739, '李益': 748, '孟郊': 751, '张继': 715, '韩愈': 768,
  '刘禹锡': 772, '白居易': 772, '柳宗元': 773, '元稹': 779, '贾岛': 779,
  '李贺': 790, '许浑': 791, '杜牧': 803, '温庭筠': 812, '李商隐': 813,
  '皮日休': 834, '陆龟蒙': 830, '韦庄': 836, '罗隐': 833, '杜荀鹤': 846,
  '韩偓': 842, '贯休': 832, '齐己': 863, '王建': 768, '张籍': 766,
  '李颀': 690, '崔涂': 850, '秦韬玉': 840, '郑谷': 851, '吴融': 850,
  // 宋
  '范仲淹': 989, '张先': 990, '柳永': 984, '晏殊': 991, '梅尧臣': 1002,
  '欧阳修': 1007, '苏洵': 1009, '曾巩': 1019, '王安石': 1021, '晏几道': 1038,
  '苏轼': 1037, '苏辙': 1039, '黄庭坚': 1045, '秦观': 1049, '贺铸': 1052,
  '周邦彦': 1056, '李清照': 1084, '岳飞': 1103, '陈与义': 1090, '杨万里': 1127,
  '陆游': 1125, '范成大': 1126, '朱熹': 1130, '辛弃疾': 1140, '姜夔': 1155,
  '刘克庄': 1187, '文天祥': 1236, '林逋': 967, '司马光': 1019, '米芾': 1051,
  // 元
  '关汉卿': 1220, '白朴': 1226, '王实甫': 1230, '马致远': 1250, '卢挚': 1242,
  '刘因': 1249, '张养浩': 1270, '揭傒斯': 1274, '虞集': 1272, '萨都剌': 1272,
  '贯云石': 1286, '张可久': 1280, '乔吉': 1280, '黄溍': 1277, '欧阳玄': 1283,
  '王冕': 1287, '杨维桢': 1296, '乃贤': 1309, '郑光祖': 1260, '睢景臣': 1250
}

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
const labelsOn = ref(true)
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
function poetX(p: GalaxyPoet): number {
  const range = DYN_RANGES[p.dynasty] || [800, 1100]
  const known = KNOWN_YEARS[p.name]
  const year = known ?? (range[0] + rand(p.id + 'y') * (range[1] - range[0]))
  const t = Math.min(1, Math.max(0, (year - YEAR_MIN) / (YEAR_MAX - YEAR_MIN)))
  return X_LEFT + t * (X_RIGHT - X_LEFT) + (rand(p.id + 'x') - 0.5) * 14
}
function placePoet(p: GalaxyPoet): THREE.Vector3 {
  const laneY = LANE_Y[p.dynasty] ?? 0
  return new THREE.Vector3(
    poetX(p),
    laneY + (rand(p.id + 'lane') - 0.5) * 22,
    (rand(p.id + 'z') - 0.5) * 60
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
    map: GLOW, color: GOLD, transparent: true, opacity: 0.15,
    depthWrite: false, blending: THREE.AdditiveBlending
  }))
  sp.scale.set(700, 500, 1)
  galaxy.add(sp)
}

// 朝代泳道基线 + 左侧轴标
function makeTextSprite(text: string, color: string, scale = 1): THREE.Sprite {
  const c = document.createElement('canvas')
  const pad = 10, fs = 46
  const ctx = c.getContext('2d')!
  ctx.font = `700 ${fs}px "PingFang SC","Microsoft YaHei",sans-serif`
  const w = ctx.measureText(text).width
  c.width = w + pad * 2
  c.height = fs + pad * 2
  const x = c.getContext('2d')!
  x.font = `700 ${fs}px "PingFang SC","Microsoft YaHei",sans-serif`
  x.textBaseline = 'middle'
  x.fillStyle = color
  x.fillText(text, pad, c.height / 2)
  const tex = new THREE.CanvasTexture(c)
  tex.colorSpace = THREE.SRGBColorSpace
  const sp = new THREE.Sprite(new THREE.SpriteMaterial({
    map: tex, transparent: true, depthWrite: false
  }))
  sp.scale.set((c.width / c.height) * scale * 14, scale * 14, 1)
  return sp
}

function buildLanes() {
  if (!galaxy) return
  const mat = new THREE.LineBasicMaterial({
    color: GOLD, transparent: true, opacity: 0.28, depthWrite: false
  })
  Object.entries(LANE_Y).forEach(([dyn, y]) => {
    const range = DYN_RANGES[dyn] || [800, 1100]
    const x0 = X_LEFT - 30, x1 = X_RIGHT + 30
    const geo = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(x0, y, -10), new THREE.Vector3(x1, y, -10)
    ])
    galaxy!.add(new THREE.Line(geo, mat))
    // 轴标：朝代 + 年代范围
    const label = makeTextSprite(`${dyn} ${range[0]}–${range[1]}`, DYN_COLORS[dyn] || '#D4AF37', 1)
    label.position.set(X_LEFT - 105, y, 0)
    galaxy!.add(label)
  })
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

// ---------- 标签（随缩放自适应） ----------
function toggleLabels() {
  labelsOn.value = !labelsOn.value
  if (labelsOn.value) ensureLabelEls()
  else labelEls.forEach(l => { l.style.display = 'none' })
}
function resetView() {
  fly = { camTo: new THREE.Vector3(0, 0, 720), tgtTo: new THREE.Vector3(0, 0, 0) }
  closePanel()
}
function ensureLabelEls() {
  if (labelEls.length) return
  starObjs.forEach((o, idx) => {
    if (o.poet.count < 20) return   // 标签池：存诗 ≥20 的作者
    const el = document.createElement('div')
    el.className = 'g-plabel' + (idx % 2 ? ' g-plabel-b' : '')   // 上下交错减少碰撞
    el.textContent = o.poet.name
    el.style.color = dynColorOf(o.poet.dynasty)
    el.style.display = 'none'
    document.body.appendChild(el)
    o.labelEl = el
    labelEls.push(el)
  })
}
function updateLabels() {
  if (!labelsOn.value || !camera || !controls) return
  const cam = camera
  const dist = camera.position.distanceTo(controls.target)
  // 越近显示越多：远景只标巨星（≥250 首），中景 ≥80，较近 ≥30，贴近后 ≥20
  const thr = dist > 850 ? 250 : dist > 550 ? 80 : dist > 350 ? 30 : 20
  const v = new THREE.Vector3()
  let visible = 0
  for (const o of starObjs) {
    if (!o.labelEl) continue
    if (visible >= 520) { o.labelEl.style.display = 'none'; continue }
    o.sprite.getWorldPosition(v)
    v.project(cam)
    const inFront = v.z < 1 && v.x > -1.08 && v.x < 1.08 && v.y > -1.08 && v.y < 1.08
    if (inFront && o.poet.count >= thr) {
      o.labelEl.style.display = 'block'
      o.labelEl.style.left = (v.x * 0.5 + 0.5) * innerWidth + 'px'
      o.labelEl.style.top = (-v.y * 0.5 + 0.5) * innerHeight + 'px'
      visible++
    } else {
      o.labelEl.style.display = 'none'
    }
  }
}

// ---------- 键盘 ----------
function onResize() {
  if (!camera || !renderer) return
  camera.aspect = innerWidth / innerHeight
  camera.updateProjectionMatrix()
  renderer.setSize(innerWidth, innerHeight)
}

// ---------- 主循环 ----------
const clock = new THREE.Clock()
function animate() {
  if (disposed) return
  rafId = requestAnimationFrame(animate)
  Math.min(clock.getDelta(), 0.05)
  if (fly && camera && controls) {
    camera.position.lerp(fly.camTo, 0.06)
    controls.target.lerp(fly.tgtTo, 0.06)
    if (camera.position.distanceTo(fly.camTo) < 2) fly = null
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
  camera.position.set(0, 0, 720)

  renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' })
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2))
  renderer.setSize(innerWidth, innerHeight)
  renderer.setClearColor(BG, 1)
  canvasHost.value?.appendChild(renderer.domElement)

  controls = new OrbitControls(camera, renderer.domElement)
  controls.enableDamping = true
  controls.dampingFactor = 0.08
  controls.enableRotate = false      // 时间轴不需要旋转，平移 + 缩放
  controls.screenSpacePanning = true
  controls.minDistance = 60
  controls.maxDistance = 1600

  buildStarfield()
  buildCoreGlow()
  buildLanes()
  poets.forEach(addStar)
  buildLegend()
  ensureLabelEls()

  window.addEventListener('resize', onResize)
  renderer.domElement.addEventListener('pointermove', onPointerMove)
  renderer.domElement.addEventListener('click', onClick)

  // 开场：从高空落到正面视角
  camera.position.set(0, 420, 1500)
  fly = { camTo: new THREE.Vector3(0, 0, 720), tgtTo: new THREE.Vector3(0, 0, 0) }

  loading.value = false
  animate()
}

onMounted(init)

onBeforeUnmount(() => {
  disposed = true
  cancelAnimationFrame(rafId)
  window.removeEventListener('resize', onResize)
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

/* 星名标签（动态创建，走全局样式，见下方非 scoped 块） */
</style>

<style>
/* 星名标签：JS 动态创建的 DOM 拿不到 scoped 属性，必须用全局样式 */
.g-plabel {
  position: fixed;
  z-index: 15;
  display: none;
  transform: translate(-50%, -140%);
  font-size: 12px;
  font-weight: 600;
  pointer-events: none;
  text-shadow: 0 0 6px rgba(0, 0, 0, 0.9), 0 0 12px rgba(0, 0, 0, 0.7);
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
}
.g-plabel-b {
  transform: translate(-50%, 45%);
}
</style>
