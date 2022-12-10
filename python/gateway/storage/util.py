import pika
import json


def upload(f, fs, channel, access):
    ''' 1. first the file is uploded to mongodb server
        2. A msg is put in rabbitmq queue when file is uploaded successfully 
        3. downstream service will pull up the msg, can process the file from monogodb 
        4. queue create async flow between gateway service and processing service 
    '''

    try:
        fid: fs.put(f)
    except Exception as err:
        return "internal server error", 500
    message = {
        "video_fid": str(fid),
        "mp3_fid": None,
        "username": access["username"],
    }
    try:
        channel.basic_publish(
            exchange="",
            routing_key="video",  # name of queue,
            body=json.dumps(message),
            properties=pika.BasicProperites(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )
    except:
        fs.delete(fid)
        return "internal server error", 500
