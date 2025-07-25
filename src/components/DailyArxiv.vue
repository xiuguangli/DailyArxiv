<template>
  <div>
    <!-- 统一容器：包含过滤器、搜索和结果区域 -->
    <div class="filter-container">
      <!-- 过滤器和搜索区域 -->
      <el-row :gutter="5" class="filter-row top-controls-row" type="flex" justify="space-between">

        <el-col :span="6" class="control-container">
          <div class="control-wrapper">
            <el-select
              id="category-select"
              v-model="selectedCategory"
              placeholder="选择类别"
              @change="searchPapers"
              class="perfectly-aligned-control"
              title="选择类别"
            >
              <el-option label="cs.CV" value="cs.CV"></el-option>
              <el-option label="cs.AI" value="cs.AI"></el-option>
              <el-option label="cs.LG" value="cs.LG"></el-option>
            </el-select>
          </div>
        </el-col>

        <el-col :span="6" class="control-container">
          <div class="control-wrapper">
            <el-date-picker
              id="date-picker"
              v-model="selectedDate"
              type="date"
              placeholder="选择日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              :cell-class-name="dateCellClass"
              @change="searchPapers"
              class="perfectly-aligned-control"
              title="选择日期"
              :picker-options="{
                firstDayOfWeek: 1,
                // 自定义周标题
                dayNames: ['日', '一', '二', '三', '四', '五', '六'],
                // 限制可选年份和月份
                disabledDate: (date) => {
                  const y = date.getFullYear();
                  const m = (date.getMonth() + 1).toString().padStart(2, '0');
                  // 只允许data.json中出现过的年份和月份
                  if (!this.availableDates.some(d => d.startsWith(`${y}-${m}`))) {
                    return true;
                  }
                  return false;
                }
              }"
            ></el-date-picker>
          </div>
        </el-col>

        <el-col :span="6" class="control-container">
          <div class="control-wrapper">
            <label for="title-search" style="display:none;">标题搜索</label>
            <el-input
              id="title-search"
              v-model="searchQuery"
              placeholder="在标题中搜索"
              clearable
              @clear="searchQuery = ''; searchPapers()"
              @input="searchPapers"
              class="perfectly-aligned-control"
              title="在标题中搜索"
            >
              <template #prefix><el-icon><Search /></el-icon></template>
            </el-input>
          </div>
        </el-col>

        <el-col :span="6" class="control-container">
          <div class="control-wrapper">
            <label for="abstract-search" style="display:none;">摘要搜索</label>
            <el-input
              id="abstract-search"
              v-model="abstractSearchQuery"
              placeholder="在摘要中搜索"
              clearable
              @clear="abstractSearchQuery = ''; searchPapers()"
              @input="searchPapers"
              class="perfectly-aligned-control"
              title="在摘要中搜索"
            >
              <template #prefix><el-icon><Search /></el-icon></template>
            </el-input>
          </div>
        </el-col>
      </el-row>
      
      <el-row :gutter="5" class="filter-row"> 
        
        <el-col :span="12" class="search-results-info">
          <span>找到 {{ filteredPapers.length }} 篇匹配论文</span>
        </el-col>

        <el-col :span="6">
          <el-row :gutter="5" class="expand-row">
            <el-col :span="11">
              <div class="custom-button-wrapper" :class="{'active-wrapper': expandAll.abstract}">
                <div class="button-text" @click="expandAllAbstracts">
                  <span class="no-padding-text">{{ expandAll.abstract ? '收起摘要' : '展开摘要' }}</span>
                </div>
              </div>
            </el-col>
            <!-- <el-col :span="1"></el-col>> -->
            <el-col :span="11">
              <div class="custom-button-wrapper" :class="{'active-wrapper': expandAll.gemini}">
                <div class="button-text" @click="expandAllGemini">
                  <span class="no-padding-text">{{ expandAll.gemini ? '收起解读' : '展开解读' }}</span>
                </div>
              </div>
            </el-col>
          </el-row>
        </el-col>


        <el-col :span="6">
          <el-row :gutter="5">
            <el-col :span="12">
              <span>共 {{ filteredPapers.length }} 篇</span>
            </el-col>
            <el-col :span="12">
              <el-select v-model="pageSize" @change="handleSizeChange" size="small">
                <el-option :value="10" label="10 篇/页" />
                <el-option :value="50" label="50 篇/页" />
                <el-option :value="100" label="100 篇/页" />
                <el-option :value="filteredPapers.length" label="全部显示" />
              </el-select>
            </el-col>
          </el-row>
        </el-col>

      </el-row>
    </div>

    <!-- 论文列表容器 -->
    <div class="paper-list-container">
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container">
        <div>
          <h3>正在加载数据...</h3>
          <div class="progress-container">
            <el-progress
              :percentage="loadingProgress"
              :stroke-width="20"
              status="success"
            />
          </div>
          <p>正在加载多个会议的数据，请稍候...</p>
        </div>
        <el-skeleton :rows="5" animated />
      </div>

      <!-- 错误提示 -->
      <div v-else-if="error" class="error-container">
        <el-empty
          description="加载数据失败"
          :image-size="200"
        >
          <template #description>
            <p>{{ error }}</p>
          </template>
          <el-button @click="searchPapers">重试</el-button>
        </el-empty>
      </div>

      <!-- 论文列表 -->
      <div v-else-if="paginatedPapers.length > 0">
        <paper-card
          v-for="(paper, index) in paginatedPapers"
          :key="paper.id || index"
          :paper="paper"
          :index="(currentPage - 1) * pageSize + index"
          :title-keywords="searchKeywords"
          :abstract-keywords="abstractSearchKeywords"
          :expanded="expandedAbstracts[index]"
          :expand-all="expandAll"
          @toggle-abstract="handleToggleAbstract"
        />

        <!-- 底部分页导航 -->
        <div v-if="filteredPapers.length > pageSize" class="pagination-container">
          <el-pagination
            :current-page="currentPage"
            :page-size="pageSize"
            layout="prev, pager, next, jumper"
            :total="filteredPapers.length"
            :pager-count="7"
            @current-change="handleCurrentChange"
            background
            hide-on-single-page
          />
        </div>
      </div>

      <!-- 无数据提示 -->
      <div v-else class="empty-container">
        <el-empty :description="!searchPerformed ? '请选择搜索条件并点击搜索' : '未找到匹配的论文'" />
      </div>
    </div>

    <!-- 回到顶部 -->
    <el-backtop :right="40" :bottom="40" />
  </div>
