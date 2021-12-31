import boto3
import logging

from pathlib import Path
from tqdm import tqdm

logger = logging.getLogger(__name__)


class S3:
    """
    Class for uploading and downloading files from Amazon S3
    ...
    Attributes
    -----------
    bucket_name : str
        The name of the bucket in Amazon S3.
    src : str
        Source Location
    dst : str
        Destination Location
    Methods
    -----------
    download(src, dst='.', bucket_name=None)
        Downlaods the file from Amazon S3 and save in destination location.
    upload(src, dst='.', bucket_name=None)
        Upload from from source to destination in Amazon S3.
    """
    def __init__(self, bucket_name=None, *args, **kwargs):
        """
        Parameters
        -----------
        bucket_name : str
            The name of the bucket in Amazon S3
        """
        self.buckets_name = bucket_name

        logger.info('Loading resources from S3 Bucket...')
        self.resource = boto3.resource('s3', *args, **kwargs)
        # boto3.resource('s3', aws_access_key_id=aws_access_key_id,
        # aws_secret_access_key=aws_secret_access_key, region_name=region_name)
        logger.info('Resources loaded')

    def download_file(self, src, dst='.', bucket_name=None):
        return self.download(src, dst, bucket_name)

    def download(self, src, dst='.', bucket_name=None):
        """
        Downloads the file from Amazon S3 using source location
        to the destination location.
        Parameters
        -----------
        src : str
            Source location
        dst: str
            Destination location
        bucket_name : str
            The name of the bucket in Amazon S3.
        Raises
        -----------
        ValueError
            If bucket_name is not set or passed as parameter.
        """
        bucket_name = bucket_name or self.bucket_name
        if bucket_name is None:
            raise ValueError('Please specify a bucket name')

        logger.info(f'Downloading {src} from S3 to {dst}...')
        src_len = len(Path(src).parts) - 1
        bucket = self.resource.Bucket(bucket_name)
        files = [file for file in bucket.objects.filter(Prefix=str(src))]
        for file in tqdm(files):
            dst_path = Path(dst, *Path(file.key).parts[src_len:])
            dst_path.parent.mkdir(parents=True, exist_ok=True)

            bucket.download_file(file.key, str(dst_path))
        logger.info(f'Download Complete')
        return self

    def upload_file(self, src, dst='.', bucket_name=None, verbose=True):
        """
        Uploads the file to Amazon S3 using source location
        to the destination location.
        Parameters
        -----------
        src : str
            Source location
        dst: str
            Destination location
        bucket_name:
            The name of the bucket in S3.
        verbose: bool
            True : to log the message otherwise not.
        Raises
        -----------
        ValueError
            If bucket_name is not set or passed as parameter.
        """
        bucket_name = bucket_name or self.bucket_name
        if bucket_name is None:
            raise ValueError('Please specify a bucket name')

        src_path = Path(src)
        if not src_path.is_file():
            return self.upload(src, dst)

        if verbose:
            logger.info(f'Uploading {src} to S3...')
        dst_path = Path(dst, src_path.name)
        self.resource.meta.client.upload_file(
            str(src_path), bucket_name, str(dst_path)
        )
        if verbose:
            logger.info('Upload Complete')

    def upload(self, src, dst='.', bucket_name=None):
        """
        Uploads the file to Amazon S3 using source location
        to the destination location.
        Parameters
        -----------
        src : str
            Source location
        dst: str
            Destination location
        bucket_name: str
            The name of the bucket in Amazon S3.
        Raises
        -----------
        ValueError
            If bucket_name is not set or passed as parameter.
        """
        bucket_name = bucket_name or self.bucket_name
        if bucket_name is None:
            raise ValueError('Please specify a bucket name')

        src_path = Path(src)
        if src_path.is_file():
            return self.upload_file(src, dst)

        logger.info(f'Uploading {src} to S3...')
        src_len = len(src_path.parts) - 1
        for file in tqdm(list(src_path.rglob('*.*'))):
            dst_path = Path(dst, *file.parts[src_len:-1])
            self.upload_file(file, dst_path, bucket_name, verbose=False)
        logger.info('Upload Complete')


class SQS:
    def __init__(self, queue_name=None, message_url=None, *args, **kwargs):
        """
        Parameters
        ------------
        receiver_queue_name: str
            The name of the queue from which the message is to be received.
        runner
            The runner to be used.
                FrameExtractionRunner or,
                FaceDetectionRunner   or,
                FaceMatchingRunner
        """
        self.queue_name = queue_name
        self.message_url = message_url

        logger.info('Connecting to SQS...')
        self.resource = boto3.resource('sqs', *args, **kwargs)
        logger.info('Connection Established')

    def send_message(
            self, message: str, queue_name: str = None, url: str = None
    ):
        queue_name = queue_name or self.queue_name
        queue = self.resource.get_queue_by_name(QueueName=queue_name)

        url = url or self.message_url
        logger.info(f'Sending message to {url}')
        response = queue.send_message(QueueUrl=url, MessageBody=message)

        status_code = response['ResponseMetadata']['HTTPStatusCode']
        message_id = response['MessageId']

        logger.info(
            f'Message sent as {message_id} with status code {status_code}'
        )

        return response

    def receive_message(self, queue_name=None):
        queue_name = queue_name or self.queue_name
        queue = self.resource.get_queue_by_name(QueueName=queue_name)

        messages = queue.receive_messages(MaxNumberOfMessages=1)
        message = messages[0] if messages else messages
        return message