class PIController:
    def __init__(self, kp, ki, dt):
        self.kp = kp
        self.ki = ki
        self.dt = dt
        self.integral_x = 0.0
        self.integral_y = 0.0

    def update(self, error_x, error_y):
        # Update the integral terms
        self.integral_x += error_x * self.dt
        self.integral_y += error_y * self.dt

        # Compute the control output (setpoint) using both proportional and integral terms
        setpoint_x = self.kp * error_x + self.ki * self.integral_x
        setpoint_y = self.kp * error_y + self.ki * self.integral_y

        return setpoint_x, setpoint_y