</template>

<script>
import { Search, ArrowUp, ArrowDown } from '@element-plus/icons-vue';
import PaperCard from './PaperCard.vue';

export default {
  components: {
    Search,
    ArrowUp,
    ArrowDown,
    PaperCard
  },
  name: 'DailyArxiv',
  data() {
    return {
      // 数据
      allPapers: [],
      filteredPapers: [],
      loadedDatasets: new Set(),

      // 状态
      loading: false,
      error: null,
      expandedAbstracts: {},
      searchPerformed: false,
      expandAll: {
        abstract: false,
        gemini: false
      },

      // 加载进度
      loadingProgress: 0,
      loadedDatasetCount: 0,
      totalDatasetCount: 0,

      // 过滤和搜索
      selectedCategory: 'cs.CV',
      selectedDate: (new Date()).toISOString().slice(0, 10),
      availableDates: [],
      searchQuery: '',
      searchKeywords: [],
      abstractSearchQuery: '',
      abstractSearchKeywords: [],

      // 分页
      currentPage: 1,
      pageSize: 10,

    }
  },

  computed: {
    paginatedPapers() {
      // 如果页面大小等于总数量，则显示全部
      if (this.pageSize >= this.filteredPapers.length) {
        return this.filteredPapers;
      }

      const start = (this.currentPage - 1) * this.pageSize;
      const end = start + this.pageSize;
      return this.filteredPapers.slice(start, end);
    },

    totalPages() {
      return Math.ceil(this.filteredPapers.length / this.pageSize);
    }
  },

  async mounted() {
    // 预加载可用日期（从 data.json 读取）
    await this.fetchAvailableDatesFromJson();

    // 默认类别为 cs.CV，默认日期为 data.yml 里的最新日期（无论今天是否有数据）
    this.selectedCategory = 'cs.CV';
    if (this.availableDates && this.availableDates.length > 0) {
      // 按降序排列，取第一个（最新）
      this.selectedDate = this.availableDates.slice().sort((a, b) => b.localeCompare(a))[0];
    } else {
      this.selectedDate = '';
    }
    // 自动搜索
    this.searchPapers();
  },

  methods: {
    // 分页
    handleSizeChange(newPageSize) {
      this.pageSize = newPageSize;
      this.currentPage = 1; // 更改每页数量后，回到第一页
    },

    handleCurrentChange(newPage) {
      this.currentPage = newPage;
      window.scrollTo(0, 0); // 切换页面后滚动到顶部
    },
    

    // 搜索论文

    async searchPapers() {
      // 校验筛选条件
      if (!this.selectedCategory) {
        this.error = "请选择类别";
        return;
      }
      if (!this.selectedDate) {
        this.error = "请选择日期";
        return;
      }

      // 检查选中的日期是否为有效日期
      if (!this.availableDates.includes(this.selectedDate)) {
        this.error = "当前日期无论文";
        this.filteredPapers = [];
        this.loading = false;
        this.searchPerformed = true;
        return;
      }

      this.loading = true;
      this.error = null;
      this.searchPerformed = true;
      this.filteredPapers = [];
      this.currentPage = 1;

      try {
        // 拆分日期
        const [year, month, day] = this.selectedDate.split('-');
        // const filePath = `/data/${year}/${month}/${year}-${month}-${day}_${this.selectedCategory}.json`;
        const filePath = `${import.meta.env.BASE_URL}data/${year}/${month}/${year}-${month}-${day}_${this.selectedCategory}.json`;
        let response = await fetch(filePath);
        if (!response.ok) {
          this.error = "未找到对应日期的 arxiv 数据";
          this.loading = false;
          return;
        }
        const data = await response.json();
        this.allPapers = Array.isArray(data) ? data : (data.papers || []);

        // 处理搜索关键词
        this.processSearchKeywords();

        // 应用搜索过滤
        this.applySearch();

        console.log('搜索完成，找到匹配论文数量:', this.filteredPapers.length);
      } catch (error) {
        console.error('搜索 arxiv 论文失败:', error);
        this.error = "搜索 arxiv 论文失败。请检查网络连接或重试。";
      } finally {
        this.loading = false;
      }
    },


    // 处理搜索关键词
    processSearchKeywords() {
      // 处理标题搜索关键词
      this.searchKeywords = this.searchQuery
        ? this.searchQuery.toLowerCase().split(/\s+/).filter(keyword => keyword.length > 0)
        : [];

      // 处理摘要搜索关键词
      this.abstractSearchKeywords = this.abstractSearchQuery
        ? this.abstractSearchQuery.toLowerCase().split(/\s+/).filter(keyword => keyword.length > 0)
        : [];
    },

    // 应用搜索过滤
    applySearch() {
      // 过滤出符合当前类别和日期的论文
      this.filteredPapers = this.allPapers.filter(paper => {
        // 类别判断
        const subjects = (paper.subjects || '').toLowerCase();
        const category = this.selectedCategory.toLowerCase();
        const isCategoryMatch = subjects.includes(category);

        // 日期判断
        const isDateMatch = paper.date === this.selectedDate;

        if (!isCategoryMatch || !isDateMatch) {
          return false;
        }

        const title = (paper.title || '').toLowerCase();
        const abstract = (paper.abstract || '').toLowerCase();

        // 标题搜索逻辑
        let titleMatch = true;
        if (this.searchKeywords.length > 0) {
          titleMatch = this.searchKeywords.every(keyword => title.includes(keyword));
        }

        // 摘要搜索逻辑
        let abstractMatch = true;
        if (this.abstractSearchKeywords.length > 0) {
          abstractMatch = this.abstractSearchKeywords.every(keyword => abstract.includes(keyword));
        }

        if (this.searchKeywords.length === 0 && this.abstractSearchKeywords.length === 0) {
          return true;
        } else if (this.searchKeywords.length === 0) {
          return abstractMatch;
        } else if (this.abstractSearchKeywords.length === 0) {
          return titleMatch;
        } else {
          return titleMatch && abstractMatch;
        }
      });
      // 不再排序，保持原始顺序
    },



    // 重置筛选条件
    resetFilters() {
      // 清空搜索条件
      this.searchQuery = '';
      this.abstractSearchQuery = '';
      this.searchKeywords = [];
      this.abstractSearchKeywords = [];


      // 保留已加载的数据，但清空过滤结果
      this.filteredPapers = [];
      this.searchPerformed = false;
      this.error = null;

      // 不清空 allPapers 和 loadedDatasets，以便保留已加载的数据
    },

    toggleAbstract(index) {
      // Vue 3 中直接修改对象属性即可触发响应式更新
      this.expandedAbstracts[index] = !this.expandedAbstracts[index];
    },

    handleToggleAbstract(index, isExpanded) {
      // 从子组件接收展开/收起事件
      this.expandedAbstracts[index] = isExpanded;
    },

    handleSizeChange(size) {
      this.currentPage = 1; // 改变每页显示数量时，重置为第一页
      this.pageSize = size;
    },

    expandAllAbstracts() {
      // 切换摘要的展开/收起状态
      this.expandAll.abstract = !this.expandAll.abstract;
      
      // 如果展开摘要，则确保解读是收起的
      if (this.expandAll.abstract) {
        this.expandAll.gemini = false;
      }
      
      // 强制更新，确保子组件接收到变化
      this.$forceUpdate();
    },

    expandAllGemini() {
      // 切换解读的展开/收起状态
      this.expandAll.gemini = !this.expandAll.gemini;
      
      // 如果展开解读，则确保摘要是收起的
      if (this.expandAll.gemini) {
        this.expandAll.abstract = false;
      }
      
      // 强制更新，确保子组件接收到变化
      this.$forceUpdate();
    },

    // 日期面板自定义样式
    dateCellClass(cell) {
      // 兼容 Element Plus 2.x/1.x 的参数传递方式
      let date;
      if (cell && cell.date instanceof Date) {
        date = cell.date;
      } else if (cell instanceof Date) {
        date = cell;
      } else {
        return '';
      }
      const y = date.getFullYear();
      const m = (date.getMonth() + 1).toString().padStart(2, '0');
      const d = date.getDate().toString().padStart(2, '0');
      const dateStr = `${y}-${m}-${d}`;
      // 只有 availableDates 里的日期高亮，其余灰色
      return this.availableDates && this.availableDates.includes(dateStr)
        ? 'arxiv-date-available'
        : 'arxiv-date-unavailable arxiv-date-disabled is-today-fix';
    },

    // 新的：从 data.json 读取所有可用日期和类别
    async fetchAvailableDatesFromJson() {
      // 读取 JSON 格式的日期数据（结构示例：2025: { '07': [18] }）
      try {
          // const resp = await fetch('/data/data.json');
          // 从配置文件加载会议和年份信息
          const resp = await fetch(`${import.meta.env.BASE_URL}data/data.json`);
        if (!resp.ok) {
          this.availableDates = [];
          console.error('无法加载 data.json');
          return;
        }
          const data = await resp.json();
          console.log('data.json:', data);
        if (data) {
          // 转换为 ['2025-07-18', ...] 格式
          const dates = [];
          for (const year in data) {
            for (const month in data[year]) {
              for (const day of data[year][month]) {
                dates.push(`${year}-${month.padStart(2, '0')}-${String(day).padStart(2, '0')}`);
              }
            }
          }
          this.availableDates = dates;
          // 默认选中最新日期
          if (!this.selectedDate && this.availableDates.length > 0) {
            this.selectedDate = this.availableDates.slice().sort((a, b) => b.localeCompare(a))[0];
          }
        }
      } catch {
        this.availableDates = [];
      }
    },
  }
};
</script>

