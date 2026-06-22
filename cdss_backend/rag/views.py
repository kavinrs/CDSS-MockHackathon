"""
RAG API Views: Simple API endpoint for medical guideline retrieval.
Follows Django REST Framework patterns from patient_management/views.py
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .vector_store import VectorStore
from .rag_retriever import RAGRetriever


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rag_query_view(request):
    """
    RAG query endpoint for retrieving relevant medical guidelines.
    
    Endpoint: POST /api/rag/query/
    
    Request body:
    {
        "query": "diabetes management guidelines"
    }
    
    Returns top 5 most relevant clinical guideline excerpts with source information.
    
    Requirements: 7.1-7.4, 17.6
    """
    # Extract query from request body
    query = request.data.get('query', '').strip()
    
    if not query:
        return Response(
            {'error': 'Query is required. Please provide a clinical query string.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Initialize VectorStore and RAGRetriever
        vector_store = VectorStore(persist_directory="./chroma_db")
        vector_store.initialize_collection(collection_name="medical_guidelines")
        
        # Create retriever and perform query
        retriever = RAGRetriever(vector_store)
        results = retriever.retrieve(query=query, top_k=5)
        
        # Handle empty results
        if not results:
            return Response({
                'query': query,
                'results': [],
                'count': 0,
                'message': 'No relevant guidelines found for this query. The RAG index may be empty or query may be too specific.'
            }, status=status.HTTP_200_OK)
        
        # Format results for response
        formatted_results = []
        for i, result in enumerate(results, 1):
            formatted_results.append({
                'rank': i,
                'text': result['text'],
                'source_filename': result['source_filename'],
                'relevance_score': round(1.0 - result['distance'], 4)  # Convert distance to similarity score
            })
        
        return Response({
            'query': query,
            'results': formatted_results,
            'count': len(formatted_results),
            'message': f'Retrieved {len(formatted_results)} relevant guideline excerpts'
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        # Handle errors gracefully
        return Response(
            {
                'error': 'Failed to retrieve guidelines',
                'details': str(e),
                'message': 'There was an error processing your query. Please ensure the RAG system is properly initialized.'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
