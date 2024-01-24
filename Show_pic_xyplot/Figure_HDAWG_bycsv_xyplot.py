"""
Zurich Instruments LabOne Python API Example

Demonstrate how to connect to a Zurich Instruments HDAWG and upload and run an
AWG program using the command table.
"""

# Copyright 2020 Zurich Instruments AG

import os
import time
import json
import textwrap
import zhinst.utils
import wave
import numpy as np
import matplotlib.pyplot as plt
import Figure_convert as fc


data = fc.fig_xy_convert("C:/Users/panhuih/Pictures/Fu.png")
xx = data[0]
yy = data[1]


def run_example(device_id):
    """
    Run the example: Connect to a Zurich Instruments HDAWG upload and run a
    basic AWG sequence program. It also demonstrates how to upload (replace) a
    waveform without changing the sequencer program.

    Requirements:

       HDAWG Instrument.

    Arguments:

      device_id (str): The ID of the device to run the example with. For
        example, `dev8006` or `hdawg-dev8006`.

    Returns:

      No return value.

    Raises:

      Exception: If the device is not an HDAWG.

      RuntimeError: If the device is not "discoverable" from the API.

    See the "LabOne Programming Manual" for further help, available:
      - On Windows via the Start-Menu:
        Programs -> Zurich Instruments -> Documentation
      - On Linux in the LabOne .tar.gz archive in the "Documentation"
        sub-folder.
    """

    # Settings
    apilevel_example = 6  # The API level supported by this example.
    err_msg = "This example can only be ran on an HDAWG."
    # Call a zhinst utility function that returns:
    # - an API session `daq` in order to communicate with devices via the data server.
    # - the device ID string that specifies the device branch in the server's node hierarchy.
    # - the device's discovery properties.
    (daq, device, _) = zhinst.utils.create_api_session(
        device_id, apilevel_example, required_devtype="HDAWG", required_err_msg=err_msg
    )
    zhinst.utils.api_server_version_check(daq)

    # Create a base configuration: Disable all available outputs, awgs, demods, scopes,...
    zhinst.utils.disable_everything(daq, device)

    # 'system/awg/channelgrouping' : Configure how many independent sequencers
    #   should run on the AWG and how the outputs are grouped by sequencer.
    #   0 : 4x2 with HDAWG8; 2x2 with HDAWG4.
    #   1 : 2x4 with HDAWG8; 1x4 with HDAWG4.
    #   2 : 1x8 with HDAWG8.
    # Configure the HDAWG to use one sequencer for each pair of output channels
    daq.setInt(f"/{device}/system/awg/channelgrouping", 0)

    # Some basic device configuration to output the generated wave.
    out_channel_0 = 0
    out_channel_1 = 1
    awg_channel = 0
    amplitude = 1.0

    exp_setting = [
        ["/%s/sigouts/%d/on" % (device, out_channel_0), 1],
        ["/%s/sigouts/%d/on" % (device, out_channel_1), 1],
        ["/%s/sigouts/%d/range" % (device, out_channel_0), 1],
        ["/%s/sigouts/%d/range" % (device, out_channel_1), 1],
        ["/%s/awgs/0/outputs/%d/amplitude" % (device, awg_channel), amplitude],
        ["/%s/awgs/0/outputs/0/modulation/mode" % device, 0],
        ["/%s/awgs/0/time" % device, 0],
        ["/%s/awgs/0/userregs/0" % device, 0],
    ]
    daq.set(exp_setting)
    # Ensure that all settings have taken effect on the device before continuing.
    daq.sync()

    # Define an AWG program as a string stored in the variable awg_program, equivalent to what would
    # be entered in the Sequence Editor window in the graphical UI.
    # This example demonstrates four methods of definig waveforms via the API
    # - (wave w2) using the vect() function and programmatic string replacement.



    awg_program = textwrap.dedent(
        """\
        wave w2_x = "wave_x";
        wave w2_y = "wave_y";
        playWave (w2_x,w2_y);
        """
    )


    # Create an instance of the AWG Module
    awgModule = daq.awgModule()
    awgModule.set("device", device)
    awgModule.execute()

    # Transfer the AWG sequence program. Compilation starts automatically.
    awgModule.set("compiler/sourcestring", awg_program)
    # Note: when using an AWG program from a source file (and only then), the compiler needs to
    # be started explicitly with awgModule.set('compiler/start', 1)
    while awgModule.getInt("compiler/status") == -1:
        time.sleep(0.1)

    if awgModule.getInt("compiler/status") == 1:
        # compilation failed, raise an exception
        raise Exception(awgModule.getString("compiler/statusstring"))

    if awgModule.getInt("compiler/status") == 0:
        print("Compilation successful with no warnings, will upload the program to the instrument.")
    if awgModule.getInt("compiler/status") == 2:
        print("Compilation successful with warnings, will upload the program to the instrument.")
        print("Compiler warning: ", awgModule.getString("compiler/statusstring"))

    # Wait for the waveform upload to finish
    time.sleep(1)
    i = 0
    while (awgModule.getDouble("progress") < 1.0) and (awgModule.getInt("elf/status") != 1):
        print(f"{i} progress: {awgModule.getDouble('progress'):.2f}")
        time.sleep(0.2)
        i += 1
    print(f"{i} progress: {awgModule.getDouble('progress'):.2f}")
    if awgModule.getInt("elf/status") == 0:
        print("Upload to the instrument successful.")
    if awgModule.getInt("elf/status") == 1:
        raise Exception("Upload to the instrument failed.")

    print(f"Enabling the AWG: Set /{device}/awgs/0/userregs/0 to 1 to trigger waveform playback.")
    # This is the preferred method of using the AWG: Run in single mode continuous waveform playback is best achieved by
    # using an infinite loop (e.g., while (true)) in the sequencer program.

    daq.setInt(f"/{device}/awgs/0/single", 0)
    daq.setInt(f"/{device}/awgs/0/enable", 1)


run_example('dev8220')