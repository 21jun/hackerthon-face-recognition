<template>
    <div>
        <v-text-field
            v-model="user_id"
            :counter="10"
            label="사용자 id를 입력하세요"
        ></v-text-field>
        <v-btn color="info" @click="get_userLogs(user_id)">사용시간</v-btn>        

         <GChart
            type="ColumnChart"
            :data="cData"
            :options="chartOptions"
        />
    

    </div>
    
</template>


<script>
import axios from 'axios'
import get_user_logs from '../modules/GetUserLogs'
export default {
  name: 'App',
  components: {

  },
  data () {
    return {
        time_spend:[],
        user_id: 0,
        arr: new Array(),
        brr: new Array(),
        MainEntrance: 0,
        VRARROOM: 0,
        VisualStudio: 0,
        user_logs:[],
        cData:[],
        chartData: [
            ['Year', 'Sales', 'Expenses', 'Profit'],
            ['2014', 1000, 400, 200],
            ['2015', 1170, 460, 250],
            ['2016', 660, 1120, 300],
            ['2017', 1030, 540, 350]
        ],
        chartOptions: {
            chart: {
                title: 'Company Performance',
                subtitle: 'Sales, Expenses, and Profit: 2014-2017',
            }
        }
    }
  },
  created() {
      
  },

  methods: {
      get_userLogs(user_id){
        const baseURI = 'http://localhost:5000/api/log/';

        axios.get(baseURI+user_id).then((response)=>{
            this.user_logs = get_user_logs(response.data['list'])
            this.time_spend = get_user_logs(response.data['list'])
            this.place = get_user_logs(response.data['list'])
        })

        var k =0;
        for (let i = 0; i < this.user_logs.length - 1; i++) {
        
            
            if (this.user_logs[i][0] == this.user_logs[i+1][0]) {
                var prev = new Date(this.user_logs[i][1])
                var next = new Date(this.user_logs[i+1][1])
                var res = Math.abs(next-prev)/1000
                //console.log(res)
                this.time_spend[k] = res;
                this.place[k] = this.user_logs[i][0]
                k++;
                i++;
            }
            else {
                var prev = new Date(this.user_logs[i][1])
                var next = new Date(this.user_logs[i+1][1])
                var res = Math.abs(next-prev)/1000
                //console.log(res)
                this.time_spend[k] = res;
                this.place[k] = this.user_logs[i][0]
                k++;
            }
        }
        
        for (let i = 0; i < k; i++) {
            this.arr[i] = this.time_spend[i]
            this.brr[i] = this.place[i];
        }

        //console.log(this.arr)
        //console.log(this.brr)

        this.MainEntrance = 0;
        this.VRARROOM = 0;
        this.VisualStudio =0 ;

        for (let i = 0; i < k; i++) {
            if (this.brr[i] == "Main Entrance"){
    
                this.MainEntrance += this.arr[i];
            }
            else if(this.brr[i] == "AR/VR ROOM")
            {
                this.VRARROOM += this.arr[i];
            }
            else if(this.brr[i] == "Visual Studio")
            {
                this.VisualStudio += this.arr[i];
            }
        }

        console.log(this.MainEntrance)
        console.log(this.VRARROOM)
        console.log(this.VisualStudio)

        this.cData= [
            ["Fercil", "sec"],
            ["Main Enterance" ,this.MainEntrance], 
            ["VR/AR ROOM" ,this.VRARROOM], 
            ["Visual Studio", this.VisualStudio]
        ]

        console.log(this.cData)

      } 
  }
}
</script>