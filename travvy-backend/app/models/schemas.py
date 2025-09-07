"""
Pydantic Models and Schemas

This module contains all Pydantic models for request/response validation
and data serialization based on the LLD specifications.
"""

from pydantic import BaseModel, validator, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date
from enum import Enum


# ==================== Enums ====================

class TripStatus(str, Enum):
    """Trip status enumeration."""
    PLANNING = "planning"
    GENERATING = "generating"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class BudgetRange(str, Enum):
    """Budget range enumeration."""
    BUDGET = "budget"
    MODERATE = "moderate"
    LUXURY = "luxury"


class CollaboratorRole(str, Enum):
    """Collaborator role enumeration."""
    OWNER = "owner"
    EDITOR = "editor"
    VIEWER = "viewer"


# ==================== Core Models ====================

class GeoPoint(BaseModel):
    """Geographical coordinates."""
    lat: float
    lng: float


class Location(BaseModel):
    """Location information."""
    name: str
    placeId: Optional[str] = ""
    coordinates: Optional[GeoPoint] = None
    address: Optional[str] = ""
    country: Optional[str] = ""
    city: Optional[str] = ""


class Destination(BaseModel):
    """Trip destination information."""
    name: str
    placeId: Optional[str] = ""
    coordinates: Optional[GeoPoint] = None
    country: Optional[str] = ""
    city: Optional[str] = ""


class DateRange(BaseModel):
    """Date range for trips."""
    startDate: datetime
    endDate: datetime
    duration: int = 0  # Days
    flexible: bool = False


class TravelerInfo(BaseModel):
    """Traveler information."""
    adults: int = Field(..., ge=1, le=20)
    children: int = Field(0, ge=0, le=10)
    infants: int = Field(0, ge=0, le=5)
    totalCount: int = 0
    
    @validator('totalCount', always=True)
    def calculate_total(cls, v, values):
        """Calculate total traveler count."""
        return values.get('adults', 0) + values.get('children', 0) + values.get('infants', 0)


class BudgetBreakdown(BaseModel):
    """Budget breakdown by category."""
    accommodation: float = 0
    transportation: float = 0
    food: float = 0
    activities: float = 0
    miscellaneous: float = 0


class Budget(BaseModel):
    """Trip budget information."""
    currency: str = Field(..., pattern="^[A-Z]{3}$")
    total: float = Field(..., gt=0)
    breakdown: BudgetBreakdown = BudgetBreakdown()


class AccessibilityInfo(BaseModel):
    """Accessibility information."""
    mobility: bool = False
    vision: bool = False
    hearing: bool = False


class UserPreferences(BaseModel):
    """User travel preferences."""
    budgetRange: BudgetRange = BudgetRange.MODERATE
    travelStyle: List[str] = []
    accommodationType: List[str] = []
    activityTypes: List[str] = []
    dietaryRestrictions: List[str] = []
    accessibility: AccessibilityInfo = AccessibilityInfo()


class UserProfile(BaseModel):
    """User profile information."""
    firstName: str = ""
    lastName: str = ""
    dateOfBirth: Optional[date] = None
    nationality: Optional[str] = None
    languages: List[str] = ["en"]


class TravelHistory(BaseModel):
    """User travel history."""
    totalTrips: int = 0
    countries: List[str] = []
    favoriteDestinations: List[str] = []
    averageBudget: float = 0
    preferredSeasons: List[str] = []


class User(BaseModel):
    """Complete user model."""
    uid: str
    email: str
    displayName: str = ""
    photoURL: Optional[str] = None
    profile: UserProfile = UserProfile()
    preferences: UserPreferences = UserPreferences()
    travelHistory: TravelHistory = TravelHistory()
    createdAt: datetime
    updatedAt: datetime
    lastActiveAt: datetime


class Collaborator(BaseModel):
    """Trip collaborator information."""
    role: CollaboratorRole
    joinedAt: datetime
    permissions: List[str] = []


