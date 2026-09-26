import { createApp } from 'vue'
import { createPinia } from 'pinia'
import {
  Button, Icon, Field, Tab, Tabs, Tag, Empty, Toast,
  Cell, CellGroup, Popup, Dialog, ActionSheet,
  Loading, Search, Divider, Radio, RadioGroup,
  Switch, SwipeCell, Stepper, Picker, DatePicker, Cascader
} from 'vant'
import router from './router'
import App from './App.vue'
import { useTheme } from './composables/useTheme'
import 'vant/lib/index.css'
import './styles/main.css'

const app = createApp(App)
const pinia = createPinia()

// 应用持久化的国风皮肤（在挂载前，避免闪色）
useTheme().initTheme()

app.use(pinia)
app.use(router)
app.use(Button)
app.use(Icon)
app.use(Field)
app.use(Tab)
app.use(Tabs)
app.use(Tag)
app.use(Empty)
app.use(Toast)
app.use(Cell)
app.use(CellGroup)
app.use(Popup)
app.use(Dialog)
app.use(ActionSheet)
app.use(Loading)
app.use(Search)
app.use(Divider)
app.use(Radio)
app.use(RadioGroup)
app.use(Switch)
app.use(SwipeCell)
app.use(Stepper)
app.use(Picker)
app.use(DatePicker)
app.use(Cascader)

app.mount('#app')
