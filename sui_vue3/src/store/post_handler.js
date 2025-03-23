import { defineStore } from 'pinia'
import { get_woulds } from '../API/textDection'

const usePostHandler = defineStore('postHandler', {

  state: () => ({
    post_list:[],
  }),

  actions: {

  },
}
)

