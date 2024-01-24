"""DAQ Module."""
from zhinst.toolkit import Session
#from zhinst.toolkit.driver import devices
from zhinst.toolkit.driver import modules
from pathlib import Path

def DLTS_load_file(device_id:str):

    #path = r"C:/Users/panhuih/AppData/Roaming/Zurich Instruments/LabOne/WebServer/setting/2024_01_02_DLTSsettings.xml"
    session = Session("localhost")
    device = session.connect_device(device_id)

    print(device.serial)
    device_settings = session.modules.device_settings
    filename = Path("C:/Users/panhuih/AppData/Roaming/Zurich Instruments/LabOne/WebServer/setting/2024_01_02_DLTSsettings.xml")
    #modules.device_settings_module.DeviceSettingsModule.load_from_file(Path(path), device)
    device_settings.device(device)
    device_settings.filename(filename.stem)
    device_settings.path(filename.parent)
    device_settings.command("load")

    device_settings.execute()

    #streming_node = devices.base.BaseInstrument(device_id,"MFIA",session)
    #result  = streming_node.get_streamingnodes()

    #print(result)
    #len(device())
    #print(device.features())


DLTS_load_file("dev4625")