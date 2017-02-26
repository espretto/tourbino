
serial port testing
-------------------

virtualbox
- shutdown the machine
- go to serial ports settings
- enable the second port with the following options
  - name: `COM1`
  - type: `Host Pipe`
  - check `Create Pipe`
  - path: `/tmp/com1`
- start virtual machine and verify existence of COM1 interface in device manager
- launch the serial listener app on the guest
- on linux hosts `Host Pipe`s are represented through domain sockets. connect to
  it through `socat - UNIX-CONNECT:/tmp/com1` and then just write an see it appear
  on the guest.


troubleshooting
---------------

the below issue is solved by downgrading to python version 3.4.x as was pointed out [here][2].

Problem: Windows error message
```
The procedure entry point ucrtbase.terminate could not be located in the dynamic link library api-ms-win-crt-runtime-l1-1-0.dll
```
Solution: install the [Visual C++ Redistributable for Visual Studio 2015][1]. Usually this package comes with Windows Updates.

[1]: https://www.microsoft.com/en-us/download/details.aspx?id=48145
[2]: https://github.com/pyinstaller/pyinstaller/issues/1566#issuecomment-146564554
