from django.urls import path
from .views import RegisterView, LoginView, CreateElectionView, ListCandidatesView, VoteView, ElectionResultsView, CandidateRegistrationView, ListCandidatesByPositionView, LogoutView


urlpatterns = [
    # User Authentication Endpoints
    path('auth/register/', RegisterView.as_view(), name='register'),  # User Registration
    path('auth/login/', LoginView.as_view(), name='login'),  # User Login
    
    # Election Endpoints
    path('elections/create/', CreateElectionView.as_view(), name='create-election'),  # Create an Election
    path('elections/<int:election_id>/results/', ElectionResultsView.as_view(), name='election-results'),  # View Election Results

    # Candidate Endpoints
    path('candidates/', ListCandidatesView.as_view(), name='list-candidates'),  # List all Candidates
    path('candidates/register/', CandidateRegistrationView.as_view(), name='register-candidate'),  # Register as a Candidate

    # Voting Endpoints
    path('elections/<int:election_id>/positions/<int:position_id>/candidates/vote/', VoteView.as_view(), name='cast_vote'),
    path('elections/<int:election_id>/positions/<int:position_id>/candidates/', ListCandidatesByPositionView.as_view(), name='list_candidates_by_position'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
]
