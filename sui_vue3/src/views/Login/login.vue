<template>
  <el-row class="login-container" justify="center" :align="'middle'">
    
    <el-card > 
      <template #header>
        <div class="card-header">
          <img :src="newImg" alt="" />
        </div>
      </template>
      <div class="jump-link">
        <el-link type="primary" @click="jumpToRegister">{{
          !is_reggister ? "注册" : "返回登录"
        }}</el-link>
      </div>

      <el-form label-width="80px" style="text-align: center">
        <el-form-item
          label="用户名:"
          style="display: flex; justify-content: center"
        >
          <el-input
            v-model="form.username"
            placeholder="请输入用户名"
          ></el-input>
        </el-form-item>
        <el-form-item
          label="密码:"
          style="display: flex; justify-content: center"
        >
          <el-input type="password"  v-model="form.password" placeholder="请输入密码"></el-input>
        </el-form-item>
        <el-form-item style="text-align: center">
          <el-input
            v-model="form.validateCode"
            placeholder="请输入验证码"
          >
            <template #append><span @click="startCountdown">{{countdown==0?'验证码':`${countdown}秒后重试` }}</span></template>
          </el-input>
        </el-form-item>
        
      </el-form>
    <div style="display: flex; justify-content: center; ">
        <el-button style="width: 60%;" type="primary" @click="login" class="el-button">
      登录
    </el-button>
  </div>
    </el-card>
  </el-row>
</template>

<script setup>
import { ref, reactive } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();

const form = reactive({
  username: "",
  password: "",
  validateCode: "",
});

const is_reggister = ref(false);

const jumpToRegister = () => {
  is_reggister.value = !is_reggister.value;
};

const newImg = new URL("../../assets/login-head.png", import.meta.url).href;


const login = () => {
  router.push("/");
};


const countdown = ref(0);
    let timer = null;

const startCountdown = () => {
  if (countdown.value === 0) {
    countdown.value = 60;
    timer = setInterval(() => {
      countdown.value--;
      if (countdown.value === 0) {
        clearInterval(timer);
      }
    }, 1000);
  }
};
</script>

<style lang="less" scoped>
:deep(.el-card__header) {
  padding: 0;
}
.login-container {
  height: 100%;
  .card-header {
    background-color: #899fe1;
    img {
      width: 430px;
    }
  }
  .jump-link {
    text-align: right;
    margin-bottom: 10px;
  }
}



</style>