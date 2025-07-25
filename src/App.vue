<template>
  <div id="app">
    <header class="app-header">
      <div class="header-container">
        <div class="nav-links-container">
          <router-link to="/daily-arxiv" class="nav-link" :class="{ 'active-link': $route.path === '/daily-arxiv' }">
            <span>每日Arxiv</span>
          </router-link>
          <router-link to="/stats" class="nav-link" :class="{ 'active-link': $route.path === '/stats' }">
            <span>数据统计</span>
          </router-link>
        </div>
      </div>
    </header>
    <main class="app-main">
      <router-view />
    </main>
    <footer class="app-footer">
      <p class="copyright">&copy; {{ new Date().getFullYear() }} DailyArxiv</p>
    </footer>
  </div>
</template>

<script>
import { Document, Search, Collection, HomeFilled } from '@element-plus/icons-vue';

export default {
  name: 'App',
  components: {
    Document,
    Search,
    Collection,
    HomeFilled
  },
  methods: {
    goHome() {
      this.$router.push('/daily-arxiv');
    }
  }
};
</script>

<style>
:root {
  /* Layout variables */
  --content-width: 80%;
  --content-max-width: 1200px;
  --content-padding: 0;

  /* Font variables */
  --font-family-serif: "Microsoft YaHei", 'Noto Serif', 'Source Serif Pro', 'Palatino', 'Georgia', serif;
  --font-family-sans: "Microsoft YaHei", 'Noto Sans', 'Open Sans', 'Segoe UI', 'Arial', sans-serif;
  --font-family-mono: "Microsoft YaHei", 'Source Code Pro', 'JetBrains Mono', 'Courier New', monospace;

  /* Font size variables */
  --font-size-small: 18px;
  --font-size-medium: 20px;
  --font-size-large: 22px;
  --font-size-xlarge: 26px;
  --font-size-xxlarge: 30px;

  /* Font weight variables */
  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-bold: 600;

  /* Color variables - Warm Reading Mode */
  --bg-color-primary: #f8f5f1;
  --bg-color-secondary: #f3efe9;
  --bg-color-tertiary: #fffaf3;
  --text-color-primary: #5c4b3c;
  --text-color-regular: #7a6a5b;
  --text-color-secondary: #9c8c7d;
  --border-color: #e8e0d5;
  --highlight-color: #d2a76a;
  --link-color: #a06e3b;
  --shadow-color: rgba(92, 75, 60, 0.1);

  /* Form element variables */
  --form-element-height: 40px;
  --form-element-border-radius: 6px;
  --form-element-padding: 0 15px;

  /* Spacing variables */
  --spacing-small: 10px;
  --spacing-medium: 20px;
  --spacing-large: 30px;
}

/* 设置全局背景色 */
html, body {
  margin: 0;
  padding: 0;
  background-color: var(--bg-color-tertiary);
  font-family: var(--font-family-serif);
  font-size: var(--font-size-medium);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeLegibility;
  line-height: 1.6;
}

/* 隐藏页面右侧滚动条 */
html, body, #app {
  overflow-y: auto;
  /* scrollbar-width: none; */ /* Firefox */
  /* -ms-overflow-style: none; */  /* IE and Edge */
}

html::-webkit-scrollbar, 
body::-webkit-scrollbar, 
#app::-webkit-scrollbar {
  /* display: none; */ /* Chrome, Safari, Opera */
  /* width: 0; */
  /* background: transparent; */
}

/* Apply serif font to all Element Plus components */
.el-message-box,
.el-dialog,
.el-dropdown-menu,
.el-select-dropdown,
.el-tooltip__popper,
.el-popover,
.el-menu,
.el-table {
  font-family: var(--font-family-sans) !important;
}

#app {
  font-family: var(--font-family-serif);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  font-size: var(--font-size-medium);
  background-color: var(--bg-color-tertiary);
  color: var(--text-color-primary);
  letter-spacing: 0.01em;
}

