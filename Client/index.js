var app = new Vue({
    el: '#app',
    data(){
        return{
            x:[],
            y:[],
            y_real:[],
            rightShow:"true",
            history:"",
            rowNo:0,
            lambda:0,
            beta0:0,
            beta1:0,
            beta2:0
        }
    },
    mounted(){
        this.getTestData();
    },
    methods: {
        getTestData:function(){
            axios.get("http://127.0.0.1:5000/api/test")
                .then((response) => {
                    this.x = response.data.tIndex;
                    this.y = response.data.spots;
                    this.y_real = response.data.yields;
                    this.plot();
                }, (err) => {
                    console.log(err.data);
                })
        },
        getOne:function(){
            axios.get(`http://127.0.0.1:5000/api/${this.rowNo}`)
                .then((response) => {
                    if(response.data.avgDict == "error"){
                        this.rowNo = "Should between 0 ~ "+response.data.spots;
                    }else{
                        this.x = response.data.tIndex;
                        this.y = response.data.spots;
                        this.y_real = response.data.yields;
                        this.lambda = response.data.avgDict.t;
                        this.beta0 = response.data.avgDict.b0;
                        this.beta1 = response.data.avgDict.b1;
                        this.beta2 = response.data.avgDict.b2;
                    }
                    this.plot();
                }, (err) => {
                    console.log(err.data);
                })
        },
        getAll:function(){
            axios.get("http://127.0.0.1:5000/api/all")
                .then((response) => {
                    this.lambda = response.data.avgDict.t;
                    this.beta0 = response.data.avgDict.b0;
                    this.beta1 = response.data.avgDict.b1;
                    this.beta2 = response.data.avgDict.b2;
                }, (err) => {
                    console.log(err.data);
                })
        },
        postApi:function(){
            axios.post("/axios", { key: 'value' })
                .then(function (response) {
                    console.log(response);
                }, function (err) {
                    console.log(err);
                })
        },
        plot:function(){
            var myChart = echarts.init(document.getElementById('charts'));
            option = {
                xAxis: {
                    name:'time',
                    type: 'category',
                    data: this.x
                },
                yAxis: {
                    name: 'yields',
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
            this.rightShow = flag;
        }
    }
});