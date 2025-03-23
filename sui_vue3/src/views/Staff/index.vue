<template>
  <div class="mapshow">
    <mapDocotor :locations="locationsData" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import mapDocotor from '../../components/mapDocotor.vue';
import { get_map } from '../../API/textDection';

// 创建响应式变量
const locationsData = ref([]);

// 使用 onMounted 生命周期钩子调用 get_map
onMounted(async () => {
  try {
    locationsData.value = await get_map(); // 将获取的值赋给 locationsData
  } catch (error) {
    console.error('Failed to fetch map data:', error);
  }
});
</script>

<style lang="less" scoped>
.mapshow {
  width: 100%;
  height: 100%;
}
</style>
