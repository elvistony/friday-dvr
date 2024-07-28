import configparser
import os
import time
from datetime import datetime
from vidgear.gears import CamGear, WriteGear
import multiprocessing

CONFIG_FILE = 'config.ini'
RETRY_INTERVAL = 30  # in seconds
_LOGGING = False

def read_config():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    global RETRY_INTERVAL 
    RETRY_INTERVAL = int(config['DEFAULT']['retry_interval'])
    return config

def is_stream_up(rtsp_url):
    try:
        stream = CamGear(source=rtsp_url,  logging=_LOGGING).start()
        frame = stream.read()
        stream.stop()
        return frame is not None
    except Exception as e:
        print(f"Error checking stream: {e}")
        return False

# def get_free_space_mb(folder):
#     # return 1000
#     st = os.statvfs(folder)
#     return (st.f_bavail * st.f_frsize) / 1024 / 1024

import os
import platform
  # For Windows

def get_free_space_mb(folder):
    """Returns the free disk space in megabytes for the specified folder."""

    if platform.system() == "Windows":
        import win32api
        free_bytes = win32api.GetDiskFreeSpaceEx(folder)[0]
        return free_bytes / (1024 * 1024)
    else:
        st = os.statvfs(folder)
        return (st.f_bavail * st.f_frsize) / 1024 / 1024
'''
def create_local_writer(camera_name, max_file_size):
    timestamp = datetime.now()
    date_dir = timestamp.strftime('%d_%m_%Y')
    time_filename = timestamp.strftime('%H:%M.mp4')
    output_dir = os.path.join('recordings', camera_name, date_dir)
    os.makedirs(output_dir, exist_ok=True)
    
    local_output_params = {
        "-input_framerate": 30,  # This should match the stream's framerate
        "-c:v": "libx264",
        "-preset": "veryfast",
        "-b:v": "3000k",
        "-bufsize": "6000k",
        "-pix_fmt": "yuv420p",
        "-g": "60",
        "-c:a": "aac",
        "-b:a": "128k",
        "-ar": "44100",
        "-f": "segment",
        "-segment_time": str(max_file_size * 60),
        "-reset_timestamps": "1"
    }
    local_writer = WriteGear(output_filename=os.path.join(output_dir, time_filename), logging=_LOGGING, **local_output_params)
    return local_writer

def stream_and_record(rtsp_url, youtube_key, local_recording, max_file_size, camera_name):
    stream = CamGear(source=rtsp_url,  logging=_LOGGING).start()

    output_params = {
    "-clones": ["-f", "lavfi", "-i", "anullsrc"],  # Add fake audio
    "-vcodec": "libx264",
    "-preset": "medium",
    "-b:v": "4500k",  # Adjust bitrate as needed
    "-bufsize": "512k",
    "-pix_fmt": "yuv420p",
    "-f": "flv",
}
    output_params = {
        "-clones": ["-f", "lavfi", "-i", "anullsrc"],  # Add fake audio
        "-vcodec": "libx264",
        "-preset": "ultrafast",
        "-tune": "zerolatency",
        "-b:v": "3000k",  # Adjust bitrate as needed
        "-maxrate": "3000k",
        "-bufsize": "6000k",
        "-pix_fmt": "yuv420p",
        "-g": "60",  # Set keyframe interval to 2 seconds (30 FPS * 2)
        "-f": "flv",
    }


    # output_params = {
    #     "-vcodec": "libx264",
    #     "-preset": "medium",
    #     "-b:v": "4500k",  # Adjust bitrate as needed
    #     "-bufsize": "512k",
    #     "-pix_fmt": "yuv420p",
    #     "-acodec": "aac",  # Audio codec
    #     "-ar": "44100",  # Audio sample rate
    #     "-f": "flv",
    # }

    youtube_url = f"rtmp://a.rtmp.youtube.com/live2/{youtube_key}"
    writer = WriteGear(output_filename=youtube_url, logging=_LOGGING, **output_params)

    local_writer = create_local_writer(camera_name, max_file_size) if local_recording else None

    while True:
        frame = stream.read()
        if frame is None:
            break
        writer.write(frame)
        if local_writer:
            local_writer.write(frame)

    stream.stop()
    writer.close()
    if local_writer:
        local_writer.close()
'''
def create_local_writer(camera_name, max_file_size):
    timestamp = datetime.now()
    date_dir = timestamp.strftime('%d_%m_%Y')
    output_dir = os.path.join('recordings', camera_name, date_dir)
    os.makedirs(output_dir, exist_ok=True)

    local_output_params = {
        "-input_framerate": 30,  # This should match the stream's framerate
        "-vcodec": "libx264",
        "-preset": "veryfast",
        "-b:v": "3000k",
        "-bufsize": "6000k",
        "-pix_fmt": "yuv420p",
        "-g": "60",  # Set keyframe interval to 2 seconds (30 FPS * 2)
        "-c:a": "aac",
        "-b:a": "128k",
        "-ar": "44100",
        "-f": "segment",
        "-segment_time": str(max_file_size * 60),
        "-reset_timestamps": "1"
    }
    local_writer = WriteGear(output_filename=os.path.join(output_dir, 'output'), logging=_LOGGING, **local_output_params)
    return local_writer

