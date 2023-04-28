from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status, authentication, permissions

from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser
import boto3

from conversation.models import ConversationModel
from conversation.serializers import ConversationSerializer, ConversationUploadSerializer


class ConversationView(GenericAPIView):

    serializer_class = ConversationSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        queryset = ConversationModel.objects.all()
        serializer = ConversationSerializer(queryset, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)


def start_job(job_name, bucket_name, file_name, media_format, language_code, transcribe_client, vocabulary_name=None):
    """Start an asynchronous transcription job."""
    media_uri = f"s3://{bucket_name}/{file_name}"
    try:
        job_args = {
            "TranscriptionJobName": job_name,
            "Media": {"MediaFileUri": media_uri},
            "MediaFormat": media_format,
            "LanguageCode": language_code,
            "OutputBucketName": bucket_name,
            "OutputKey": file_name.replace(".wav", ".json"),
        }
        if vocabulary_name is not None:
            job_args["Settings"] = {"VocabularyName": vocabulary_name}
        response = transcribe_client.start_transcription_job(**job_args)
        job = response["TranscriptionJob"]
        print(f"Started transcription job {job_name}.")
    except Exception:
        print(f"Couldn't start transcription job {job_name}")
        raise
    else:
        return job


class ConversationUploadView(GenericAPIView):
    """View for transcribing a conversation file (a wav file)"""

    serializer_class = ConversationUploadSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FileUploadParser)

    def post(self, request):
        serializer = ConversationUploadSerializer(data=request.data)
        bucket_name = "fundcraft-backend-dev"
        if serializer.is_valid():
            file = request.FILES["conversation_file"]
            s3 = boto3.client("s3")
            transcribe = boto3.client("transcribe")
            file_name = file.name
            s3.upload_fileobj(file, bucket_name, file_name)
            job_name = "transcribe-job-" + file_name

            # Start transcription job
            start_job(
                job_name=job_name,
                bucket_name=bucket_name,
                file_name=file_name,
                media_format="wav",
                language_code="en-US",
                transcribe_client=transcribe,
            )

            job_status = transcribe.get_transcription_job(TranscriptionJobName=job_name)["TranscriptionJob"][
                "TranscriptionJobStatus"
            ]

            # wait for the transcription job to complete
            while job_status == "IN_PROGRESS":
                job_status = transcribe.get_transcription_job(TranscriptionJobName=job_name)["TranscriptionJob"][
                    "TranscriptionJobStatus"
                ]
            # if the job completed successfully, retrieve the transcription result and store it in S3
            if job_status == "COMPLETED":
                response = s3.get_object(Bucket=bucket_name, Key=file_name.replace(".wav", ".json"))
                transcription_result = json.loads(response["Body"].read().decode("utf-8"))["results"]["transcripts"][0][
                    "transcript"
                ]
            else:
                print(f"Transcription job failed with status: {job_status}")

            return Response(status=status.HTTP_200_OK, data={"transcript": transcription_result})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
