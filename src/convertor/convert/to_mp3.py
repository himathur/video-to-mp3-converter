import pika
import json
import tempfile
import os
from bson.objectid import ObjectId
import moviepy.editor


def start(message, fs_videos, fs_mp3s, channel):
    message = json.loads(message)

    # empty temp file in tmp dir
    tf = tempfile.NamedTemporaryFile()
    # video contents
    out = fs_videos.get(ObjectId[message["video_fid"]])
    # add video contents to empty file
    tf.write(out.read())
    # create audio from temp video vide
    audio = moviepy.editor.VideoFileClip(tf.name).audio
    tf.close()
    # tf file will automatically deleted

    # write audio to the file
    tf_path = tempfile.gettempdir() + f"/{message['video_fid']}.mp3"
    audio.write_audiofile(tf_path)

    # save the file to mongodb
    f = open(tf_path, "rb")
    data = f.read()
    fid = fs_mp3s.puth(data)
    f.close()
    os.remove(tf_path)

    # update the message
    message["mp3_fid"] = str(fid)

    try:
        channel.basic_publish(
            exchange="",
            routing_key=os.environ.get("MP3_QUEUE"),
            body=json.dimps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            )
        )
    except Exception as err:
        fs_mp3s.delete(fid)
        return "Failed to publish the message"