<style>

.filter-container{
  padding: 20px var(--content-padding, 0);
  margin-bottom: 20px;
  margin-top: 0;
  width: var(--content-width);
  max-width: var(--content-max-width);
  margin-left: auto;
  margin-right: auto;
  box-sizing: border-box;
  /* 覆盖全局变量，统一本区域表单控件高度 */
  --form-element-height: 32px;
}

/* Add paper-list-container style for consistent alignment */
.paper-list-container {
  padding: 0;
  width: var(--content-width);
  max-width: var(--content-max-width);
  margin-left: auto;
  margin-right: auto;
  box-sizing: border-box;
}

/* Add specific rules for perfect alignment */
.paper-list-container > div {
  padding: 0;
  margin: 0;
  width: 100%;
  box-sizing: border-box;
}

/* Ensure no extra margins or padding in result items */
.result-item-container {
  padding: 0;
  margin: 0;
  box-sizing: border-box;
}

/* 统一行高和高度，使用变量 */
.filter-container .el-button--default,
.filter-container .el-radio-button__inner,
.filter-container .el-input__wrapper {
  line-height: var(--form-element-height) !important;
  height: var(--form-element-height) !important;
}

/* 确保顶部控件行完美对齐 */
.top-controls-row {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
  height: 32px;
}

