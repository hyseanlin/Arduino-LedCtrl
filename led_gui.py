
import tkinter as tk
from tkinter import ttk, messagebox
import serial
from serial.tools import list_ports


class LEDController:
    def __init__(self, root):
        self.root = root
        self.root.title("Arduino LED Controller")
        self.root.geometry("440x340")
        self.root.resizable(False, False)

        self.arduino = None
        self.send_job = None
        self.ready_job = None
        self.connected_ready = False

        # COM Port
        ttk.Label(
            root, text="Arduino COM Port:"
        ).pack(pady=(15, 5))

        self.port_combo = ttk.Combobox(
            root, state="readonly", width=25
        )
        self.port_combo.pack()

        ttk.Button(
            root, text="Refresh Ports",
            command=self.refresh_ports
        ).pack(pady=5)

        # Connection buttons
        self.connect_button = ttk.Button(
            root, text="Connect",
            command=self.connect
        )
        self.connect_button.pack(pady=5)

        self.disconnect_button = ttk.Button(
            root, text="Disconnect",
            command=self.disconnect,
            state="disabled"
        )
        self.disconnect_button.pack(pady=5)

        # Frequency control
        ttk.Label(
            root, text="LED Breathing Delay (ms)"
        ).pack(pady=(15, 5))

        self.frequency = tk.IntVar(value=100)

        # Create label BEFORE slider
        self.value_label = ttk.Label(
            root,
            text="FREQUENCY = 100 ms",
            font=("Arial", 12, "bold")
        )
        self.value_label.pack(pady=10)

        self.slider = ttk.Scale(
            root,
            from_=1,
            to=1000,
            orient="horizontal",
            command=self.update_label
        )
        self.slider.set(100)
        self.slider.pack(fill="x", padx=35)

        # Status
        self.status_label = ttk.Label(
            root,
            text="Status: Disconnected",
            foreground="red"
        )
        self.status_label.pack(pady=10)

        self.refresh_ports()
        self.root.protocol(
            "WM_DELETE_WINDOW", self.on_close
        )

    def refresh_ports(self):
        ports = [
            p.device for p in list_ports.comports()
        ]
        self.port_combo["values"] = ports

        if ports:
            self.port_combo.current(0)

    def connect(self):
        port = self.port_combo.get()

        if not port:
            messagebox.showerror(
                "Error", "Please select a COM port."
            )
            return

        try:
            self.arduino = serial.Serial(
                port=port,
                baudrate=9600,
                timeout=1,
                write_timeout=1
            )

            self.connected_ready = False

            self.connect_button.config(
                state="disabled"
            )
            self.disconnect_button.config(
                state="normal"
            )

            self.status_label.config(
                text="Status: Waiting for Arduino...",
                foreground="orange"
            )

            # Arduino normally resets when
            # the Serial port is opened.
            self.ready_job = self.root.after(
                2000, self.connection_ready
            )

        except serial.SerialException as e:
            messagebox.showerror(
                "Connection Error", str(e)
            )

    def connection_ready(self):
        self.ready_job = None

        if not self.arduino or not self.arduino.is_open:
            return

        self.connected_ready = True

        self.status_label.config(
            text="Status: Connected",
            foreground="green"
        )

        # Send current slider value immediately
        self.send_frequency()

    def disconnect(self):
        self.connected_ready = False

        if self.send_job is not None:
            self.root.after_cancel(self.send_job)
            self.send_job = None

        if self.ready_job is not None:
            self.root.after_cancel(self.ready_job)
            self.ready_job = None

        if self.arduino:
            self.arduino.close()
            self.arduino = None

        self.connect_button.config(
            state="normal"
        )
        self.disconnect_button.config(
            state="disabled"
        )

        self.status_label.config(
            text="Status: Disconnected",
            foreground="red"
        )

    def update_label(self, value):
        frequency = round(float(value))
        self.frequency.set(frequency)

        self.value_label.config(
            text=f"FREQUENCY = {frequency} ms"
        )

        # Debounce: wait until slider
        # stops moving for 100 ms.
        if self.send_job is not None:
            self.root.after_cancel(self.send_job)
            self.send_job = None

        if self.connected_ready:
            self.send_job = self.root.after(
                100, self.send_frequency
            )

    def send_frequency(self):
        self.send_job = None

        if not self.connected_ready:
            return

        if self.arduino and self.arduino.is_open:
            try:
                frequency = self.frequency.get()

                command = f"{frequency}\n"

                self.arduino.write(
                    command.encode("utf-8")
                )

                self.status_label.config(
                    text=f"Sent FREQUENCY = {frequency} ms",
                    foreground="green"
                )

            except (serial.SerialException,
                    serial.SerialTimeoutException) as e:
                messagebox.showerror(
                    "Serial Error", str(e)
                )
                self.disconnect()

    def on_close(self):
        self.disconnect()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = LEDController(root)
    root.mainloop()
