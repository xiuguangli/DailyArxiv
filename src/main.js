import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './element-overrides.css'
import router from './router'
import 'katex/dist/katex.min.css'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'




const app = createApp(App)

app.use(ElementPlus, { locale: zhCn })
app.use(router)
app.mount('#app')