/* 每个控件容器垂直居中 */
.control-container {
  display: flex;
  align-items: center;
  height: 32px;
}

.expand-row{
  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* 控件包装容器，确保高度一致 */
.control-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 32px;
  width: 100%;
}

/* 年份选择列样式 */
.year-select-col {
  display: flex;
  align-items: center;
  height: 32px;
  padding: 0;
}

/* 确保所有 Element Plus 表单控件的包装器都有一致的高度和对齐方式 */
.filter-container .el-select .el-input__wrapper,
.filter-container .el-input .el-input__wrapper {
  height: var(--form-element-height) !important;
  box-sizing: border-box !important;
  padding-top: 0 !important;
  padding-bottom: 0 !important;
  display: flex !important;
  align-items: center !important;
}

/* 确保下拉选择器的高度和行高一致 */
.el-select {
  width: 100%;
}

/* 精确设置表单组件的尺寸 */
.perfectly-aligned-control {
  width: 100% !important;
  min-width: 0 !important;
}

/* 确保输入框内部元素垂直居中 */
.filter-container .el-input__inner {
  height: calc(var(--form-element-height) - 2px) !important;
  line-height: calc(var(--form-element-height) - 2px) !important;
  margin: 0 !important;
  padding-top: 0 !important;
  padding-bottom: 0 !important;
}

