
import service from '../utils/request';
const  get_woulds = async (listData) => {
  return await service.post('/process-list', listData)
    .then(response => {
      return response.data
    })
    .catch(error => {
      console.error('Error:', error)
      throw error
    })
}



const get_map = async () => {
  return await service.get('/map')
    .then(response => {
      return response.data
    })
    .catch(error => {
      console.error('Error:', error)
      throw error
    })
}

const get_user = async (page = 1, size = 10, dataSource = 'dataset') => {
  return await service.get('/data', {
    params: { page, size, dataSource }
  })
    .then(response => response.data)
    .catch(error => {
      console.error('Error:', error)
      throw error
    })
}

const getUserPosts = async (userId,data_type) => {
  try {
      const response = await service.get('/user/posts/detail',{params: {userId,data_type}});
      return response.data;
  } catch (error) {
      if (error.response) {
          console.error('Error Response:', error.response.data);
      } else if (error.request) {
          console.error('Error Request:', error.request);
      } else {
          console.error('Error:', error.message);
      }
  }
}


const getUserEmotion = async (userId,data_type) => {
  try {
    const response = await service.get('/user/emotions/detail',{params: {userId,data_type}});
    return response.data;
  } catch (error) {
      if (error.response) {
          console.error('Error Response:', error.response.data);
      } else if (error.request) {
          console.error('Error Request:', error.request);
      } else {
          console.error('Error:', error.message);
      }
  }
}


const SaveUser = async (userID) => {
    try {
      const response = await service.post('/store_detection', userID);
      return response.data;
    } catch (error) {
      console.error("Error storing detection data:", error);
      throw error;
    }
}


const checkEmotionWave = async (sentence_list) => {
  try {
    const response = await service.post('/user/emotionsWave',{sentence_list});
    return response.data;
  } catch (error) {
      if (error.response) {
          console.error('Error Response:', error.response.data);
      } else if (error.request) {
          console.error('Error Request:', error.request);
      } else {
          console.error('Error:', error.message);
      }
  }
}


export {
  get_woulds,
  get_map,
  get_user,
  getUserPosts,
  getUserEmotion,
  SaveUser,
  checkEmotionWave
}
