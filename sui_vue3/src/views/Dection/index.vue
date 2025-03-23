<template>
  <el-row :gutter="20">
    <el-col :span="12" style="margin-top: 5px">
      <el-form>
        <!-- 输入方式切换 -->
        <el-form-item label="选择输入方式:" label-width="100px">
          <el-radio-group v-model="inputMode">
            <el-radio label="custom">自定义文本</el-radio>
            <el-radio label="file">文件上传</el-radio>
          </el-radio-group>
        </el-form-item>
        <!-- 固定尺寸的输入区域 -->
        <el-form-item :label="inputMode === 'custom' ? '请输入文本:' : '上传文件:'" label-width="100px">
          <div class="fixed-input-container">
            <el-input
              v-if="inputMode === 'custom'"
              type="textarea"
              v-model="inputText"
              placeholder="请输入检测内容"
              :rows="8"
              resize="none"
              style="width: 100%;"
            />
            <el-upload
              v-else
              :action="''"
              :auto-upload="false"
              :file-list="fileList"
              accept=".txt"
              :on-change="handleFileChange"
              class="upload-box"
            >
              <el-button slot="trigger" type="primary">选取文件</el-button>
              <div slot="tip" class="el-upload__tip">仅支持文本文件上传</div>
            </el-upload>
          </div>
        </el-form-item>
      </el-form>

      <div class="button-group">
        <el-button type="primary" @click="handleSubmit">提交预测</el-button>
        <el-button type="info" @click="handleReset">重置</el-button>
        <el-button type="warning" @click="handleCon">添加帖子</el-button>
        <el-button type="success" @click="handleStore">存储信息</el-button>
      </div>
      <el-divider />
      <div class="result-display">
        <div>预测结果:</div>
        <div class="tags">
          <el-tag
            v-for="(tag, index) in tags"
            :key="index"
            type="success"
            effect="plain"
            size="large"
          >
            {{ tag }}
          </el-tag>
        </div>
      </div>
      <div class="list-heading">输入帖子文本集</div>
      <!-- 帖子列表：固定宽度和高度，保持和上面输入区域一致 -->
      <ul ref="postsContainer" class="submitted-texts">
        <li 
          v-for="(text, index) in submittedTexts" 
          :key="index" 
          class="text-item"
          @click="showFullText(text)"
        >
          {{ text }}
        </li>
      </ul>
    </el-col>
    <el-col :span="12">
      <div class="card-container">
        <el-card shadow="never" class="card_set">
          <span>帖子集词云：</span>
          <world-clude :words="wordData" />
        </el-card>
        <el-card shadow="never" class="card_set">
          <span>帖子正负情感分布：</span>
          <pie-chart :chartData="pieData" />
        </el-card>
      </div>
    </el-col>
  </el-row>

  <!-- 检测结果对话框 -->
  <el-dialog v-model="dialogVisible" title="检测结果" width="500" center>
    <span>{{ dialogMessage }}</span>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="dialogVisible = false">确定</el-button>
      </div>
    </template>
  </el-dialog>

  <!-- 存储信息对话框 -->
  <el-dialog v-model="userDialogVisible" title="存储信息" width="400" center>
    <el-form :model="storeForm">
      <el-form-item label="用户名:" label-width="80px">
        <el-input v-model="storeForm.userName" placeholder="请输入用户名" />
      </el-form-item>
      <el-form-item label="输入方式:" label-width="80px">
        <el-select v-model="storeForm.inputType" placeholder="请选择输入方式">
          <el-option label="自定义输入" value="custom" />
          <el-option label="文件输入" value="file" />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="cancelStore">取消</el-button>
        <el-button type="primary" @click="confirmStore">确定</el-button>
      </div>
    </template>
  </el-dialog>

  <!-- 全文显示对话框 -->
  <el-dialog v-model="fullTextDialogVisible" title="完整帖子文本" width="500" center>
    <span>{{ fullTextDialogContent }}</span>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="fullTextDialogVisible = false">关闭</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from "vue";
import { get_woulds, SaveUser } from "../../API/textDection";
import { ElMessage } from "element-plus";
import WorldClude from "../../components/worldClude.vue";
import PieChart from "../../components/cirpai.vue";

const inputText = ref("");
const tags = ref([]);
const submittedTexts = ref([]);
const wordData = ref([]);
const pieData = ref([]);
const is_sui = ref(false);
const dialogVisible = ref(false);        // 检测结果对话框显示
const userDialogVisible = ref(false);      // 存储信息对话框显示
const fullTextDialogVisible = ref(false);    // 全文显示对话框显示
const fullTextDialogContent = ref("");       // 存储点击后显示的完整文本

// 输入方式及文件上传处理
const inputMode = ref("custom");
const fileList = ref([]);
const handleFileChange = (file, fileListNew) => {
  const reader = new FileReader();
  reader.onload = (e) => {
    const content = e.target.result;
    // 按行拆分文件内容，并过滤掉空行
    const lines = content.split('\n').filter(line => line.trim() !== '').reverse();;
    // 将拆分后的每一行添加到帖子列表中（在顶部添加）
    submittedTexts.value = lines.concat(submittedTexts.value);
  };
  reader.readAsText(file.raw);
};

// 存储信息表单数据
const storeForm = ref({
  userName: "",
  inputType: ""
});

// 获取帖子列表的容器引用，用于滚动
const postsContainer = ref(null);

