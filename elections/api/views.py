from django.contrib.auth.models import User
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from .serializers import UserSerializer, LoginSerializer
from elections.models import Election, Candidate, Vote
from .serializers import ElectionSerializer, CandidateSerializer, VoteSerializer, PositionSerializer, UserVoteHistorySerializer
from rest_framework.exceptions import ValidationError
from django.db import models

# User Registration View
# class RegisterView(generics.CreateAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)  # This will raise a ValidationError if invalid
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            # Return a structured error response
            return Response({"errors": e.detail}, status=status.HTTP_400_BAD_REQUEST)

# Login View
class LoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer  # Specify the serializer here

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # If credentials are valid, generate a token
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'token': token.key,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.username
        })

# Create Election View
class CreateElectionView(generics.CreateAPIView):
    queryset = Election.objects.all()
    serializer_class = ElectionSerializer
    permission_classes = [IsAuthenticated]  # Require authentication

# List Candidates View
class ListCandidatesView(generics.ListAPIView):
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer
    permission_classes = [IsAuthenticated]  # Require authentication


class VoteView(generics.CreateAPIView):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer  # Use the updated VoteSerializer
    permission_classes = [IsAuthenticated]  # Require authentication for voting

    def post(self, request, *args, **kwargs):
        candidate_id = request.data.get('candidate')  # Get the candidate ID from the request
        election_id = kwargs['election_id']
        position_id = kwargs['position_id']
        voter = request.user

        # Validate that the election is active
        election_instance = Election.objects.get(id=election_id)
        if election_instance.status != 'active':
            raise ValidationError("Voting is not allowed at this time.")

        # Ensure the user has not voted for this position already
        if Vote.objects.filter(election=election_instance, voter=voter, position__id=position_id).exists():
            raise ValidationError("You have already voted for this position.")

        # Ensure the candidate belongs to the specified position
        try:
            candidate = Candidate.objects.get(id=candidate_id, position_id=position_id)
        except Candidate.DoesNotExist:
            raise ValidationError("The selected candidate does not belong to the specified position.")

        # Create a new vote
        Vote.objects.create(election=election_instance, voter=voter, position_id=position_id, candidate=candidate)

        # Increment the vote count for the candidate
        candidate.vote_count += 1
        candidate.save()

        return Response({"message": "Vote cast successfully."}, status=201)


from django.db.models import Count
from elections.models import Vote, Position, Candidate

class ElectionResultsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]  # Require authentication

    def get_queryset(self):
        election_id = self.kwargs['election_id']
        return Vote.objects.filter(election_id=election_id)

    def list(self, request, *args, **kwargs):
        election_id = self.kwargs['election_id']
        
        # Get all positions related to the election
        positions = Position.objects.all()
        
        results = []
        
        for position in positions:
            # Get candidates for the current position
            candidates = Candidate.objects.filter(position=position)
            
            # Get vote counts for each candidate in the current position
            candidate_votes = (
                Vote.objects.filter(election_id=election_id, position=position)
                .values('candidate')
                .annotate(vote_count=Count('id'))
            )
            
            # Create a dictionary to hold candidate names and their vote counts
            candidate_results = {}
            for candidate_vote in candidate_votes:
                candidate_id = candidate_vote['candidate']
                vote_count = candidate_vote['vote_count']
                candidate = candidates.get(id=candidate_id)
                candidate_results[candidate.candidate_name] = vote_count
            
            # Append the position and its candidates' results to the results list
            results.append({
                'position': position.name,
                'candidates': candidate_results
            })
        
        return Response(results)

# Candidate Registration View
class CandidateRegistrationView(generics.CreateAPIView):
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer
    permission_classes = [IsAuthenticated]  # Require authentication

    def perform_create(self, serializer):
        # Optionally, ensure that the user can only register once for a position
        user = self.request.user
        position = serializer.validated_data['position']

        if Candidate.objects.filter(user=user, position=position).exists():
            raise ValidationError("You have already registered for this position.")

        serializer.save(user=user)

class ListCandidatesByPositionView(generics.ListAPIView):
    serializer_class = CandidateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # election_id = self.kwargs['election_id']
        position_id = self.kwargs['position_id']
        # Filter candidates for the election and position
        return Candidate.objects.filter(position_id=position_id)

    def list(self, request, *args, **kwargs):
        candidates = self.get_queryset()
        serializer = CandidateSerializer(candidates, many=True)
        return Response(serializer.data)


class ListPositionsView(generics.ListAPIView):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    permission_classes = [IsAuthenticated]  # Require authentication to view positions

# views.py
class UserVoteHistoryView(generics.ListAPIView):
    serializer_class = UserVoteHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filter votes for the currently authenticated user
        return Vote.objects.filter(voter=self.request.user).select_related(
            'position', 'candidate', 'election'
        ).order_by('-created_at')

from rest_framework.views import APIView
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        try:
            # Get the token for the authenticated user
            token = Token.objects.get(user=request.user)
            token.delete()  # Delete the token
            return Response({"detail": "Successfully logged out."}, status=status.HTTP_204_NO_CONTENT)
        except Token.DoesNotExist:
            return Response({"detail": "Token does not exist."}, status=status.HTTP_400_BAD_REQUEST)