<template>
  <div>
    <el-table 
      :data="tableData" 
      style="width: 100%; border: 1px solid #ebeef5;" 
      @filter-change="handleFilterChange"
      class="custom-table"
    >
      <!-- 增大 ID 列宽度 -->
      <el-table-column 
        prop="id" 
        label="ID" 
        width="150" 
        class-name="custom-id-column" 
      />
      <el-table-column prop="username" label="用户名" />
      <!-- 修改数据来源列，添加过滤器（只允许单选） -->
      <el-table-column 
        column-key="dataSource"
        prop="dataSource" 
        label="数据来源" 
        :filters="dataSourceFilters" 
        filter-placement="bottom-end"
        :filter-multiple="false"
      />
      <el-table-column label="数据样例" width="500">
        <template v-slot="scope">
          <el-tag type="info">{{ scope.row.sampleData }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="150">
        <template v-slot="scope">
          <el-tag v-if="scope.row.status === 1 || scope.row.status == true" type="danger">
            具有自杀意念
          </el-tag>
          <el-tag v-else type="success">
            正常
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="250">
        <template v-slot="scope">
          <el-button @click="editItem(scope.row)" type="primary">帖子详情</el-button>
          <el-button @click="deleteItem(scope.row.id)" type="danger">情感分布</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      :current-page="currentPage"
      :page-size="pageSize"
      :total="totalItems"
      layout="total, prev, pager, next, jumper"
      @current-change="handleCurrentChange"
      style="margin-top: 20px;"
    />

    <UserPostsDrawer v-model="drawerVisible" :posts="userPosts" :labels="label_detail" />
    <postsEomtion v-model="drawerEmotion" :chartData="chartData" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { get_user, getUserPosts, getUserEmotion } from '../../API/textDection';
import UserPostsDrawer from '../../components/drawer.vue';
import postsEomtion from '../../components/postsEomtion.vue';

// 分页及数据列表
const totalItems = ref(0);
const currentPage = ref(1);
const pageSize = ref(10);
const tableData = ref([]);

// 当前选择的数据来源（默认值为 'dataset'）
const selectedDataSource = ref('dataset');
// 数据来源过滤器配置：只包含“数据集”和“已检测”两个选项
const dataSourceFilters = [
  { text: '数据集', value: 'dataset' },
  { text: '已检测', value: 'detected' }
];

const drawerVisible = ref(false);
const drawerEmotion = ref(false);
const userPosts = ref([]);
const label_detail = ref(0);
const chartData = ref([]);

// 根据页码、页面大小以及数据来源加载数据
const fetchData = async (page, size, dataSource) => {
  const res = await get_user(page, size, dataSource);
  tableData.value = res.items;
  totalItems.value = res.total;

};

const handleCurrentChange = (newPage) => {
  currentPage.value = newPage;
  fetchData(newPage, pageSize.value, selectedDataSource.value);
};

// 当过滤条件改变时，只取单选的选项，如果未选择则自动设置为默认的“数据集”
const handleFilterChange = (filters) => {
  if (filters.dataSource && filters.dataSource.length > 0) {
    selectedDataSource.value = filters.dataSource[0];
  } else {
    selectedDataSource.value = 'dataset';
  }
  currentPage.value = 1;
  fetchData(1, pageSize.value, selectedDataSource.value);
};

onMounted(() => {
  fetchData(currentPage.value, pageSize.value, selectedDataSource.value);
});

// 查看帖子详情
const editItem = async (item) => {
  // console.log(item);
  const res = await getUserPosts(item.id, selectedDataSource.value);
  // console.log(res,22222222222222222);

  userPosts.value = res.posts;
  drawerVisible.value = true;
  label_detail.value = res.labels;
};

// 查看情感分布
const deleteItem = async (id) => {
  drawerEmotion.value = true;
  const res = await getUserEmotion(id, selectedDataSource.value);
  chartData.value = Object.entries(res.emotion_num).map(([key, value]) => ({
    name: key,
    value,
  }));
};
</script>

<style scoped>
.custom-table {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  border-radius: 4px;
  overflow: hidden;
}

/* 美化表头 */
.el-table th {
  background-color: #f5f7fa;
  color: #606266;
  font-weight: 600;
  padding: 12px 8px;
}

/* 增大 ID 列字体和对齐 */
.custom-id-column .cell {
  text-align: center;
  font-size: 16px;
  font-weight: bold;
}

/* 表格单元格增加内边距 */
.el-table .cell {
  padding: 10px 8px;
}

/* 按钮间距 */
.el-button {
  margin-right: 5px;
}
</style>