class Activity(BaseModel):
    """Trip activity information."""
    activityId: str
    name: str
    description: str
    location: Location
    timing: Dict[str, Any] = {}
    pricing: Dict[str, Any] = {}
    category: str = ""
    rating: Optional[float] = None
    images: List[str] = []
    bookingInfo: Optional[Union[Dict[str, Any], str]] = None
    accessibility: AccessibilityInfo = AccessibilityInfo()
    tags: List[str] = []


class Meal(BaseModel):
    """Meal information for itinerary."""
    type: str  # breakfast, lunch, dinner
    restaurant: str
    cuisine: str
    budgetRange: Optional[str] = "moderate"
    location: Optional[Location] = None
    specialties: List[str] = []


class Transportation(BaseModel):
    """Transportation information."""
    fromLocation: str
    toLocation: str
    method: str
    cost: float = 0
    durationMinutes: int = 0
    bookingInfo: Optional[str] = None


class Accommodation(BaseModel):
    """Accommodation details for a day."""
    name: str
    type: Optional[str] = "hotel"  # hotel, airbnb, hostel, etc. - default for backward compatibility
    rating: Optional[float] = None
    priceRange: Optional[str] = None
    pricing: Optional[float] = None  # Legacy field for backward compatibility
    location: Optional[Location] = None
    amenities: List[str] = []
    bookingInfo: Optional[str] = None


class DayPlan(BaseModel):
    """Single day itinerary plan."""
    day: int
    date: datetime
    theme: Optional[str] = None
    activities: List[Activity] = []
    transportation: List[Transportation] = []
    meals: List[Meal] = []
    accommodation: Optional[Accommodation] = None
    totalBudget: float = 0
    notes: Optional[str] = None


class HotelOption(BaseModel):
    """Hotel recommendation."""
    hotelId: str
    name: str
    description: str
    location: Location
    rating: float = 0
    pricePerNight: float = 0
    amenities: List[str] = []
    images: List[str] = []
    bookingUrl: Optional[str] = None


class AIGeneration(BaseModel):
    """AI generation metadata."""
    conversationId: str = ""
    prompts: List[Dict[str, Any]] = []
    generatedAt: Optional[datetime] = None
    model: str = ""
    confidence: float = 0.0
    userFeedback: Optional[Dict[str, Any]] = None


class TripMetadata(BaseModel):
    """Trip metadata information."""
    title: str
    description: Optional[str] = None
    destination: Destination
    dates: DateRange
    travelers: TravelerInfo
    budget: Budget


class Trip(BaseModel):
    """Complete trip model."""
    tripId: str
    createdBy: str
    collaborators: Dict[str, Collaborator] = {}
    metadata: TripMetadata
    aiGeneration: AIGeneration = AIGeneration()
    itinerary: List[DayPlan] = []
    hotels: List[HotelOption] = []
    status: TripStatus = TripStatus.PLANNING
    version: int = 1
    createdAt: datetime
    updatedAt: datetime


# ==================== Request Models ====================

class TripCreateRequest(BaseModel):
    """Request model for creating a trip."""
    destination: str = Field(..., min_length=2, max_length=100)
    start_date: date
    end_date: date
    budget: float = Field(..., gt=0, le=100000)
    currency: str = Field(..., pattern="^[A-Z]{3}$")
    travelers: Dict[str, int]
    preferences: Optional[Dict[str, Any]] = {}
    conversation_context: Optional[Dict[str, Any]] = {}
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('End date must be after start date')
        return v


class TripUpdateRequest(BaseModel):
    """Request model for updating a trip."""
    title: Optional[str] = None
    description: Optional[str] = None
    dates: Optional[DateRange] = None
    budget: Optional[Budget] = None
    travelers: Optional[TravelerInfo] = None
    version: int


class TripOptimizationRequest(BaseModel):
    """Request model for trip optimization."""
    criteria: str = "time"  # time, cost, experience
    constraints: Dict[str, Any] = {}


class GoogleTokenRequest(BaseModel):
    """Request model for Google OAuth token."""
    id_token: str = Field(..., min_length=10)