def stream_and_record(rtsp_url, youtube_key, local_recording, max_file_size, camera_name):
    stream = CamGear(source=rtsp_url, stream_mode=False, logging=_LOGGING).start()

    output_params = {
        "-vcodec": "libx264",
        "-preset": "ultrafast",  # Use ultrafast preset for least CPU usage
        "-tune": "zerolatency",
        "-b:v": "3000k",  # Adjust bitrate as needed
        "-maxrate": "3000k",
        "-bufsize": "6000k",
        "-pix_fmt": "yuv420p",
        "-g": "60",  # Set keyframe interval to 2 seconds (30 FPS * 2)
        "-f": "flv",
    }

    # output_params = {
    #     "-clones": ["-f", "lavfi", "-i", "anullsrc"],  # Add fake audio
    #     "-vcodec": "libx264",
    #     "-preset": "medium",
    #     "-b:v": "4500k",  # Adjust bitrate as needed
    #     "-bufsize": "512k",
    #     "-pix_fmt": "yuv420p",
    #     "-f": "flv",
    # }

    youtube_url = f"rtmp://a.rtmp.youtube.com/live2/{youtube_key}"
    writer = WriteGear(output_filename=youtube_url, logging=_LOGGING, **output_params)

    local_writer = create_local_writer(camera_name, max_file_size) if local_recording else None

    try:
        while True:
            frame = stream.read()
            if frame is None:
                break

            # Check frame dimensions and format
            if local_writer:
                try:
                    local_writer.write(frame)
                except Exception as e:
                    print(f"Error writing frame to local file: {e}")

            try:
                writer.write(frame)
            except Exception as e:
                print(f"Error writing frame to YouTube: {e}")
    finally:
        stream.stop()
        writer.close()
        if local_writer:
            local_writer.close()

def main():
    config = read_config()
    max_total_size = int(config['DEFAULT'].get('max_total_size', 10000))  # in MB
    max_file_size = int(config['DEFAULT'].get('max_file_size', 500))  # in MB

    while True:
        processes = []
        for section in config.sections():
            rtsp_url = config[section]['rtsp_url']
            youtube_key = config[section]['youtube_key']
            local_recording = 'local_recording' in config[section] and config[section].getboolean('local_recording')
            camera_name = section
            print("Starting Camera:", camera_name)
            if is_stream_up(rtsp_url):
                p = multiprocessing.Process(target=stream_and_record, args=(rtsp_url, youtube_key, local_recording, max_file_size, camera_name))
                processes.append(p)
                p.start()
            else:
                print(f'Stream {rtsp_url} is down. Retrying in {RETRY_INTERVAL} seconds.')

        for p in processes:
            p.join()

        time.sleep(RETRY_INTERVAL)

if __name__ == '__main__':
    main()