/* 去除排序按钮的边框 */
.sort-direction-btn {
  border: none !important;
  background: transparent !important;
  box-shadow: none !important;
  font-size: 16px;
}

/* 年份区间分隔符样式 */
.separator-text {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}

/* 展开按钮样式 */
.expand-row .el-button {
  width: 100%;
  height: 28px;
  padding: 0;
  margin: 0;
  font-size: 13px;
  transition: all 0.3s ease;
  border: none;
  background: transparent;
  box-shadow: none;
  color: #333;
}

.expand-button {
  position: relative;
}

/* 覆盖 Element Plus 的内部样式 */
.expand-button .el-button__content {
  margin-left: 0;
  padding-left: 0;
  justify-content: flex-start;
}

.text-left {
  text-align: left !important;
  padding-left: 0 !important;
}

/* 所有激活按钮特效已移除 */

/* 为了使按钮看起来更像第二张图中所示的效果 */
.expand-button {
  border: 1px dashed transparent !important;
  margin: 0;
}

/* 分隔符容器样式 */
.separator-container {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 32px;
  padding: 0;
}

/* 年份范围行样式 */
.year-range-row {
  display: flex;
  align-items: center;
  height: 32px;
  margin: 0;
}

/* 水平对齐筛选按钮 */
.filter-row {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

/* 确保下拉框和按钮组的高度一致 */
.el-select,
.el-radio-group,
.el-input,
.el-button {
  height: 32px !important;
  line-height: 32px !important;
}

/* 精确设置输入框包装器的高度 */
.el-input__wrapper {
  height: 32px !important;
  line-height: 32px !important;
  padding: 0 11px !important;
}

/* 确保下拉框的高度一致 */
.el-select__wrapper {
  height: 32px !important;
  line-height: 32px !important;
}

/* 让按钮和图标垂直居中 */
.el-button {
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 确保单选按钮组和按钮在同一水平线上 */
.el-radio-group {
  display: flex;
  align-items: center;
}

/* 确保无线电按钮内容垂直居中 */
.el-radio-button__inner {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

/* 标题对齐 */
.search-results-info {
  display: flex;
  align-items: center;
}

/* 让排序控件严格在同一水平线上对齐 */
.control-align-row {
  display: flex;
  align-items: center;
}

.control-align-row .el-radio-button,
.control-align-row .el-button {
  height: 32px;
  box-sizing: border-box;
}

/* 确保单选按钮和排序按钮的内容都处于中央位置 */
.control-align-row .el-radio-button__inner,
.control-align-row .el-button {
  padding: 0 12px;
  line-height: 30px;
  vertical-align: middle;
}

/* 强制文本完全贴左 */
.expand-row .el-button span {
  display: block;
  width: 100%;
  text-align: left;
  padding: 0;
  margin: 0;
}

/* 覆盖按钮的默认边距 */
.expand-row .el-button--default {
  padding-left: 0 !important;
  display: flex;
  align-items: center;
  justify-content: flex-start;
}

/* 确保文字没有边距 */
.active-button > span {
  margin-left: 0;
}

/* 自定义按钮容器样式 */
.custom-button-wrapper {
  position: relative;
  display: block;
  padding: 0; /* 完全去除所有padding */
  cursor: pointer;
  border: none; /* 完全移除边框 */
  transition: all 0.3s;
  border-radius: 0; /* 移除圆角 */
  line-height: 1.5;
  height: 32px;
  box-sizing: border-box;
}

/* 激活状态的容器样式 - 不使用任何特效 */
/* 确保激活状态下的文本贴左 */
.active-wrapper .button-text {
  left: 0;
  padding-left: 0;
}

/* 按钮文字样式 */
.button-text {
  display: flex;
  align-items: center; /* 垂直居中 */
  text-align: left;
  padding: 0;
  margin: 0;
  padding-left: 0; /* 确保没有左padding */
  width: 100%;
  line-height: 30px; /* 与按钮高度一致，实现垂直居中 */
  white-space: nowrap; /* 防止文本换行 */
  position: absolute; /* 使用绝对定位确保完全靠左 */
  left: 0; /* 确保文本完全靠左边框 */
  top: 0; /* 顶部对齐 */
  height: 100%; /* 占满整个高度 */
  border-left: 0; /* 确保左边没有边框 */
}

/* 确保文字完全没有padding */
.no-padding-text {
  padding: 0;
  margin: 0;
  display: block;
  text-align: left;
}
/* 日历整体背景和选中颜色自定义，协调页面风格 */
.el-picker-panel,
.el-picker-panel__body,
.el-date-table,
.el-date-table td {
  background: #f7f8fa !important;
  color: #222 !important;
  border-radius: 0 !important;
}

/* 选中日期样式 */
.el-date-table td.is-selected span,
.el-date-table td.is-range span,
.el-date-table td.in-range span {
  background: #222 !important;
  color: #fff !important;
  border-radius: 6px !important;
}

/* 日期悬浮样式 */
.el-date-table td.available:hover span {
  background: #e5e7eb !important;
  color: #222 !important;
}

/* 年份、月份选择器选中和悬浮 */
.el-year-table .el-date-table-cell.is-selected div,
.el-month-table .el-date-table-cell.is-selected div,
.el-year-table .el-date-table-cell:hover div,
.el-month-table .el-date-table-cell:hover div {
  background: #222 !important;
  color: #fff !important;
  border-radius: 6px !important;
}

/* 年份、月份选择器普通项 */
.el-year-table .el-date-table-cell div,
.el-month-table .el-date-table-cell div {
  background: transparent !important;
  color: #222 !important;
}

/* 去除element默认蓝色边框和阴影 */
.el-picker-panel *:focus {
  outline: none !important;
  box-shadow: none !important;
  border-color: #222 !important;
}
/* 修正“今天”日期在不可用时也为灰色 */
.is-today-fix span {
  font-weight: normal !important;
  color: #b0b3ba !important;
  background: #f3f4f6 !important;
}
/* 强制去除当前日期加粗高亮，仅根据 data.json 控制显示 */
.el-picker-panel__content .el-date-table td.is-today span {
  font-weight: normal !important;
  color: inherit !important;
}
/* 去除当前日期加粗高亮，仅根据 data.json 控制显示 */
.el-picker-panel__content .is-today {
  font-weight: normal !important;
  color: inherit !important;
}
/* 日历不可用日期灰色样式 */
.arxiv-date-unavailable,
.arxiv-date-disabled {
  color: #b0b3ba !important;
  background: #f3f4f6 !important;
  pointer-events: none;
  opacity: 1;
  border-radius: 4px;
}
.arxiv-date-available {
  color: #222 !important;
  background: inherit !important;
}
</style>