class UserLoginRequest(BaseModel):
    """Request model for user login."""
    email: str = Field(..., pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    password: str = Field(..., min_length=8)


class UserRegistrationRequest(BaseModel):
    """Request model for user registration."""
    email: str = Field(..., pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    password: str = Field(..., min_length=8)
    display_name: str = Field(..., min_length=2, max_length=50)
    profile: Optional[UserProfile] = UserProfile()


class UserProfileUpdate(BaseModel):
    """Request model for updating user profile."""
    displayName: Optional[str] = None
    profile: Optional[UserProfile] = None


class UserPreferencesUpdate(BaseModel):
    """Request model for updating user preferences."""
    budgetRange: Optional[BudgetRange] = None
    travelStyle: Optional[List[str]] = None
    accommodationType: Optional[List[str]] = None
    activityTypes: Optional[List[str]] = None
    dietaryRestrictions: Optional[List[str]] = None
    accessibility: Optional[AccessibilityInfo] = None


class TokenRefreshRequest(BaseModel):
    """Request model for token refresh."""
    refresh_token: str


class ConversationStartRequest(BaseModel):
    """Request model for AI conversation."""
    message: str = Field(..., min_length=1, max_length=5000)
    conversation_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = {}


class CollaborationInvite(BaseModel):
    """Request model for collaboration invitation."""
    email: str = Field(..., pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    role: CollaboratorRole = CollaboratorRole.VIEWER
    message: Optional[str] = Field(None, max_length=500)


class VoteCreateRequest(BaseModel):
    """Request model for creating a vote."""
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., max_length=1000)
    options: List[str] = Field(..., min_items=2, max_items=10)
    type: str = "single"  # single, multiple, ranking
    deadline: Optional[datetime] = None


class VoteCastRequest(BaseModel):
    """Request model for casting a vote."""
    selections: List[str] = Field(..., min_items=1)


class NotificationPreferences(BaseModel):
    """Notification preferences model."""
    push_notifications: bool = True
    email_notifications: bool = True
    trip_updates: bool = True
    collaboration_invites: bool = True
    marketing: bool = False


# ==================== Response Models ====================

class TripResponse(BaseModel):
    """Response model for trip creation."""
    trip_id: str
    status: str
    message: Optional[str] = None
    estimated_completion: Optional[str] = None
    task_id: Optional[str] = None


class TripDetail(BaseModel):
    """Detailed trip response model."""
    # Use the same structure as Trip model
    tripId: str
    createdBy: str
    collaborators: Dict[str, Collaborator] = {}
    metadata: TripMetadata
    aiGeneration: AIGeneration = AIGeneration()
    itinerary: List[DayPlan] = []
    hotels: List[HotelOption] = []
    status: TripStatus = TripStatus.PLANNING
    version: int = 1
    createdAt: datetime
    updatedAt: datetime


class TripListResponse(BaseModel):
    """Response model for trip list."""
    trips: List[Trip]
    total: int
    has_more: bool
    offset: int
    limit: int


class AuthResponse(BaseModel):
    """Authentication response model."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: User


class ConversationResponse(BaseModel):
    """AI conversation response model."""
    conversation_id: str
    response: str
    suggested_actions: List[str] = []
    context: Dict[str, Any] = {}
    confidence_score: float = 0.0


class ImageAnalysisResponse(BaseModel):
    """Image analysis response model."""
    landmarks: List[Dict[str, Any]] = []
    suggestions: List[Dict[str, Any]] = []
    confidence: float = 0.0


class VoiceProcessingResponse(BaseModel):
    """Voice processing response model."""
    transcription: str
    intent: str
    entities: Dict[str, Any] = {}
    suggested_response: str
    confidence: float = 0.0


class AITaskStatusResponse(BaseModel):
    """AI task status response model."""
    task_id: str
    status: str
    progress: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    message: str


class CollaborationSession(BaseModel):
    """Collaboration session model."""
    sessionId: str
    tripId: str
    activeUsers: Dict[str, Dict[str, Any]] = {}
    operations: List[Dict[str, Any]] = []
    votes: Dict[str, Dict[str, Any]] = {}
    chat: List[Dict[str, Any]] = []
    createdAt: datetime
    expiresAt: datetime
