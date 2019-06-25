<template>
  <div class="container">
    <div class="row">
      <div class="col-md-6">
        <h2>Current Camera</h2>
        <code v-if="device">{{ device.label }}</code>
        <div class="border">
          <vue-web-cam ref="webcam"
                       :device-id="deviceId"
                       width="100%"
                       @started="onStarted" 
                       @stopped="onStopped" 
                       @error="onError"
                       @cameras="onCameras"
                       @camera-change="onCameraChange" />
        </div>

        <div class="row">
          <div class="col-md-12">
            <select v-model="camera">
              <option>-- Select Device --</option>
              <option v-for="device in devices" 
                      :key="device.deviceId" 
                      :value="device.deviceId">{{ device.label }}</option>
            </select>
          </div>
          <div class="col-md-12">
            <v-btn color="success"
                    @click="onCapture">Capture Photo</v-btn>
            <button type="button" 
                    class="btn btn-danger" 
                    @click="onStop">Stop Camera</button>
            <button type="button" 
                    class="btn btn-success" 
                    @click="onStart">Start Camera</button>
          </div>
        </div>
      </div>
      <div class="col-md-6">
        <h2>Captured Image</h2>
        <figure class="figure">
          <img :src="img" class="img-responsive" >
        </figure>
      </div>
      <div>
        <v-text-field
            v-model="user_id"
            :counter="10"
            label="학번을 입력하세요"
        ></v-text-field>
        <v-text-field
            v-model="user_name"
            :counter="10"
            label="이름을 입력하세요"
        ></v-text-field>
        <v-text-field
            v-model="user_birth"
            :counter="10"
            label="생년월일을 입력하세요"
        ></v-text-field>
        <v-text-field
            v-model="user_phone"
            :counter="10"
            label="전화번호을 입력하세요"
        ></v-text-field>
        <v-text-field
            v-model="user_email"
            :counter="10"
            label="이메일을 입력하세요"
        ></v-text-field>

        <v-checkbox v-model="checkbox" :label="'개인정보 처리 약관에 동의합니다.'"></v-checkbox>
        <v-btn color="blue" @click="sendImgToServer">회원 가입</v-btn>

      </div>
    </div>
  </div>
</template>

<script>
import { WebCam } from "vue-web-cam";
import axios from 'axios'

export default {
  name: "App",
  components: {
    "vue-web-cam": WebCam
  },
  data() {
    return {
      checkbox : false,
      user_name : '',
      user_id: 0,
      user_birth : '',
      user_phone : '',
      user_email : '',
      img: null,
      camera: null,
      deviceId: null,
      devices: []
    };
  },
  computed: {
    device: function() {
      return this.devices.find(n => n.deviceId === this.deviceId);
    }
  },
  watch: {
    camera: function(id) {
      this.deviceId = id;
    },
    devices: function() {
      // Once we have a list select the first one
      const [first, ...tail] = this.devices;
      if (first) {
        this.camera = first.deviceId;
        this.deviceId = first.deviceId;
      }
    }
  },
  methods: {
    sendImgToServer()
    {
      if(this.checkbox){

        if(this.img == null){
          this.onCapture()
        }

        const baseURI = 'http://localhost:5000/api/regist/';
        var data = new FormData();
        data.append('name', this.user_name)
        data.append('user_id', this.user_id)
        data.append('photo', this.img)
        data.append('phone', this.user_phone)
        data.append('birth', this.user_birth)
        data.append('email', this.user_email)
        axios.post(baseURI, data
        ).then(response=>{
          console.log(response.data)
        }).catch((ex) => {
          console.log("ERROR", ex)
        })
      }
      else{
        return
      }
    },
    onCapture() {
      this.img = this.$refs.webcam.capture();
      //this.sendImgToServer()
    },
    onStarted(stream) {
      console.log("On Started Event", stream);
    },
    onStopped(stream) {
      console.log("On Stopped Event", stream);
    },
    onStop() {
      this.$refs.webcam.stop();
    },
    onStart() {
      this.$refs.webcam.start();
    },
    onError(error) {
      console.log("On Error Event", error);
    },
    onCameras(cameras) {
      this.devices = cameras;
      console.log("On Cameras Event", cameras);
    },
    onCameraChange(deviceId) {
      this.deviceId = deviceId;
      this.camera = deviceId;
      console.log("On Camera Change Event", deviceId);
    }
  }
};
</script>