import os
import boto3
import logging
import json
import pg8000
from botocore.exceptions import ClientError
import re
from typing import List

# Initialize logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
s3 = boto3.client('s3')
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

def lambda_handler(event, context):
    try:
        # Get the S3 bucket and key from the event
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = event['Records'][0]['s3']['object']['key']
        
        logger.info(f"Processing file: {key} from bucket: {bucket}")
        
        # Download the file from S3
        file_content = download_file_from_s3(bucket, key)
        
        # Parse and chunk the document
        chunks = chunk_document(file_content, chunk_size=500)
        
        # Connect to PostgreSQL
        conn = connect_to_postgresql()
        
        # Process each chunk
        for i, chunk in enumerate(chunks):
            # Generate embedding using Amazon Bedrock
            embedding = generate_embedding(chunk)
            
            # Store in PostgreSQL
            store_chunk(conn, key, chunk, embedding, i)
            
        logger.info(f"Successfully processed {len(chunks)} chunks from {key}")
        return {
            'statusCode': 200,
            'body': json.dumps(f"Processed {len(chunks)} chunks from {key}")
        }
        
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        raise e

def download_file_from_s3(bucket: str, key: str) -> str:
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        return response['Body'].read().decode('utf-8')
    except ClientError as e:
        logger.error(f"Error downloading file from S3: {e}")
        raise

def chunk_document(text: str, chunk_size: int = 500) -> List[str]:
    """Split document into chunks of approximately chunk_size tokens"""
    # Simple whitespace-based chunking - consider more sophisticated methods
    words = text.split()
    chunks = []
    current_chunk = []
    current_size = 0
    
    for word in words:
        if current_size + len(word.split()) > chunk_size and current_chunk:
            chunks.append(' '.join(current_chunk))
            current_chunk = []
            current_size = 0
        current_chunk.append(word)
        current_size += len(word.split())
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

def generate_embedding(text: str) -> List[float]:
    """Generate embedding using Amazon Bedrock Titan Embeddings model"""
    try:
        response = bedrock.invoke_model(
            modelId='amazon.titan-embed-text-v1',
            body=json.dumps({'inputText': text})
        )
        response_body = json.loads(response['body'].read())
        return response_body.get('embedding', [])
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        raise

def connect_to_postgresql():
    """Connect to PostgreSQL database"""
    try:
        conn = pg8000.connect(
            host=os.environ['DB_HOST'],
            database=os.environ['DB_NAME'],
            user=os.environ['DB_USER'],
            password=os.environ['DB_PASSWORD']
        )
        return conn
    except Exception as e:
        logger.error(f"Error connecting to PostgreSQL: {e}")
        raise

def store_chunk(conn, document_name: str, chunk_text: str, embedding: List[float], chunk_num: int):
    """Store chunk in PostgreSQL with pgvector"""
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """INSERT INTO document_chunks 
                   (document_name, chunk_text, chunk_vector, metadata) 
                   VALUES (%s, %s, %s, %s)""",
                (document_name, chunk_text, embedding, json.dumps({'chunk_num': chunk_num}))
            )
        conn.commit()
    except Exception as e:
        logger.error(f"Error storing chunk in database: {e}")
        raise