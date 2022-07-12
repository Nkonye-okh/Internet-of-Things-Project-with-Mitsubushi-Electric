# Internet-of-Things-Project-with-Mitsubushi-Electric
Project invloved getting data from PLC devices (i.e., Robot controllers) and publishing data for visualisation and analysis.

In information and communication technology, the Internet of Things refers to a global infrastructure that allows physical objects and virtual ones to be connected and work together.

Integrated sensors, instruments, and other devices networked with computers for applications in the industrial sector, such as manufacturing and energy management, comprise the Industrial Internet of Things (IIoT). As a result of this connectivity, data can be collected, shared, and analyzed, resulting in productivity and efficiency gains. In the Internet of Things (IoT), distributed control systems can be automated to a greater level by leveraging cloud computing to optimize and refine control processes.

An Industrial Internet of Things (IIoT) connects systems and devices that are larger than smartphones and wireless devices. A network is used to connect industrial assets such as motors, power grids, and sensors to the cloud.

Here, the application reads data (i.e., runtime data, temperature from temperature sensors, and other base info) from Robot contriollers using the SLMP protocol and publishes these data to the MQTT Broker using an MQTT client. From the MQTT broker, the data is published on a chart for visualisation and analysis using a javascript client.
