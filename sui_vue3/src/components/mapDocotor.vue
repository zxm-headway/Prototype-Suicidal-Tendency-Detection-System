<template>
  <div style="display: flex; height: 100%;">
    <div style="flex: 0 0 70%; position: relative;">
      <el-button 
        id="resetButton" 
        @click="resetMap" 
        type="primary" 
        size="small" 
        style="position: absolute; top: 10px; left: 10px; z-index: 1000;">
        重定位
      </el-button>
      <div id="map" style="width: 100%; height: 100%;"></div>
    </div>
    <div style="flex: 0 0 30%; padding: 5px;">
      <!-- 自动补全搜索框 -->
      <el-autocomplete
        v-model="searchTerm"
        :fetch-suggestions="fetchSuggestions"
        placeholder="请输入标题搜索地点"
        @select="handleSelect"
        clearable
        style="margin-bottom: 10px;">
      </el-autocomplete>
      
      <!-- 展示过滤后的列表（分页处理） -->
      <el-card 
        v-for="(location, index) in paginatedLocations"
        :key="index"
        class="location-card"
        style="margin-bottom: 10px;"
      >
        <div>
          <!-- 点击标签展示详情并重定位 -->
          <el-check-tag @click="showDetail(location, true)" checked>
            {{ location.title }}
          </el-check-tag>
          <p class="card-text">
            <el-tag type="info">地址:</el-tag> {{ location.address }}
          </p>
          <p class="card-text">
            <el-tag type="success">电话:</el-tag> {{ location.phone }}
          </p>
        </div>
      </el-card>
      
      <!-- 分页组件 -->
      <el-pagination
        background
        layout="prev, pager, next"
        :total="filteredLocations.length"
        :current-page="currentPage"
        :page-size="pageSize"
        @current-change="handlePageChange"
      />
    </div>
  </div>

  <!-- 弹窗展示详细信息 -->
  <el-dialog v-model="detailDialogVisible" title="详细信息" width="30%">
    <div v-if="selectedLocation">
      <p><strong>标题：</strong>{{ selectedLocation.title }}</p>
      <p><strong>地址：</strong>{{ selectedLocation.address }}</p>
      <p><strong>电话：</strong>{{ selectedLocation.phone }}</p>
      <p><strong>经度：</strong>{{ selectedLocation.lng }}</p>
      <p><strong>纬度：</strong>{{ selectedLocation.lat }}</p>
    </div>
  </el-dialog>
</template>

<script setup>
import { onMounted, defineProps, ref, computed, watch } from 'vue';

const newImg = new URL("../assets/blue-dot.png", import.meta.url).href;
const props = defineProps({
  locations: {
    type: Array,
    required: true,
  }
});

// 搜索关键字
const searchTerm = ref("");

// 当前页码和每页显示数量
const currentPage = ref(1);
const pageSize = ref(4);

// 仅对标题进行过滤
const filteredLocations = computed(() => {
  const term = searchTerm.value.trim().toLowerCase();
  if (!term) {
    return props.locations;
  }
  return props.locations.filter(location => {
    return location.title.toLowerCase().includes(term);
  });
});

// 根据分页计算当前展示的地点数据
const paginatedLocations = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  const end = currentPage.value * pageSize.value;
  return filteredLocations.value.slice(start, end);
});

// 当搜索关键字变化时，重置分页到第一页
watch(searchTerm, () => {
  currentPage.value = 1;
});

// 自动补全 fetchSuggestions 只匹配标题
const fetchSuggestions = (queryString, callback) => {
  const term = queryString.trim().toLowerCase();
  let results = [];
  if (term) {
    results = props.locations.filter(location => {
      return location.title.toLowerCase().includes(term);
    });
  } else {
    results = props.locations;
  }
  // 转换为自动补全要求的格式，每项至少包含 value 字段
  const suggestions = results.map(location => ({
    value: location.title,
    ...location
  }));
  callback(suggestions);
};

// 当自动补全选择某个选项时，调用 showDetail 进行地图重定位
const handleSelect = (item) => {
  showDetail(item, true);
};

// 处理分页页码变化
const handlePageChange = (page) => {
  currentPage.value = page;
};

let mapInstance = null;

// 百度地图初始化
window.initMap = () => {
  if (!window.BMap) {
    console.error("BMap 未加载，请检查 API Key 和网络连接");
    return;
  }
  const centerPoint = new BMap.Point(106.5589, 29.5647);
  mapInstance = new BMap.Map("map");
  mapInstance.centerAndZoom(centerPoint, 12);
  mapInstance.enableScrollWheelZoom(true);
  mapInstance.setMinZoom(10);
  mapInstance.setMaxZoom(18);
  
  // 设置重庆范围限制
  const chongqingBounds = new BMap.Bounds(
    new BMap.Point(105.9180, 28.3375),
    new BMap.Point(108.6472, 31.2733)
  );
  mapInstance.addEventListener("moveend", () => {
    const currentBounds = mapInstance.getBounds();
    if (!chongqingBounds.containsBounds(currentBounds)) {
      mapInstance.panTo(centerPoint);
    }
  });
  
  const icon = new BMap.Icon(newImg, new BMap.Size(32, 32));
  // 为所有地点添加标注
  props.locations.forEach(location => {
    const marker = new BMap.Marker(new BMap.Point(location.lng, location.lat), { icon });
    mapInstance.addOverlay(marker);
    marker.setTitle(location.title);
    
    // 点击地图标注时展示详情，但不重定位也不放大
    marker.addEventListener("click", () => {
      setTimeout(() => {
        showDetail(location, false);
      }, 0);
    });
  });
};

const loadMapScript = () => {
  return new Promise((resolve) => {
    const script = document.createElement('script');
    script.src = "https://api.map.baidu.com/api?v=3.0&ak=MeLLOo56zBCp0shiwqbgFlNqFMDoKSsk&callback=initMap";
    script.async = true;
    script.onload = () => {
      resolve();
    };
    document.head.appendChild(script);
  });
};

// 弹窗展示详细信息状态
const detailDialogVisible = ref(false);
const selectedLocation = ref(null);

/**
 * 显示地点详情，并根据参数决定是否重定位地图
 * @param {Object} location - 地点信息对象
 * @param {Boolean} reposition - 是否重定位地图（默认为 true）
 */
function showDetail(location, reposition = true) {
  selectedLocation.value = location;
  detailDialogVisible.value = true;
  
  if (reposition && mapInstance) {
    const point = new BMap.Point(location.lng, location.lat);
    mapInstance.setCenter(point);
    // 放大一级地图
    mapInstance.setZoom(mapInstance.getZoom() + 4);
  }
}

onMounted(async () => {
  await loadMapScript();
});

// 重定位函数：恢复初始中心点和默认级别
function resetMap() {
  if (mapInstance) {
    const centerPoint = new BMap.Point(106.5589, 29.5647);
    mapInstance.setCenter(centerPoint);
    mapInstance.setZoom(15);
  }
}
</script>

<style scoped lang="less">
#resetButton {
  padding: 8px 12px;
}

.location-card {
  transition: box-shadow 0.3s, transform 0.3s;
  border-radius: 8px;
  overflow: hidden;
}

.location-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  transform: translateY(-5px);
}

.card-text {
  margin: 4px 0;
  color: #666;
  display: flex;
  align-items: center;
  border-bottom: 1px solid #e0e0e0;
  padding-bottom: 4px;
}

.card-text .el-tag {
  margin-right: 8px;
}
</style>