.app-header {
  padding: 15px 0;
  background-color: #f5f1e8;
  border-bottom: 1px solid #e8e0d5;
  width: 100%;
}

.header-container {
  display: flex;
  justify-content: center;
  align-items: center;
  width: var(--content-width);
  max-width: var(--content-max-width);
  margin: 0 auto;
  box-sizing: border-box;
}

.logo-container {
  display: flex;
  align-items: center;
  cursor: pointer;
  height: 40px;
}

.app-title {
  font-size: 1.125rem;
  color: #6d5c4d;
  font-weight: 600;
  letter-spacing: 0.5px;
  white-space: nowrap;
}

.nav-links-container {
  display: flex;
  align-items: center;
  gap: 20px;
}

.nav-link {
  display: inline-block;
  text-decoration: none;
  color: var(--text-color-primary);
  padding: 4px 8px;
  transition: all 0.3s;
  font-size: 1.125rem;
  white-space: nowrap;
}

.nav-link:hover {
  color: var(--highlight-color) !important;
}

.active-link {
  color: var(--highlight-color) !important;
  font-weight: bold;
}

.nav-icon {
  margin-right: 5px;
}

.app-main {
  padding: var(--spacing-medium) 0;
  min-height: calc(100vh - 80px);
  width: var(--content-width);
  max-width: var(--content-max-width);
  margin: 0 auto;
  background-color: var(--bg-color-tertiary);
  margin-top: 5px;
  margin-bottom: var(--spacing-small);
  box-sizing: border-box;
}

.app-footer {
  text-align: center;
  padding: var(--spacing-medium) 0;
  background-color: var(--bg-color-tertiary);
  border-top: 1px solid var(--border-color);
  width: var(--content-width);
  max-width: var(--content-max-width);
  margin: 0 auto;
  box-sizing: border-box;
}

.copyright {
  margin: 0;
  color: var(--text-color-secondary);
  font-size: var(--font-size-small);
}

/* Global Element Plus component styles for consistent heights and warm theme */
.el-input__wrapper,
.el-select .el-input__wrapper,
.el-button,
.el-radio-group,
.el-radio-button,
.el-pagination-editor {
  font-family: var(--font-family-sans) !important;
  height: var(--form-element-height) !important;
  line-height: var(--form-element-height) !important;
  box-sizing: border-box !important;
  background-color: var(--bg-color-tertiary) !important;
  border-color: var(--border-color) !important;
  color: var(--text-color-primary) !important;
  box-shadow: 0 0 0 1px var(--border-color) !important;
}

.el-input__inner {
  height: 100% !important;
  line-height: var(--form-element-height) !important;
  color: var(--text-color-primary) !important;
  background-color: transparent !important;
  font-family: var(--font-family-sans) !important;
}

.el-select {
  width: 100%;
}

.el-select__wrapper {
  height: var(--form-element-height) !important;
}

.el-radio-button__inner {
  /* height: var(--form-element-height) !important; */
  line-height: calc(var(--form-element-height) - 2px) !important;
  /* padding: var(--form-element-padding) !important; */
  background-color: transparent !important;
  border: none !important;
  color: var(--text-color-primary) !important;
  border-radius: var(--form-element-border-radius) !important;
  margin: 0 !important;
  box-shadow: none !important;
  outline: none !important;
  display: inline-flex;
  align-items: center;
  justify-content: center;  
}

.el-radio-button.is-active .el-radio-button__inner {
  background-color: var(--highlight-color) !important;
  border: none !important;
  color: white !important;
  box-shadow: none !important;
}

.el-button--small,
.el-button--default {
  height: var(--form-element-height) !important;
  line-height: var(--form-element-height) !important;
  padding: var(--form-element-padding) !important;
  background-color: var(--bg-color-tertiary) !important;
  border-color: var(--border-color) !important;
  color: var(--text-color-primary) !important;
}

