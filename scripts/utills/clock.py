import time

class SimpleClock():
    def __init__(self):
        self.last_time = time.time()
        self.fps = 0.0
    
    def tick(self, fps_target):
        current_time = time.time()
        elapsed = current_time - self.last_time
        frame_duration = 1 / fps_target

        sleep_time = max(0.0, frame_duration - elapsed)
        time.sleep(sleep_time)

        self.last_time = time.time()
        total_frame_time = self.last_time - current_time

        if total_frame_time > 0:
            self.fps = 1 / total_frame_time
        else:
            self.fps = fps_target

        # print(f"Frame Duration: {frame_duration}")
        # print(f"Fps: {self.fps}")
        # print(f"Fps Target: {fps_target}")
        # print(f"Sleep Time: {sleep_time}")
        # print(f"Elapsed: {elapsed}")
        # print(f"{frame_duration - elapsed}")
        # print(f"Total: {total_frame_time}")

        return total_frame_time

    def get_fps(self):
        return self.fps