
import { defineStore } from 'pinia'

const useHeaderList = defineStore('headerList', {
  state: () => ({
    header_list:[],
    is_close:false

  }),
  actions: {
    addHeaderList(item) {
      if ( this.header_list.findIndex((element) => element.path == item.meta.path) === -1) {
        this.header_list.push(item.meta)
      }
    },
    removeHeaderList(path) {
      let Index  = this.header_list.findIndex((element) => element.path ==path)
      this.header_list.splice(Index,1)
      return Index
      
    },
    closeHeader(){
      this.is_close = !this.is_close
    }
  },
  getters: {
    getHeaderListLen: (state) => state.header_list.length,
    getIsClose: (state) => state.is_close
  }

})



export {
  useHeaderList
}