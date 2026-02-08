"""Conversation service for CRUD operations."""

from datetime import datetime
from typing import List, Optional
from uuid import uuid4
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database.models import Conversation, Message, User
from app.orchestration.state import Message as StateMessage


class ConversationService:
    """Service for managing conversations and messages."""
    
    @staticmethod
    def get_or_create_user(db: Session, username: str) -> User:
        """
        Get existing user or create new one.
        
        Args:
            db: Database session
            username: Username
            
        Returns:
            User object
        """
        user = db.query(User).filter(User.username == username).first()
        if not user:
            user = User(id=str(uuid4()), username=username)
            db.add(user)
            db.commit()
            db.refresh(user)
        return user
    
    @staticmethod
    def create_conversation(
        db: Session,
        user_id: str,
        title: Optional[str] = None
    ) -> Conversation:
        """
        Create a new conversation.
        
        Args:
            db: Database session
            user_id: User ID
            title: Optional conversation title
            
        Returns:
            Created conversation
        """
        conversation = Conversation(
            id=str(uuid4()),
            user_id=user_id,
            title=title or f"Conversation {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        return conversation
    
    @staticmethod
    def get_conversation(db: Session, conversation_id: str) -> Optional[Conversation]:
        """
        Get conversation by ID.
        
        Args:
            db: Database session
            conversation_id: Conversation ID
            
        Returns:
            Conversation or None
        """
        return db.query(Conversation).filter(Conversation.id == conversation_id).first()
    
    @staticmethod
    def list_conversations(
        db: Session,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Conversation]:
        """
        List user's conversations.
        
        Args:
            db: Database session
            user_id: User ID
            limit: Maximum number of conversations
            offset: Offset for pagination
            
        Returns:
            List of conversations
        """
        return db.query(Conversation)\
            .filter(Conversation.user_id == user_id)\
            .order_by(desc(Conversation.updated_at))\
            .offset(offset)\
            .limit(limit)\
            .all()
    
    @staticmethod
    def add_message(
        db: Session,
        conversation_id: str,
        role: str,
        content: str,
        agent: Optional[str] = None,
        confidence: Optional[float] = None,
        processing_time_ms: Optional[float] = None,
        extra_data: Optional[dict] = None
    ) -> Message:
        """
        Add a message to a conversation.
        
        Args:
            db: Database session
            conversation_id: Conversation ID
            role: Message role ('user' or 'assistant')
            content: Message content
            agent: Agent that generated the response (optional)
            confidence: Router confidence score (optional)
            processing_time_ms: Processing time in milliseconds (optional)
            extra_data: Additional metadata (optional)
            
        Returns:
            Created message
        """
        message = Message(
            id=str(uuid4()),
            conversation_id=conversation_id,
            role=role,
            content=content,
            agent=agent,
            confidence=confidence,
            processing_time_ms=processing_time_ms,
            extra_data=extra_data or {}
        )
        db.add(message)
        
        # Update conversation updated_at
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if conversation:
            conversation.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(message)
        return message
    
    @staticmethod
    def get_conversation_messages(
        db: Session,
        conversation_id: str,
        limit: Optional[int] = None
    ) -> List[Message]:
        """
        Get messages for a conversation.
        
        Args:
            db: Database session
            conversation_id: Conversation ID
            limit: Optional limit on number of messages
            
        Returns:
            List of messages
        """
        query = db.query(Message)\
            .filter(Message.conversation_id == conversation_id)\
            .order_by(Message.timestamp)
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @staticmethod
    def delete_conversation(db: Session, conversation_id: str) -> bool:
        """
        Delete a conversation and all its messages.
        
        Args:
            db: Database session
            conversation_id: Conversation ID
            
        Returns:
            True if deleted, False if not found
        """
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if conversation:
            db.delete(conversation)
            db.commit()
            return True
        return False
    
    @staticmethod
    def messages_to_state_format(messages: List[Message]) -> List[StateMessage]:
        """
        Convert database messages to state message format.
        
        Args:
            messages: List of database messages
            
        Returns:
            List of state messages
        """
        return [
            StateMessage(
                role=msg.role,
                content=msg.content,
                agent=msg.agent,
                timestamp=msg.timestamp.isoformat()
            )
            for msg in messages
        ]
