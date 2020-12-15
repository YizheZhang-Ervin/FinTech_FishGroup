var app = new Vue({
    el: '#app',
    data(){
        return{
            x:[],
            y:[],
            y_real:[],
            homeShow:true,
            modelShow:false,
            teamShow:false,
            menuShow:true,
            paperShow:false,
            data2019Show:false,
            data2020Show:false,
            history:"",
            engine:"Engine: NSModel",
            rowNo:0,
            tau0:0,
            tau1:0,
            beta0:0,
            beta1:0,
            beta2:0,
            beta3:0,
            dataSet:2019,
            rsquare:0,
            width:{width:(parseInt(window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth)) + 'px'},
            height:{height:(parseInt(window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight)-128) + 'px'},
            halfheight:{height:(parseInt(window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight)/1.5) + 'px'}
        }
    },
    mounted(){
        this.getOne();
        setInterval(()=>{
            this.checkVisibility();
        },1000)
        
    },
    methods: {
        clear:function(){
            this.x=[];
            this.y=[];
            this.y_real=[];
            this.rowNo=0;
            this.tau0=0;
            this.tau1=0;
            this.beta0=0;
            this.beta1=0;
            this.beta2=0;
            this.beta3=0;
            this.dataSet=2019;
            this.rsquare=0;
            this.plot();
        },
        changeEngine:function(){
            if(this.engine=="Engine: NSModel"){
                this.engine = "Engine: NSSModel"
                document.getElementById("tau1").hidden = false;
                document.getElementById("tau1label").style.display = "inline-block";
                document.getElementById("beta3").hidden = false;
                document.getElementById("beta3label").style.display = "inline-block";
                document.getElementById("manualNSS").hidden = false;
                document.getElementById("autoNSS").hidden = false;
                document.getElementById("manualNS").hidden = true;
                document.getElementById("autoNS").hidden = true;
            }else{
                this.engine = "Engine: NSModel"
                document.getElementById("tau1").hidden = true;
                document.getElementById("tau1label").style.display = "none";
                document.getElementById("beta3").hidden = true;
                document.getElementById("beta3label").style.display = "none";
                document.getElementById("manualNSS").hidden = true;
                document.getElementById("autoNSS").hidden = true;
                document.getElementById("manualNS").hidden = false;
                document.getElementById("autoNS").hidden = false;
            }
        },
        getName:function(dataSet){
            if(dataSet==2020){
                return "Treasury_2020_1To11"
            }else if(dataSet==2019){
                return "Treasury_2019_Full"
            }
        },
        getOne:function(){
            axios.get(`http://127.0.0.1:5000/api/${this.getName(this.dataSet)}/${this.rowNo}`)
                .then((response) => {
                    if(response.data.error == "error"){
                        this.rowNo = "0-249(2019), 0-228(2020) ";
                        this.dataSet = "2019 or 2020";
                        document.getElementById("ds").style.background="rgba(255,0,0,0.5)";
                        document.getElementById("rowNo").style.background="rgba(255,0,0,0.5)";
                    }else{
                        document.getElementById("ds").style.background="transparent";
                        document.getElementById("rowNo").style.background="transparent";
                        this.x = response.data.x;
                        this.y = response.data.y;
                        this.y_real = response.data.y_real;
                        this.tau0 = response.data.t0;
                        this.tau1="none";
                        this.beta0 = response.data.b0;
                        this.beta1 = response.data.b1;
                        this.beta2 = response.data.b2;
                        this.beta3="none";
                        this.rsquare = response.data.rsquare;
                        this.plot();
                    }
                }, (err) => {
                    console.log(err.data);
                })
        },
        getAll:function(){
            axios.get(`http://127.0.0.1:5000/api/${this.getName(this.dataSet)}/-1`)
                .then((response) => {
                    if(response.data.error == "error"){
                        this.rowNo = "Should > 0 ";
                        this.dataSet = "2019 or 2020";
                    }else{
                        this.rsquare = response.data.rsquare;
                        this.x = response.data.x;
                        this.y = response.data.y;
                        this.y_real = response.data.y_real;
                        this.tau0 = response.data.paras[0];
                        this.tau1="none";
                        this.beta0 = response.data.paras[1];
                        this.beta1 = response.data.paras[2];
                        this.beta2 = response.data.paras[3];
                        this.beta3="none";
                        this.plot();
                    }
                }, (err) => {
                    console.log(err.data);
                })
        },
        postOne:function(){
            axios.post(`http://127.0.0.1:5000/api/fit/one`, {
                 "parameters": JSON.stringify(Array(this.tau0,this.beta0,this.beta1,this.beta2)),
                 "row": this.rowNo,
                 "dataSet": JSON.stringify(this.getName(this.dataSet)) 
                })
                .then((response)=> {
                    if(response.data.error == "error"){
                        this.rowNo = "Should > 0 ";
                        this.dataSet = "2019 or 2020";
                        this.tau0 = "type in number";
                        this.tau1 = "type in number";
                        this.beta0 = "type in number";
                        this.beta1 = "type in number";
                        this.beta2 = "type in number";
                        this.beta3 = "type innumber";
                    }else{
                        this.rsquare = response.data.rsquare;
                        this.x = response.data.x;
                        this.y = response.data.y;
                        this.y_real = response.data.y_real;
                        this.tau0 = response.data.paras[0];
                        this.tau1 = "none";
                        this.beta0 = response.data.paras[1];
                        this.beta1 = response.data.paras[2];
                        this.beta2 = response.data.paras[3];
                        this.beta3 = "none";
                        this.plot();
                    }
                }, function (err) {
                    console.log(err.data);
                })
        },
        getNSSOne:function(){
            axios.get(`http://127.0.0.1:5000/api2/${this.getName(this.dataSet)}/${this.rowNo}`)
                .then((response) => {
                    if(response.data.error == "error"){
                        this.rowNo = "0-249(2019), 0-228(2020) ";
                        this.dataSet = "2019 or 2020";
                        document.getElementById("ds").style.background="rgba(255,0,0,0.5)";
                        document.getElementById("rowNo").style.background="rgba(255,0,0,0.5)";
                    }else{
                        document.getElementById("ds").style.background="transparent";
                        document.getElementById("rowNo").style.background="transparent";
                        this.x = response.data.x;
                        this.y = response.data.y;
                        this.y_real = response.data.y_real;
                        this.tau0 = response.data.t0;
                        this.tau1 = response.data.t1;
                        this.beta0 = response.data.b0;
                        this.beta1 = response.data.b1;
                        this.beta2 = response.data.b2;
                        this.beta3 = response.data.b3;
                        this.rsquare = response.data.rsquare;
                        this.plot();
                    }
                }, (err) => {
                    console.log(err.data);
                })
        },
        postNSSOne:function(){
            axios.post(`http://127.0.0.1:5000/api2/fit/one`, {
                 "parameters": JSON.stringify(Array(this.tau0,this.tau1,this.beta0,this.beta1,this.beta2,this.beta3)),
                 "row": this.rowNo,
                 "dataSet": JSON.stringify(this.getName(this.dataSet)) 
                })
                .then((response)=> {
                    if(response.data.error == "error"){
                        this.rowNo = "Should > 0 ";
                        this.dataSet = "2019 or 2020";
                        this.tau0 = "type in number";
                        this.tau1 = "type in number";
                        this.beta0 = "type in number";
                        this.beta1 = "type in number";
                        this.beta2 = "type in number";
                        this.beta3 = "type innumber";
                    }else{
                        this.rsquare = response.data.rsquare;
                        this.x = response.data.x;
                        this.y = response.data.y;
                        this.y_real = response.data.y_real;
                        this.tau0 = response.data.paras[0];
                        this.tau1 = response.data.paras[1];
                        this.beta0 = response.data.paras[2];
                        this.beta1 = response.data.paras[3];
                        this.beta2 = response.data.paras[4];
                        this.beta3 = response.data.paras[5];
                        this.plot();
                    }
                }, function (err) {
                    console.log(err.data);
                })
        },
        plot:function(){
            var myChart = echarts.init(document.getElementById('charts'));
            option = {
                xAxis: {
                    name:'time\n(year)',
                    type: 'category',
                    data: this.x
                },
                yAxis: {
                    name: 'yields(%)',
                    type: 'value'
                },
                series: [{
                    data: this.y,
                    type: 'line',
                    smooth: true
                },{
                    data: this.y_real,
                    type: 'line',
                    smooth: true
                }],
                dataZoom:[{
                    type:"inside"
                }],
                tooltip:{
                    trigger:'axis'
                },
            };
            myChart.setOption(option);
        },
        changeRightShow:function(flag){
            if(flag==1){
                this.homeShow = true;
                this.modelShow = false;
                this.teamShow = false;
                this.paperShow = false;
                this.data2019Show = false;
                this.data2020Show = false;
            }else if(flag==2){
                this.homeShow = false;
                this.modelShow = true;
                this.teamShow = false;
                this.paperShow = false;
                this.data2019Show = false;
                this.data2020Show = false;
            }else if(flag==3){
                this.homeShow = false;
                this.modelShow = false;
                this.teamShow = true;
                this.paperShow = false;
                this.data2019Show = false;
                this.data2020Show = false;
            }else if(flag==4){
                this.homeShow = false;
                this.modelShow = false;
                this.teamShow = false;
                this.paperShow = true;
                this.data2019Show = false;
                this.data2020Show = false;
            }else if(flag==5){
                this.homeShow = false;
                this.modelShow = false;
                this.teamShow = false;
                this.paperShow = false;
                this.data2019Show = true;
                this.data2020Show = false;
            }else if(flag==6){
                this.homeShow = false;
                this.modelShow = false;
                this.teamShow = false;
                this.paperShow = false;
                this.data2019Show = false;
                this.data2020Show = true;
            }
            
        },
        changeMenuShow:function(){
            this.menuShow = !this.menuShow;
        },
        checkVisibility:function(){
            let vs = document.visibilityState;
            let date = new Date(Date.now());
            if(vs=="visible"){
                document.title = "FISH Group - "+ date.getHours() + ":" + date.getMinutes() + ":" + date.getSeconds();
            }
        }
    }
});