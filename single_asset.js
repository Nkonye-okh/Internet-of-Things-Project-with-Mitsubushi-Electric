var BROKER_URL = "i40.mitsubishielectric.de"; //"test.mosquitto.org"; //;
var BROKER_PORT = 4840; //8080; //4840;
var BROKER_KEEP_ALIVE = 60;
var QOS = 1;
var ROOT_SUBSCRIPTION_TOPIC = "ReDI-School";
var USERNAME="ReDI";
var PASSWORD="XG#oLG%ubuN4";
var OWN_TOPIC = ROOT_SUBSCRIPTION_TOPIC + "/3002";

var MQTT_CLIENT_ID = "iot_web_"+Math.floor((2 + Math.random()) * 0x10000000000).toString(16);
var MQTT_CLIENT = new Paho.MQTT.Client(BROKER_URL, BROKER_PORT, "/ws", MQTT_CLIENT_ID);

MQTT_CLIENT.connect({ 
	userName : USERNAME,
	password : PASSWORD,
	onSuccess: myClientConnected,
	onFailure: myClientConFailed
});


const labels = [
    '0'
  ];

  var data = {
    labels: labels,
    datasets: [{
      label: 'Position 1',
      backgroundColor: 'rgb(255, 99, 132)',
      borderColor: 'rgb(255, 99, 132)',
      cubicInterpolationMode: 'monotone',
      tension: 0.4,
      data: [],
    }, 
	{
      label: 'Position 2',
      backgroundColor: 'rgb(255, 99, 0)',
      borderColor: 'rgb(255, 99, 0)',
      cubicInterpolationMode: 'monotone',
      tension: 0.4,
      data: [],
    }]
  };
  
  var data2 = {
  labels: [
    'Current',
    'Buffer'
  ],
  datasets: [{
    label: 'Temperature',
    data: [300, 50],
    backgroundColor: [
      'rgb(255, 99, 132)',
      'rgb(255, 255, 255)'
    ],
    hoverOffset: 4
  }]
};

 const config = {
    type: 'line',
    data: data,
    options: {}
  };
  
 const config2 = {
	type: 'doughnut',
	data: data2, 
 };

var myChart;
var myChart2;
function init_chart() {
  myChart = new Chart(
    document.getElementById('myChart'),
    config
  );
  
  myChart2 = new Chart(
    document.getElementById('myChart2'),
    config2
  );
  
}

function update_chart() {
		myChart.update()
}

function clear_chart() {
	data.datasets[0].data = [];
	data.datasets[1].data = [];
	data.labels = ['0']
	myChart.update()
}



function myClientConnected() 
{
	document.getElementById("conStatus").innerHTML = "<p>Connected to broker "+BROKER_URL+"</p>";
	MQTT_CLIENT.subscribe(ROOT_SUBSCRIPTION_TOPIC+"/#");
	document.getElementById("header").innerHTML = "<p>Broker on "+BROKER_URL+"</p>";
}

function myClientConFailed(responseObject) 
{
	document.getElementById("conStatus").innerHTML = "<p>Failed to connect to broker "+BROKER_URL+"</p>";
}

function myMessageArrived(message) 
{
	var messageTopic = message.destinationName;

	switch (messageTopic)
    {
        case OWN_TOPIC + "/RuntimeData":
            document.getElementById("runtimeDataTxt").innerHTML = message.payloadString;
			var result = JSON.parse(message.payloadString);
			
			data.datasets[0].data.push(result.data[1])
			data.datasets[1].data.push(result.data[2])
			//data.labels.push(message.payloadString)
			data.labels.push(data.labels.length.toString())
			myChart.update()
			
			
			data2.datasets[0].data[0] = result.data[3]
			data2.datasets[0].data[1] = 45 - result.data[3]
			myChart2.update()
            break;
		case OWN_TOPIC + "/BaseInfo":
			var result = JSON.parse(message.payloadString);
									
			document.getElementById("plcTypeTxt").innerHTML = "PLC Type: " + result.cpu_type
			document.getElementById("timeZoneTxt").innerHTML = "Time Zone UTC " + (result.time_zone/60)
			document.getElementById("firmwareTxt").innerHTML = "F/W Version: " + result.firmware;
			
			break;
		case OWN_TOPIC + "/StatusInfo":
			document.getElementById("statusInfoTxt").innerHTML = message.payloadString;
			break;
        default:
			console.log(messageTopic)
            console.log(message.payloadString)
			break;
    }
}

MQTT_CLIENT.onMessageArrived = myMessageArrived;

