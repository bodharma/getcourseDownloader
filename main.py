import m3u8_To_MP4
import zipfile
import json


def download_video(full_url, video_out_path, name):
    """

    :param full_url: "https://player02.getcourse.ru/player/d3cbefc3984d55d63da38aa1e6ab37b7/6d28b119fc5d5ed1f53566070302b98b/media/1080.m3u8\?sid\=\&user-cdn\=integros\&version\=5%3A2%3A1%3A0%3Aintegros\&user-id\=290461568\&jwt\=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyLWlkIjoyOTA0NjE1Njh9.JbJQr1hU5TQLTPTCiT_uz4oayfS4bcVqJkJs7meu_Sk"
    :param name: 'day1'
    :return:
    """
    valid_url = full_url.split("\\")[0]

    fn = f"{name}.mp4"
    filepath = video_out_path/fn
    filepath.touch(exist_ok=True)
    m3u8_To_MP4.multithread_download(valid_url, mp4_file_dir=str(video_out_path), mp4_file_name=fn)
    if filepath.stat().st_size == 0:
        print(f"File {filepath} is empty")
        filepath.unlink()



def get_data_from_archive(archive):
    quality_videos_list = []
    with zipfile.ZipFile(archive) as z:
        network_trace = z.open('trace.network', 'r')
        for line in network_trace:
            decoded_line = line.decode(encoding='utf-8')
            if 'm3u8' in decoded_line:
                line_data = json.loads(decoded_line)
                url = line_data['snapshot']['request']['url']
                if '720.m3u8' in url or '1080.m3u8' in url or '360.m3u8' in url:
                    quality_videos_list.append({archive.stem: url})
    return quality_videos_list



