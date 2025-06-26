import os
import json
import logging
import pg8000
from botocore.exceptions import ClientError
import boto3

# Initialize logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

def lambda_handler(event, context):
    try:
        # Parse query from API Gateway event
        body = json.loads(event['body'])
        query = body.get('query', '')
        
        if not query:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Query parameter is required'})
            }
        
        logger.info(f"Processing search query: {query}")
        
        # Generate embedding for the query
        query_embedding = generate_embedding(query)
        
        # Connect to PostgreSQL
        conn = connect_to_postgresql()
        
        # Perform similarity search
        results = search_similar_chunks(conn, query_embedding, limit=5)
        
        logger.info(f"Found {len(results)} similar chunks")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'results': [
                    {
                        'document_name': r[0],
                        'chunk_text': r[1],
                        'similarity_score': float(r[2]),
                        'metadata': r[3]
                    } for r in results
                ]
            })
        }
        
    except Exception as e:
        logger.error(f"Error processing search: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

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

def search_similar_chunks(conn, query_embedding: List[float], limit: int = 5):
    """Search for similar chunks using pgvector cosine similarity"""
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """SELECT document_name, chunk_text, 
                         1 - (chunk_vector <=> %s) as similarity,
                         metadata
                   FROM document_chunks
                   ORDER BY chunk_vector <=> %s
                   LIMIT %s""",
                (query_embedding, query_embedding, limit)
            )
            return cursor.fetchall()
    except Exception as e:
        logger.error(f"Error searching similar chunks: {e}")
        raise