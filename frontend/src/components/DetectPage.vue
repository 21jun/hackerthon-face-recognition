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
          <img :src="img" class="img-responsive">
        </figure>
      </div>

      <v-text-field
            v-model="location"
            :counter="20"
            label="위치를 입력하세요"
      ></v-text-field>
      <!-- <div class="col-md-6">
        <h2>Captured Image</h2>
        <figure class="figure">
          <img :src="result_img" class="img-responsive">
        </figure>
      </div> -->
      <div class="green darken-2 text-xl-center" v-if="unKnown">
        <span class="white--text">(?)누구인지 모르겠어요</span>
      </div>
      <div class="green darken-2 text-xl-center" v-for="person in people" :key="person">
        <span class="white--text">사용자 : {{person}}</span>
      </div>
      <div class="purple darken-2 text-xl-center" v-for="person in cum_people_log" :key="person">
        <span class="white--text">사용자 : {{person}}</span>
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
      location: '',
      unKnown:false,
      people:[],
      cum_people_log:[],
      result_img: null,
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
  // mounted: function () {
  //       this.$nextTick(function () {
  //           window.setInterval(() => {
  //               this.onCapture();
  //           },1000);
  //       })
  // },
  methods: {
    sendDetectFrame()
    {
      const baseURI = 'http://localhost:5000/api/detect/';
      var data = new FormData();
      data.append('photo', this.img)
      data.append('location', this.location)
      axios.post(baseURI, data
      ).then(response=>{
        console.log(response.data)
        this.people = []
        response.data['list'].forEach(element => {
          this.people.push(element)
          this.cum_people_log.push(element)
        });

        // this.result_img = response.data['img']
        // console.log(response.data['img'])

        // 조건부 렌더링
        //console.log(people.length)
        if (this.people.length == 0){
          this.unKnown = true;
        }
        else{
          console.log(this.people)
          this.unKnown = false;
        }
      }).catch((ex) => {
        console.log("ERROR", ex)
      })
    },
    onCapture() {
      this.people = []
      this.img = this.$refs.webcam.capture();
      this.sendDetectFrame()
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