from flask import Flask, flash, redirect, render_template, request
from infoblox_netmri.client import InfobloxNetMRI

from configparser import ConfigParser
  
configur = ConfigParser()
print (configur.read('config.ini'))

app = Flask(__name__,static_url_path="/static")

netmri_url = configur.get('netmri','url')
netmri_user = configur.get('netmri','user')
netmri_password = configur.get('netmri','password')

c = InfobloxNetMRI(host=netmri_url,
                username=netmri_user,
                password=netmri_password)

@app.route('/')
def netmri():
    devices = c.api_request('infra_devices/index', {'limit': 1000})
    inventory = {}
    x = 0
    for device in devices['infra_devices']:
        id =device['DeviceID']
        sn = c.api_request(f'infra_devices/chassis_serial_number?id={id}', {'limit': 1})
        #print(device['DeviceName'], sn['chassis_serial_number'], device['DeviceVersion'])
        x+=1
        inventory[x]={}
        inventory[x]['id'] = device['DeviceID']
        inventory[x]['name'] = device['DeviceName']
        inventory[x]['version'] = device['DeviceVersion']
        inventory[x]['model'] = device['DeviceModel']
        inventory[x]['ipaddress'] = device['DeviceIPDotted']
        inventory[x]['serial'] = sn['chassis_serial_number']
    return render_template('netmri.html', posts=inventory)

@app.route("/device_config/<ipspace>")
def get_running_details(ipspace):
    devices = c.show('device', ipspace )
    devicename = devices['device']['DeviceName']
    config = c.api_request(f'devices/running_config_text?id={ipspace}', {'limit': 1})
    return render_template('device_details.html', posts=config, devicename=devicename)


@app.route('/netmri_if')
def netmri_if():
    devices = c.api_request('devices/index', {'limit': 100})
    return render_template('netmri_if.html', posts=devices)

@app.route("/interfaces/<ipspace>")
def get_interface_details(ipspace):
    devices = c.show('device', ipspace )
    devicename = devices['device']['DeviceName']
    config = c.api_request(f'interfaces/find?op_DeviceID==&val_c_DeviceID={ipspace}', {'limit': 500})
    int_total = c.api_request(f'interfaces/port_status_aggregate_count?DeviceID={ipspace}', {'limit': 10})
    return render_template('interfaces.html', posts=config, total=int_total, devicename=devicename)

@app.route("/routes/<ipspace>")
def get_routes_details(ipspace):
    devices = c.show('device', ipspace )
    devicename = devices['device']['DeviceName']
    config = c.api_request(f'device_routes/find?op_DeviceID==&val_c_DeviceID={ipspace}', {'limit': 5000})
    return render_template('routes.html', posts=config, devicename=devicename)


if __name__ == "__main__":
    app.run(debug=True)
