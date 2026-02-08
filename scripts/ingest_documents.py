#!/usr/bin/env python3
"""Document Ingestion Script

Manual script for ingesting documents into agent-specific vector stores.

Usage:
    python scripts/ingest_documents.py --domain professional --file path/to/document.pdf
    python scripts/ingest_documents.py --domain communication --directory data/documents/communication/
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.rag import get_ingestion_pipeline, AGENT_DOMAINS


def main():
    parser = argparse.ArgumentParser(description="Ingest documents into RAG vector stores")
    parser.add_argument(
        "--domain",
        required=True,
        choices=AGENT_DOMAINS,
        help="Agent domain to ingest into"
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Path to single document file"
    )
    parser.add_argument(
        "--directory",
        type=str,
        help="Path to directory of documents"
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Recursively search directory"
    )
    parser.add_argument(
        "--source",
        type=str,
        help="Source identifier for documents"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.file and not args.directory:
        parser.error("Either --file or --directory must be specified")
    
    if args.file and args.directory:
        parser.error("Cannot specify both --file and --directory")
    
    # Initialize pipeline
    pipeline = get_ingestion_pipeline()
    
    try:
        if args.file:
            # Ingest single file
            print(f"Ingesting file: {args.file}")
            print(f"Domain: {args.domain}")
            
            chunks = pipeline.ingest_document(
                file_path=args.file,
                domain=args.domain,
                source=args.source
            )
            
            print(f"✓ Successfully ingested {chunks} chunks")
            
        elif args.directory:
            # Ingest directory
            print(f"Ingesting directory: {args.directory}")
            print(f"Domain: {args.domain}")
            print(f"Recursive: {args.recursive}")
            
            results = pipeline.ingest_directory(
                directory_path=args.directory,
                domain=args.domain,
                recursive=args.recursive
            )
            
            print(f"\n✓ Ingestion complete!")
            print(f"  Files processed: {results['files_processed']}")
            print(f"  Total chunks: {results['total_chunks']}")
            
            # Show file details
            if results['files']:
                print("\nFile details:")
                for file_info in results['files']:
                    status = file_info['status']
                    path = file_info['path']
                    
                    if status == 'success':
                        chunks = file_info['chunks']
                        print(f"  ✓ {Path(path).name}: {chunks} chunks")
                    else:
                        error = file_info.get('error', 'Unknown error')
                        print(f"  ✗ {Path(path).name}: {error}")
        
        print(f"\nDocuments are now available to the {args.domain} agent!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