// 添加帖子文本（针对自定义文本输入）
const handleCon = () => {
  if (inputText.value) {
    submittedTexts.value.unshift(inputText.value);
    inputText.value = "";
    // 滚动到最新帖子（即顶部）
    nextTick(() => {
      postsContainer.value.scrollTo({ top: 0, behavior: "smooth" });
    });
  }
};

// 调用预测接口
const handleSubmit = async () => {
  const res = await get_woulds(submittedTexts.value);
  wordData.value = res.words.map((item) => ({ name: item, value: 1 }));
  pieData.value = Object.entries(res.emotion_num).map(([key, value]) => ({
    name: key,
    value,
  }));
  is_sui.value = res.res;
  dialogVisible.value = true;
};

// 检测结果文本及标签更新
const dialogMessage = computed(() => {
  const resu = is_sui.value == true ? "具有自杀倾向" : "没有自杀倾向";
  tags.value = [resu];
  return resu;
});

// 重置数据
const handleReset = () => {
  inputText.value = "";
  tags.value = [];
  submittedTexts.value = [];
  wordData.value = [];
  pieData.value = [];
  is_sui.value = false;
  dialogVisible.value = false;
};

// 点击帖子显示全文
const showFullText = (text) => {
  fullTextDialogContent.value = text;
  fullTextDialogVisible.value = true;
};

// 弹出存储信息对话框
const handleStore = () => {
  userDialogVisible.value = true;
};

// 存储信息操作
const confirmStore = async () => {
  if (submittedTexts.value.length === 0) {
    ElMessage({
      message: "请先添加至少一条帖子文本",
      type: "warning",
      duration: 3000,
    });
    return;
  }
  if (!storeForm.value.userName.trim()) {
    ElMessage({
      message: "用户名不能为空",
      type: "warning",
      duration: 3000,
    });
    return;
  }
  if (!storeForm.value.inputType) {
    ElMessage({
      message: "请选择输入方式",
      type: "warning",
      duration: 3000,
    });
    return;
  }

  const dataToStore = {
    texts: submittedTexts.value,
    is_sui: is_sui.value,
    user_name: storeForm.value.userName,
    inputType: storeForm.value.inputType,
  };


  try {
    const result = await SaveUser(dataToStore);
    console.log("信息存储成功", result);
    ElMessage({
      message: "信息存储成功",
      type: "success",
      duration: 3000,
    });
  } catch (error) {
    console.error("存储信息失败", error);
    let errorMsg = "存储信息失败";
    if (error.response && error.response.data && error.response.data.detail) {
      errorMsg += "：" + error.response.data.detail;
    }
    ElMessage({
      message: errorMsg,
      type: "error",
      duration: 5000,
    });
  } finally {
    userDialogVisible.value = false;
    storeForm.value = {
      userName: "",
      inputType: "",
    };
  }
};

// 取消存储操作
const cancelStore = () => {
  userDialogVisible.value = false;
  storeForm.value = {
    userName: "",
    inputType: "",
  };
};

// 持久化状态
onMounted(() => {
  const persistedState = localStorage.getItem("componentState");
  if (persistedState) {
    const state = JSON.parse(persistedState);
    submittedTexts.value = state.submittedTexts || [];
    inputText.value = state.inputText || "";
    is_sui.value = state.is_sui || false;
    wordData.value = state.wordData || [];
    pieData.value = state.pieData || [];
  }
});

watch(
  [submittedTexts, inputText, is_sui, wordData, pieData],
  ([newSubmittedTexts, newInputText, newIsSui, newWordData, newPieData]) => {
    const state = {
      submittedTexts: newSubmittedTexts,
      inputText: newInputText,
      is_sui: newIsSui,
      wordData: newWordData,
      pieData: newPieData,
    };
    localStorage.setItem("componentState", JSON.stringify(state));
  },
  { deep: true }
);
</script>

<style scoped lang="less">
.fixed-input-container {
  width: 100%;        /* 保证宽度占满 */
  height: 180px;      /* 固定高度，可根据需求调整 */
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  padding: 10px;
  box-sizing: border-box;
}
.upload-box {
  width: 100%;
}

/* 保持和输入区域宽度一致 */
.submitted-texts {
  width: 100%;
  margin: 10px;
  padding: 0;
  list-style: none;
  max-height: 290px; /* 固定高度 */
  overflow-y: auto;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
}

.el-header {
  background-color: #f5f5f5;
  padding: 10px;
  text-align: left;
}

.el-main {
  padding: 20px;
}

.button-group {
  display: flex;
  justify-content: center;
  align-content: space-between;
  gap: 20px;

  .el-button {
    flex: 1;
    max-width: 100px;
  }
}

.list-heading {
  text-align: center;
  font-weight: bold;
  font-size: 16px;
  margin-bottom: 5px;
}

.result-display {
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  flex-direction: row;
  gap: 10px;

  .tags {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-top: 0;
    cursor: pointer;
  }
}

.card-container {
  display: flex;
  flex-direction: column;
  gap: 10px;

  .card_set {
    height: 42vh;

    span {
      font-weight: bold;
    }
  }
}

.text-item {
  padding: 10px;
  border-bottom: 1px solid #ccc;
  transition: background-color 0.2s ease;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  cursor: pointer;

  &:hover {
    background-color: #f0faff;
  }
}
</style>
