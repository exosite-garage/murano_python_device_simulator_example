# Murano HTTP API Python Example

This is a basic python program active as a device and connecting to Murano.

Find more on the [Murano Connectivity Documentation](http://docs.exosite.com/connectivity/)

## Requirements

* Have Python 2.7.9 or greater installed [Python website](https://www.python.org/)
* Have [Murano Account](http://exosite.io)
* Have an [IoT-Connector Product](http://docs.exosite.com/reference/ui/create-product/)
* Copy the IoT-Connector Product solution ID

## Run the Simulator

1. Get this code to your computure.

  ```
  git clone https://github.com/exosite/murano_python_device_simulator_example.git -b 2.0
  
  cd murano_python_device_simulator_example
  ```

2. Run the device simulator by entering the command below into the terminal window. Press Enter.
  
  ```
  python murano_device_simulator.py
  ```
  
If successful, the script will ask you to enter your Product ID.

3. Paste the IoT-Connector Product ID you copied from the Murano Product view in the steps above into the terminal. Press Enter.

4. Press Enter again to use the default device identity (000001). This matches the identity format for devices that you configured in the Murano product page, so it will activate correctly.

   **NOTE:** If you have already added 000001 and simulated the device before, you may need to enter a new device (e.g., 000002). This will create and activate a new device and simulate data for it.

  If the Python Simulator is running correctly, the script should show the device has been activated and whether the lightbulb is on or off.
  
5. On The Murano IoT-Connector page you should see [the device beeing activated and receiving data](http://docs.exosite.com/connectivity/quickstart/#monitor-device)

6. Use [the Murano device dashboard page](http://docs.exosite.com/connectivity/quickstart/#dashboard) to create charts

## Send command from the cloud

1. Use [the Murano device dashboard page to send a command to the device](http://docs.exosite.com/connectivity/quickstart/#send-command).

2. You should see the device printing the received command.
