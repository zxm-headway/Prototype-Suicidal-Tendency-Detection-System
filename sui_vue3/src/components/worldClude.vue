<template>
  <div ref="wordCloud" style="width: 100%; height: 40vh;"></div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue';
import * as echarts from 'echarts';
import 'echarts-wordcloud';

// 接收父组件传递的词云数据，要求数据格式为：[{ name: '词语', value: 数值 }, ...]
const props = defineProps({
  words: {
    type: Array,
    required: true,
  },
});

const wordCloud = ref(null);
let chart = null;

// 用于缓存每个词对应的随机颜色
const colorMap = {};

// 生成随机颜色的函数
const getRandomColor = () => {
  const r = Math.floor(Math.random() * 160);
  const g = Math.floor(Math.random() * 160);
  const b = Math.floor(Math.random() * 160);
  return `rgb(${r}, ${g}, ${b})`;
};

// 更新词云：旧词颜色固定，新词分配随机颜色
const updateWordCloud = () => {
  // 为每个词固定随机颜色
  const wordsWithColors = props.words.map(word => {
    if (!colorMap[word.name]) {
      colorMap[word.name] = getRandomColor();
    }
    return { ...word, color: colorMap[word.name] };
  });
  
  const options = {
    tooltip: {
      show: true,
    },
    series: [
      {
        type: 'wordCloud',
        shape: 'circle',
        left: 'center',
        top: 'center',
        width: '100%',
        height: '100%',
        sizeRange: [12, 50],
        rotationRange: [-90, 90],
        gridSize: 8,
        drawOutOfBound: false, // 设置为 false 确保词云不会超出容器
        textStyle: {
          fontFamily: 'sans-serif',
          fontWeight: 'bold',
          color: (params) => params.data.color,  // 使用固定的随机颜色
        },
        data: wordsWithColors,
      },
    ],
  };

  if (chart) {
    chart.setOption(options);
    chart.resize();  // 调整图表大小以适应容器
  }
};

// 处理窗口大小变化
const handleResize = () => {
  if (chart) {
    chart.resize();
  }
};

// 组件挂载时初始化词云图表，并监听窗口变化
onMounted(() => {
  chart = echarts.init(wordCloud.value);
  updateWordCloud();
  window.addEventListener('resize', handleResize);
});

// 组件卸载前移除事件监听
onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize);
});

// 监听词云数据变化，更新图表（旧词颜色固定，新词分配随机颜色）
watch(() => props.words, updateWordCloud, { deep: true });
</script>

<style scoped>
</style>
