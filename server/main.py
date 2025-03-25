import os
from dotenv import load_dotenv
from dotenv import load_dotenv
from app import app
# Load environment variables
load_dotenv()


app.config.update(
    AWS_ACCESS_KEY_ID=os.getenv('AWS_ACCESS_KEY_ID'),
    AWS_SECRET_ACCESS_KEY=os.getenv('AWS_SECRET_ACCESS_KEY'),
    AWS_REGION=os.getenv('AWS_REGION'),
    S3_BUCKET_NAME=os.getenv('S3_BUCKET_NAME')
)


if __name__ == '__main__':
    app.run(port=5555, debug=True)