.el-button--primary {
  background-color: var(--highlight-color) !important;
  border-color: var(--highlight-color) !important;
  color: white !important;
}

/* Pagination controls */
.el-pagination {
  display: flex;
  justify-content: center;
  margin: 20px auto;
  padding: 10px 0;
}

.el-pagination .el-select .el-input,.el-date-picker
.el-pagination button,
.el-pagination span:not([class*=suffix]),
.el-pagination .el-input__wrapper,
.el-pagination .el-input__inner {
  height: var(--form-element-height) !important;
  line-height: var(--form-element-height) !important;
  color: var(--text-color-primary) !important;
}

.el-pagination .el-select .el-input .el-date-picker {
  width: auto;
}

.el-pagination button:not(:disabled) {
  color: var(--text-color-primary) !important;
  background-color: var(--bg-color-tertiary) !important;
}

.el-pagination button:disabled {
  color: var(--text-color-secondary) !important;
  background-color: var(--bg-color-secondary) !important;
}

/* 当前页码样式 */
.el-pagination .is-active {
  color: #ffffff !important;
  background-color: var(--highlight-color) !important;
  font-weight: bold;
  border-radius: 4px;
}

/* 页码按钮样式 */
.el-pagination .el-pager li {
  background-color: #f5f1ea !important;
  color: var(--text-color-primary) !important;
  border: 1px solid #e0d6c9 !important;
  margin: 0 3px;
  min-width: 32px;
  height: 32px;
  line-height: 32px;
  border-radius: 4px;
  transition: all 0.3s;
}

/* 页码按钮悬停样式 */
.el-pagination .el-pager li:hover:not(.is-active) {
  color: var(--highlight-color) !important;
  border-color: var(--highlight-color) !important;
}

/* 前进后退按钮样式 */
.el-pagination .btn-prev,
.el-pagination .btn-next {
  background-color: #f5f1ea !important;
  color: var(--text-color-primary) !important;
  border: 1px solid #e0d6c9 !important;
  border-radius: 4px;
  margin: 0 3px;
  padding: 0 10px;
}

/* 前进后退按钮悬停样式 */
.el-pagination .btn-prev:hover,
.el-pagination .btn-next:hover {
  color: var(--highlight-color) !important;
  border-color: var(--highlight-color) !important;
}

/* Fix for select dropdown in pagination */
.el-pagination .el-select .el-input .el-input__wrapper .el-date-picker {
  padding-right: 25px !important;
}

/* Custom styles for el-backtop */
.el-backtop {
  --el-backtop-bg-color: var(--bg-color-tertiary);
  --el-backtop-hover-bg-color: var(--bg-color-secondary);
  border: 1px solid var(--border-color);
  transition: all 0.3s;
}

.el-backtop .el-icon {
  color: var(--text-color-primary);
}

.el-backtop:hover {
  border-color: var(--highlight-color);
}

.el-backtop:hover .el-icon {
  color: var(--highlight-color);
}

/* Responsive design for different screen sizes */
@media (max-width: 1200px) {
  :root {
    --content-width: 90%;
  }
}

@media (max-width: 768px) {
  .header-container,
  .app-main,
  .app-footer {
    width: 95%;
  }

  .header-container {
    flex-direction: column;
    align-items: center;
    padding: 5px 0;
  }

  .logo-container {
    margin-bottom: 10px;
  }

  .nav-links-container {
    gap: 15px;
  }

  .nav-link {
    font-size: 0.95rem;
    padding: 4px 4px;
    white-space: nowrap;
  }
  
  .app-title {
    font-size: 1.25rem;
  }

  .app-main {
    padding: var(--spacing-small) 0;
  }
}

/* Ensure content integrity when scaling/zooming */
@media (min-resolution: 1.25dppx) {
  .header-container,
  .app-main,
  .app-footer {
    transform: none;
    transform-origin: top left;
  }
}
</style>


