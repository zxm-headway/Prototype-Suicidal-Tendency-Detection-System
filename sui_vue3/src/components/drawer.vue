<template>
  <div>
    <!-- 用户帖子抽屉 -->
    <el-drawer
      v-model="drawerOC"
      size="50%"
      @close="closeDrawer"
    >
      <template #header>
        <div>
          用户帖子
          <el-tag
            v-if="props.labels === 1 || props.labels === true"
            type="danger"
            style="margin-left: 10px;"
            size="large"
          >
            具有自杀意念
          </el-tag>
          <el-tag
            v-else
            type="success"
            style="margin-left: 10px;"
          >
            正常
          </el-tag>
        </div>
      </template>

      <el-table :data="paginatedPosts" style="width: 100%">
        <el-table-column prop="post_id" label="帖子ID" width="100" />
        <el-table-column prop="content" label="内容" width="600" />
      </el-table>

      <!-- 查看情感波动按钮 -->
      <el-button
        type="primary"
        @click="viewEmotionWave"
        style="margin-top: 10px; width: 50%;"
      >
        查看情感波动
      </el-button>

      <el-pagination
        :current-page="currentPage"
        :page-size="pageSize"
        :total="props.posts.length"
        layout="total, prev, pager, next"
        @current-change="handleCurrentChange"
      />
    </el-drawer>

    <!-- 情感波动折线图对话框 -->
    <el-dialog
      title=""
      v-model="drawerEmotionWave"
      width="50%"
      @opened="initEmotionChart"
      @close="disposeChart"
    >
      <div ref="emotionChart" style="width: 100%; height: 400px;"></div>
      <template #footer>
        <el-button @click="drawerEmotionWave = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onBeforeUnmount } from 'vue';
import { defineProps, defineEmits } from 'vue';
import * as echarts from 'echarts';
import { checkEmotionWave } from "../API/textDection";  // 导入封装好的 axios 方法

const props = defineProps({
  modelValue: { type: Boolean, required: true },
  posts: { type: Array, default: () => [] },
  labels: { type: [Number, Boolean], default: 0 }
});

const emit = defineEmits(['update:modelValue']);

console.log(props);

// 控制抽屉显示
const drawerOC = ref(false);
watch(() => props.modelValue, (newVal) => {
  drawerOC.value = newVal;
});
const closeDrawer = () => {
  emit('update:modelValue', false);
};

// 分页数据
const currentPage = ref(1);
const pageSize = ref(6);
const paginatedPosts = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  return props.posts.slice(start, start + pageSize.value);
});
const handleCurrentChange = (newPage) => {
  currentPage.value = newPage;
};

// 情感波动对话框控制及 ECharts 容器引用
const drawerEmotionWave = ref(false);
const emotionChart = ref(null);
let chartInstance = null;

// 存储情感分析结果数据
const emotionData = ref([]);

// 点击按钮：从前20条帖子获取文本，调用后端情感分析接口，并打开对话框
const viewEmotionWave = async () => {
  const postsToAnalyze = props.posts.slice(0, 20).map(post => post.content);
  try {
    const res = await checkEmotionWave(postsToAnalyze);
    if (res && res.emotions_wave) {
      emotionData.value = res.emotions_wave;
      console.log("情感分析结果：", emotionData.value);
    }
  } catch (error) {
    console.error("情感分析请求失败：", error);
  }
  drawerEmotionWave.value = true;
};

// 初始化 ECharts 折线图
const initEmotionChart = async () => {
  await nextTick(); // 等待 DOM 更新
  // 延时100ms确保对话框完全展开并稳定
  setTimeout(() => {
    if (emotionChart.value) {
      if (chartInstance) {
        chartInstance.dispose();
      }
      chartInstance = echarts.init(emotionChart.value);
      
      // 横坐标为帖子序号，从1开始
      const xData = emotionData.value.map((_, index) => index + 1);

      const option = {
        title: { text: '情感波动折线图' },
        tooltip: { trigger: 'axis' },
        xAxis: {
          type: 'category',
          data: xData,
          name: '帖子序号'
        },
        yAxis: {
          type: 'value',
          min: 0,
          max: 1,
          name: '情感分数'
        },
        series: [
          {
            name: '情感值',
            type: 'line',
            data: emotionData.value,
            markArea: {
  label: {
    show: true,
    position: 'inside',
    formatter: '{b}',
    color: '#000'
  },
  emphasis: {
    label: {
      show: true,
      position: 'inside',
      formatter: '{b}',
      color: '#000'
    }
  },
  data: [
    [
      { yAxis: 0, name: '负面情感', itemStyle: { color: 'rgba(255, 0, 0, 0.2)' } },
      { yAxis: 0.3 }
    ],
    [
      { yAxis: 0.3, name: '中性情感', itemStyle: { color: 'rgba(255, 255, 0, 0.2)' } },
      { yAxis: 0.7 }
    ],
    [
      { yAxis: 0.7, name: '正面情感', itemStyle: { color: 'rgba(0, 255, 0, 0.2)' } },
      { yAxis: 1 }
    ]
  ]
}
          }
        ]
      };
      chartInstance.setOption(option);
      window.addEventListener('resize', resizeChart);
    }
  }, 100);
};

// 响应窗口大小变化，调整图表尺寸
const resizeChart = () => {
  if (chartInstance) {
    chartInstance.resize();
  }
};

// 释放图表资源
const disposeChart = () => {
  if (chartInstance) {
    chartInstance.dispose();
    chartInstance = null;
  }
  window.removeEventListener('resize', resizeChart);
};

// 在组件卸载前移除事件监听
onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeChart);
});
</script>

<style scoped>
/* 根据需要添加自定义样式 */
</style>
