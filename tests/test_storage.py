from src.services.storage import blob_client, queue_client


def test_blob_upload_download():
    data = b'hello world'
    name = 'test/test.txt'
    blob_client.upload_blob(name, data)
    got = blob_client.download_blob(name)
    assert got == data


def test_queue_send_receive_delete():
    msg = {'doc_id': 'x', 'blob_name': 'y'}
    queue_client.send_message(msg)
    msgs = queue_client.receive_messages(max_messages=5)
    assert msgs is not None
