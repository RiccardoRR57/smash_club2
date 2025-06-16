from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from booking.models import Court, Booking, InvitedPlayer
from django.urls import reverse
from django.test import Client


class InvitePlayerMethodTest(TestCase):
    """
    Complete test of the invite_player method of the Booking model
    Black-box approach: we test all possible inputs and the expected behaviors
    """
    
    def setUp(self):
        """Test data setup"""
        # Create users for testing
        self.booking_owner = User.objects.create_user(
            username='owner',
            email='owner@test.com',
            password='testpass123'
        )
        
        self.valid_invitee = User.objects.create_user(
            username='player1',
            email='player1@test.com', 
            password='testpass123'
        )
        
        self.another_user = User.objects.create_user(
            username='player2',
            email='player2@test.com',
            password='testpass123'
        )
        
        # Create court
        self.court = Court.objects.create(
            name='Test Court',
            surface='clay',
            description='Court for testing',
            is_active=True
        )
        
        # Create base booking
        future_time = timezone.now() + timedelta(days=1)
        future_time = future_time.replace(minute=0, second=0, microsecond=0)  # Set a specific time
        self.booking = Booking.objects.create(
            court=self.court,
            user=self.booking_owner,
            start_time=future_time,
            end_time=future_time + timedelta(hours=1),
            cancellable_until=future_time - timedelta(days=1)
        )

    # === VALID CASE TESTS ===
    
    def test_invite_player_valid_input_success(self):
        """
        Test Case 1: Valid input - inviting a different user from the owner
        Expected: Successful creation of InvitedPlayer with status 'pending'
        """
        # Perform the invitation
        result = self.booking.invite_player(self.valid_invitee)
        
        # Verify that the result is an InvitedPlayer object
        self.assertIsInstance(result, InvitedPlayer)
        
        # Verify the data of the created invitation
        self.assertEqual(result.booking, self.booking)
        self.assertEqual(result.user, self.valid_invitee)
        self.assertEqual(result.status, 'pending')
        
        # Verify database persistence
        saved_invitation = InvitedPlayer.objects.get(
            booking=self.booking, 
            user=self.valid_invitee
        )
        self.assertEqual(saved_invitation.status, 'pending')
        
        # Verify creation timestamp
        self.assertIsNotNone(result.invited_at)

    def test_invite_player_multiple_different_users(self):
        """
        Test Case 2: Inviting multiple different users to the same booking
        Expected: All invitations should be created successfully
        """
        # Create a third user
        user3 = User.objects.create_user(
            username='player3',
            password='testpass123'
        )
        
        # Invite all users
        invitation1 = self.booking.invite_player(self.valid_invitee)
        invitation2 = self.booking.invite_player(self.another_user)
        invitation3 = self.booking.invite_player(user3)
        
        # Verify that all invitations have been created
        self.assertIsNotNone(invitation1)
        self.assertIsNotNone(invitation2)
        self.assertIsNotNone(invitation3)
        
        # Verify the total count of invitations
        total_invitations = InvitedPlayer.objects.filter(booking=self.booking).count()
        self.assertEqual(total_invitations, 3)
        
        # Verify that all have a 'pending' status
        for invitation in [invitation1, invitation2, invitation3]:
            self.assertEqual(invitation.status, 'pending')

    # === INVALID CASE TESTS ===
    
    def test_invite_player_self_invitation_error(self):
        """
        Test Case 3: Invalid input - attempt to invite oneself
        Expected: ValueError with a specific message
        """
        with self.assertRaises(ValueError) as context:
            self.booking.invite_player(self.booking_owner)
        
        # Verify the specific error message
        expected_message = "You cannot invite yourself to your own booking."
        self.assertEqual(str(context.exception), expected_message)
        
        # Verify that no invitation was created
        invitations_count = InvitedPlayer.objects.filter(
            booking=self.booking,
            user=self.booking_owner
        ).count()
        self.assertEqual(invitations_count, 0)

    def test_invite_player_duplicate_invitation_error(self):
        """
        Test Case 4: Invalid input - duplicate invitation
        Expected: ValueError with a message that includes the username
        """
        # First invitation (valid)
        first_invitation = self.booking.invite_player(self.valid_invitee)
        self.assertIsNotNone(first_invitation)
        
        # Second invitation (duplicate) - should fail
        with self.assertRaises(ValueError) as context:
            self.booking.invite_player(self.valid_invitee)
        
        # Verify the specific error message
        expected_message = f"{self.valid_invitee.username} is already invited."
        self.assertEqual(str(context.exception), expected_message)
        
        # Verify that there is still only one invitation in the database
        invitations_count = InvitedPlayer.objects.filter(
            booking=self.booking,
            user=self.valid_invitee
        ).count()
        self.assertEqual(invitations_count, 1)

    def test_invite_player_none_user_error(self):
        """
        Test Case 5: Invalid input - user = None
        Expected: AttributeError or defined behavior
        """
        with self.assertRaises(AttributeError):
            self.booking.invite_player(None)

    # === ARCHITECTURAL CONSISTENCY TESTS ===
    
    def test_invite_player_database_integrity(self):
        """
        Test Case 6: Check database integrity and relationships
        Expected: Correct foreign key relationships, constraints respected
        """
        invitation = self.booking.invite_player(self.valid_invitee)
        
        # Verify foreign key relationships
        self.assertEqual(invitation.booking.id, self.booking.id)
        self.assertEqual(invitation.user.id, self.valid_invitee.id)
        
        # Verify that the invitation is accessible from the booking
        booking_invitations = self.booking.invited_players.all()
        self.assertIn(invitation, booking_invitations)
        
        # Verify that the invitation is accessible from the user
        user_invitations = InvitedPlayer.objects.filter(user=self.valid_invitee)
        self.assertIn(invitation, user_invitations)

    def test_invite_player_status_consistency(self):
        """
        Test Case 7: Check status consistency
        Expected: Always 'pending' for new invitations
        """
        invitation = self.booking.invite_player(self.valid_invitee)
        
        # Verify initial status
        self.assertEqual(invitation.status, 'pending')
        
        # Verify that the status is the same in the database
        db_invitation = InvitedPlayer.objects.get(id=invitation.id)
        self.assertEqual(db_invitation.status, 'pending')
        
        # Verify that the status is among the allowed values
        valid_statuses = ['pending', 'accepted', 'declined']
        self.assertIn(invitation.status, valid_statuses)

    def test_invite_player_return_value_consistency(self):
        """
        Test Case 8: Check return value consistency
        Expected: Always an InvitedPlayer object with correct data
        """
        invitation = self.booking.invite_player(self.valid_invitee)
        
        # Verify the return type
        self.assertIsInstance(invitation, InvitedPlayer)
        
        # Verify that it has all the necessary attributes
        self.assertTrue(hasattr(invitation, 'id'))
        self.assertTrue(hasattr(invitation, 'booking'))
        self.assertTrue(hasattr(invitation, 'user'))
        self.assertTrue(hasattr(invitation, 'status'))
        self.assertTrue(hasattr(invitation, 'invited_at'))
        
        # Verify that the ID is valid (not None)
        self.assertIsNotNone(invitation.id)

    # === EDGE CASE TESTS ===
    
    def test_invite_player_after_status_change(self):
        """
        Test Case 9: Edge case - invitation after a previous invitation was declined
        Expected: Should fail because the invitation still exists
        """
        # Create initial invitation
        invitation = self.booking.invite_player(self.valid_invitee)
        
        # Change the status to 'declined'
        invitation.status = 'declined'
        invitation.save()
        
        # Attempt a new invitation - should fail because the invitation still exists
        with self.assertRaises(ValueError):
            self.booking.invite_player(self.valid_invitee)

    def test_invite_player_with_different_booking_same_user(self):
        """
        Test Case 10: Edge case - same user invited to different bookings
        Expected: Should work correctly
        """
        # Create a second booking
        future_time = timezone.now() + timedelta(days=2)
        future_time = future_time.replace(minute=0, second=0, microsecond=0)  # Set a specific time
        booking2 = Booking.objects.create(
            court=self.court,
            user=self.booking_owner,
            start_time=future_time,
            end_time=future_time + timedelta(hours=1),
            cancellable_until=future_time - timedelta(days=1)
        )
        
        # Invite the same user to both bookings
        invitation1 = self.booking.invite_player(self.valid_invitee)
        invitation2 = booking2.invite_player(self.valid_invitee)
        
        # Verify that both invitations have been created
        self.assertIsNotNone(invitation1)
        self.assertIsNotNone(invitation2)
        self.assertNotEqual(invitation1.id, invitation2.id)
        
        # Verify that the user has 2 total invitations
        user_invitations = InvitedPlayer.objects.filter(user=self.valid_invitee).count()
        self.assertEqual(user_invitations, 2)

    # === PERFORMANCE AND CONCURRENCY TESTS ===
    
    def test_invite_player_concurrent_invitations(self):
        """
        Test Case 11: Simulate concurrent invitations
        Expected: Only one should succeed
        """
        # This test simulates a concurrency situation
        # In a real environment, you would use threading or async
        
        # First invitation
        invitation1 = self.booking.invite_player(self.valid_invitee)
        self.assertIsNotNone(invitation1)
        
        # Verify that subsequent invitations fail
        with self.assertRaises(ValueError):
            self.booking.invite_player(self.valid_invitee)
        
        # Verify that there is only one invitation
        total_invitations = InvitedPlayer.objects.filter(
            booking=self.booking,
            user=self.valid_invitee
        ).count()
        self.assertEqual(total_invitations, 1)

    def tearDown(self):
        """Cleanup after every test"""
        # Django's TestCase automatically manages database cleanup
        # But we can add custom cleanup if needed
        pass

class BookingViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        court = Court.objects.create(
            name='Test Court',
            surface='clay',
            description='Court for testing',
            is_active=True
        )
        future_time = timezone.now() + timedelta(days=1)
        future_time = future_time.replace(minute=0, second=0, microsecond=0)
        Booking.objects.create(
            court=court,
            user=self.user,
            start_time=future_time,
            end_time=future_time + timedelta(hours=1),
            cancellable_until=future_time - timedelta(days=1)
        )

    def test_booking_list_view(self):
        # Verify redirect if not logged in
        response = self.client.get(reverse('booking:my_bookings'))
        self.assertNotEqual(response.status_code, 200)

        # Login
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('booking:my_bookings'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Court')