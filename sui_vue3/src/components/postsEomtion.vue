<template>
  <el-drawer
    v-model="drawerOC"
    size="30%"
    @close="closeDrawer"
    direction="rtl"
    title="用户帖子情感倾向比例"
  >
    <div class="chart-container">
      <cirpai :chartData="props.chartData" />
    </div>
  </el-drawer>
</template>

<script setup>
import { defineProps, defineEmits, watch, ref } from 'vue';
import cirpai from './cirpai.vue';

const emit = defineEmits();
const drawerOC = ref(false);

const props = defineProps({
  chartData: {
    type: Array,
    required: true,
  },
  modelValue: {
    type: Boolean,
    required: true,
  },
});

// 监听 modelValue 的变化
watch(() => props.modelValue, (newValue) => {
  drawerOC.value = newValue;
});

// 关闭抽屉
const closeDrawer = () => {
  emit('update:modelValue', false);
};
</script>

<style lang="less" scoped>

.chart-container {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 400px; /* 或设置一个具体高度 */
  .pie-chart {
    width: 100%;
    height: 100%;
  }
}
</style>
