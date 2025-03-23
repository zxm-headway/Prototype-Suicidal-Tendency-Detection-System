<template>
  <div id="pie-chart" ref="chartRef" style="width: 100%; height: 40vh;"></div>
</template>

<script setup>
import { ref, onMounted, watch, onBeforeUnmount, nextTick } from 'vue';
import * as echarts from 'echarts';

const props = defineProps({
  chartData: {
    type: Array,
    required: true,
  },
});

const chartRef = ref(null);
const chartInstance = ref(null);

// 初始化图表
const initChart = () => {
  if (chartRef.value) {
    chartInstance.value = echarts.init(chartRef.value);
    window.addEventListener('resize', resizeChart);
  }
};

// 设置图表数据
const setChartOptions = (data) => {
  const option = {
    tooltip: {
      trigger: 'item',
    },
    legend: {
      top: '5%',
      left: 'center',
    },
    series: [
      {
        name: '占比',
        type: 'pie',
        radius: '50%',
        data: data,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)',
          },
        },
      },
    ],
  };
  if (chartInstance.value) {
    chartInstance.value.setOption(option);
  }
};

// 监听 props 的变化以更新图表
watch(
  () => props.chartData,
  (newData) => {
    setChartOptions(newData);
  },
  { immediate: true }
);

// 调整图表大小
const resizeChart = () => {
  if (chartInstance.value) {
    chartInstance.value.resize();
  }
};

onMounted(async () => {
  await nextTick();  // 确保 DOM 已渲染
  initChart();
  setChartOptions(props.chartData);
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeChart);
  if (chartInstance.value) {
    chartInstance.value.dispose();
  }
});
</script>

<style scoped>
#pie-chart {
  width: 100%;
  height: 100%; /* 这里保持 100% 可以让图表适应父容器 */
}
</style>
